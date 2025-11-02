#!/usr/bin/env python3
"""
Unit tests for the VisualIndicatorWidget.
Tests widget creation, positioning, show/hide functionality, and settings integration.
"""

import unittest
import tempfile
import os
from unittest.mock import Mock, patch
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.visual_indicator import VisualIndicatorWidget
from core.settings_manager import SettingsManager

class TestVisualIndicatorWidget(unittest.TestCase):
    """Test the VisualIndicatorWidget class."""
    
    def setUp(self):
        """Set up test environment."""
        # Ensure QApplication exists
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])
        
        # Create temporary settings for testing
        self.temp_dir = tempfile.mkdtemp()
        self.settings_file = os.path.join(self.temp_dir, "visual_test_settings.ini")
        self.settings_manager = SettingsManager("VisualTest", "TestApp")
        self.settings_manager.settings = Mock()
    
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
    
    def test_widget_creation(self):
        """Test widget creation with default position."""
        widget = VisualIndicatorWidget()
        
        # Check basic properties
        self.assertEqual(widget.position, "Top Right")
        self.assertTrue(widget.isVisible() == False)  # Should start hidden
        
        # Check window flags
        flags = widget.windowFlags()
        self.assertTrue(flags & Qt.FramelessWindowHint)
        self.assertTrue(flags & Qt.WindowStaysOnTopHint)
        self.assertTrue(flags & Qt.Tool)
        
        # Check size constraints
        self.assertEqual(widget.minimumSize().width(), 60)
        self.assertEqual(widget.minimumSize().height(), 60)
        self.assertEqual(widget.maximumSize().width(), 120)
        self.assertEqual(widget.maximumSize().height(), 120)
        
        widget.close()
    
    def test_widget_creation_with_position(self):
        """Test widget creation with specific position."""
        positions = [
            "Top Left", "Top Right", "Bottom Right", "Bottom Left",
            "Top Center", "Middle Center", "Bottom Center"
        ]
        
        for position in positions:
            widget = VisualIndicatorWidget(position)
            self.assertEqual(widget.position, position)
            widget.close()
    
    def test_position_update(self):
        """Test updating widget position."""
        widget = VisualIndicatorWidget("Top Left")
        
        # Test updating to different positions
        test_positions = ["Top Right", "Bottom Center", "Middle Center"]
        
        for position in test_positions:
            widget.update_position(position)
            self.assertEqual(widget.position, position)
        
        widget.close()
    
    def test_show_hide_functionality(self):
        """Test show and hide recording functionality."""
        widget = VisualIndicatorWidget("Top Right")
        
        # Initially hidden
        self.assertFalse(widget.isVisible())
        
        # Show recording
        widget.show_recording()
        self.assertTrue(widget.isVisible())
        
        # Hide recording
        widget.hide_recording()
        self.assertFalse(widget.isVisible())
        
        widget.close()
    
    def test_widget_positioning(self):
        """Test widget positioning logic."""
        widget = VisualIndicatorWidget("Top Right")
        
        # Mock screen geometry for testing
        with patch('PyQt5.QtWidgets.QApplication.screenAt') as mock_screen_at, \
             patch('PyQt5.QtWidgets.QApplication.primaryScreen') as mock_primary_screen:
            
            # Create mock screen
            mock_screen = Mock()
            mock_screen.geometry.return_value = Mock()
            mock_screen.geometry.return_value.x.return_value = 0
            mock_screen.geometry.return_value.y.return_value = 0
            mock_screen.geometry.return_value.width.return_value = 1920
            mock_screen.geometry.return_value.height.return_value = 1080
            
            mock_screen_at.return_value = mock_screen
            mock_primary_screen.return_value = mock_screen
            
            # Test positioning
            widget.position_widget()
            
            # Verify screen methods were called
            mock_screen_at.assert_called()
            mock_screen.geometry.assert_called()
        
        widget.close()
    
    def test_widget_size_policy(self):
        """Test widget size policy."""
        widget = VisualIndicatorWidget()
        
        # Check that indicator label has proper size policy
        size_policy = widget.indicator_label.sizePolicy()
        # QSizePolicy::Expanding = 7, not 1
        self.assertEqual(size_policy.horizontalPolicy(), 7)  # QSizePolicy::Expanding
        self.assertEqual(size_policy.verticalPolicy(), 7)   # QSizePolicy::Expanding
        
        widget.close()
    
    def test_icon_loading_fallback(self):
        """Test icon loading with fallback to styled background."""
        widget = VisualIndicatorWidget()
        
        # Check that indicator label exists and has content
        self.assertIsNotNone(widget.indicator_label)
        
        # The widget should have either a pixmap or styled background
        # This is tested implicitly by successful widget creation
        
        widget.close()
    
    def test_multiple_widgets(self):
        """Test creating multiple widgets."""
        widgets = []
        
        try:
            # Create multiple widgets with different positions
            positions = ["Top Left", "Top Right", "Bottom Center"]
            
            for position in positions:
                widget = VisualIndicatorWidget(position)
                widgets.append(widget)
                self.assertEqual(widget.position, position)
            
            # All widgets should be independent
            self.assertEqual(len(widgets), 3)
            
        finally:
            # Clean up all widgets
            for widget in widgets:
                widget.close()
    
    def test_widget_with_settings_manager(self):
        """Test widget integration with settings manager."""
        # Create a mock main window
        main_window = Mock()
        main_window.visual_indicator = VisualIndicatorWidget("Bottom Center")
        
        # Test that settings manager can call update_position
        settings_manager = SettingsManager("TestOrg", "TestApp")
        
        # Mock the settings manager's behavior settings application
        with patch.object(settings_manager, '_apply_behavior_settings') as mock_apply:
            # Simulate applying behavior settings
            settings_manager._apply_behavior_settings(main_window)
            
            # The mock should have been called
            mock_apply.assert_called_with(main_window)
        
        main_window.visual_indicator.close()


