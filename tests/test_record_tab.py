#!/usr/bin/env python3
"""
Unit tests for the RecordTab component.
Tests tab creation, button functionality, and integration with parent app.
"""

import unittest
import tempfile
import os
from unittest.mock import Mock, patch
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.record_tab import RecordTab


class TestRecordTab(unittest.TestCase):
    """Test cases for RecordTab component"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])
        
        # Create a mock parent app with real QWidget for waveform
        from PyQt5.QtWidgets import QWidget
        self.parent_app = Mock()
        self.parent_app.waveform_widget = QWidget()  # Real QWidget instead of Mock
        self.parent_app.start_recording = Mock()
        self.parent_app.stop_recording = Mock()
        self.parent_app.update_hotkey_instruction = Mock()
        self.parent_app.adjustSize = Mock()
        
        # Mock controller with feature status
        self.parent_app.controller = Mock()
        self.parent_app.controller.get_feature_status.return_value = {
            "audio_recording": True,
            "hotkeys": True,
            "recommendations": {
                "install_packages": [],
                "enable_permissions": []
            }
        }
        
        # Create RecordTab instance
        self.record_tab = RecordTab(self.parent_app)
    
    def tearDown(self):
        """Clean up after tests"""
        if hasattr(self, 'record_tab'):
            self.record_tab.close()
    
    def test_record_tab_creation(self):
        """Test that RecordTab creates successfully"""
        self.assertIsNotNone(self.record_tab)
        self.assertEqual(self.record_tab.parent_app, self.parent_app)
    
    def test_record_tab_has_required_widgets(self):
        """Test that RecordTab has all required UI widgets"""
        # Check that key widgets exist
        self.assertTrue(hasattr(self.record_tab, 'status_label'))
        self.assertTrue(hasattr(self.record_tab, 'start_button'))
        self.assertTrue(hasattr(self.record_tab, 'stop_button'))
        self.assertTrue(hasattr(self.record_tab, 'hotkey_instruction_label'))
    
    def test_start_button_functionality(self):
        """Test that start button calls parent's start_recording method"""
        self.record_tab.start_button.clicked.emit()
        self.parent_app.start_recording.assert_called_once()
    
    def test_stop_button_functionality(self):
        """Test that stop button calls parent's stop_recording method"""
        self.record_tab.stop_button.clicked.emit()
        self.parent_app.stop_recording.assert_called_once()
    
    def test_hotkey_instruction_update(self):
        """Test that hotkey instruction label exists and can be updated"""
        # The hotkey instruction label should exist
        self.assertTrue(hasattr(self.record_tab, 'hotkey_instruction_label'))
        
        # Should have initial text
        self.assertIsNotNone(self.record_tab.hotkey_instruction_label.text())
        
        # Should be able to update the text
        self.record_tab.hotkey_instruction_label.setText("Test instruction")
        self.assertEqual(self.record_tab.hotkey_instruction_label.text(), "Test instruction")
    
    def test_waveform_widget_integration(self):
        """Test that waveform widget is properly integrated"""
        # The waveform widget should be added to the layout
        self.assertIsNotNone(self.record_tab.parent_app.waveform_widget)
    
    def test_button_states(self):
        """Test initial button states"""
        # Start button should be enabled initially
        self.assertTrue(self.record_tab.start_button.isEnabled())
        # Stop button should be disabled initially
        self.assertFalse(self.record_tab.stop_button.isEnabled())
    
    def test_status_label_content(self):
        """Test that status label shows correct initial content"""
        self.assertEqual(self.record_tab.status_label.text(), "Idle")
    
    def test_tips_accordion_functionality(self):
        """Test that tips accordion can be toggled"""
        # Find the tips content widget
        tips_content = None
        for child in self.record_tab.findChildren(type(self.record_tab)):
            if hasattr(child, 'text') and 'Speak clearly' in str(child.text()):
                tips_content = child
                break
        
        if tips_content:
            # Initially should be hidden
            self.assertFalse(tips_content.isVisible())
            
            # Find the title label and simulate click
            title_label = None
            for child in self.record_tab.findChildren(type(self.record_tab)):
                if hasattr(child, 'text') and 'Tips for better accuracy' in str(child.text()):
                    title_label = child
                    break
            
            if title_label:
                # Simulate mouse press to toggle
                from PyQt5.QtGui import QMouseEvent
                from PyQt5.QtCore import QPoint
                event = QMouseEvent(QMouseEvent.MouseButtonPress, QPoint(0, 0), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
                title_label.mousePressEvent(event)
                
                # Should now be visible
                self.assertTrue(tips_content.isVisible())


class TestRecordTabIntegration(unittest.TestCase):
    """Integration tests for RecordTab with real parent app"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])
    
    def test_record_tab_with_real_parent_app(self):
        """Test RecordTab with a more realistic parent app"""
        # Create a mock parent app with more realistic structure
        from PyQt5.QtWidgets import QWidget
        parent_app = Mock()
        parent_app.waveform_widget = QWidget()  # Real QWidget instead of Mock
        parent_app.start_recording = Mock()
        parent_app.stop_recording = Mock()
        parent_app.update_hotkey_instruction = Mock()
        parent_app.adjustSize = Mock()
        
        # Mock controller with feature status
        parent_app.controller = Mock()
        parent_app.controller.get_feature_status.return_value = {
            "audio_recording": True,
            "hotkeys": True,
            "recommendations": {
                "install_packages": [],
                "enable_permissions": []
            }
        }
        
        # Create RecordTab
        record_tab = RecordTab(parent_app)
        
        # Verify it was created successfully
        self.assertIsNotNone(record_tab)
        self.assertEqual(record_tab.parent_app, parent_app)
        
        # Clean up
        record_tab.close()


if __name__ == '__main__':
    unittest.main()
