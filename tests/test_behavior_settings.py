#!/usr/bin/env python3
"""
Individual tests for behavior settings.
Tests behavior-related settings like auto-paste, toggle mode, and visual indicator.
"""

import unittest
import tempfile
import os
from PyQt5.QtCore import QSettings

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.settings_manager import SettingsManager

class TestBehaviorSettings(unittest.TestCase):
    """Test behavior-specific settings."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.settings_file = os.path.join(self.temp_dir, "behavior_test_settings.ini")
        self.settings_manager = SettingsManager("BehaviorTest", "TestApp")
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
    
    def test_auto_paste_setting(self):
        """Test auto-paste setting."""
        # Test boolean values
        self.settings_manager.set("behavior/auto_paste", True)
        self.assertTrue(self.settings_manager.get("behavior/auto_paste"))
        
        self.settings_manager.set("behavior/auto_paste", False)
        self.assertFalse(self.settings_manager.get("behavior/auto_paste"))
        
        # Test string representations
        self.settings_manager.set("behavior/auto_paste", "yes")
        self.assertTrue(self.settings_manager.get("behavior/auto_paste"))
        
        self.settings_manager.set("behavior/auto_paste", "no")
        self.assertFalse(self.settings_manager.get("behavior/auto_paste"))
    
    def test_toggle_mode_setting(self):
        """Test toggle mode setting."""
        # Test boolean values
        self.settings_manager.set("behavior/toggle_mode", True)
        self.assertTrue(self.settings_manager.get("behavior/toggle_mode"))
        
        self.settings_manager.set("behavior/toggle_mode", False)
        self.assertFalse(self.settings_manager.get("behavior/toggle_mode"))
        
        # Test string representations
        self.settings_manager.set("behavior/toggle_mode", "on")
        self.assertTrue(self.settings_manager.get("behavior/toggle_mode"))
        
        self.settings_manager.set("behavior/toggle_mode", "off")
        self.assertFalse(self.settings_manager.get("behavior/toggle_mode"))
    
    def test_visual_indicator_setting(self):
        """Test visual indicator setting."""
        # Test boolean values
        self.settings_manager.set("behavior/visual_indicator", True)
        self.assertTrue(self.settings_manager.get("behavior/visual_indicator"))
        
        self.settings_manager.set("behavior/visual_indicator", False)
        self.assertFalse(self.settings_manager.get("behavior/visual_indicator"))
        
        # Test string representations
        self.settings_manager.set("behavior/visual_indicator", "1")
        self.assertTrue(self.settings_manager.get("behavior/visual_indicator"))
        
        self.settings_manager.set("behavior/visual_indicator", "0")
        self.assertFalse(self.settings_manager.get("behavior/visual_indicator"))
    
    def test_indicator_position_setting(self):
        """Test indicator position setting."""
        valid_positions = [
            "Top Left", "Top Right", "Bottom Right", "Bottom Left",
            "Top Center", "Middle Center", "Bottom Center"
        ]
        
        for position in valid_positions:
            self.settings_manager.set("behavior/indicator_position", position)
            self.assertEqual(self.settings_manager.get("behavior/indicator_position"), position)
        
        # Test invalid position (should default to "Bottom Center")
        self.settings_manager.set("behavior/indicator_position", "Invalid Position")
        self.assertEqual(self.settings_manager.get("behavior/indicator_position"), "Bottom Center")
    
    def test_behavior_settings_validation(self):
        """Test behavior settings validation."""
        # Test invalid boolean values (should default to True for auto_paste and visual_indicator, False for toggle_mode)
        self.settings_manager.set("behavior/auto_paste", "maybe")
        self.assertTrue(self.settings_manager.get("behavior/auto_paste"))
        
        self.settings_manager.set("behavior/toggle_mode", "invalid")
        self.assertFalse(self.settings_manager.get("behavior/toggle_mode"))
        
        self.settings_manager.set("behavior/visual_indicator", "unknown")
        self.assertTrue(self.settings_manager.get("behavior/visual_indicator"))
        
        # Test None values
        self.settings_manager.set("behavior/auto_paste", None)
        self.assertTrue(self.settings_manager.get("behavior/auto_paste"))
        
        self.settings_manager.set("behavior/toggle_mode", None)
        self.assertFalse(self.settings_manager.get("behavior/toggle_mode"))
        
        self.settings_manager.set("behavior/visual_indicator", None)
        self.assertTrue(self.settings_manager.get("behavior/visual_indicator"))
    
    def test_behavior_settings_persistence(self):
        """Test that behavior settings persist across sessions."""
        # Set some behavior settings
        self.settings_manager.set("behavior/auto_paste", False)
        self.settings_manager.set("behavior/toggle_mode", True)
        self.settings_manager.set("behavior/visual_indicator", False)
        self.settings_manager.set("behavior/indicator_position", "Top Left")
        
        # Create new settings manager (simulating app restart)
        new_manager = SettingsManager("BehaviorTest2", "TestApp2")
        new_manager.settings = QSettings(os.path.join(self.temp_dir, "behavior_test2_settings.ini"), QSettings.IniFormat)
        
        # Import settings
        export_file = os.path.join(self.temp_dir, "behavior_export.json")
        self.settings_manager.export_json(export_file)
        new_manager.import_json(export_file)
        
        # Verify settings were imported
        self.assertFalse(new_manager.get("behavior/auto_paste"))
        self.assertTrue(new_manager.get("behavior/toggle_mode"))
        self.assertFalse(new_manager.get("behavior/visual_indicator"))
        self.assertEqual(new_manager.get("behavior/indicator_position"), "Top Left")
    
    def test_behavior_settings_defaults(self):
        """Test behavior settings default values."""
        # Test that defaults are applied when no value is set
        self.assertEqual(self.settings_manager.get("behavior/auto_paste"), True)
        self.assertEqual(self.settings_manager.get("behavior/toggle_mode"), False)
        self.assertEqual(self.settings_manager.get("behavior/visual_indicator"), True)
        self.assertEqual(self.settings_manager.get("behavior/indicator_position"), "Bottom Center")

if __name__ == '__main__':
    unittest.main()
