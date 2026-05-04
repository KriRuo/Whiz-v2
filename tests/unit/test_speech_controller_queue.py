#!/usr/bin/env python3
"""
Unit tests for SpeechController Phase 3 behaviours:
- Eager model preload on init (no QTimer delay)
- Hotkey-while-loading queue (depth-1, last wins)
"""

import threading
import time
import unittest
from unittest.mock import MagicMock, patch, call
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def _make_controller():
    """Build a minimal SpeechController via __new__, bypassing __init__ entirely."""
    from speech_controller import SpeechController
    ctrl = SpeechController.__new__(SpeechController)

    # Only the fields Phase 3 code touches
    ctrl.listening = False
    ctrl.auto_paste = False
    ctrl.toggle_mode = False
    ctrl.transcript_log = []
    ctrl.transcript_callback = None
    ctrl.status_callback = None
    ctrl.recording_state_callback = None
    ctrl._queued_audio_path = None
    ctrl._queue_lock = threading.Lock()

    ctrl.transcription_service = MagicMock()
    ctrl.transcription_service.model_loading = False
    ctrl.transcription_service.model_loaded = True
    ctrl.transcription_service.is_model_loaded.return_value = True
    ctrl.recording_service = MagicMock()
    ctrl.hotkey_manager = MagicMock()

    return ctrl


class TestAudioQueue(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from PyQt5.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])

    def test_audio_queued_when_model_loading(self):
        """_transcribe_audio stores path when model is still loading."""
        ctrl = _make_controller()
        ctrl.transcription_service.model_loading = True
        ctrl.transcription_service.model_loaded = False

        ctrl._transcribe_audio("audio1.wav")

        self.assertEqual(ctrl._queued_audio_path, "audio1.wav")

    def test_second_recording_replaces_first_last_wins(self):
        """Second call while loading overwrites the queued path (depth-1, last wins)."""
        ctrl = _make_controller()
        ctrl.transcription_service.model_loading = True
        ctrl.transcription_service.model_loaded = False

        ctrl._transcribe_audio("audio1.wav")
        ctrl._transcribe_audio("audio2.wav")

        self.assertEqual(ctrl._queued_audio_path, "audio2.wav")

    def test_no_immediate_transcription_when_model_loading(self):
        """While loading, _do_transcription must NOT be called immediately."""
        ctrl = _make_controller()
        ctrl.transcription_service.model_loading = True
        ctrl.transcription_service.model_loaded = False
        ctrl._do_transcription = MagicMock()

        ctrl._transcribe_audio("audio1.wav")

        ctrl._do_transcription.assert_not_called()

    def test_immediate_transcription_when_model_ready(self):
        """When model is already loaded, _transcribe_audio starts a thread immediately."""
        ctrl = _make_controller()
        ctrl.transcription_service.model_loading = False
        ctrl.transcription_service.model_loaded = True
        results = []
        ctrl._do_transcription = lambda path: results.append(path)

        ctrl._transcribe_audio("audio.wav")

        # Give thread a moment to run
        time.sleep(0.1)
        self.assertIn("audio.wav", results)

    def test_queued_audio_transcribed_after_model_ready(self):
        """preload_model flushes queue after ensure_model_loaded completes."""
        ctrl = _make_controller()
        # Model is not yet loaded — preload_model should start loading
        ctrl.transcription_service.model_loaded = False
        ctrl.transcription_service.model_loading = False
        ctrl.transcription_service.is_model_loaded.return_value = False

        transcribed = []

        def fake_ensure_loaded():
            time.sleep(0.05)  # simulate load time
            ctrl.transcription_service.model_loading = False
            ctrl.transcription_service.model_loaded = True

        ctrl.transcription_service.ensure_model_loaded = fake_ensure_loaded
        ctrl._do_transcription = lambda path: transcribed.append(path)

        ctrl._queued_audio_path = "queued.wav"
        ctrl.preload_model()

        # Wait for background thread to finish
        time.sleep(0.3)

        self.assertIn("queued.wav", transcribed)
        self.assertIsNone(ctrl._queued_audio_path)

    def test_queue_cleared_after_flush(self):
        """After queued audio is transcribed, _queued_audio_path is reset to None."""
        ctrl = _make_controller()
        # Model is not yet loaded — preload_model should start loading
        ctrl.transcription_service.model_loaded = False
        ctrl.transcription_service.model_loading = False
        ctrl.transcription_service.is_model_loaded.return_value = False
        ctrl.transcription_service.ensure_model_loaded = lambda: None
        ctrl._do_transcription = MagicMock()
        ctrl._queued_audio_path = "pending.wav"

        ctrl.preload_model()
        time.sleep(0.2)

        self.assertIsNone(ctrl._queued_audio_path)


class TestEagerPreload(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from PyQt5.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])

    def test_preload_model_triggers_ensure_model_loaded(self):
        """preload_model must call transcription_service.ensure_model_loaded in background."""
        ctrl = _make_controller()
        # Model is not yet loaded — preload_model should start loading
        ctrl.transcription_service.model_loaded = False
        ctrl.transcription_service.model_loading = False
        ctrl.transcription_service.is_model_loaded.return_value = False
        called = threading.Event()

        def record_call():
            called.set()

        ctrl.transcription_service.ensure_model_loaded = record_call

        ctrl.preload_model()

        self.assertTrue(called.wait(timeout=2.0), "ensure_model_loaded was never called")


if __name__ == '__main__':
    unittest.main()
