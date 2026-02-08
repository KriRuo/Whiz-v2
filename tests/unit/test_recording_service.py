#!/usr/bin/env python3
"""
Unit tests for RecordingService.
Tests recording lifecycle, state management, device selection, and error handling.
"""

import unittest
import tempfile
import os
import time
import sys
from unittest.mock import Mock, patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock sounddevice before importing audio_manager
sys.modules['sounddevice'] = MagicMock()

from core.recording_service import (
    RecordingService,
    RecordingConfig,
    RecordingResult,
    RecordingState
)


class TestRecordingConfig(unittest.TestCase):
    """Test RecordingConfig validation"""
    
    def test_valid_config(self):
        """Test creating valid configuration"""
        config = RecordingConfig(
            sample_rate=16000,
            channels=1,
            chunk_size=1024
        )
        self.assertEqual(config.sample_rate, 16000)
        self.assertEqual(config.channels, 1)
        self.assertEqual(config.chunk_size, 1024)
    
    def test_invalid_sample_rate(self):
        """Test that invalid sample rate raises error"""
        with self.assertRaises(ValueError) as cm:
            RecordingConfig(sample_rate=0)
        self.assertIn("sample_rate", str(cm.exception))
    
    def test_invalid_channels(self):
        """Test that invalid channels raises error"""
        with self.assertRaises(ValueError):
            RecordingConfig(channels=3)
    
    def test_invalid_chunk_size(self):
        """Test that invalid chunk size raises error"""
        with self.assertRaises(ValueError):
            RecordingConfig(chunk_size=-1)
    
    def test_default_values(self):
        """Test default configuration values"""
        config = RecordingConfig()
        self.assertEqual(config.sample_rate, 16000)
        self.assertEqual(config.channels, 1)
        self.assertEqual(config.chunk_size, 1024)
        self.assertIsNone(config.device_index)


class TestRecordingResult(unittest.TestCase):
    """Test RecordingResult data class"""
    
    def test_success_result(self):
        """Test successful recording result"""
        result = RecordingResult(
            success=True,
            audio_path="/tmp/test.wav",
            duration_seconds=5.5,
            samples_recorded=88200
        )
        self.assertTrue(result.success)
        self.assertEqual(result.audio_path, "/tmp/test.wav")
        self.assertIsNone(result.error)
    
    def test_error_result(self):
        """Test error recording result"""
        result = RecordingResult(
            success=False,
            error="Device not found",
            error_type="DeviceError"
        )
        self.assertFalse(result.success)
        self.assertIsNone(result.audio_path)
        self.assertEqual(result.error, "Device not found")
    
    def test_to_dict(self):
        """Test converting result to dictionary"""
        result = RecordingResult(
            success=True,
            audio_path="/tmp/test.wav",
            duration_seconds=3.0
        )
        result_dict = result.to_dict()
        
        self.assertIsInstance(result_dict, dict)
        self.assertTrue(result_dict["success"])
        self.assertEqual(result_dict["audio_path"], "/tmp/test.wav")


