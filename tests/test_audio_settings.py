#!/usr/bin/env python3
"""
Individual tests for audio settings.
Tests sound effects, tone files, and audio validation.
"""

import unittest
import tempfile
import os
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.settings_manager import SettingsManager

class TestAudioSettings(unittest.TestCase):
    """Test audio-specific settings."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.settings_file = os.path.join(self.temp_dir, "audio_test_settings.ini")
        self.settings_manager = SettingsManager("AudioTest", "TestApp")
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
    
    def test_sound_effects_enabled(self):
        """Test sound effects enabled setting."""
        # Test boolean values
        self.settings_manager.set("audio/effects_enabled", True)
        self.assertTrue(self.settings_manager.get("audio/effects_enabled"))
        
        self.settings_manager.set("audio/effects_enabled", False)
        self.assertFalse(self.settings_manager.get("audio/effects_enabled"))
        
        # Test string representations
        self.settings_manager.set("audio/effects_enabled", "yes")
        self.assertTrue(self.settings_manager.get("audio/effects_enabled"))
        
        self.settings_manager.set("audio/effects_enabled", "no")
        self.assertFalse(self.settings_manager.get("audio/effects_enabled"))
    
    def test_tone_file_paths(self):
        """Test tone file path settings."""
        # Test with existing file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_wav = f.name
        
        try:
            # Test start tone
            self.settings_manager.set("audio/start_tone", temp_wav)
            self.assertEqual(self.settings_manager.get("audio/start_tone"), temp_wav)
            
            # Test stop tone
            self.settings_manager.set("audio/stop_tone", temp_wav)
            self.assertEqual(self.settings_manager.get("audio/stop_tone"), temp_wav)
            
        finally:
            os.unlink(temp_wav)
        
        # Test with non-existent file (should keep the path)
        self.settings_manager.set("audio/start_tone", "nonexistent.wav")
        self.assertEqual(self.settings_manager.get("audio/start_tone"), "nonexistent.wav")
        
        # Test with empty path (should use default)
        self.settings_manager.set("audio/start_tone", "")
        self.assertEqual(self.settings_manager.get("audio/start_tone"), "assets/sound_start_v9.wav")
    
    def test_audio_settings_validation(self):
        """Test audio settings validation."""
        # Test invalid boolean values
        self.settings_manager.set("audio/effects_enabled", "maybe")
        self.assertTrue(self.settings_manager.get("audio/effects_enabled"))  # Should default to True
        
        # Test tone path validation - invalid value should use default
        self.settings_manager.set("audio/start_tone", None)
        result = self.settings_manager.get("audio/start_tone")
        # Should get default value (assets/sound_start_v9.wav) since None is invalid
        self.assertIsNotNone(result)
        self.assertTrue(result.endswith('.wav'))
    
    def test_audio_settings_persistence(self):
        """Test that audio settings persist across sessions."""
        # Set some audio settings using correct schema keys
        self.settings_manager.set("audio/effects_enabled", False)
        self.settings_manager.set("audio/start_tone", "custom_start.wav")
        self.settings_manager.set("audio/stop_tone", "custom_stop.wav")
        
        # Create new settings manager (simulating app restart)
        new_manager = SettingsManager("AudioTest2", "TestApp2")
        new_manager.settings = QSettings(os.path.join(self.temp_dir, "audio_test2_settings.ini"), QSettings.IniFormat)
        
        # Import settings
        export_file = os.path.join(self.temp_dir, "audio_export.json")
        self.settings_manager.export_json(export_file)
        new_manager.import_json(export_file)
        
        # Verify settings were imported
        self.assertFalse(new_manager.get("audio/effects_enabled"))
        self.assertEqual(new_manager.get("audio/start_tone"), "custom_start.wav")
        self.assertEqual(new_manager.get("audio/stop_tone"), "custom_stop.wav")

if __name__ == '__main__':
    # Set up QApplication for tests
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    unittest.main()
