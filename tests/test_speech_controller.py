#!/usr/bin/env python3
"""
Unit tests for the SpeechController class.
Tests lazy loading, model management, audio recording, and transcription functionality.
"""

import unittest
import tempfile
import os
import threading
import time
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from PyQt5.QtWidgets import QApplication
from pathlib import Path

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from speech_controller import SpeechController
from core.path_validation import get_sandbox


def create_mock_faster_whisper_model(text="test transcription"):
    """Helper to create a mock faster_whisper.WhisperModel instance"""
    mock_segment = Mock()
    mock_segment.text = text
    
    mock_info = Mock()
    
    mock_model = Mock()
    # faster-whisper transcribe returns (segments, info) tuple
    mock_model.transcribe.return_value = ([mock_segment], mock_info)
    
    return mock_model


class TestSpeechController(unittest.TestCase):
    """Test cases for SpeechController class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])
        
        # Ensure sandbox temp directory exists
        sandbox = get_sandbox()
        if not sandbox.temp_dir.exists():
            sandbox.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Mock sounddevice to avoid hardware dependencies
        with patch('core.audio_manager.sd') as mock_sounddevice:
            mock_sounddevice.query_devices.return_value = [
                {'name': 'Test Microphone', 'max_input_channels': 1, 'default_samplerate': 44100}
            ]
            # sd.default.device is a tuple (input_device, output_device)
            mock_default = Mock()
            mock_default.device = [0, 0]  # (input, output)
            mock_sounddevice.default = mock_default
            mock_sounddevice.rec.return_value = np.array([[0.1, 0.2, 0.3]])
            
            # Mock pynput to avoid system dependencies
            with patch('core.hotkey_manager.keyboard') as mock_pynput:
                mock_listener = Mock()
                mock_pynput.Listener.return_value = mock_listener
                
                # Mock faster_whisper to avoid downloading models
                with patch('faster_whisper.WhisperModel') as mock_whisper_class:
                    mock_model = create_mock_faster_whisper_model()
                    mock_whisper_class.return_value = mock_model
                    
                    self.controller = SpeechController(
                        hotkey="alt gr",
                        model_size="tiny",
                        auto_paste=True,
                        language=None,
                        temperature=0.0
                    )
    
    def tearDown(self):
        """Clean up after tests"""
        if hasattr(self, 'controller'):
            # Clean up any temporary files
            if hasattr(self.controller, 'temp_dir') and os.path.exists(self.controller.temp_dir):
                try:
                    import shutil
                    shutil.rmtree(self.controller.temp_dir)
                except OSError:
                    pass
    
    def test_controller_initialization(self):
        """Test that SpeechController initializes correctly"""
        self.assertIsNotNone(self.controller)
        self.assertEqual(self.controller.hotkey, "alt gr")
        self.assertEqual(self.controller.model_size, "tiny")
        self.assertTrue(self.controller.auto_paste)
        self.assertEqual(self.controller.language, "auto")  # Defaults to "auto" when None
        self.assertEqual(self.controller.temperature, 0.0)
    
    def test_lazy_loading_initialization(self):
        """Test that lazy loading is properly initialized"""
        # Model should not be loaded initially
        self.assertIsNone(self.controller.model)
        self.assertFalse(self.controller.model_loaded)
        self.assertFalse(self.controller.model_loading)
        self.assertIsNone(self.controller.model_load_error)
    
    def test_model_status_not_loaded(self):
        """Test model status when not loaded"""
        status = self.controller.get_model_status()
        self.assertEqual(status, "not_loaded")
    
    def test_is_model_ready_false_when_not_loaded(self):
        """Test is_model_ready returns False when model not loaded"""
        self.assertFalse(self.controller.is_model_ready())
    
    def test_preload_model_starts_loading(self):
        """Test that preload_model starts background loading"""
        with patch('faster_whisper.WhisperModel') as mock_whisper_class:
            mock_model = create_mock_faster_whisper_model()
            mock_whisper_class.return_value = mock_model
            
            # Start preloading
            result = self.controller.preload_model()
            self.assertTrue(result)
            
            # The model might load very quickly in tests, so check if it's either loading or loaded
            time.sleep(0.05)  # Shorter wait time
            
            # Should be either loading or loaded (both are valid states)
            self.assertTrue(self.controller.model_loading or self.controller.model_loaded)
    
    def test_preload_model_already_loaded(self):
        """Test preload_model when model is already loaded"""
        # Manually set model as loaded
        self.controller.model = Mock()
        self.controller.model_loaded = True
        
        result = self.controller.preload_model()
        self.assertFalse(result)
    
    def test_preload_model_already_loading(self):
        """Test preload_model when model is already loading"""
        # Manually set model as loading
        self.controller.model_loading = True
        
        result = self.controller.preload_model()
        self.assertFalse(result)
    
    def test_preload_model_with_error(self):
        """Test preload_model when previous load failed"""
        # Manually set model load error
        self.controller.model_load_error = "Previous error"
        
        result = self.controller.preload_model()
        self.assertFalse(result)
    
    def test_ensure_model_loaded_success(self):
        """Test successful model loading"""
        with patch('faster_whisper.WhisperModel') as mock_whisper_class:
            mock_model = create_mock_faster_whisper_model()
            mock_whisper_class.return_value = mock_model
            
            result = self.controller._ensure_model_loaded()
            
            self.assertTrue(result)
            self.assertTrue(self.controller.model_loaded)
            self.assertFalse(self.controller.model_loading)
            self.assertIsNone(self.controller.model_load_error)
            self.assertEqual(self.controller.model, mock_model)
    
    def test_ensure_model_loaded_failure(self):
        """Test model loading failure with fallback"""
        # Patch both faster_whisper and openai-whisper to fail
        with patch('faster_whisper.WhisperModel') as mock_faster_whisper:
            with patch('whisper.load_model') as mock_openai_whisper:
                mock_faster_whisper.side_effect = Exception("Model load failed")
                mock_openai_whisper.side_effect = Exception("Fallback also failed")
                
                result = self.controller._ensure_model_loaded()
                
                self.assertFalse(result)
                self.assertFalse(self.controller.model_loaded)
                self.assertFalse(self.controller.model_loading)
                self.assertIsNotNone(self.controller.model_load_error)
    
    def test_ensure_model_loaded_already_loaded(self):
        """Test _ensure_model_loaded when model is already loaded"""
        # Manually set model as loaded
        self.controller.model = Mock()
        self.controller.model_loaded = True
        
        result = self.controller._ensure_model_loaded()
        self.assertTrue(result)
    
    def test_ensure_model_loaded_currently_loading(self):
        """Test _ensure_model_loaded when model is currently loading"""
        # Manually set model as loading
        self.controller.model_loading = True
        
        result = self.controller._ensure_model_loaded()
        self.assertFalse(result)
    
    def test_ensure_model_loaded_previous_error(self):
        """Test _ensure_model_loaded when previous load failed"""
        # Manually set model load error
        self.controller.model_load_error = "Previous error"
        
        result = self.controller._ensure_model_loaded()
        self.assertFalse(result)
    
    def test_model_status_loaded(self):
        """Test model status when loaded"""
        self.controller.model = Mock()
        self.controller.model_loaded = True
        
        status = self.controller.get_model_status()
        self.assertEqual(status, "loaded")
    
    def test_model_status_loading(self):
        """Test model status when loading"""
        self.controller.model_loading = True
        
        status = self.controller.get_model_status()
        self.assertEqual(status, "loading")
    
    def test_model_status_error(self):
        """Test model status when error occurred"""
        self.controller.model_load_error = "Test error"
        
        status = self.controller.get_model_status()
        self.assertEqual(status, "error: Test error")
    
    def test_is_model_ready_true_when_loaded(self):
        """Test is_model_ready returns True when model is loaded"""
        self.controller.model = Mock()
        self.controller.model_loaded = True
        
        self.assertTrue(self.controller.is_model_ready())
    
    def test_is_model_ready_false_when_loading(self):
        """Test is_model_ready returns False when model is loading"""
        self.controller.model_loading = True
        
        self.assertFalse(self.controller.is_model_ready())
    
    def test_is_model_ready_false_when_error(self):
        """Test is_model_ready returns False when model load error"""
        self.controller.model_load_error = "Test error"
        
        self.assertFalse(self.controller.is_model_ready())
    
    def test_status_callback_setting(self):
        """Test setting status callback"""
        callback = Mock()
        self.controller.set_status_callback(callback)
        
        self.assertEqual(self.controller.status_callback, callback)
    
    def test_status_callback_called(self):
        """Test that status callback is called during status updates"""
        callback = Mock()
        self.controller.set_status_callback(callback)
        
        self.controller._update_status("Test status")
        
        callback.assert_called_once_with("Test status")
    
    def test_transcript_callback_setting(self):
        """Test setting transcript callback"""
        callback = Mock()
        self.controller.set_transcript_callback(callback)
        
        self.assertEqual(self.controller.transcript_callback, callback)
    
    def test_audio_level_callback_setting(self):
        """Test setting audio level callback"""
        callback = Mock()
        self.controller.set_audio_level_callback(callback)
        
        self.assertEqual(self.controller.audio_level_callback, callback)
    
    def test_visual_indicator_settings(self):
        """Test visual indicator settings"""
        self.assertTrue(self.controller.visual_indicator_enabled)
        self.assertEqual(self.controller.visual_indicator_position, "Bottom Center")
    
    def test_audio_parameters(self):
        """Test audio recording parameters"""
        self.assertEqual(self.controller.CHUNK, 2048)
        self.assertEqual(self.controller.CHANNELS, 1)
        self.assertEqual(self.controller.RATE, 16000)
    
    def test_temp_directory_creation(self):
        """Test that temporary directory is created"""
        self.assertTrue(os.path.exists(self.controller.temp_dir))
        self.assertTrue(os.path.isdir(self.controller.temp_dir))
    
    def test_audio_path_setting(self):
        """Test that audio path is set correctly"""
        # Audio path now uses random filenames (whiz_*.wav) for safety
        self.assertTrue(self.controller.audio_path.startswith(self.controller.temp_dir))
        self.assertTrue(self.controller.audio_path.endswith('.wav'))
        self.assertTrue('whiz_' in os.path.basename(self.controller.audio_path))


class TestSpeechControllerIntegration(unittest.TestCase):
    """Integration tests for SpeechController with mocked dependencies"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])
        
        # Ensure sandbox temp directory exists
        sandbox = get_sandbox()
        if not sandbox.temp_dir.exists():
            sandbox.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def test_controller_with_real_dependencies(self):
        """Test controller with more realistic mocked dependencies"""
        with patch('core.audio_manager.sd') as mock_sounddevice, \
             patch('core.hotkey_manager.keyboard') as mock_pynput, \
             patch('faster_whisper.WhisperModel') as mock_whisper_class:
            
            # Setup realistic sounddevice mock
            mock_sounddevice.query_devices.return_value = [
                {'name': 'Microphone 1', 'max_input_channels': 1, 'default_samplerate': 44100},
                {'name': 'Microphone 2', 'max_input_channels': 2, 'default_samplerate': 48000}
            ]
            # sd.default.device is a tuple (input_device, output_device)
            mock_default = Mock()
            mock_default.device = [0, 0]  # (input, output)
            mock_sounddevice.default = mock_default
            mock_sounddevice.rec.return_value = np.array([[0.1, 0.2, 0.3]])
            
            # Setup pynput mock
            mock_listener = Mock()
            mock_pynput.Listener.return_value = mock_listener
            
            # Setup realistic faster_whisper mock
            mock_model = create_mock_faster_whisper_model(text="Hello world")
            mock_whisper_class.return_value = mock_model
            
            # Create controller
            controller = SpeechController(
                hotkey="ctrl+shift+v",
                model_size="base",
                auto_paste=False,
                language="en",
                temperature=0.7
            )
            
            # Test initialization
            self.assertEqual(controller.hotkey, "ctrl+shift+v")
            self.assertEqual(controller.model_size, "base")
            self.assertFalse(controller.auto_paste)
            self.assertEqual(controller.language, "en")
            self.assertEqual(controller.temperature, 0.7)
            
            # Test model loading
            result = controller._ensure_model_loaded()
            self.assertTrue(result)
            self.assertTrue(controller.is_model_ready())
            
            # Clean up
            if os.path.exists(controller.temp_dir):
                import shutil
                shutil.rmtree(controller.temp_dir)


if __name__ == '__main__':
    unittest.main()
