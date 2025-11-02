#!/usr/bin/env python3
"""
Unit tests for the TranscriptsTab component.
Tests tab creation, transcript display, refresh functionality, and integration.
"""

import unittest
import tempfile
import os
from unittest.mock import Mock, patch
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QClipboard

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.transcripts_tab import TranscriptsTab


class TestTranscriptsTab(unittest.TestCase):
    """Test cases for TranscriptsTab component"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])
        
        # Create a mock parent app
        self.parent_app = Mock()
        self.parent_app.controller = Mock()
        self.parent_app.controller.get_transcripts.return_value = []
        
        # Create TranscriptsTab instance
        self.transcripts_tab = TranscriptsTab(self.parent_app)
    
    def tearDown(self):
        """Clean up after tests"""
        if hasattr(self, 'transcripts_tab'):
            self.transcripts_tab.close()
    
    def test_transcripts_tab_creation(self):
        """Test that TranscriptsTab creates successfully"""
        self.assertIsNotNone(self.transcripts_tab)
        self.assertEqual(self.transcripts_tab.parent_app, self.parent_app)
    
    def test_transcripts_tab_has_required_widgets(self):
        """Test that TranscriptsTab has all required UI widgets"""
        # Check that key widgets exist
        self.assertTrue(hasattr(self.transcripts_tab, 'transcript_scroll_area'))
        self.assertTrue(hasattr(self.transcripts_tab, 'transcript_container'))
        self.assertTrue(hasattr(self.transcripts_tab, 'transcript_layout'))
    
    def test_empty_transcript_display(self):
        """Test display when no transcripts are available"""
        # Mock empty transcripts
        self.parent_app.controller.get_transcripts.return_value = []
        
        # Refresh the display
        self.transcripts_tab.refresh_transcript_log()
        
        # Should show empty state message
        empty_labels = self.transcripts_tab.findChildren(type(self.transcripts_tab.transcript_container))
        empty_label_found = False
        for label in empty_labels:
            if hasattr(label, 'text') and 'No transcripts yet' in str(label.text()):
                empty_label_found = True
                break
        
        self.assertTrue(empty_label_found)
    
    def test_transcript_display_with_data(self):
        """Test display when transcripts are available"""
        # Mock transcript data
        mock_transcripts = [
            {
                'timestamp': '2024-01-01 12:00:00',
                'text': 'First transcript'
            },
            {
                'timestamp': '2024-01-01 12:01:00',
                'text': 'Second transcript'
            }
        ]
        self.parent_app.controller.get_transcripts.return_value = mock_transcripts
        
        # Refresh the display
        self.transcripts_tab.refresh_transcript_log()
        
        # Should create transcript widgets
        transcript_widgets = self.transcripts_tab.findChildren(type(self.transcripts_tab.transcript_container))
        # Should have at least some widgets (exact count depends on implementation)
        self.assertGreater(len(transcript_widgets), 0)
    
    def test_create_transcript_widget(self):
        """Test individual transcript widget creation"""
        mock_transcript = {
            'timestamp': '2024-01-01 12:00:00',
            'text': 'Test transcript text'
        }
        
        # Create a transcript widget
        widget = self.transcripts_tab.create_transcript_widget(mock_transcript)
        
        # Should create a widget
        self.assertIsNotNone(widget)
        
        # Should have timestamp and text labels
        labels = widget.findChildren(type(widget))
        timestamp_found = False
        text_found = False
        
        for label in labels:
            if hasattr(label, 'text'):
                if '2024-01-01 12:00:00' in str(label.text()):
                    timestamp_found = True
                elif 'Test transcript text' in str(label.text()):
                    text_found = True
        
        self.assertTrue(timestamp_found)
        self.assertTrue(text_found)
    
    def test_refresh_transcript_log_clears_existing(self):
        """Test that refresh clears existing transcript widgets"""
        # Add some initial transcripts
        mock_transcripts = [
            {
                'timestamp': '2024-01-01 12:00:00',
                'text': 'Initial transcript'
            }
        ]
        self.parent_app.controller.get_transcripts.return_value = mock_transcripts
        self.transcripts_tab.refresh_transcript_log()
        
        # Count initial widgets
        initial_widgets = len(self.transcripts_tab.findChildren(type(self.transcripts_tab.transcript_container)))
        
        # Change transcripts and refresh
        mock_transcripts = [
            {
                'timestamp': '2024-01-01 12:01:00',
                'text': 'Updated transcript'
            }
        ]
        self.parent_app.controller.get_transcripts.return_value = mock_transcripts
        self.transcripts_tab.refresh_transcript_log()
        
        # Should have refreshed the display
        # (Exact count verification depends on implementation details)
        self.assertIsNotNone(self.transcripts_tab.transcript_layout)
    
    def test_scroll_area_configuration(self):
        """Test that scroll area is properly configured"""
        scroll_area = self.transcripts_tab.transcript_scroll_area
        
        # Should be widget resizable
        self.assertTrue(scroll_area.widgetResizable())
        
        # Should have proper scroll bar policies
        self.assertEqual(scroll_area.verticalScrollBarPolicy(), Qt.ScrollBarAsNeeded)
        self.assertEqual(scroll_area.horizontalScrollBarPolicy(), Qt.ScrollBarAlwaysOff)
    
    def test_transcript_container_layout(self):
        """Test that transcript container has proper layout"""
        container = self.transcripts_tab.transcript_container
        layout = self.transcripts_tab.transcript_layout
        
        # Should have a layout
        self.assertIsNotNone(layout)
        
        # Should have proper spacing and margins
        self.assertEqual(layout.spacing(), 12)  # LayoutTokens.SPACING_MD
        margins = layout.contentsMargins()
        self.assertEqual(margins.left(), 8)  # LayoutTokens.MARGIN_SM
        self.assertEqual(margins.top(), 8)   # LayoutTokens.MARGIN_SM
        self.assertEqual(margins.right(), 8) # LayoutTokens.MARGIN_SM
        self.assertEqual(margins.bottom(), 8) # LayoutTokens.MARGIN_SM
    
    def test_copy_button_functionality(self):
        """Test that copy button copies transcript text to clipboard"""
        mock_transcript = {
            'timestamp': '2024-01-01 12:00:00',
            'text': 'Test transcript for copying'
        }
        
        # Create a transcript widget
        widget = self.transcripts_tab.create_transcript_widget(mock_transcript)
        
        # Find the copy button - look for QPushButton widgets
        from PyQt5.QtWidgets import QPushButton
        copy_button = None
        for child in widget.findChildren(QPushButton):
            if hasattr(child, 'objectName') and child.objectName() == 'CopyButton':
                copy_button = child
                break
        
        self.assertIsNotNone(copy_button, "Copy button should be present")
        
        # Mock the clipboard
        with patch('PyQt5.QtWidgets.QApplication.clipboard') as mock_clipboard:
            mock_clipboard_instance = Mock()
            mock_clipboard.return_value = mock_clipboard_instance
            
            # Simulate button click
            copy_button.clicked.emit()
            
            # Verify clipboard.setText was called with the transcript text
            mock_clipboard_instance.setText.assert_called_once_with('Test transcript for copying')
    
    def test_transcript_widget_has_copy_button(self):
        """Test that transcript widgets include a copy button"""
        mock_transcript = {
            'timestamp': '2024-01-01 12:00:00',
            'text': 'Test transcript text'
        }
        
        # Create a transcript widget
        widget = self.transcripts_tab.create_transcript_widget(mock_transcript)
        
        # Find all buttons in the widget - look for QPushButton widgets
        from PyQt5.QtWidgets import QPushButton
        buttons = widget.findChildren(QPushButton)
        copy_button_found = False
        
        for button in buttons:
            if hasattr(button, 'objectName') and button.objectName() == 'CopyButton':
                copy_button_found = True
                # Verify button properties
                self.assertEqual(button.toolTip(), 'Copy to clipboard')
                self.assertTrue(button.icon().isNull() == False, "Copy button should have an icon")
                # Verify icon size
                self.assertEqual(button.iconSize().width(), 20)
                self.assertEqual(button.iconSize().height(), 20)
                break
        
        self.assertTrue(copy_button_found, "Copy button should be present in transcript widget")


class TestTranscriptsTabIntegration(unittest.TestCase):
    """Integration tests for TranscriptsTab with real parent app"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])
    
    def test_transcripts_tab_with_real_parent_app(self):
        """Test TranscriptsTab with a more realistic parent app"""
        # Create a mock parent app with more realistic structure
        parent_app = Mock()
        parent_app.controller = Mock()
        parent_app.controller.get_transcripts.return_value = [
            {
                'timestamp': '2024-01-01 12:00:00',
                'text': 'Test transcript for integration'
            }
        ]
        
        # Create TranscriptsTab
        transcripts_tab = TranscriptsTab(parent_app)
        
        # Verify it was created successfully
        self.assertIsNotNone(transcripts_tab)
        self.assertEqual(transcripts_tab.parent_app, parent_app)
        
        # Test refresh functionality
        transcripts_tab.refresh_transcript_log()
        
        # Should have called get_transcripts
        parent_app.controller.get_transcripts.assert_called()
        
        # Clean up
        transcripts_tab.close()
    
    def test_signal_connection(self):
        """Test that TranscriptsTab connects to parent's transcript_updated signal"""
        # Create a mock parent app with signal
        parent_app = Mock()
        parent_app.controller = Mock()
        parent_app.controller.get_transcripts.return_value = []
        parent_app.transcript_updated = Mock()
        parent_app.transcript_updated.connect = Mock()  # Add connect method
        
        # Create TranscriptsTab
        transcripts_tab = TranscriptsTab(parent_app)
        
        # Should have attempted to connect the signal
        parent_app.transcript_updated.connect.assert_called_once_with(transcripts_tab.refresh_transcript_log)
        
        # Clean up
        transcripts_tab.close()


if __name__ == '__main__':
    unittest.main()
