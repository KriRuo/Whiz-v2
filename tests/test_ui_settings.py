#!/usr/bin/env python3
"""
Individual tests for UI settings.
Tests theme, auto dark mode, and startup tab settings.
"""

import unittest
import tempfile
import os
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.settings_manager import SettingsManager

class TestUISettings(unittest.TestCase):
    """Test UI-specific settings."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.settings_file = os.path.join(self.temp_dir, "ui_test_settings.ini")
        self.settings_manager = SettingsManager("UITest", "TestApp")
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
    
    def test_theme_settings(self):
        """Test theme setting validation and persistence."""
        # Test valid themes
        valid_themes = ["system", "light", "dark"]
        for theme in valid_themes:
            self.settings_manager.set("ui/theme", theme)
            self.assertEqual(self.settings_manager.get("ui/theme"), theme)
        
        # Test invalid theme (should default to system)
        self.settings_manager.set("ui/theme", "invalid_theme")
        self.assertEqual(self.settings_manager.get("ui/theme"), "system")
    
    def test_minimize_to_tray_setting(self):
        """Test minimize_to_tray setting validation and persistence."""
        # Test default value
        self.assertFalse(self.settings_manager.get("behavior/minimize_to_tray"))
        
        # Test setting to True
        self.settings_manager.set("behavior/minimize_to_tray", True)
        self.assertTrue(self.settings_manager.get("behavior/minimize_to_tray"))
        
        # Test setting to False
        self.settings_manager.set("behavior/minimize_to_tray", False)
        self.assertFalse(self.settings_manager.get("behavior/minimize_to_tray"))
        
        # Test string values
        self.settings_manager.set("behavior/minimize_to_tray", "true")
        self.assertTrue(self.settings_manager.get("behavior/minimize_to_tray"))
        
        self.settings_manager.set("behavior/minimize_to_tray", "false")
        self.assertFalse(self.settings_manager.get("behavior/minimize_to_tray"))
        
        # Test invalid value (should default to False)
        self.settings_manager.set("behavior/minimize_to_tray", "invalid")
        self.assertFalse(self.settings_manager.get("behavior/minimize_to_tray"))
        
        # Test case insensitive
        self.settings_manager.set("ui/theme", "DARK")
        self.assertEqual(self.settings_manager.get("ui/theme"), "dark")
    
    
    def test_ui_settings_persistence(self):
        """Test that UI settings persist across sessions."""
        # Set some UI settings
        self.settings_manager.set("ui/theme", "dark")
        self.settings_manager.set("ui/auto_dark_follow_system", False)
        
        # Create new settings manager (simulating app restart)
        new_manager = SettingsManager("UITest2", "TestApp2")
        new_manager.settings = QSettings(os.path.join(self.temp_dir, "ui_test2_settings.ini"), QSettings.IniFormat)
        
        # Import settings
        export_file = os.path.join(self.temp_dir, "ui_export.json")
        self.settings_manager.export_json(export_file)
        new_manager.import_json(export_file)
        
        # Verify settings were imported
        self.assertEqual(new_manager.get("ui/theme"), "dark")
        self.assertFalse(new_manager.get("ui/auto_dark_follow_system"))

if __name__ == '__main__':
    # Set up QApplication for tests
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    unittest.main()
