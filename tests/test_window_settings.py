#!/usr/bin/env python3
"""
Individual tests for window settings.
Tests window geometry and state persistence controls.
"""

import unittest
import tempfile
import os
from PyQt5.QtCore import QSettings, QByteArray
from PyQt5.QtWidgets import QApplication, QMainWindow

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.settings_manager import SettingsManager

class TestWindowSettings(unittest.TestCase):
    """Test window-specific settings."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.settings_file = os.path.join(self.temp_dir, "window_test_settings.ini")
        self.settings_manager = SettingsManager("WindowTest", "TestApp")
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
    
    def test_window_geometry_automatic(self):
        """Test that window geometry is automatically saved."""
        # Window geometry should always be saved automatically
        # This test verifies the basic functionality still works
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        main_window = QMainWindow()
        main_window.setGeometry(100, 100, 400, 300)
        
        # Save window - should always work
        self.settings_manager.save_window(main_window)
        
        # Check that geometry was saved
        geometry = self.settings_manager.settings.value("window/geometry")
        self.assertIsNotNone(geometry)
    
    def test_window_state_automatic(self):
        """Test that window state is automatically saved."""
        # Window state should always be saved automatically
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        main_window = QMainWindow()
        main_window.setGeometry(100, 100, 400, 300)
        
        # Save window - should always work
        self.settings_manager.save_window(main_window)
        
        # Check that state was saved
        state = self.settings_manager.settings.value("window/state")
        self.assertIsNotNone(state)
    
    def test_window_restore_behavior(self):
        """Test window restore behavior - always automatic."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        main_window = QMainWindow()
        main_window.setGeometry(0, 0, 200, 200)  # Different initial geometry
        
        # Save some geometry
        main_window.setGeometry(100, 100, 400, 300)
        self.settings_manager.save_window(main_window)
        
        # Test restore - should always work
        new_window = QMainWindow()
        new_window.setGeometry(0, 0, 200, 200)
        self.settings_manager.restore_window(new_window)
        
        # Check that geometry was restored (approximately)
        geometry = new_window.geometry()
        self.assertGreater(geometry.width(), 300)  # Should be restored to ~400
        self.assertGreater(geometry.height(), 200)  # Should be restored to ~300
    
    def test_window_settings_persistence(self):
        """Test that window settings persist across sessions."""
        # Window settings are now automatic, so we test the basic functionality
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        main_window = QMainWindow()
        main_window.setGeometry(100, 100, 400, 300)
        
        # Save window
        self.settings_manager.save_window(main_window)
        
        # Verify that window data was saved in the original settings
        geometry = self.settings_manager.settings.value("window/geometry")
        state = self.settings_manager.settings.value("window/state")
        self.assertIsNotNone(geometry)
        self.assertIsNotNone(state)
        
        # Test that we can restore the window
        new_window = QMainWindow()
        new_window.setGeometry(0, 0, 200, 200)
        self.settings_manager.restore_window(new_window)
        
        # Check that geometry was restored
        restored_geometry = new_window.geometry()
        self.assertGreater(restored_geometry.width(), 300)  # Should be restored to ~400
        self.assertGreater(restored_geometry.height(), 200)  # Should be restored to ~300

if __name__ == '__main__':
    # Set up QApplication for tests
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    unittest.main()
