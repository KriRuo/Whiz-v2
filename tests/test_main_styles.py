#!/usr/bin/env python3
"""
Unit tests for the MainStyles component.
Tests style methods, CSS generation, and component-specific styling.
"""

import unittest
import tempfile
import os
from unittest.mock import Mock, patch

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.styles.main_styles import MainStyles


class TestMainStyles(unittest.TestCase):
    """Test cases for MainStyles component"""
    
    def test_get_main_stylesheet(self):
        """Test that main stylesheet returns valid CSS"""
        stylesheet = MainStyles.get_main_stylesheet()
        
        # Should return a string
        self.assertIsInstance(stylesheet, str)
        
        # Should not be empty
        self.assertGreater(len(stylesheet), 0)
        
        # Should contain key CSS elements
        self.assertIn('QMainWindow', stylesheet)
        self.assertIn('background:', stylesheet)
        self.assertIn('QPushButton', stylesheet)
    
    def test_get_status_label_style(self):
        """Test status label style method"""
        style = MainStyles.get_status_label_style()
        
        # Should return a string
        self.assertIsInstance(style, str)
        
        # Should contain label styling
        self.assertIn('QLabel', style)
        self.assertIn('color:', style)
        self.assertIn('font-weight:', style)
    
    def test_get_start_button_style(self):
        """Test start button style method"""
        style = MainStyles.get_start_button_style()
        
        # Should return a string
        self.assertIsInstance(style, str)
        
        # Should contain button styling
        self.assertIn('QPushButton', style)
        self.assertIn('background-color:', style)
        self.assertIn('border:', style)
    
    def test_get_stop_button_style(self):
        """Test stop button style method"""
        style = MainStyles.get_stop_button_style()
        
        # Should return a string
        self.assertIsInstance(style, str)
        
        # Should contain button styling
        self.assertIn('QPushButton', style)
        self.assertIn('background-color:', style)
        self.assertIn('border:', style)
    
    def test_get_hotkey_instruction_style(self):
        """Test hotkey instruction style method"""
        style = MainStyles.get_hotkey_instruction_style()
        
        # Should return a string
        self.assertIsInstance(style, str)
        
        # Should contain label styling
        self.assertIn('QLabel', style)
        self.assertIn('color:', style)
    
    def test_get_header_line_style(self):
        """Test header line style method"""
        style = MainStyles.get_header_line_style()
        
        # Should return a string
        self.assertIsInstance(style, str)
        
        # Should contain frame styling
        self.assertIn('QFrame', style)
        self.assertIn('color:', style)
    
    def test_get_tips_title_style(self):
        """Test tips title style method"""
        style = MainStyles.get_tips_title_style()
        
        # Should return a string
        self.assertIsInstance(style, str)
        
        # Should contain label styling
        self.assertIn('QLabel', style)
        self.assertIn('color:', style)
        self.assertIn('font-weight:', style)
    
    def test_get_tips_content_style(self):
        """Test tips content style method"""
        style = MainStyles.get_tips_content_style()
        
        # Should return a string
        self.assertIsInstance(style, str)
        
        # Should contain label styling
        self.assertIn('QLabel', style)
        self.assertIn('color:', style)
    
    def test_get_transcript_scroll_area_style(self):
        """Test transcript scroll area style method"""
        style = MainStyles.get_transcript_scroll_area_style()
        
        # Should return a string
        self.assertIsInstance(style, str)
        
        # Should contain scroll area styling
        self.assertIn('QScrollArea', style)
        self.assertIn('background-color:', style)
        self.assertIn('border:', style)
    
    def test_get_empty_transcript_style(self):
        """Test empty transcript style method"""
        style = MainStyles.get_empty_transcript_style()
        
        # Should return a string
        self.assertIsInstance(style, str)
        
        # Should contain label styling
        self.assertIn('QLabel', style)
        self.assertIn('color:', style)
    
    def test_get_transcript_item_style(self):
        """Test transcript item style method"""
        style = MainStyles.get_transcript_item_style()
        
        # Should return a string
        self.assertIsInstance(style, str)
        
        # Should contain frame styling
        self.assertIn('QFrame', style)
        self.assertIn('background-color:', style)
        self.assertIn('border:', style)
    
    def test_get_timestamp_style(self):
        """Test timestamp style method"""
        style = MainStyles.get_timestamp_style()
        
        # Should return a string
        self.assertIsInstance(style, str)
        
        # Should contain styling properties (no widget selector in this style)
        self.assertIn('color:', style)
        self.assertIn('font-size:', style)
    
    def test_get_transcript_text_style(self):
        """Test transcript text style method"""
        style = MainStyles.get_transcript_text_style()
        
        # Should return a string
        self.assertIsInstance(style, str)
        
        # Should contain styling properties (no widget selector in this style)
        self.assertIn('color:', style)
        self.assertIn('font-size:', style)
    
    def test_get_dark_theme_addition(self):
        """Test dark theme addition method"""
        style = MainStyles.get_dark_theme_addition()
        
        # Should return a string
        self.assertIsInstance(style, str)
        
        # Should contain dark theme styling
        self.assertIn('QMainWindow', style)
        self.assertIn('background:', style)
    
    def test_all_style_methods_exist(self):
        """Test that all expected style methods exist"""
        expected_methods = [
            'get_main_stylesheet',
            'get_status_label_style',
            'get_start_button_style',
            'get_stop_button_style',
            'get_hotkey_instruction_style',
            'get_header_line_style',
            'get_tips_title_style',
            'get_tips_content_style',
            'get_transcript_scroll_area_style',
            'get_empty_transcript_style',
            'get_transcript_item_style',
            'get_timestamp_style',
            'get_transcript_text_style',
            'get_dark_theme_addition'
        ]
        
        for method_name in expected_methods:
            self.assertTrue(hasattr(MainStyles, method_name))
            method = getattr(MainStyles, method_name)
            self.assertTrue(callable(method))
    
    def test_style_methods_return_strings(self):
        """Test that all style methods return strings"""
        style_methods = [
            'get_main_stylesheet',
            'get_status_label_style',
            'get_start_button_style',
            'get_stop_button_style',
            'get_hotkey_instruction_style',
            'get_header_line_style',
            'get_tips_title_style',
            'get_tips_content_style',
            'get_transcript_scroll_area_style',
            'get_empty_transcript_style',
            'get_transcript_item_style',
            'get_timestamp_style',
            'get_transcript_text_style',
            'get_dark_theme_addition'
        ]
        
        for method_name in style_methods:
            method = getattr(MainStyles, method_name)
            result = method()
            self.assertIsInstance(result, str, f"{method_name} should return a string")
            self.assertGreater(len(result), 0, f"{method_name} should return non-empty string")


