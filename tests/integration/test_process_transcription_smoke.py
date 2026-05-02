import os
import tempfile
from unittest.mock import Mock, patch

from PyQt5.QtWidgets import QApplication

from speech_controller import SpeechController
from core.path_validation import get_sandbox
from core.cleanup_manager import reset_cleanup_manager


class FakeTranscriptionService:
    def __init__(self, model_name, device, compute_type):
        self.model_name = model_name
        self.device = device
        self.compute_type = compute_type
        self.is_ready = False
        self.started = False
        self.stopped = False

    def start(self, timeout_seconds=30.0):
        self.started = True
        self.is_ready = True
        return True

    def transcribe(self, audio_path, language, temperature, speed_mode, timeout_seconds=60.0):
        return {
            "text": "integration transcript",
            "metadata": {
                "engine": "faster",
                "language": language,
                "temperature": temperature,
                "speed_mode": speed_mode,
            },
        }

    def stop(self):
        self.stopped = True
        self.is_ready = False


def test_faster_engine_uses_process_service_smoke():
    # Reset cleanup manager for test isolation
    reset_cleanup_manager()
    
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    sandbox = get_sandbox()
    if not sandbox.temp_dir.exists():
        sandbox.temp_dir.mkdir(parents=True, exist_ok=True)

    with patch("core.audio_manager.sd") as mock_sounddevice, \
         patch("core.hotkey_manager.keyboard") as mock_pynput, \
         patch("speech_controller.TranscriptionService", FakeTranscriptionService):
        mock_sounddevice.query_devices.return_value = [
            {"name": "Test Microphone", "max_input_channels": 1, "default_samplerate": 44100}
        ]
        mock_default = Mock()
        mock_default.device = [0, 0]
        mock_sounddevice.default = mock_default

        mock_listener = Mock()
        mock_pynput.Listener.return_value = mock_listener

        controller = SpeechController(
            hotkey="alt gr",
            model_size="tiny",
            auto_paste=False,
            language="en",
            temperature=0.0,
            engine="faster",
        )

        try:
            # Trigger model preload path (starts fake service)
            assert controller.preload_model() is True
            assert controller._ensure_model_loaded(timeout_seconds=5.0) is True
            assert controller.transcription_service is not None
            assert controller.transcription_service.is_ready is True

            # Prepare a valid audio file because process_recorded_audio validates path + size
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                temp_audio.write(b"0" * 4096)
                audio_path = temp_audio.name

            controller.audio_path = audio_path
            controller.recording_frames = [b"dummy-frame"]
            controller.save_audio_to_file = Mock(return_value=True)

            controller.process_recorded_audio()

            assert len(controller.transcript_log) > 0
            assert controller.transcript_log[0]["text"] == "integration transcript"
        finally:
            if hasattr(controller, "cleanup"):
                controller.cleanup()
            if "audio_path" in locals() and os.path.exists(audio_path):
                os.unlink(audio_path)
            # Reset for next test
            reset_cleanup_manager()

