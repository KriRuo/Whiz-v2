#!/usr/bin/env python3
"""
tests/test_splash_screen.py
--------------------------
Tests for splash screen functionality.

This module contains comprehensive tests for the splash screen implementation,
including UI creation, background initialization, and error handling.

Test Coverage:
    - Splash screen creation and display
    - Initialization worker thread
    - Progress updates and logging
    - Error handling and recovery
    - Fade-out animation
    - Main window handoff

Author: Whiz Development Team
Last Updated: October 10, 2025
"""

import unittest
import sys
import time
from unittest.mock import Mock, patch, MagicMock
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# Import the modules to test
try:
    from splash_screen import SplashScreen, InitializationWorker
    SPLASH_AVAILABLE = True
except ImportError:
    SPLASH_AVAILABLE = False


@unittest.skipUnless(SPLASH_AVAILABLE, "Splash screen module not available")
class TestSplashScreen(unittest.TestCase):
    """Test cases for SplashScreen class"""
    
    def setUp(self):
        """Set up test environment"""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])
        self.splash = None
    
    def tearDown(self):
        """Clean up test environment"""
        if self.splash:
            self.splash.close()
            self.splash = None
    
    def test_splash_creation(self):
        """Test splash screen can be created"""
        self.splash = SplashScreen(self.app)
        self.assertIsNotNone(self.splash)
        self.assertEqual(self.splash.windowTitle(), "")
        
    def test_splash_ui_elements(self):
        """Test splash screen UI elements are created"""
        self.splash = SplashScreen(self.app)
        
        # Check that key UI elements exist
        self.assertTrue(hasattr(self.splash, 'title_label'))
        self.assertTrue(hasattr(self.splash, 'status_label'))
        self.assertTrue(hasattr(self.splash, 'log_text'))
        
        # Check initial text
        self.assertEqual(self.splash.title_label.text(), "Whiz")
        self.assertEqual(self.splash.status_label.text(), "Preparing something spectacular...")
        
    def test_splash_worker_setup(self):
        """Test initialization worker is set up correctly"""
        self.splash = SplashScreen(self.app)
        
        # Check worker exists
        self.assertTrue(hasattr(self.splash, 'worker'))
        self.assertIsInstance(self.splash.worker, InitializationWorker)
        
    def test_splash_show(self):
        """Test splash screen can be shown"""
        self.splash = SplashScreen(self.app)
        self.splash.show()
    
        # Check window is visible
        self.assertTrue(self.splash.isVisible())
        
    def test_splash_center_window(self):
        """Test splash screen centers correctly"""
        self.splash = SplashScreen(self.app)
        self.splash.show()
        
        # Check window has reasonable position
        self.assertGreater(self.splash.x(), 0)
        self.assertGreater(self.splash.y(), 0)
        
    def test_splash_progress_update(self):
        """Test progress updates work correctly"""
        self.splash = SplashScreen(self.app)
        
        # Simulate progress update
        self.splash.update_progress(50, "Testing progress")
        
        # Check status label updated
        self.assertEqual(self.splash.status_label.text(), "Testing progress")
        
        # Check log text updated
        log_content = self.splash.log_text.toPlainText()
        self.assertIn("Testing progress", log_content)
        self.assertIn("50%", log_content)


@unittest.skipUnless(SPLASH_AVAILABLE, "Splash screen module not available")
class TestInitializationWorker(unittest.TestCase):
    """Test cases for InitializationWorker class"""
    
    def setUp(self):
        """Set up test environment"""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])
        self.worker = None
        
    def tearDown(self):
        """Clean up test environment"""
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
            
    def test_worker_creation(self):
        """Test initialization worker can be created"""
        self.worker = InitializationWorker()
        self.assertIsNotNone(self.worker)
        
    def test_worker_steps(self):
        """Test worker has correct initialization steps"""
        self.worker = InitializationWorker()
        
        # Check steps exist
        self.assertTrue(hasattr(self.worker, 'steps'))
        self.assertIsInstance(self.worker.steps, list)
        self.assertGreater(len(self.worker.steps), 0)
        
        # Check step format
        for step in self.worker.steps:
            self.assertIsInstance(step, tuple)
            self.assertEqual(len(step), 2)
            self.assertIsInstance(step[0], str)  # message
            self.assertIsInstance(step[1], int)  # progress
            
    def test_worker_signals(self):
        """Test worker signals are defined"""
        self.worker = InitializationWorker()
        
        # Check signals exist
        self.assertTrue(hasattr(self.worker, 'progress_updated'))
        self.assertTrue(hasattr(self.worker, 'initialization_complete'))
        self.assertTrue(hasattr(self.worker, 'initialization_failed'))
        
    @patch('splash_screen.SettingsManager')
    @patch('core.platform_features.PlatformFeatures')
    @patch('core.audio_manager.AudioManager')
    @patch('core.hotkey_manager.HotkeyManager')
    @patch('splash_screen.SpeechController')
    def test_worker_initialization_success(self, mock_controller, mock_hotkey, 
                                        mock_audio, mock_features, mock_settings):
        """Test worker initialization succeeds with mocked dependencies"""
        # Set up mocks
        mock_settings.return_value.load_all.return_value = {}
        mock_features.return_value.detect_all_features.return_value = {}
        mock_audio.return_value.is_available.return_value = True
        mock_hotkey.return_value.is_available.return_value = True
        
        self.worker = InitializationWorker()
        
        # Mock signal handlers
        progress_calls = []
        complete_calls = []
        
        def mock_progress(progress, message):
            progress_calls.append((progress, message))
            
        def mock_complete(controller, settings):
            complete_calls.append((controller, settings))
            
        self.worker.progress_updated.connect(mock_progress)
        self.worker.initialization_complete.connect(mock_complete)
        
        # Run worker
        self.worker.run()
        
        # Check progress was reported
        self.assertGreater(len(progress_calls), 0)
        
        # Check completion was signaled
        self.assertEqual(len(complete_calls), 1)
        
    def test_worker_initialization_failure(self):
        """Test worker handles initialization failures"""
        self.worker = InitializationWorker()
        
        # Mock signal handler
        failure_calls = []
        
        def mock_failure(error_msg):
            failure_calls.append(error_msg)
            
        self.worker.initialization_failed.connect(mock_failure)
        
        # Mock a failure by patching SettingsManager to raise exception
        with patch('splash_screen.SettingsManager', side_effect=Exception("Test error")):
            self.worker.run()
            
        # Check failure was signaled
        self.assertEqual(len(failure_calls), 1)
        self.assertIn("Test error", failure_calls[0])


