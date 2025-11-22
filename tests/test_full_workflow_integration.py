#!/usr/bin/env python3
"""
Full Workflow Integration Tests

Tests the complete user workflow from start to finish:
- Hotkey press → Recording → Transcription → Auto-paste
"""

import unittest
import time
import wave
import os
import shutil
from unittest.mock import Mock, patch, MagicMock, call
from PyQt5.QtWidgets import QApplication
from pathlib import Path

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from speech_controller import SpeechController
from core.audio_manager import AudioManager
from core.hotkey_manager import HotkeyManager, HotkeyMode
from core.path_validation import get_sandbox
from core.cleanup_manager import get_cleanup_manager


class TestFullWorkflowIntegration(unittest.TestCase):
    """Integration tests for complete user workflows"""
    
    def setUp(self):
        """Set up test environment"""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])
        
        # Reset cleanup manager
        cleanup_mgr = get_cleanup_manager()
        cleanup_mgr._cleanup_started = False
        cleanup_mgr._cleanup_completed = False
        cleanup_mgr.tasks = {}
        
        # Ensure sandbox exists
        sandbox = get_sandbox()
        if not sandbox.temp_dir.exists():
            sandbox.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        """Clean up after tests"""
        if hasattr(self, 'controller'):
            self.controller.cleanup()
    
    def test_recording_to_transcription_workflow(self):
        """
        Test: Start Recording → Record Audio → Stop Recording → Transcription
        This tests the core workflow without hotkeys
        """
        # Skip if FFmpeg not available
        if not shutil.which('ffmpeg'):
            self.skipTest("FFmpeg not available")
        
        # Create controller with mocked hotkey
        with patch('core.hotkey_manager.keyboard') as mock_pynput:
            mock_listener = Mock()
            mock_pynput.Listener.return_value = mock_listener
            
            self.controller = SpeechController(
                hotkey="ctrl+shift+space",
                model_size="tiny",
                auto_paste=False,  # Don't paste for this test
                language="en",
                temperature=0.0,
                engine="openai"
            )
        
        # Load model
        self.controller.preload_model()
        time.sleep(2)  # Wait for model
        
        model_ready = self.controller._ensure_model_loaded(timeout_seconds=30)
        if not model_ready:
            self.skipTest("Model loading failed")
        
        # Track callbacks
        status_updates = []
        transcripts = []
        
        def capture_status(status):
            status_updates.append(status)
        
        def capture_transcript():
            if len(self.controller.transcript_log) > 0:
                transcripts.append(self.controller.transcript_log[0]['text'])
        
        self.controller.set_status_callback(capture_status)
        self.controller.set_transcript_callback(capture_transcript)
        
        # Step 1: Start recording
        started = self.controller.start_recording()
        
        # Skip if audio not available
        if not started:
            self.skipTest("Audio recording not available on this system")
        
        self.assertTrue(self.controller.listening, "Should be listening")
        
        # Step 2: Simulate recording (very short to speed up test)
        time.sleep(0.5)
        
        # Step 3: Stop recording
        self.controller.stop_recording()
        self.assertFalse(self.controller.listening, "Should stop listening")
        
        # Step 4: Verify transcription happened
        # (For such short audio, transcript may be empty, but process should complete)
        time.sleep(2)  # Wait for transcription
        
        # Verify status updates occurred
        self.assertGreater(len(status_updates), 0, "Should have status updates")
        
        # Verify recording frames were captured
        self.assertIsNotNone(self.controller.recording_frames)
    
    @patch('pyautogui.write')
    def test_transcription_to_autopaste_workflow(self, mock_write):
        """
        Test: Transcription Completes → Auto-paste Triggered
        """
        # Create controller with auto-paste enabled
        with patch('core.hotkey_manager.keyboard') as mock_pynput:
            mock_listener = Mock()
            mock_pynput.Listener.return_value = mock_listener
            
            self.controller = SpeechController(
                hotkey="ctrl+shift+space",
                model_size="tiny",
                auto_paste=True,  # Enable auto-paste
                language="en",
                temperature=0.0,
                engine="openai"
            )
        
        # Mock the model
        self.controller.model = Mock()
        self.controller.model_loaded = True
        
        # Create fake audio file
        sandbox = get_sandbox()
        test_audio = str(sandbox.create_temp_file(suffix='.wav'))
        
        # Write minimal WAV file
        import numpy as np
        audio_data = np.zeros(16000, dtype=np.int16)  # 1 second silence
        with wave.open(test_audio, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(audio_data.tobytes())
        
        self.controller.audio_path = test_audio
        
        # Mock transcription result
        test_text = "Hello world test"
        with patch.object(self.controller.model, 'transcribe') as mock_transcribe:
            mock_transcribe.return_value = {'text': test_text}
            
            # Simulate recording frames
            with wave.open(test_audio, 'rb') as wf:
                audio_bytes = wf.readframes(wf.getnframes())
            self.controller.recording_frames = [audio_bytes]
            
            # Process audio (should trigger auto-paste)
            self.controller.process_recorded_audio()
            
            # Verify auto-paste was called
            mock_write.assert_called_once()
            pasted_text = mock_write.call_args[0][0]
            self.assertEqual(pasted_text.strip(), test_text.strip())
    
    def test_settings_to_behavior_integration(self):
        """
        Test: Settings Change → Runtime Behavior Changes
        """
        with patch('core.hotkey_manager.keyboard') as mock_pynput:
            mock_listener = Mock()
            mock_pynput.Listener.return_value = mock_listener
            
            self.controller = SpeechController(
                hotkey="ctrl+shift+space",
                model_size="tiny",
                auto_paste=True,
                language="en",
                temperature=0.5,
                engine="openai"
            )
        
        # Verify initial settings
        self.assertTrue(self.controller.auto_paste)
        self.assertEqual(self.controller.language, "en")
        self.assertEqual(self.controller.temperature, 0.5)
        
        # Change settings
        self.controller.set_auto_paste(False)
        self.controller.set_language("es")
        self.controller.set_temperature(0.2)
        
        # Verify changes applied
        self.assertFalse(self.controller.auto_paste)
        self.assertEqual(self.controller.language, "es")
        self.assertEqual(self.controller.temperature, 0.2)
    
    def test_device_selection_to_recording_integration(self):
        """
        Test: Device Selection → Recording Uses Selected Device
        """
        audio_mgr = AudioManager(sample_rate=16000, channels=1)
        
        if not audio_mgr.is_available():
            self.skipTest("Audio not available")
        
        # Get available devices
        devices = audio_mgr.get_devices()
        if len(devices) == 0:
            self.skipTest("No audio devices available")
        
        # Select first device
        device_idx = devices[0]['index']
        success = audio_mgr.select_device(device_idx)
        self.assertTrue(success, "Should select device successfully")
        
        # Verify device was selected
        self.assertEqual(audio_mgr.input_device, device_idx)
        
        # Try to start recording (should use selected device)
        started = audio_mgr.start_recording()
        if started:
            # Recording started successfully
            time.sleep(0.2)
            frames = audio_mgr.stop_recording()
            self.assertIsInstance(frames, list)
            audio_mgr.cleanup()
    
    def test_model_loading_workflow(self):
        """
        Test: Model Loading → Model Ready → Can Transcribe
        """
        with patch('core.hotkey_manager.keyboard') as mock_pynput:
            mock_listener = Mock()
            mock_pynput.Listener.return_value = mock_listener
            
            self.controller = SpeechController(
                hotkey="ctrl+shift+space",
                model_size="tiny",
                auto_paste=False,
                language="en",
                temperature=0.0,
                engine="openai"
            )
        
        # Initially model not loaded
        self.assertFalse(self.controller.is_model_ready())
        
        # Preload model
        self.controller.preload_model()
        
        # Wait for loading
        time.sleep(2)
        
        # Ensure model is loaded
        loaded = self.controller._ensure_model_loaded(timeout_seconds=30)
        
        if loaded:
            # Model should now be ready
            self.assertTrue(self.controller.is_model_ready())
            self.assertTrue(self.controller.model_loaded)
            self.assertIsNotNone(self.controller.model)
    
    def test_error_recovery_workflow(self):
        """
        Test: Error Occurs → System Recovers → Can Continue
        """
        with patch('core.hotkey_manager.keyboard') as mock_pynput:
            mock_listener = Mock()
            mock_pynput.Listener.return_value = mock_listener
            
            self.controller = SpeechController(
                hotkey="ctrl+shift+space",
                model_size="tiny",
                auto_paste=False,
                language="en",
                temperature=0.0,
                engine="openai"
            )
        
        # Try to process without recording (should handle gracefully)
        self.controller.recording_frames = []
        self.controller.process_recorded_audio()
        
        # System should still be functional
        self.assertFalse(self.controller.listening)
        
        # Should be able to start recording after error
        started = self.controller.start_recording()
        # May or may not start depending on audio availability
        # But should not crash
        if started:
            self.controller.stop_recording()


if __name__ == '__main__':
    unittest.main()

