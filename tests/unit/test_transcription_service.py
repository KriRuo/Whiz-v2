#!/usr/bin/env python3
"""
Unit tests for TranscriptionService.
Tests model loading, transcription, error handling, and configuration.
"""

import unittest
import tempfile
import os
import wave
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.transcription_service import (
    TranscriptionService,
    TranscriptionConfig,
    TranscriptionResult,
    TranscriptionEngine,
    TranscriptionStatus
)
from core.transcription_exceptions import ModelLoadingError, WhisperError


class TestTranscriptionConfig(unittest.TestCase):
    """Test TranscriptionConfig validation"""
    
    def test_valid_config(self):
        """Test creating valid configuration"""
        config = TranscriptionConfig(
            model_size="tiny",
            engine="faster",
            language="en",
            temperature=0.5
        )
        self.assertEqual(config.model_size, "tiny")
        self.assertEqual(config.engine, "faster")
        self.assertEqual(config.language, "en")
        self.assertEqual(config.temperature, 0.5)
    
    def test_invalid_model_size(self):
        """Test that invalid model size raises error"""
        with self.assertRaises(ValueError) as cm:
            TranscriptionConfig(model_size="invalid")
        self.assertIn("Invalid model_size", str(cm.exception))
    
    def test_invalid_engine(self):
        """Test that invalid engine raises error"""
        with self.assertRaises(ValueError) as cm:
            TranscriptionConfig(engine="invalid")
        self.assertIn("Invalid engine", str(cm.exception))
    
    def test_invalid_temperature(self):
        """Test that invalid temperature raises error"""
        with self.assertRaises(ValueError):
            TranscriptionConfig(temperature=-0.1)
        
        with self.assertRaises(ValueError):
            TranscriptionConfig(temperature=1.5)
    
    def test_default_values(self):
        """Test default configuration values"""
        config = TranscriptionConfig()
        self.assertEqual(config.model_size, "tiny")
        self.assertEqual(config.engine, "faster")
        self.assertEqual(config.language, "auto")
        self.assertEqual(config.temperature, 0.0)
        self.assertTrue(config.speed_mode)


class TestTranscriptionResult(unittest.TestCase):
    """Test TranscriptionResult data class"""
    
    def test_success_result(self):
        """Test successful transcription result"""
        result = TranscriptionResult(
            success=True,
            text="Hello world",
            duration_seconds=1.5
        )
        self.assertTrue(result.success)
        self.assertEqual(result.text, "Hello world")
        self.assertIsNone(result.error)
        self.assertEqual(result.duration_seconds, 1.5)
    
    def test_error_result(self):
        """Test error transcription result"""
        result = TranscriptionResult(
            success=False,
            error="Model not loaded",
            error_type="ModelLoadingError"
        )
        self.assertFalse(result.success)
        self.assertIsNone(result.text)
        self.assertEqual(result.error, "Model not loaded")
        self.assertEqual(result.error_type, "ModelLoadingError")
    
    def test_to_dict(self):
        """Test converting result to dictionary"""
        result = TranscriptionResult(
            success=True,
            text="Test",
            duration_seconds=2.0,
            model_info={"engine": "faster"}
        )
        result_dict = result.to_dict()
        
        self.assertIsInstance(result_dict, dict)
        self.assertTrue(result_dict["success"])
        self.assertEqual(result_dict["text"], "Test")
        self.assertEqual(result_dict["duration_seconds"], 2.0)
        self.assertEqual(result_dict["model_info"]["engine"], "faster")