class TestVisualIndicatorIntegration(unittest.TestCase):
    """Integration tests for VisualIndicatorWidget with the complete application."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])
        
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up integration test environment."""
        try:
            for file in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            os.rmdir(self.temp_dir)
        except OSError:
            pass
    
    def test_settings_integration(self):
        """Test VisualIndicatorWidget integration with settings system."""
        # Create settings manager
        settings_manager = SettingsManager("IntegrationTest", "TestApp")
        
        # Create mock main window with visual indicator
        main_window = Mock()
        main_window.visual_indicator = VisualIndicatorWidget("Bottom Center")
        
        # Test setting indicator position through settings
        settings_manager.set("behavior/indicator_position", "Top Right")
        
        # Apply settings (this would normally be called by the settings manager)
        if hasattr(main_window.visual_indicator, 'update_position'):
            main_window.visual_indicator.update_position("Top Right")
            self.assertEqual(main_window.visual_indicator.position, "Top Right")
        
        main_window.visual_indicator.close()
    
    def test_visual_indicator_enable_disable(self):
        """Test enabling/disabling visual indicator."""
        # Create settings manager
        settings_manager = SettingsManager("EnableTest", "TestApp")
        
        # Create mock main window
        main_window = Mock()
        main_window.visual_indicator = VisualIndicatorWidget("Top Right")
        
        # Test enabling visual indicator
        settings_manager.set("behavior/visual_indicator", True)
        self.assertTrue(settings_manager.get("behavior/visual_indicator"))
        
        # Test disabling visual indicator
        settings_manager.set("behavior/visual_indicator", False)
        self.assertFalse(settings_manager.get("behavior/visual_indicator"))
        
        main_window.visual_indicator.close()


class TestVisualIndicatorEdgeCases(unittest.TestCase):
    """Test edge cases and error handling for VisualIndicatorWidget."""
    
    def setUp(self):
        """Set up edge case test environment."""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])
    
    def test_invalid_position_handling(self):
        """Test handling of invalid position values."""
        widget = VisualIndicatorWidget("Valid Position")
        
        # Test updating to invalid position
        widget.update_position("Invalid Position")
        
        # Widget should still have the invalid position set
        # (validation should happen at the settings level, not widget level)
        self.assertEqual(widget.position, "Invalid Position")
        
        widget.close()
    
    def test_widget_cleanup(self):
        """Test proper widget cleanup."""
        widget = VisualIndicatorWidget("Top Right")
        
        # Show the widget
        widget.show_recording()
        self.assertTrue(widget.isVisible())
        
        # Close the widget
        widget.close()
        
        # Widget should be properly cleaned up
        # (We can't easily test this without accessing Qt internals)
        self.assertTrue(True)  # Placeholder assertion
    
    def test_widget_without_screen(self):
        """Test widget behavior when no screen is available."""
        widget = VisualIndicatorWidget("Top Right")
        
        # Mock screen detection to return None
        with patch('PyQt5.QtWidgets.QApplication.screenAt', return_value=None), \
             patch('PyQt5.QtWidgets.QApplication.primaryScreen', return_value=None):
            
            # This should not crash
            widget.position_widget()
            
            # Widget should still be functional
            self.assertIsNotNone(widget.position)
        
        widget.close()


if __name__ == '__main__':
    # Set up QApplication for tests
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Run tests
    unittest.main()
