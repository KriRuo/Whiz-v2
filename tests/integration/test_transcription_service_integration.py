#!/usr/bin/env python3
"""
Integration test for TranscriptionService end-to-end workflow.
Tests the complete transcription pipeline from audio file to text output.
"""

import unittest
import tempfile
import os
import wave
import numpy as np
from unittest.mock import patch, Mock
from pathlib import Path

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.transcription_service import TranscriptionService, TranscriptionConfig


class TestTranscriptionServiceIntegration(unittest.TestCase):
    """Integration tests for complete transcription workflow"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory for audio files
        self.temp_dir = tempfile.mkdtemp()
        self.audio_files = []
        
        # Create test audio files
        self.short_audio = self._create_test_audio("short_test.wav", duration=1)
        self.medium_audio = self._create_test_audio("medium_test.wav", duration=3)
        self.audio_files.extend([self.short_audio, self.medium_audio])
    
    def tearDown(self):
        """Clean up after tests"""
        # Remove test audio files
        for audio_file in self.audio_files:
            if os.path.exists(audio_file):
                try:
                    os.unlink(audio_file)
                except OSError:
                    pass
        
        # Remove temporary directory
        try:
            os.rmdir(self.temp_dir)
        except OSError:
            pass
    
    def _create_test_audio(self, filename: str, duration: int = 1) -> str:
        """Create a test WAV file with specified duration"""
        filepath = os.path.join(self.temp_dir, filename)
        sample_rate = 16000
        samples = np.random.randint(-32768, 32767, sample_rate * duration, dtype=np.int16)
        
        with wave.open(filepath, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(samples.tobytes())
        
        return filepath
    
    @patch('core.transcription_service.faster_whisper')
    def test_end_to_end_transcription_faster_whisper(self, mock_faster_whisper):
        """Test complete end-to-end transcription with faster-whisper"""
        # Mock the Whisper model
        mock_segment1 = Mock()
        mock_segment1.text = "Hello"
        mock_segment2 = Mock()
        mock_segment2.text = "world"
        
        mock_info = Mock()
        mock_info.language = "en"
        mock_info.duration = 1.0
        
        mock_model = Mock()
        mock_model.transcribe.return_value = ([mock_segment1, mock_segment2], mock_info)
        mock_whisper_class = Mock(return_value=mock_model)
        mock_faster_whisper.WhisperModel = mock_whisper_class
        
        # Create service
        config = TranscriptionConfig(
            model_size="tiny",
            engine="faster",
            language="auto",
            temperature=0.0
        )
        service = TranscriptionService(config)
        service._faster_whisper_available = True
        service._engines_checked = True
        
        # Transcribe audio
        result = service.transcribe(self.short_audio)
        
        # Verify results
        self.assertTrue(result.success, f"Transcription failed: {result.error}")
        self.assertIsNotNone(result.text)
        self.assertEqual(result.text, "Hello world")
        self.assertIsNone(result.error)
        self.assertGreater(result.duration_seconds, 0)
        self.assertEqual(result.model_info["engine"], "faster-whisper")
        self.assertEqual(result.model_info["model_size"], "tiny")
    
    @patch('core.transcription_service.whisper')
    def test_end_to_end_transcription_openai_whisper(self, mock_whisper):
        """Test complete end-to-end transcription with openai-whisper"""
        # Mock the Whisper model
        mock_model = Mock()
        mock_model.transcribe.return_value = {
            "text": "This is a test transcription",
            "language": "en"
        }
        mock_whisper.load_model = Mock(return_value=mock_model)
        
        # Create service
        config = TranscriptionConfig(
            model_size="base",
            engine="openai",
            language="en",
            temperature=0.2
        )
        service = TranscriptionService(config)
        service._openai_whisper_available = True
        service._engines_checked = True
        
        # Transcribe audio
        result = service.transcribe(self.medium_audio)
        
        # Verify results
        self.assertTrue(result.success, f"Transcription failed: {result.error}")
        self.assertIsNotNone(result.text)
        self.assertEqual(result.text, "This is a test transcription")
        self.assertIsNone(result.error)
        self.assertGreater(result.duration_seconds, 0)
        self.assertEqual(result.model_info["engine"], "openai-whisper")
    
    @patch('core.transcription_service.faster_whisper')
    def test_multiple_transcriptions_same_service(self, mock_faster_whisper):
        """Test multiple transcriptions using the same service instance"""
        # Mock the Whisper model with different responses
        def mock_transcribe(audio_path, **kwargs):
            if "short" in audio_path:
                mock_segment = Mock()
                mock_segment.text = "Short audio"
                return ([mock_segment], Mock(language="en", duration=1.0))
            else:
                mock_segment = Mock()
                mock_segment.text = "Medium audio"
                return ([mock_segment], Mock(language="en", duration=3.0))
        
        mock_model = Mock()
        mock_model.transcribe.side_effect = mock_transcribe
        mock_whisper_class = Mock(return_value=mock_model)
        mock_faster_whisper.WhisperModel = mock_whisper_class
        
        # Create service (model loads once)
        config = TranscriptionConfig(model_size="tiny", engine="faster")
        service = TranscriptionService(config)
        service._faster_whisper_available = True
        service._engines_checked = True
        
        # First transcription
        result1 = service.transcribe(self.short_audio)
        self.assertTrue(result1.success)
        self.assertEqual(result1.text, "Short audio")
        
        # Second transcription (reuses loaded model)
        result2 = service.transcribe(self.medium_audio)
        self.assertTrue(result2.success)
        self.assertEqual(result2.text, "Medium audio")
        
        # Model should be loaded only once
        self.assertEqual(mock_whisper_class.call_count, 1)
    
    @patch('core.transcription_service.faster_whisper')
    def test_transcription_with_status_callbacks(self, mock_faster_whisper):
        """Test transcription with status update callbacks"""
        # Mock model
        mock_segment = Mock()
        mock_segment.text = "Test with callbacks"
        mock_info = Mock(language="en", duration=1.0)
        
        mock_model = Mock()
        mock_model.transcribe.return_value = ([mock_segment], mock_info)
        mock_whisper_class = Mock(return_value=mock_model)
        mock_faster_whisper.WhisperModel = mock_whisper_class
        
        # Track status updates
        status_updates = []
        
        def status_callback(message):
            status_updates.append(message)
        
        # Create service with callback
        config = TranscriptionConfig(model_size="tiny", engine="faster")
        service = TranscriptionService(config)
        service.set_status_callback(status_callback)
        service._faster_whisper_available = True
        service._engines_checked = True
        
        # Transcribe
        result = service.transcribe(self.short_audio)
        
        # Verify transcription succeeded
        self.assertTrue(result.success)
        self.assertEqual(result.text, "Test with callbacks")
        
        # Verify status callbacks were called
        self.assertGreater(len(status_updates), 0)
        self.assertTrue(any("Loading" in msg for msg in status_updates))
        self.assertTrue(any("Transcribing" in msg or "complete" in msg for msg in status_updates))
    
    @patch('core.transcription_service.faster_whisper')
    def test_transcription_error_recovery(self, mock_faster_whisper):
        """Test error handling in transcription pipeline"""
        # Mock failure scenario
        mock_model = Mock()
        mock_model.transcribe.side_effect = Exception("Transcription failed")
        mock_whisper_class = Mock(return_value=mock_model)
        mock_faster_whisper.WhisperModel = mock_whisper_class
        
        # Create service
        config = TranscriptionConfig(model_size="tiny", engine="faster")
        service = TranscriptionService(config)
        service._faster_whisper_available = True
        service._engines_checked = True
        
        # Transcription should fail (after retries are exhausted)
        result = service.transcribe(self.short_audio)
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)
        self.assertEqual(result.error_type, "WhisperError")
    
    @patch('core.transcription_service.faster_whisper')
    def test_transcription_with_different_languages(self, mock_faster_whisper):
        """Test transcription with different language configurations"""
        def mock_transcribe_lang(audio_path, **kwargs):
            lang = kwargs.get("language", "auto")
            mock_segment = Mock()
            mock_segment.text = f"Text in {lang}"
            return ([mock_segment], Mock(language=lang, duration=1.0))
        
        mock_model = Mock()
        mock_model.transcribe.side_effect = mock_transcribe_lang
        mock_whisper_class = Mock(return_value=mock_model)
        mock_faster_whisper.WhisperModel = mock_whisper_class
        
        # Test English
        config_en = TranscriptionConfig(model_size="tiny", engine="faster", language="en")
        service_en = TranscriptionService(config_en)
        service_en._faster_whisper_available = True
        service_en._engines_checked = True
        
        result_en = service_en.transcribe(self.short_audio)
        self.assertTrue(result_en.success)
        self.assertIn("en", result_en.text)
        
        # Test Spanish
        config_es = TranscriptionConfig(model_size="tiny", engine="faster", language="es")
        service_es = TranscriptionService(config_es)
        service_es._faster_whisper_available = True
        service_es._engines_checked = True
        
        result_es = service_es.transcribe(self.short_audio)
        self.assertTrue(result_es.success)
        self.assertIn("es", result_es.text)
    
    @patch('core.transcription_service.faster_whisper')
    def test_service_lifecycle(self, mock_faster_whisper):
        """Test complete service lifecycle: init -> load -> transcribe -> unload"""
        # Mock model
        mock_segment = Mock()
        mock_segment.text = "Lifecycle test"
        mock_info = Mock(language="en", duration=1.0)
        
        mock_model = Mock()
        mock_model.transcribe.return_value = ([mock_segment], mock_info)
        mock_whisper_class = Mock(return_value=mock_model)
        mock_faster_whisper.WhisperModel = mock_whisper_class
        
        # 1. Initialize service
        config = TranscriptionConfig(model_size="tiny", engine="faster")
        service = TranscriptionService(config)
        service._faster_whisper_available = True
        service._engines_checked = True
        
        self.assertFalse(service.is_model_loaded())
        
        # 2. Load model
        success = service.ensure_model_loaded(timeout_seconds=5)
        self.assertTrue(success)
        self.assertTrue(service.is_model_loaded())
        
        # 3. Transcribe
        result = service.transcribe(self.short_audio)
        self.assertTrue(result.success)
        self.assertEqual(result.text, "Lifecycle test")
        
        # 4. Check status
        status = service.get_status()
        self.assertTrue(status["model_loaded"])
        self.assertEqual(status["engine"], "faster")
        
        # 5. Unload model
        service.unload_model()
        self.assertFalse(service.is_model_loaded())
        
        # 6. Model reloads automatically on next transcription
        result2 = service.transcribe(self.short_audio)
        self.assertTrue(result2.success)
        self.assertTrue(service.is_model_loaded())


if __name__ == '__main__':
    unittest.main()