class TestTranscriptionService(unittest.TestCase):
    """Test TranscriptionService class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = TranscriptionConfig(
            model_size="tiny",
            engine="faster",
            language="auto",
            temperature=0.0
        )
        
        # Create temporary audio file for testing
        self.temp_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        self._create_test_audio(self.temp_audio.name)
        
    def tearDown(self):
        """Clean up after tests"""
        if hasattr(self, 'temp_audio') and os.path.exists(self.temp_audio.name):
            try:
                os.unlink(self.temp_audio.name)
            except OSError:
                pass
    
    def _create_test_audio(self, filepath: str):
        """Create a test WAV file"""
        sample_rate = 16000
        duration = 1  # seconds
        samples = np.random.randint(-32768, 32767, sample_rate * duration, dtype=np.int16)
        
        with wave.open(filepath, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(samples.tobytes())
    
    def test_service_initialization(self):
        """Test that service initializes correctly"""
        service = TranscriptionService(self.config)
        
        self.assertIsNotNone(service)
        self.assertEqual(service.config.model_size, "tiny")
        self.assertEqual(service.config.engine, "faster")
        self.assertFalse(service.model_loaded)
        self.assertIsNone(service.model)
    
    def test_status_callback(self):
        """Test status callback functionality"""
        service = TranscriptionService(self.config)
        
        callback_messages = []
        def callback(message):
            callback_messages.append(message)
        
        service.set_status_callback(callback)
        service._update_status("Test message")
        
        self.assertEqual(len(callback_messages), 1)
        self.assertEqual(callback_messages[0], "Test message")
    
    def test_is_model_loaded(self):
        """Test model loaded status check"""
        service = TranscriptionService(self.config)
        
        self.assertFalse(service.is_model_loaded())
        
        # Simulate model loading
        service.model = Mock()
        service.model_loaded = True
        
        self.assertTrue(service.is_model_loaded())
    
    @patch('core.transcription_service.faster_whisper')
    def test_load_faster_whisper_model(self, mock_faster_whisper):
        """Test loading faster-whisper model"""
        mock_model = Mock()
        mock_whisper_class = Mock(return_value=mock_model)
        mock_faster_whisper.WhisperModel = mock_whisper_class
        
        service = TranscriptionService(self.config)
        service._faster_whisper_available = True
        service._engines_checked = True
        
        success = service.ensure_model_loaded(timeout_seconds=5)
        
        self.assertTrue(success)
        self.assertTrue(service.model_loaded)
        self.assertIsNotNone(service.model)
        mock_whisper_class.assert_called_once()
    
    @patch('core.transcription_service.whisper')
    def test_load_openai_whisper_model(self, mock_whisper):
        """Test loading openai-whisper model"""
        mock_model = Mock()
        mock_whisper.load_model.return_value = mock_model
        
        config = TranscriptionConfig(engine="openai")
        service = TranscriptionService(config)
        service._openai_whisper_available = True
        service._engines_checked = True
        
        success = service.ensure_model_loaded(timeout_seconds=5)
        
        self.assertTrue(success)
        self.assertTrue(service.model_loaded)
        self.assertIsNotNone(service.model)
        mock_whisper.load_model.assert_called_once_with("tiny")
    
    @patch('core.transcription_service.faster_whisper')
    def test_transcribe_success_faster_whisper(self, mock_faster_whisper):
        """Test successful transcription with faster-whisper"""
        # Mock model and segments
        mock_segment = Mock()
        mock_segment.text = "test transcription"
        
        mock_info = Mock()
        mock_info.language = "en"
        mock_info.duration = 1.0
        
        mock_model = Mock()
        mock_model.transcribe.return_value = ([mock_segment], mock_info)
        mock_whisper_class = Mock(return_value=mock_model)
        mock_faster_whisper.WhisperModel = mock_whisper_class
        
        service = TranscriptionService(self.config)
        service._faster_whisper_available = True
        service._engines_checked = True
        
        result = service.transcribe(self.temp_audio.name)
        
        self.assertTrue(result.success)
        self.assertEqual(result.text, "test transcription")
        self.assertIsNone(result.error)
        self.assertGreater(result.duration_seconds, 0)
        self.assertEqual(result.model_info["engine"], "faster-whisper")
    
    @patch('core.transcription_service.whisper')
    def test_transcribe_success_openai_whisper(self, mock_whisper):
        """Test successful transcription with openai-whisper"""
        mock_model = Mock()
        mock_model.transcribe.return_value = {
            "text": "test transcription",
            "language": "en"
        }
        mock_whisper.load_model.return_value = mock_model
        
        config = TranscriptionConfig(engine="openai")
        service = TranscriptionService(config)
        service._openai_whisper_available = True
        service._engines_checked = True
        
        result = service.transcribe(self.temp_audio.name)
        
        self.assertTrue(result.success)
        self.assertEqual(result.text, "test transcription")
        self.assertIsNone(result.error)
        self.assertEqual(result.model_info["engine"], "openai-whisper")
    
    def test_transcribe_file_not_found(self):
        """Test transcription with non-existent file"""
        service = TranscriptionService(self.config)
        
        result = service.transcribe("/nonexistent/file.wav")
        
        self.assertFalse(result.success)
        self.assertIsNone(result.text)
        self.assertIsNotNone(result.error)
        self.assertEqual(result.error_type, "FileNotFound")
    
    @patch('core.transcription_service.faster_whisper')
    def test_transcribe_model_loading_failure(self, mock_faster_whisper):
        """Test transcription when model loading fails"""
        mock_faster_whisper.WhisperModel.side_effect = Exception("Model loading failed")
        
        service = TranscriptionService(self.config)
        service._faster_whisper_available = True
        service._engines_checked = True
        
        result = service.transcribe(self.temp_audio.name)
        
        self.assertFalse(result.success)
        self.assertIsNone(result.text)
        self.assertIsNotNone(result.error)
        self.assertEqual(result.error_type, "ModelLoadingError")
    
    @patch('core.transcription_service.faster_whisper')
    def test_engine_fallback(self, mock_faster_whisper):
        """Test fallback to available engine"""
        mock_model = Mock()
        mock_whisper_class = Mock(return_value=mock_model)
        mock_faster_whisper.WhisperModel = mock_whisper_class
        
        # Request openai but only faster is available
        config = TranscriptionConfig(engine="openai")
        service = TranscriptionService(config)
        service._faster_whisper_available = True
        service._openai_whisper_available = False
        service._engines_checked = True
        
        success = service.ensure_model_loaded(timeout_seconds=5)
        
        self.assertTrue(success)
        # Should have fallen back to faster
        self.assertEqual(service.config.engine, "faster")
    
    @patch('core.transcription_service.faster_whisper')
    def test_unload_model(self, mock_faster_whisper):
        """Test model unloading"""
        mock_model = Mock()
        mock_whisper_class = Mock(return_value=mock_model)
        mock_faster_whisper.WhisperModel = mock_whisper_class
        
        service = TranscriptionService(self.config)
        service._faster_whisper_available = True
        service._engines_checked = True
        
        # Load model
        service.ensure_model_loaded(timeout_seconds=5)
        self.assertTrue(service.model_loaded)
        
        # Unload model
        service.unload_model()
        self.assertFalse(service.model_loaded)
        self.assertIsNone(service.model)
    
    @patch('core.transcription_service.faster_whisper')
    def test_get_status(self, mock_faster_whisper):
        """Test getting service status"""
        mock_model = Mock()
        mock_whisper_class = Mock(return_value=mock_model)
        mock_faster_whisper.WhisperModel = mock_whisper_class
        
        service = TranscriptionService(self.config)
        service._faster_whisper_available = True
        service._engines_checked = True
        
        # Before loading
        status = service.get_status()
        self.assertFalse(status["model_loaded"])
        self.assertEqual(status["engine"], "faster")
        self.assertEqual(status["model_size"], "tiny")
        
        # After loading
        service.ensure_model_loaded(timeout_seconds=5)
        status = service.get_status()
        self.assertTrue(status["model_loaded"])
    
    @patch('core.transcription_service.faster_whisper')
    def test_concurrent_model_loading(self, mock_faster_whisper):
        """Test that concurrent model loading requests are handled correctly"""
        import threading
        import time
        
        mock_model = Mock()
        # Simulate slow model loading
        def slow_load(*args, **kwargs):
            time.sleep(0.5)
            return mock_model
        mock_whisper_class = Mock(side_effect=slow_load)
        mock_faster_whisper.WhisperModel = mock_whisper_class
        
        service = TranscriptionService(self.config)
        service._faster_whisper_available = True
        service._engines_checked = True
        
        results = []
        
        def load_model():
            result = service.ensure_model_loaded(timeout_seconds=5)
            results.append(result)
        
        # Start multiple threads trying to load the model
        threads = [threading.Thread(target=load_model) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All threads should succeed
        self.assertEqual(len(results), 3)
        self.assertTrue(all(results))
        
        # Model should be loaded only once
        self.assertEqual(mock_whisper_class.call_count, 1)


if __name__ == '__main__':
    unittest.main()