@unittest.skipUnless(SPLASH_AVAILABLE, "Splash screen module not available")
class TestSplashScreenIntegration(unittest.TestCase):
    """Integration tests for splash screen with main application"""
    
    def setUp(self):
        """Set up test environment"""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])
        self.splash = None
        
    def tearDown(self):
        """Clean up test environment"""
        if self.splash:
            self.splash.close()
            self.splash = None
            
    @patch('splash_screen.SpeechApp')
    @patch('splash_screen.SettingsManager')
    @patch('core.platform_features.PlatformFeatures')
    @patch('core.audio_manager.AudioManager')
    @patch('core.hotkey_manager.HotkeyManager')
    @patch('speech_controller.SpeechController')
    def test_splash_to_main_window_handoff(self, mock_controller, mock_hotkey,
                                         mock_audio, mock_features, mock_settings,
                                         mock_speech_app):
        """Test splash screen hands off to main window correctly"""
        # Set up mocks
        mock_settings.return_value.load_all.return_value = {}
        mock_features.return_value.detect_all_features.return_value = {}
        mock_audio.return_value.is_available.return_value = True
        mock_hotkey.return_value.is_available.return_value = True
        
        self.splash = SplashScreen(self.app)
        
        # Mock the initialization completion
        mock_controller_instance = Mock()
        mock_settings_instance = Mock()
        
        # Mock QTimer to avoid actual delay
        with patch('splash_screen.QTimer') as mock_timer:
            # Simulate initialization completion
            self.splash.on_initialization_complete(mock_controller_instance, mock_settings_instance)
            
            # Check that QTimer.singleShot was called to schedule fade out
            mock_timer.singleShot.assert_called_once()
            
            # Check that objects were stored
            self.assertEqual(self.splash.controller, mock_controller_instance)
            self.assertEqual(self.splash.settings_manager, mock_settings_instance)
        
    def test_splash_error_handling(self):
        """Test splash screen error handling"""
        self.splash = SplashScreen(self.app)
        
        # Mock QMessageBox and QTimer to avoid actual dialog
        with patch('splash_screen.QMessageBox') as mock_msgbox, \
             patch('splash_screen.QTimer') as mock_timer:
            mock_msgbox.return_value.exec_.return_value = None
            
            # Simulate initialization failure
            self.splash.on_initialization_failed("Test error message")
            
            # Check that QTimer.singleShot was called to schedule the error dialog
            mock_timer.singleShot.assert_called_once()
            
            # Check that the status label was updated
            self.assertEqual(self.splash.status_label.text(), "Initialization Failed!")


class TestSplashScreenDocumentation(unittest.TestCase):
    """Test documentation coverage for splash screen"""
    
    def test_splash_screen_docstring(self):
        """Test splash screen has proper docstring"""
        if not SPLASH_AVAILABLE:
            self.skipTest("Splash screen module not available")
            
        from splash_screen import SplashScreen
        
        # Check class has docstring
        self.assertIsNotNone(SplashScreen.__doc__)
        self.assertGreater(len(SplashScreen.__doc__), 50)
        
        # Check key methods have docstrings
        methods_to_check = ['__init__', 'init_ui', 'start_initialization', 
                          'update_progress', 'on_initialization_complete']
        
        for method_name in methods_to_check:
            method = getattr(SplashScreen, method_name)
            self.assertIsNotNone(method.__doc__, f"{method_name} missing docstring")
            self.assertGreater(len(method.__doc__), 20, f"{method_name} docstring too short")
            
    def test_initialization_worker_docstring(self):
        """Test initialization worker has proper docstring"""
        if not SPLASH_AVAILABLE:
            self.skipTest("Splash screen module not available")
            
        from splash_screen import InitializationWorker
        
        # Check class has docstring
        self.assertIsNotNone(InitializationWorker.__doc__)
        self.assertGreater(len(InitializationWorker.__doc__), 50)
        
        # Check key methods have docstrings
        methods_to_check = ['__init__', 'run']
        
        for method_name in methods_to_check:
            method = getattr(InitializationWorker, method_name)
            self.assertIsNotNone(method.__doc__, f"{method_name} missing docstring")
            self.assertGreater(len(method.__doc__), 20, f"{method_name} docstring too short")


if __name__ == '__main__':
    # Set up test environment
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Run tests
    unittest.main()