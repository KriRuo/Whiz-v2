"""
Queue-based transcription service using multiprocessing.

This module isolates faster-whisper/ONNX runtime work from the PyQt process
to avoid threading/runtime conflicts while preserving a simple client API.
"""

from __future__ import annotations

import logging
import multiprocessing as mp
import tempfile
import time
import faulthandler
from queue import Empty
from typing import Any, Callable, Dict, Optional

from core.config import TIMEOUT_CONFIG, WHISPER_CONFIG

logger = logging.getLogger(__name__)

# region agent log
try:
    import json
    import os

    def _agent_debug_log(hypothesis_id: str, message: str, data: Dict[str, Any]) -> None:
        """
        Lightweight NDJSON logger for debugging faster-whisper worker startup.
        Writes to .cursor/debug.log in the project root.
        """
        try:
            ts_ms = int(time.time() * 1000)
            log_path = r"c:\Users\krir\Documents\Solutions\Whiz\.cursor\debug.log"
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            entry = {
                "id": f"log_{ts_ms}",
                "timestamp": ts_ms,
                "location": "core/transcription_service.py",
                "message": message,
                "data": data,
                "runId": "pre-fix",
                "hypothesisId": hypothesis_id,
            }
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            # Never let debug logging break normal execution
            pass
except Exception:
    def _agent_debug_log(hypothesis_id: str, message: str, data: Dict[str, Any]) -> None:  # type: ignore[no-redef]
        pass


def _safe_runtime_fingerprint() -> Dict[str, Any]:
    try:
        import os
        import platform
        import sys

        return {
            "python_version": sys.version.split()[0],
            "python_exe": sys.executable,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "cwd": os.getcwd(),
        }
    except Exception:
        return {}


def _safe_library_versions() -> Dict[str, Any]:
    """
    Best-effort version capture for faster-whisper stack. Must be safe to call
    from worker process.
    """
    versions: Dict[str, Any] = {}
    try:
        import importlib

        fw = importlib.import_module("faster_whisper")
        versions["faster_whisper"] = getattr(fw, "__version__", None)
    except Exception:
        pass

    for pkg in ("ctranslate2", "tokenizers", "huggingface_hub"):
        try:
            import importlib

            mod = importlib.import_module(pkg)
            versions[pkg] = getattr(mod, "__version__", None)
        except Exception:
            continue

    return versions


def _safe_thread_fingerprint() -> Dict[str, Any]:
    try:
        import threading

        cur = threading.current_thread()
        return {
            "name": cur.name,
            "ident": cur.ident,
            "is_main": cur is threading.main_thread(),
        }
    except Exception:
        return {}


def _decode_windows_exitcode(exitcode: Optional[int]) -> str:
    if exitcode is None:
        return "None"
    unsigned = exitcode & 0xFFFFFFFF
    if unsigned == 0xC0000005:
        return f"{exitcode} (0x{unsigned:08X} ACCESS_VIOLATION)"
    return f"{exitcode} (0x{unsigned:08X})"
# endregion


