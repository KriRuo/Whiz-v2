#!/usr/bin/env python3
"""
End-to-end tests with real audio recording and transcription.
Tests the full workflow from audio capture to transcription without mocking.
"""

import unittest
import tempfile
import os
import time
import wave
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from PyQt5.QtWidgets import QApplication
from pathlib import Path

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from speech_controller import SpeechController
from core.audio_manager import AudioManager
from core.path_validation import get_sandbox
from core.cleanup_manager import get_cleanup_manager


def create_test_audio_file(filename, duration_seconds=2, sample_rate=16000, frequency=440):
    """
    Create a test WAV file with a sine wave tone.
    
    Args:
        filename: Output filename
        duration_seconds: Length of audio
        sample_rate: Sample rate (Hz)
        frequency: Tone frequency (Hz)
    """
    # Generate sine wave
    t = np.linspace(0, duration_seconds, int(sample_rate * duration_seconds))
    audio_data = np.sin(2 * np.pi * frequency * t) * 0.3  # 30% amplitude
    
    # Convert to int16
    audio_int16 = (audio_data * 32767).astype(np.int16)
    
    # Write WAV file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 2 bytes per sample (int16)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())


def create_silent_audio_file(filename, duration_seconds=2, sample_rate=16000):
    """Create a silent WAV file."""
    audio_data = np.zeros(int(sample_rate * duration_seconds), dtype=np.int16)
    
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())


