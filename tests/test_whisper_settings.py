#!/usr/bin/env python3
"""
Individual tests for Whisper settings.
Tests model selection, temperature, and speed mode settings.
"""

import unittest
import tempfile
import os
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.settings_manager import SettingsManager

class TestWhisperSettings(unittest.TestCase):
    """Test Whisper-specific settings."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.settings_file = os.path.join(self.temp_dir, "whisper_test_settings.ini")
        self.settings_manager = SettingsManager("WhisperTest", "TestApp")
        self.settings_manager.settings = QSettings(self.settings_file, QSettings.IniFormat)
    
    def tearDown(self):
        """Clean up test environment."""
        try:
            if os.path.exists(self.settings_file):
                os.unlink(self.settings_file)
            for file in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            os.rmdir(self.temp_dir)
        except OSError:
            pass
    
    def test_model_selection(self):
        """Test Whisper model selection."""
        # Test valid models
        valid_models = ["tiny", "base", "small", "medium", "large"]
        for model in valid_models:
            self.settings_manager.set("whisper/model_name", model)
            self.assertEqual(self.settings_manager.get("whisper/model_name"), model)
        
        # Test invalid model (should default to tiny)
        self.settings_manager.set("whisper/model_name", "huge")
        self.assertEqual(self.settings_manager.get("whisper/model_name"), "tiny")
        
        # Test case insensitive
        self.settings_manager.set("whisper/model_name", "LARGE")
        self.assertEqual(self.settings_manager.get("whisper/model_name"), "large")
    
    def test_temperature_setting(self):
        """Test temperature setting validation."""
        # Test valid temperatures
        valid_temps = [0.0, 0.2, 0.5, 0.8, 1.0]
        for temp in valid_temps:
            self.settings_manager.set("whisper/temperature", temp)
            self.assertEqual(self.settings_manager.get("whisper/temperature"), temp)
        
        # Test clamping
        self.settings_manager.set("whisper/temperature", -0.1)
        self.assertEqual(self.settings_manager.get("whisper/temperature"), 0.0)
        
        self.settings_manager.set("whisper/temperature", 1.5)
        self.assertEqual(self.settings_manager.get("whisper/temperature"), 1.0)
        
        # Test string values
        self.settings_manager.set("whisper/temperature", "0.7")
        self.assertEqual(self.settings_manager.get("whisper/temperature"), 0.7)
        
        # Test invalid values (should default to 0.0)
        self.settings_manager.set("whisper/temperature", "invalid")
        self.assertEqual(self.settings_manager.get("whisper/temperature"), 0.0)
    
    def test_speed_mode(self):
        """Test speed mode setting."""
        # Test boolean values
        self.settings_manager.set("whisper/speed_mode", True)
        self.assertTrue(self.settings_manager.get("whisper/speed_mode"))
        
        self.settings_manager.set("whisper/speed_mode", False)
        self.assertFalse(self.settings_manager.get("whisper/speed_mode"))
        
        # Test string representations
        self.settings_manager.set("whisper/speed_mode", "1")
        self.assertTrue(self.settings_manager.get("whisper/speed_mode"))
        
        self.settings_manager.set("whisper/speed_mode", "0")
        self.assertFalse(self.settings_manager.get("whisper/speed_mode"))
    
    def test_whisper_settings_validation(self):
        """Test Whisper settings validation edge cases."""
        # Test invalid model
        self.settings_manager.set("whisper/model_name", None)
        self.assertEqual(self.settings_manager.get("whisper/model_name"), "tiny")
        
        # Test invalid temperature
        self.settings_manager.set("whisper/temperature", None)
        self.assertEqual(self.settings_manager.get("whisper/temperature"), 0.0)
        
        # Test invalid speed mode
        self.settings_manager.set("whisper/speed_mode", "maybe")
        self.assertTrue(self.settings_manager.get("whisper/speed_mode"))  # Should default to True
    
    def test_whisper_settings_persistence(self):
        """Test that Whisper settings persist across sessions."""
        # Set some Whisper settings
        self.settings_manager.set("whisper/model_name", "medium")
        self.settings_manager.set("whisper/temperature", 0.3)
        self.settings_manager.set("whisper/speed_mode", False)
        
        # Create new settings manager (simulating app restart)
        new_manager = SettingsManager("WhisperTest2", "TestApp2")
        new_manager.settings = QSettings(os.path.join(self.temp_dir, "whisper_test2_settings.ini"), QSettings.IniFormat)
        
        # Import settings
        export_file = os.path.join(self.temp_dir, "whisper_export.json")
        self.settings_manager.export_json(export_file)
        new_manager.import_json(export_file)
        
        # Verify settings were imported
        self.assertEqual(new_manager.get("whisper/model_name"), "medium")
        self.assertEqual(new_manager.get("whisper/temperature"), 0.3)
        self.assertFalse(new_manager.get("whisper/speed_mode"))

if __name__ == '__main__':
    # Set up QApplication for tests
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    unittest.main()