class TestRecordingService(unittest.TestCase):
    """Test RecordingService class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = RecordingConfig(
            sample_rate=16000,
            channels=1,
            chunk_size=1024
        )
    
    @patch('core.recording_service.AudioManager')
    def test_service_initialization(self, mock_audio_manager_class):
        """Test that service initializes correctly"""
        mock_audio_manager = Mock()
        mock_audio_manager.is_available.return_value = True
        mock_audio_manager_class.return_value = mock_audio_manager
        
        service = RecordingService(self.config)
        
        self.assertIsNotNone(service)
        self.assertEqual(service.config.sample_rate, 16000)
        self.assertEqual(service.get_state(), RecordingState.IDLE)
        self.assertFalse(service.is_recording())
    
    @patch('core.recording_service.AudioManager')
    def test_callbacks(self, mock_audio_manager_class):
        """Test callback functionality"""
        mock_audio_manager = Mock()
        mock_audio_manager.is_available.return_value = True
        mock_audio_manager_class.return_value = mock_audio_manager
        
        service = RecordingService(self.config)
        
        # Test status callback
        status_messages = []
        service.set_status_callback(lambda msg: status_messages.append(msg))
        service._update_status("Test message")
        self.assertEqual(len(status_messages), 1)
        self.assertEqual(status_messages[0], "Test message")
        
        # Test audio level callback
        levels = []
        service.set_audio_level_callback(lambda level: levels.append(level))
        service._on_audio_level(0.5)
        self.assertEqual(len(levels), 1)
        self.assertEqual(levels[0], 0.5)
        
        # Test state change callback
        states = []
        service.set_state_change_callback(lambda state: states.append(state))
        service._set_state(RecordingState.RECORDING)
        self.assertEqual(len(states), 1)
        self.assertEqual(states[0], RecordingState.RECORDING)
    
    @patch('core.recording_service.AudioManager')
    def test_get_available_devices(self, mock_audio_manager_class):
        """Test getting available devices"""
        mock_audio_manager = Mock()
        mock_audio_manager.is_available.return_value = True
        mock_audio_manager.get_devices.return_value = [
            {"name": "Device 1", "index": 0},
            {"name": "Device 2", "index": 1}
        ]
        mock_audio_manager_class.return_value = mock_audio_manager
        
        service = RecordingService(self.config)
        devices = service.get_available_devices()
        
        self.assertEqual(len(devices), 2)
        self.assertEqual(devices[0]["name"], "Device 1")
    
    @patch('core.recording_service.AudioManager')
    def test_select_device(self, mock_audio_manager_class):
        """Test device selection"""
        mock_audio_manager = Mock()
        mock_audio_manager.is_available.return_value = True
        mock_audio_manager.select_device.return_value = True
        mock_audio_manager.get_devices.return_value = [
            {"name": "Test Device", "index": 0}
        ]
        mock_audio_manager_class.return_value = mock_audio_manager
        
        service = RecordingService(self.config)
        success = service.select_device(0)
        
        self.assertTrue(success)
        mock_audio_manager.select_device.assert_called_with(0)
    
    @patch('core.recording_service.create_safe_temp_file')
    @patch('core.recording_service.AudioManager')
    def test_start_recording_success(self, mock_audio_manager_class, mock_create_temp):
        """Test successful recording start"""
        mock_audio_manager = Mock()
        mock_audio_manager.is_available.return_value = True
        mock_audio_manager.start_recording.return_value = True
        mock_audio_manager_class.return_value = mock_audio_manager
        
        mock_create_temp.return_value = "/tmp/test_audio.wav"
        
        service = RecordingService(self.config)
        success = service.start_recording()
        
        self.assertTrue(success)
        self.assertEqual(service.get_state(), RecordingState.RECORDING)
        self.assertTrue(service.is_recording())
        mock_audio_manager.start_recording.assert_called_once()
    
    @patch('core.recording_service.AudioManager')
    def test_start_recording_when_already_recording(self, mock_audio_manager_class):
        """Test starting recording when already recording"""
        mock_audio_manager = Mock()
        mock_audio_manager.is_available.return_value = True
        mock_audio_manager.start_recording.return_value = True
        mock_audio_manager_class.return_value = mock_audio_manager
        
        service = RecordingService(self.config)
        service._set_state(RecordingState.RECORDING)
        
        success = service.start_recording()
        self.assertFalse(success)
    
    @patch('core.recording_service.Path')
    @patch('core.recording_service.create_safe_temp_file')
    @patch('core.recording_service.AudioManager')
    def test_stop_recording_success(self, mock_audio_manager_class, mock_create_temp, mock_path_class):
        """Test successful recording stop"""
        mock_audio_manager = Mock()
        mock_audio_manager.is_available.return_value = True
        mock_audio_manager.start_recording.return_value = True
        mock_audio_manager.stop_recording.return_value = "/tmp/test_audio.wav"
        mock_audio_manager_class.return_value = mock_audio_manager
        
        mock_create_temp.return_value = "/tmp/test_audio.wav"
        
        # Mock Path.exists
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path_class.return_value = mock_path_instance
        
        service = RecordingService(self.config)
        service.start_recording()
        
        time.sleep(0.1)  # Small delay to ensure duration > 0
        
        result = service.stop_recording()
        
        self.assertTrue(result.success)
        self.assertEqual(result.audio_path, "/tmp/test_audio.wav")
        self.assertGreater(result.duration_seconds, 0)
        self.assertEqual(service.get_state(), RecordingState.IDLE)
        self.assertFalse(service.is_recording())
    
    @patch('core.recording_service.AudioManager')
    def test_stop_recording_when_not_recording(self, mock_audio_manager_class):
        """Test stopping recording when not recording"""
        mock_audio_manager = Mock()
        mock_audio_manager.is_available.return_value = True
        mock_audio_manager_class.return_value = mock_audio_manager
        
        service = RecordingService(self.config)
        result = service.stop_recording()
        
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)
        self.assertEqual(result.error_type, "InvalidState")
    
    @patch('core.recording_service.AudioManager')
    def test_cancel_recording(self, mock_audio_manager_class):
        """Test cancelling recording"""
        mock_audio_manager = Mock()
        mock_audio_manager.is_available.return_value = True
        mock_audio_manager.start_recording.return_value = True
        mock_audio_manager.stop_recording.return_value = None
        mock_audio_manager_class.return_value = mock_audio_manager
        
        service = RecordingService(self.config)
        service._set_state(RecordingState.RECORDING)
        
        service.cancel_recording()
        
        self.assertEqual(service.get_state(), RecordingState.IDLE)
        mock_audio_manager.stop_recording.assert_called_with(None)
    
    @patch('core.recording_service.AudioManager')
    def test_get_recording_duration(self, mock_audio_manager_class):
        """Test getting recording duration"""
        mock_audio_manager = Mock()
        mock_audio_manager.is_available.return_value = True
        mock_audio_manager.start_recording.return_value = True
        mock_audio_manager_class.return_value = mock_audio_manager
        
        service = RecordingService(self.config)
        
        # No duration when not recording
        self.assertEqual(service.get_recording_duration(), 0.0)
        
        # Duration increases while recording
        service._set_state(RecordingState.RECORDING)
        service.recording_start_time = time.time()
        
        time.sleep(0.1)
        duration = service.get_recording_duration()
        self.assertGreater(duration, 0.05)
    
    @patch('core.recording_service.AudioManager')
    def test_get_status(self, mock_audio_manager_class):
        """Test getting service status"""
        mock_audio_manager = Mock()
        mock_audio_manager.is_available.return_value = True
        mock_audio_manager_class.return_value = mock_audio_manager
        
        service = RecordingService(self.config)
        status = service.get_status()
        
        self.assertEqual(status["state"], "idle")
        self.assertFalse(status["is_recording"])
        self.assertEqual(status["sample_rate"], 16000)
        self.assertTrue(status["audio_available"])
    
    @patch('core.recording_service.AudioManager')
    def test_cleanup(self, mock_audio_manager_class):
        """Test service cleanup"""
        mock_audio_manager = Mock()
        mock_audio_manager.is_available.return_value = True
        mock_audio_manager.start_recording.return_value = True
        mock_audio_manager.stop_recording.return_value = None
        mock_audio_manager_class.return_value = mock_audio_manager
        
        service = RecordingService(self.config)
        service._set_state(RecordingState.RECORDING)
        
        service.cleanup()
        
        self.assertEqual(service.get_state(), RecordingState.IDLE)


if __name__ == '__main__':
    unittest.main()