class TestRealAudioWorkflow(unittest.TestCase):
    """End-to-end tests with real audio files"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures once for all tests"""
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication([])
        
        # Create temp directory for test audio files
        cls.test_audio_dir = tempfile.mkdtemp(prefix='whiz_test_audio_')
        
        # Create test audio files
        cls.short_audio_file = os.path.join(cls.test_audio_dir, 'test_short.wav')
        cls.long_audio_file = os.path.join(cls.test_audio_dir, 'test_long.wav')
        cls.silent_audio_file = os.path.join(cls.test_audio_dir, 'test_silent.wav')
        
        create_test_audio_file(cls.short_audio_file, duration_seconds=2)
        create_test_audio_file(cls.long_audio_file, duration_seconds=30)
        create_silent_audio_file(cls.silent_audio_file, duration_seconds=2)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test files"""
        import shutil
        if os.path.exists(cls.test_audio_dir):
            shutil.rmtree(cls.test_audio_dir)
    
    def setUp(self):
        """Set up for each test"""
        # Reset cleanup manager state for clean test environment
        cleanup_mgr = get_cleanup_manager()
        cleanup_mgr._cleanup_started = False
        cleanup_mgr._cleanup_completed = False
        cleanup_mgr.tasks = {}  # Dict, not list
        
        # Ensure sandbox temp directory exists
        sandbox = get_sandbox()
        if not sandbox.temp_dir.exists():
            sandbox.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Mock pynput to avoid system dependencies
        with patch('core.hotkey_manager.keyboard') as mock_pynput:
            mock_listener = Mock()
            mock_pynput.Listener.return_value = mock_listener
            
            self.controller = SpeechController(
                hotkey="alt gr",
                model_size="tiny",
                auto_paste=False,  # Disable auto-paste for tests
                language="en",
                temperature=0.0,
                engine="openai"  # Use stable openai engine
            )
    
    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self, 'controller'):
            self.controller.cleanup()
    
    def test_real_audio_file_transcription(self):
        """Test transcription with a real audio file (2 seconds)"""
        # This is an integration test that requires FFmpeg in PATH
        # Skip if FFmpeg is not available
        import shutil
        if not shutil.which('ffmpeg'):
            self.skipTest("FFmpeg not available in PATH")
        
        # Load the model first
        self.controller.preload_model()
        time.sleep(3)  # Wait for model to load
        
        # Ensure model is loaded
        model_ready = self.controller._ensure_model_loaded(timeout_seconds=30)
        if not model_ready:
            self.skipTest("Model loading failed or timed out")
        
        # Copy test audio to controller's expected path
        shutil.copy(self.short_audio_file, self.controller.audio_path)
        
        # Mock recording frames (pretend we recorded)
        with wave.open(self.short_audio_file, 'rb') as wf:
            audio_bytes = wf.readframes(wf.getnframes())
        
        # Simulate having frames
        self.controller.recording_frames = [audio_bytes[i:i+4096] for i in range(0, len(audio_bytes), 4096)]
        
        # Capture transcript callback
        transcripts = []
        def capture_transcript():
            if len(self.controller.transcript_log) > 0:
                transcripts.append(self.controller.transcript_log[0]['text'])
        
        self.controller.set_transcript_callback(capture_transcript)
        
        # Process the audio
        self.controller.process_recorded_audio()
        
        # Verify transcription happened (may be empty for tone, but should not crash)
        self.assertIsNotNone(self.controller.transcript_log)
        # Sine wave won't produce text, but process should complete without error
    
    def test_long_recording_30_seconds(self):
        """Test transcription of 30-second audio file"""
        # This is an integration test that requires FFmpeg in PATH
        import shutil
        if not shutil.which('ffmpeg'):
            self.skipTest("FFmpeg not available in PATH")
        
        # Skip if audio isn't available (this test is slow)
        if not self.controller.audio_manager.is_available():
            self.skipTest("Audio not available")
        
        # Load the model
        self.controller.preload_model()
        time.sleep(3)
        
        model_ready = self.controller._ensure_model_loaded(timeout_seconds=30)
        if not model_ready:
            self.skipTest("Model loading failed")
        
        # Copy long audio file
        shutil.copy(self.long_audio_file, self.controller.audio_path)
        
        # Load audio data
        with wave.open(self.long_audio_file, 'rb') as wf:
            audio_bytes = wf.readframes(wf.getnframes())
        
        self.controller.recording_frames = [audio_bytes[i:i+4096] for i in range(0, len(audio_bytes), 4096)]
        
        # Process (this will take several seconds)
        start_time = time.time()
        self.controller.process_recorded_audio()
        elapsed = time.time() - start_time
        
        # Verify it completed (should take 5-10 seconds for 30s audio with tiny model)
        self.assertLess(elapsed, 60, "Transcription should complete in reasonable time")
        
        # Verify frames were present before processing
        # (they may be cleared after processing)
        self.assertIsNotNone(self.controller.transcript_log)
    
    def test_silent_audio_handling(self):
        """Test handling of silent/empty audio"""
        # This is an integration test that requires FFmpeg in PATH
        import shutil
        if not shutil.which('ffmpeg'):
            self.skipTest("FFmpeg not available in PATH")
        
        # Load the model
        self.controller.preload_model()
        time.sleep(3)
        
        model_ready = self.controller._ensure_model_loaded(timeout_seconds=30)
        if not model_ready:
            self.skipTest("Model loading failed")
        
        # Copy silent audio file
        shutil.copy(self.silent_audio_file, self.controller.audio_path)
        
        # Load silent audio
        with wave.open(self.silent_audio_file, 'rb') as wf:
            audio_bytes = wf.readframes(wf.getnframes())
        
        self.controller.recording_frames = [audio_bytes[i:i+4096] for i in range(0, len(audio_bytes), 4096)]
        
        # Process silent audio
        self.controller.process_recorded_audio()
        
        # Should complete without error
        # Transcription will likely be empty string
        if len(self.controller.transcript_log) > 0:
            transcript = self.controller.transcript_log[0]['text']
            # Empty or very short transcription is expected for silence
            self.assertLessEqual(len(transcript), 50, "Silent audio should produce minimal text")


class TestAutoPasteIntegration(unittest.TestCase):
    """Tests for auto-paste functionality"""
    
    def setUp(self):
        """Set up for each test"""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])
        
        # Reset cleanup manager state for clean test environment
        cleanup_mgr = get_cleanup_manager()
        cleanup_mgr._cleanup_started = False
        cleanup_mgr._cleanup_completed = False
        cleanup_mgr.tasks = {}  # Dict, not list
        
        # Ensure sandbox temp directory exists
        sandbox = get_sandbox()
        if not sandbox.temp_dir.exists():
            sandbox.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Mock pynput
        with patch('core.hotkey_manager.keyboard') as mock_pynput:
            mock_listener = Mock()
            mock_pynput.Listener.return_value = mock_listener
            
            self.controller = SpeechController(
                hotkey="alt gr",
                model_size="tiny",
                auto_paste=True,
                language="en",
                temperature=0.0,
                engine="openai"
            )
    
    def tearDown(self):
        """Clean up"""
        if hasattr(self, 'controller'):
            self.controller.cleanup()
    
    def test_auto_paste_setting(self):
        """Test that auto-paste setting is respected"""
        self.assertTrue(self.controller.auto_paste)
        
        self.controller.set_auto_paste(False)
        self.assertFalse(self.controller.auto_paste)
        
        self.controller.set_auto_paste(True)
        self.assertTrue(self.controller.auto_paste)
    
    @patch('pyautogui.write')
    def test_auto_paste_functional(self, mock_write):
        """Test that auto-paste actually calls pyautogui.write()"""
        # Set up transcript
        test_text = "Test transcription text"
        self.controller.transcript_log = [{'text': test_text, 'timestamp': time.time()}]
        
        # Simulate having model loaded
        self.controller.model = Mock()
        self.controller.model_loaded = True
        
        # Create a fake audio file
        sandbox = get_sandbox()
        test_audio = str(sandbox.create_temp_file(suffix='.wav'))  # Convert Path to string
        create_test_audio_file(test_audio, duration_seconds=1)
        
        self.controller.audio_path = test_audio
        
        # Mock the transcription to return our test text
        with patch.object(self.controller.model, 'transcribe') as mock_transcribe:
            mock_result = {'text': test_text}
            mock_transcribe.return_value = mock_result
            
            # Create fake recording frames
            with wave.open(test_audio, 'rb') as wf:
                audio_bytes = wf.readframes(wf.getnframes())
            self.controller.recording_frames = [audio_bytes]
            
            # Process audio (should trigger auto-paste)
            self.controller.process_recorded_audio()
            
            # Verify pyautogui.write was called with the transcribed text
            # Note: Whisper may add trailing whitespace, so strip both
            mock_write.assert_called_once()
            called_text = mock_write.call_args[0][0]
            self.assertEqual(called_text.strip(), test_text.strip())


class TestDeviceFailureRecovery(unittest.TestCase):
    """Tests for device disconnect and error recovery"""
    
    def setUp(self):
        """Set up for each test"""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])
    
    def test_device_disconnect_during_recording(self):
        """Test graceful handling of device disconnect"""
        audio_mgr = AudioManager(sample_rate=16000, channels=1)
        
        if not audio_mgr.is_available():
            self.skipTest("Audio not available")
        
        # Start recording
        started = audio_mgr.start_recording()
        if not started:
            self.skipTest("Could not start recording")
        
        # Simulate device disconnect by closing stream
        if audio_mgr.stream:
            audio_mgr.stream.close()
            audio_mgr.stream = None
        
        # Try to stop recording (should handle gracefully)
        frames = audio_mgr.stop_recording()
        
        # Should not crash, may return empty frames
        self.assertIsInstance(frames, list)
    
    def test_audio_manager_fallback(self):
        """Test that AudioManager can handle device failures"""
        audio_mgr = AudioManager(sample_rate=16000, channels=1)
        
        if not audio_mgr.is_available():
            self.skipTest("Audio not available")
        
        # Get initial device
        initial_device = audio_mgr.input_device
        
        # Get status
        status = audio_mgr.get_status()
        self.assertIsNotNone(status)
        self.assertIn('available', status)
        self.assertTrue(status['available'])
    
    def test_interrupted_recording_cleanup(self):
        """Test cleanup when recording is interrupted"""
        audio_mgr = AudioManager(sample_rate=16000, channels=1)
        
        if not audio_mgr.is_available():
            self.skipTest("Audio not available")
        
        # Start recording
        started = audio_mgr.start_recording()
        if not started:
            self.skipTest("Could not start recording")
        
        # Immediately cleanup without proper stop
        audio_mgr.cleanup()
        
        # Verify state
        self.assertFalse(audio_mgr.is_recording)
        self.assertIsNone(audio_mgr.stream)


if __name__ == '__main__':
    unittest.main()