class TestMainStylesIntegration(unittest.TestCase):
    """Integration tests for MainStyles with PyQt5 widgets"""
    
    def setUp(self):
        """Set up test fixtures"""
        from PyQt5.QtWidgets import QApplication
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])
    
    def test_styles_can_be_applied_to_widgets(self):
        """Test that styles can be applied to actual PyQt5 widgets"""
        from PyQt5.QtWidgets import QLabel, QPushButton, QFrame
        
        # Test label styling
        label = QLabel("Test")
        label.setStyleSheet(MainStyles.get_status_label_style())
        self.assertIsNotNone(label.styleSheet())
        
        # Test button styling
        button = QPushButton("Test")
        button.setStyleSheet(MainStyles.get_start_button_style())
        self.assertIsNotNone(button.styleSheet())
        
        # Test frame styling
        frame = QFrame()
        frame.setStyleSheet(MainStyles.get_transcript_item_style())
        self.assertIsNotNone(frame.styleSheet())
    
    def test_main_stylesheet_can_be_applied(self):
        """Test that main stylesheet can be applied to main window"""
        from PyQt5.QtWidgets import QMainWindow
        
        window = QMainWindow()
        window.setStyleSheet(MainStyles.get_main_stylesheet())
        
        # Should have stylesheet applied
        self.assertIsNotNone(window.styleSheet())
        self.assertGreater(len(window.styleSheet()), 0)


if __name__ == '__main__':
    unittest.main()
