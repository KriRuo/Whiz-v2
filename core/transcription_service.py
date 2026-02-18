"""
Queue-based transcription service using multiprocessing.

This module isolates faster-whisper/ONNX runtime work from the PyQt process
to avoid threading/runtime conflicts while preserving a simple client API.
"""

from __future__ import annotations

import logging
import multiprocessing as mp
import time
from queue import Empty
from typing import Any, Callable, Dict, Optional

from core.config import TIMEOUT_CONFIG, WHISPER_CONFIG

logger = logging.getLogger(__name__)


def _transcription_worker_main(
    request_queue: "mp.queues.Queue",
    response_queue: "mp.queues.Queue",
    config: Dict[str, Any],
) -> None:
    """Worker process entrypoint for transcription requests."""
    model = None

    try:
        from faster_whisper import WhisperModel

        model = WhisperModel(
            config.get("model_name", WHISPER_CONFIG.DEFAULT_MODEL),
            device=config.get("device", "cpu"),
            compute_type=config.get("compute_type", WHISPER_CONFIG.COMPUTE_TYPE_CPU),
            cpu_threads=config.get("cpu_threads", 4),
            num_workers=config.get("num_workers", 1),
        )
        response_queue.put({"type": "ready"})
    except Exception as exc:
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

        self.worker_process = self._ctx.Process(
            target=self._worker_target,
            args=(self.request_queue, self.response_queue, config),
            daemon=True,
        )
        self.worker_process.start()

        try:
            response = self.response_queue.get(timeout=timeout_seconds)
        except Empty:
            logger.error("Transcription worker did not signal readiness before timeout")
            self.stop()
            return False
        except Exception as exc:
            logger.error(f"Error waiting for worker readiness: {exc}")
            self.stop()
            return False

        if response.get("type") == "ready":
            self.is_ready = True
            return True

        logger.error(f"Worker failed to initialize: {response}")
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