def _transcription_worker_main(
    request_queue: "mp.queues.Queue",
    response_queue: "mp.queues.Queue",
    config: Dict[str, Any],
) -> None:
    """Worker process entrypoint for transcription requests."""
    model = None
    crash_log_path: Optional[str] = None

    try:
        pid = mp.current_process().pid if mp.current_process() else "unknown"
        crash_log_path = os.path.join(
            tempfile.gettempdir(),
            f"whiz_worker_crash_{pid}.log",
        )
    except Exception:
        crash_log_path = None

    def _stage(stage: str, payload: Optional[Dict[str, Any]] = None) -> None:
        if not crash_log_path:
            return
        try:
            with open(crash_log_path, "a", encoding="utf-8") as handle:
                data = payload or {}
                handle.write(
                    f"{time.time():.3f} | {stage} | {json.dumps(data, ensure_ascii=False)}\n"
                )
        except Exception:
            pass

    _stage("worker_entry")
    if crash_log_path:
        try:
            with open(crash_log_path, "a", encoding="utf-8") as handle:
                faulthandler.enable(file=handle, all_threads=True)
        except Exception:
            pass

    _agent_debug_log(
        "H1",
        "worker_main_start",
        {
            "pid": mp.current_process().pid if mp.current_process() else None,
            "config": {
                "model_name": config.get("model_name"),
                "device": config.get("device"),
                "compute_type": config.get("compute_type"),
            },
            "runtime": _safe_runtime_fingerprint(),
            "crash_log_path": crash_log_path,
        },
    )

    try:
        _stage("before_import_faster_whisper")
        from faster_whisper import WhisperModel
        _stage("after_import_faster_whisper", _safe_library_versions())
        _agent_debug_log("H1", "worker_import_ok", _safe_library_versions())

        _stage(
            "before_model_init",
            {
                "model_name": config.get("model_name", WHISPER_CONFIG.DEFAULT_MODEL),
                "device": config.get("device", "cpu"),
                "compute_type": config.get("compute_type", WHISPER_CONFIG.COMPUTE_TYPE_CPU),
                "cpu_threads": config.get("cpu_threads", 4),
                "num_workers": config.get("num_workers", 1),
            },
        )
        model = WhisperModel(
            config.get("model_name", WHISPER_CONFIG.DEFAULT_MODEL),
            device=config.get("device", "cpu"),
            compute_type=config.get("compute_type", WHISPER_CONFIG.COMPUTE_TYPE_CPU),
            cpu_threads=config.get("cpu_threads", 4),
            num_workers=config.get("num_workers", 1),
        )
        _stage("after_model_init")
        _agent_debug_log("H2", "worker_model_initialized", {})
        response_queue.put({"type": "ready"})
    except Exception as exc:
        _stage("model_init_exception", {"error": str(exc)})
        _agent_debug_log("H2", "worker_model_init_failed", {"error": str(exc)})
        response_queue.put({"type": "error", "error": f"Model init failed: {exc}"})
        return

    while True:
        try:
            request = request_queue.get(timeout=0.5)
        except Empty:
            continue
        except Exception as exc:
            response_queue.put({"type": "error", "error": f"Request queue error: {exc}"})
            continue

        if request is None:
            break

        request_id = request.get("request_id")
        audio_path = request.get("audio_path")
        language = request.get("language")
        temperature = request.get("temperature", WHISPER_CONFIG.DEFAULT_TEMPERATURE)
        speed_mode = request.get("speed_mode", True)

        try:
            if speed_mode:
                transcribe_params = {
                    "temperature": temperature,
                    "compression_ratio_threshold": 2.4,
                    "no_speech_threshold": 0.6,
                    "condition_on_previous_text": False,
                    "word_timestamps": False,
                    "without_timestamps": True,
                    "vad_filter": WHISPER_CONFIG.VAD_FILTER,
                    "beam_size": WHISPER_CONFIG.BEAM_SIZE,
                }
            else:
                transcribe_params = {
                    "temperature": temperature,
                    "condition_on_previous_text": True,
                    "word_timestamps": False,
                    "vad_filter": WHISPER_CONFIG.VAD_FILTER,
                    "beam_size": WHISPER_CONFIG.BEAM_SIZE,
                }

            if language and language != "auto":
                transcribe_params["language"] = language

            started_at = time.time()
            segments, info = model.transcribe(audio_path, **transcribe_params)
            segments_list = list(segments) if segments is not None else []
            text = " ".join(
                segment.text for segment in segments_list if segment is not None and hasattr(segment, "text")
            ).strip()

            response_queue.put(
                {
                    "type": "result",
                    "request_id": request_id,
                    "text": text,
                    "metadata": {
                        "duration": getattr(info, "duration", None),
                        "language": getattr(info, "language", None),
                        "language_probability": getattr(info, "language_probability", None),
                        "processing_seconds": time.time() - started_at,
                        "engine": "faster",
                        "model": config.get("model_name"),
                        "device": config.get("device"),
                    },
                }
            )
        except Exception as exc:
            response_queue.put(
                {
                    "type": "error",
                    "request_id": request_id,
                    "error": str(exc),
                }
            )


