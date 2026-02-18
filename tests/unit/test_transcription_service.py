import time
from queue import Empty

from core.transcription_service import TranscriptionService


def ready_and_echo_worker(request_queue, response_queue, _config):
    response_queue.put({"type": "ready"})
    while True:
        try:
            req = request_queue.get(timeout=0.2)
        except Empty:
            continue

        if req is None:
            break

        if req.get("type") == "transcribe":
            response_queue.put(
                {
                    "type": "result",
                    "request_id": req.get("request_id"),
                    "text": "worker transcript",
                    "metadata": {"engine": "faster", "processing_seconds": 0.01},
                }
            )


def ready_but_no_response_worker(request_queue, response_queue, _config):
    response_queue.put({"type": "ready"})
    while True:
        try:
            req = request_queue.get(timeout=0.2)
        except Empty:
            continue
        if req is None:
            break


def error_on_start_worker(_request_queue, response_queue, _config):
    response_queue.put({"type": "error", "error": "intentional init failure"})


def test_service_start_and_stop_with_ready_worker():
    service = TranscriptionService(
        model_name="tiny",
        device="cpu",
        compute_type="int8",
        worker_target=ready_and_echo_worker,
    )

    assert service.start(timeout_seconds=2.0)
    assert service.is_ready
    assert service.worker_process is not None
    assert service.worker_process.is_alive()

    service.stop()
    assert not service.is_ready
    assert service.worker_process is None


def test_service_transcribe_returns_result_payload():
    service = TranscriptionService(
        model_name="tiny",
        device="cpu",
        compute_type="int8",
        worker_target=ready_and_echo_worker,
    )
    try:
        assert service.start(timeout_seconds=2.0)
        result = service.transcribe(
            audio_path="fake.wav",
            language="en",
            temperature=0.0,
            speed_mode=True,
            timeout_seconds=2.0,
        )

        assert result is not None
        assert result["text"] == "worker transcript"
        assert result["metadata"]["engine"] == "faster"
    finally:
        service.stop()


def test_service_transcribe_timeout_returns_none():
    service = TranscriptionService(
        model_name="tiny",
        device="cpu",
        compute_type="int8",
        worker_target=ready_but_no_response_worker,
    )
    try:
        assert service.start(timeout_seconds=2.0)
        started_at = time.time()
        result = service.transcribe(
            audio_path="fake.wav",
            language="en",
            temperature=0.0,
            speed_mode=True,
            timeout_seconds=1.0,
        )
        elapsed = time.time() - started_at

        assert result is None
        assert elapsed >= 1.0
    finally:
        service.stop()


def test_service_start_failure_returns_false():
    service = TranscriptionService(
        model_name="tiny",
        device="cpu",
        compute_type="int8",
        worker_target=error_on_start_worker,
    )

    assert not service.start(timeout_seconds=2.0)
    assert not service.is_ready
    service.stop()
