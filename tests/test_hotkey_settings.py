#!/usr/bin/env python3
"""
Individual tests for hotkey settings.
Tests hotkey selection and validation.
"""

import unittest
import tempfile
import os
from PyQt5.QtCore import QSettings

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.settings_manager import SettingsManager

class TestHotkeySettings(unittest.TestCase):
    """Test hotkey-specific settings."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.settings_file = os.path.join(self.temp_dir, "hotkey_test_settings.ini")
        self.settings_manager = SettingsManager("HotkeyTest", "TestApp")
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
    
    def test_hotkey_setting(self):
        """Test hotkey setting."""
        valid_hotkeys = [
            "F8", "F9", "ctrl+shift+R", "ctrl+alt+S", "alt gr", 
            "caps lock", "cmd+R", "shift+F12"
        ]
        
        for hotkey in valid_hotkeys:
            self.settings_manager.set("behavior/hotkey", hotkey)
            self.assertEqual(self.settings_manager.get("behavior/hotkey"), hotkey)
    
    def test_hotkey_validation(self):
        """Test hotkey validation."""
        # Test invalid hotkey (should default to "alt gr")
        self.settings_manager.set("behavior/hotkey", "invalid_hotkey")
        self.assertEqual(self.settings_manager.get("behavior/hotkey"), "alt gr")
        
        # Test None value (should default to "alt gr")
        self.settings_manager.set("behavior/hotkey", None)
        self.assertEqual(self.settings_manager.get("behavior/hotkey"), "alt gr")
        
        # Test empty string (should default to "alt gr")
        self.settings_manager.set("behavior/hotkey", "")
        self.assertEqual(self.settings_manager.get("behavior/hotkey"), "alt gr")
    
    def test_hotkey_case_sensitivity(self):
        """Test that hotkey validation is case sensitive."""
        # Test exact case match
        self.settings_manager.set("behavior/hotkey", "alt gr")
        self.assertEqual(self.settings_manager.get("behavior/hotkey"), "alt gr")
        
        # Test different case (should default to "alt gr")
        self.settings_manager.set("behavior/hotkey", "ALT GR")
        self.assertEqual(self.settings_manager.get("behavior/hotkey"), "alt gr")
    
    def test_hotkey_whitespace_handling(self):
        """Test hotkey whitespace handling."""
        # Test with leading/trailing whitespace
        self.settings_manager.set("behavior/hotkey", "  alt gr  ")
        self.assertEqual(self.settings_manager.get("behavior/hotkey"), "alt gr")
        
        # Test with extra spaces
        self.settings_manager.set("behavior/hotkey", "alt  gr")
        self.assertEqual(self.settings_manager.get("behavior/hotkey"), "alt gr")
    
    def test_hotkey_settings_persistence(self):
        """Test that hotkey settings persist across sessions."""
        # Set a hotkey
        self.settings_manager.set("behavior/hotkey", "F8")
        
        # Create new settings manager (simulating app restart)
        new_manager = SettingsManager("HotkeyTest2", "TestApp2")
        new_manager.settings = QSettings(os.path.join(self.temp_dir, "hotkey_test2_settings.ini"), QSettings.IniFormat)
        
        # Import settings
        export_file = os.path.join(self.temp_dir, "hotkey_export.json")
        self.settings_manager.export_json(export_file)
        new_manager.import_json(export_file)
        
        # Verify hotkey was imported
        self.assertEqual(new_manager.get("behavior/hotkey"), "F8")
    
    def test_hotkey_default_value(self):
        """Test hotkey default value."""
        # Test that default is "alt gr" when no value is set
        self.assertEqual(self.settings_manager.get("behavior/hotkey"), "alt gr")

if __name__ == '__main__':
    unittest.main()