class TranscriptionService:
    """Client API for queue/process-based transcription."""

    def __init__(
        self,
        model_name: str,
        device: str,
        compute_type: str,
        worker_target: Optional[Callable[..., None]] = None,
    ):
        self.model_name = model_name
        self.device = device
        self.compute_type = compute_type
        self._worker_target = worker_target or _transcription_worker_main

        self._ctx = mp.get_context("spawn")
        self.request_queue: "mp.queues.Queue" = self._ctx.Queue()
        self.response_queue: "mp.queues.Queue" = self._ctx.Queue()
        self.worker_process: Optional[mp.Process] = None
        self.is_ready = False
        self._request_counter = 0

    def start(self, timeout_seconds: float = TIMEOUT_CONFIG.MODEL_LOADING_TIMEOUT) -> bool:
        """Start worker process and wait for readiness signal."""
        if self.worker_process is not None and self.worker_process.is_alive():
            return self.is_ready

        config = {
            "model_name": self.model_name,
            "device": self.device,
            "compute_type": self.compute_type,
        }

        _agent_debug_log(
            "H3",
            "service_start_spawning_worker",
            {"timeout_seconds": timeout_seconds, "config": config, "thread": _safe_thread_fingerprint()},
        )

        self.worker_process = self._ctx.Process(
            target=self._worker_target,
            args=(self.request_queue, self.response_queue, config),
            daemon=True,
        )
        self.worker_process.start()

        _agent_debug_log(
            "H3",
            "service_worker_started",
            {
                "pid": self.worker_process.pid,
                "alive": self.worker_process.is_alive(),
                "thread": _safe_thread_fingerprint(),
            },
        )

        try:
            response = self.response_queue.get(timeout=timeout_seconds)
        except Empty:
            pid = getattr(self.worker_process, "pid", None)
            alive = self.worker_process.is_alive() if self.worker_process else None
            exitcode = self.worker_process.exitcode if self.worker_process else None
            logger.error(
                "Transcription worker did not signal readiness before timeout "
                f"(pid={pid}, alive={alive}, exitcode={_decode_windows_exitcode(exitcode)})"
            )
            _agent_debug_log(
                "H4",
                "service_worker_timeout_waiting_ready",
                {
                    "pid": pid,
                    "alive": alive,
                    "exitcode": exitcode,
                    "decoded_exitcode": _decode_windows_exitcode(exitcode),
                },
            )
            self.stop()
            return False
        except Exception as exc:
            logger.error(f"Error waiting for worker readiness: {exc}")
            _agent_debug_log(
                "H4",
                "service_worker_wait_exception",
                {"error": str(exc)},
            )
            self.stop()
            return False

        if response.get("type") == "ready":
            self.is_ready = True
            _agent_debug_log(
                "H3",
                "service_worker_ready",
                {"pid": getattr(self.worker_process, "pid", None)},
            )
            return True

        logger.error(f"Worker failed to initialize: {response}")
        _agent_debug_log(
            "H4",
            "service_worker_failed_init",
            {"response": response},
        )
        self.stop()
        return False

    def transcribe(
        self,
        audio_path: str,
        language: Optional[str],
        temperature: float,
        speed_mode: bool,
        timeout_seconds: float = TIMEOUT_CONFIG.TRANSCRIPTION_TIMEOUT,
    ) -> Optional[Dict[str, Any]]:
        """Send a transcription request and wait for matching response."""
        if not self.is_ready or self.worker_process is None or not self.worker_process.is_alive():
            logger.error("Transcription worker not ready")
            return None

        self._request_counter += 1
        request_id = f"req_{self._request_counter}_{int(time.time() * 1000)}"
        payload = {
            "type": "transcribe",
            "request_id": request_id,
            "audio_path": audio_path,
            "language": language,
            "temperature": temperature,
            "speed_mode": speed_mode,
        }

        try:
            self.request_queue.put(payload)
        except Exception as exc:
            logger.error(f"Failed to enqueue transcription request: {exc}")
            return None

        started_at = time.time()
        while time.time() - started_at <= timeout_seconds:
            try:
                response = self.response_queue.get(timeout=0.5)
            except Empty:
                continue
            except Exception as exc:
                logger.error(f"Failed to read worker response: {exc}")
                return None

            if response.get("request_id") != request_id and response.get("type") != "error":
                continue

            response_type = response.get("type")
            if response_type == "result" and response.get("request_id") == request_id:
                return {
                    "text": response.get("text", ""),
                    "metadata": response.get("metadata", {}),
                }

            if response_type == "error":
                if response.get("request_id") in (None, request_id):
                    logger.error(f"Worker transcription error: {response.get('error')}")
                    return None

        logger.error(f"Transcription request timed out after {timeout_seconds}s")
        return None

    def stop(self) -> None:
        """Stop worker process and clear ready state."""
        try:
            if self.worker_process is not None and self.worker_process.is_alive():
                try:
                    self.request_queue.put(None)
                except Exception:
                    pass

                self.worker_process.join(timeout=3.0)
                if self.worker_process.is_alive():
                    self.worker_process.terminate()
                    self.worker_process.join(timeout=2.0)
        finally:
            self.worker_process = None
            self.is_ready = False
