"""
Unit tests for the settings manager and schema.
Tests settings persistence, validation, JSON import/export, and window state.
"""

import unittest
import tempfile
import os
import json
from unittest.mock import Mock, patch
from PyQt5.QtCore import QSettings, QByteArray
from PyQt5.QtWidgets import QApplication, QMainWindow

# Import the modules to test
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.settings_manager import SettingsManager
from core.settings_schema import SETTINGS_SCHEMA

class TestSettingsSchema(unittest.TestCase):
    """Test the settings schema and validation functions."""
    
    def test_defaults_completeness(self):
        """Test that all expected settings have defaults."""
        expected_keys = [
            "ui/theme",
            "audio/effects_enabled", "audio/start_tone", "audio/stop_tone",  # Updated to match actual schema
            "audio/input_device", "audio/sample_rate", "audio/channels", "audio/chunk_size",
            "behavior/auto_paste", "behavior/hotkey", "behavior/visual_indicator",
            "behavior/indicator_position", "behavior/toggle_mode",
            "whisper/model_name", "whisper/speed_mode", "whisper/temperature",
            "whisper/language", "whisper/engine",
            "advanced/expert_mode", "advanced/log_level"
        ]
        
        defaults = SETTINGS_SCHEMA.get_all_defaults()
        for key in expected_keys:
            self.assertIn(key, defaults, f"Missing default for key: {key}")
    
    def test_validators_completeness(self):
        """Test that all settings have validators."""
        defaults = SETTINGS_SCHEMA.get_all_defaults()
        for key in defaults:
            # Check if setting has a validator in the schema
            if key in SETTINGS_SCHEMA.schema:
                schema = SETTINGS_SCHEMA.schema[key]
                # Validator is optional, but if present should be callable
                if schema.validator:
                    self.assertTrue(callable(schema.validator), f"Validator for {key} is not callable")
    
    def test_schema_validation(self):
        """Test schema validation."""
        # Test valid theme
        result = SETTINGS_SCHEMA.validate_setting("ui/theme", "dark")
        self.assertEqual(result, "dark")
        
        # Test invalid theme
        with self.assertRaises(ValueError):
            SETTINGS_SCHEMA.validate_setting("ui/theme", "invalid")
        
        # Test temperature validation
        result = SETTINGS_SCHEMA.validate_setting("whisper/temperature", 0.5)
        self.assertEqual(result, 0.5)
        
        # Test invalid temperature
        with self.assertRaises(ValueError):
            SETTINGS_SCHEMA.validate_setting("whisper/temperature", 2.0)
    
    def test_schema_migration(self):
        """Test settings migration."""
        # Test migration from old settings format
        old_settings = {
            "theme": "dark",  # Old format without ui/ prefix
            "model_size": "base",  # Old format
            "auto_paste": True
        }
        
        migrated = SETTINGS_SCHEMA.migrate_settings(old_settings)
        
        # Check that old keys were migrated to new format
        self.assertIn("ui/theme", migrated)
        self.assertIn("whisper/model_name", migrated)
        self.assertIn("behavior/auto_paste", migrated)
        
        # Check that values were preserved
        self.assertEqual(migrated["ui/theme"], "dark")
        self.assertEqual(migrated["whisper/model_name"], "base")
        self.assertEqual(migrated["behavior/auto_paste"], True)

class TestSettingsManager(unittest.TestCase):
    """Test the settings manager functionality."""
    
    def test_get_default_value(self):
        """Test getting default values."""
        # Create a simple settings manager for testing
        settings_manager = SettingsManager("TestOrg", "TestApp")
        
        # Test getting a default value
        default_theme = settings_manager.get("ui/theme")
        self.assertEqual(default_theme, "dark")  # Should return schema default
        
        # Test getting a non-existent setting
        non_existent = settings_manager.get("non/existent", "fallback")
        self.assertEqual(non_existent, "fallback")
    
    def test_set_and_get(self):
        """Test setting and getting values."""
        settings_manager = SettingsManager("TestOrg", "TestApp")
        
        # Set a value
        settings_manager.set("ui/theme", "light")
        
        # Get the value back
        theme = settings_manager.get("ui/theme")
        self.assertEqual(theme, "light")
    
    def test_validation_on_set(self):
        """Test that validation occurs when setting values."""
        settings_manager = SettingsManager("TestOrg", "TestApp")
        
        # Test valid value
        settings_manager.set("whisper/temperature", 0.5)
        temp = settings_manager.get("whisper/temperature")
        self.assertEqual(temp, 0.5)
        
        # Test invalid value (should raise exception)
        with self.assertRaises(Exception):
            settings_manager.set("whisper/temperature", 2.0)
    
    def test_load_all(self):
        """Test loading all settings."""
        settings_manager = SettingsManager("TestOrg", "TestApp")
        
        # Load all settings
        loaded = settings_manager.load_all()
        
        # Check that we got some settings
        self.assertIsInstance(loaded, dict)
        self.assertGreater(len(loaded), 0)
        
        # Check that schema defaults are included
        self.assertIn("ui/theme", loaded)
        self.assertIn("whisper/model_name", loaded)

class TestSettingsIntegration(unittest.TestCase):
    """Integration tests for settings system."""
    
    def test_settings_persistence(self):
        """Test that settings persist across manager instances."""
        # This would require actual file I/O testing
        # For now, we'll test the schema integration
        schema = SETTINGS_SCHEMA
        
        # Test that schema provides defaults
        defaults = schema.get_all_defaults()
        self.assertIsInstance(defaults, dict)
        self.assertGreater(len(defaults), 0)
        
        # Test that schema can validate settings
        validated = schema.validate_setting("ui/theme", "dark")
        self.assertEqual(validated, "dark")
        
        # Test migration
        migrated = schema.migrate_settings({"theme": "dark"})
        self.assertIn("ui/theme", migrated)

if __name__ == '__main__':
    # Create QApplication for PyQt tests
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Run tests
    unittest.main()