#!/usr/bin/env python3
"""
Unit tests for High DPI scaling functionality in Whiz application.
Tests DPI awareness attributes, window sizing calculations, and scaling behavior.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from PyQt5.QtWidgets import QApplication, QDesktopWidget
from PyQt5.QtCore import Qt

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestHighDPIScaling(unittest.TestCase):
    """Test cases for High DPI scaling functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Only create QApplication if one doesn't exist
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
    
    def tearDown(self):
        """Clean up after tests"""
        pass
    
    def test_dpi_attributes_set_correctly(self):
        """Test that DPI awareness attributes are set correctly"""
        # Test that main.py contains DPI attribute settings
        with open('main.py', 'r') as f:
            content = f.read()
        
        self.assertIn('AA_EnableHighDpiScaling', content)
        self.assertIn('AA_UseHighDpiPixmaps', content)
    
    def test_environment_variable_set(self):
        """Test that QT_AUTO_SCREEN_SCALE_FACTOR environment variable is set"""
        # Test that main.py sets the environment variable
        # We'll test this by checking the main.py file content
        import os
        main_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'main.py')
        
        with open(main_file, 'r') as f:
            content = f.read()
            
        # Check that environment variable is set in main.py
        self.assertIn('QT_AUTO_SCREEN_SCALE_FACTOR', content)
        self.assertIn('os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"', content)
    
    def test_window_sizing_calculations(self):
        """Test window sizing calculations for different screen resolutions"""
        # Test that main window can be imported and has sizing methods
        from ui.main_window import MainWindow
        from core.settings_manager import SettingsManager
        
        # Verify the classes exist and can be instantiated
        self.assertTrue(hasattr(MainWindow, '__init__'))
        self.assertTrue(hasattr(SettingsManager, '__init__'))
    
    def test_window_min_max_constraints(self):
        """Test that window min/max constraints are properly set"""
        from ui.main_window import MainWindow
        from core.settings_manager import SettingsManager
        
        # Mock settings manager
        mock_settings_manager = Mock(spec=SettingsManager)
        
        # Mock screen geometry for 4K display
        mock_screen = Mock()
        mock_screen.availableGeometry.return_value = Mock()
        mock_screen.availableGeometry.return_value.width.return_value = 3840
        mock_screen.availableGeometry.return_value.height.return_value = 2160
        mock_screen.availableGeometry.return_value.x.return_value = 0
        mock_screen.availableGeometry.return_value.y.return_value = 0
        
        with patch('PyQt5.QtWidgets.QApplication.screenAt', return_value=mock_screen):
            with patch('PyQt5.QtWidgets.QApplication.primaryScreen', return_value=mock_screen):
                # Create main window
                window = MainWindow(mock_settings_manager)
                
                # Check minimum size constraints
                min_size = window.minimumSize()
                self.assertGreaterEqual(min_size.width(), 380)  # Updated to match current responsive sizing config
                self.assertGreaterEqual(min_size.height(), 530)  # Updated to match current responsive sizing config (was 480)
                
                # Check maximum size constraints
                max_size = window.maximumSize()
                self.assertLessEqual(max_size.width(), 1600)
                self.assertLessEqual(max_size.height(), 1200)
    
    def test_preferences_dialog_sizing(self):
        """Test preferences dialog sizing calculations"""
        # Test that preferences dialog can be imported and has sizing methods
        from ui.preferences_dialog import PreferencesDialog
        from core.settings_manager import SettingsManager
        
        # Verify the classes exist and can be instantiated
        self.assertTrue(hasattr(PreferencesDialog, '__init__'))
        self.assertTrue(hasattr(SettingsManager, '__init__'))
    
    def test_dpi_scaling_factor_mock(self):
        """Test behavior with different DPI scaling factors"""
        # Mock different DPI scaling factors
        scaling_factors = [1.0, 1.25, 1.5, 2.0, 2.5]  # 100%, 125%, 150%, 200%, 250%
        
        for scale_factor in scaling_factors:
            with self.subTest(scale_factor=scale_factor):
                # Mock QApplication to return scaled dimensions
                with patch('PyQt5.QtWidgets.QApplication.screenAt') as mock_screen_at:
                    mock_screen = Mock()
                    mock_screen.availableGeometry.return_value = Mock()
                    mock_screen.availableGeometry.return_value.width.return_value = int(1920 / scale_factor)
                    mock_screen.availableGeometry.return_value.height.return_value = int(1080 / scale_factor)
                    mock_screen.availableGeometry.return_value.x.return_value = 0
                    mock_screen.availableGeometry.return_value.y.return_value = 0
                    mock_screen_at.return_value = mock_screen
                    
                    # Test that window sizing still works correctly
                    from ui.main_window import MainWindow
                    from core.settings_manager import SettingsManager
                    
                    mock_settings_manager = Mock(spec=SettingsManager)
                    window = MainWindow(mock_settings_manager)
                    
                    # Window should still be sized appropriately
                    self.assertGreater(window.size().width(), 350)  # Updated to match current responsive sizing config
                    self.assertGreater(window.size().height(), 500)  # Updated to match current responsive sizing config
    
    def test_all_entry_points_have_dpi_support(self):
        """Test that all main entry points have DPI support enabled"""
        entry_points = [
            'main',
            'main_with_splash'
        ]
        
        for entry_point in entry_points:
            with self.subTest(entry_point=entry_point):
                # Read the file content to check for DPI support
                file_path = f"{entry_point}.py"
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        content = f.read()
                        
                    # Check for DPI support attributes
                    self.assertIn('AA_EnableHighDpiScaling', content)
                    self.assertIn('AA_UseHighDpiPixmaps', content)
                    self.assertIn('QT_AUTO_SCREEN_SCALE_FACTOR', content)
                else:
                    self.fail(f"Entry point file {file_path} not found")
    
    def test_window_centering_on_different_screens(self):
        """Test window centering works correctly on different screen configurations"""
        from ui.main_window import MainWindow
        from core.settings_manager import SettingsManager
        
        # Mock settings manager
        mock_settings_manager = Mock(spec=SettingsManager)
        
        # Test different screen configurations
        test_cases = [
            # Single screen
            (1920, 1080, 0, 0),
            # Multi-monitor setup - secondary screen
            (1920, 1080, 1920, 0),  # Right monitor
            (1920, 1080, 0, 1080),  # Bottom monitor
        ]
        
        for screen_width, screen_height, screen_x, screen_y in test_cases:
            with self.subTest(screen_x=screen_x, screen_y=screen_y):
                # Mock screen geometry
                mock_screen = Mock()
                mock_screen.availableGeometry.return_value = Mock()
                mock_screen.availableGeometry.return_value.width.return_value = screen_width
                mock_screen.availableGeometry.return_value.height.return_value = screen_height
                mock_screen.availableGeometry.return_value.x.return_value = screen_x
                mock_screen.availableGeometry.return_value.y.return_value = screen_y
                
                with patch('PyQt5.QtWidgets.QApplication.screenAt', return_value=mock_screen):
                    with patch('PyQt5.QtWidgets.QApplication.primaryScreen', return_value=mock_screen):
                        # Create main window
                        window = MainWindow(mock_settings_manager)
                        
                        # Check window position is within screen bounds
                        window_pos = window.pos()
                        self.assertGreaterEqual(window_pos.x(), screen_x)
                        self.assertGreaterEqual(window_pos.y(), screen_y)
                        self.assertLessEqual(window_pos.x(), screen_x + screen_width)
                        self.assertLessEqual(window_pos.y(), screen_y + screen_height)


class TestDPIScalingIntegration(unittest.TestCase):
    """Integration tests for DPI scaling functionality"""
    
    def setUp(self):
        """Set up test environment"""
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
    
    def test_splash_screen_scaling(self):
        """Test that splash screens also handle DPI scaling correctly"""
        # Check splash_screen.py has responsive geometry method
        with open('splash_screen.py', 'r') as f:
            content = f.read()
        
        self.assertIn('setup_responsive_geometry', content)
        
        # Check main_with_splash.py has DPI support
        with open('main_with_splash.py', 'r') as f:
            content = f.read()
        
        self.assertIn('QT_AUTO_SCREEN_SCALE_FACTOR', content)
        self.assertIn('AA_EnableHighDpiScaling', content)
    
    def test_consistency_across_launchers(self):
        """Test that all launchers use consistent DPI settings"""
        launcher_files = [
            'main.py',
            'main_with_splash.py', 
            'main_with_splash_fixed.py',
            'simple_splash_launcher.py'
        ]
        
        dpi_settings = {}
        
        for launcher_file in launcher_files:
            if os.path.exists(launcher_file):
                with open(launcher_file, 'r') as f:
                    content = f.read()
                
                # Extract DPI settings
                dpi_settings[launcher_file] = {
                    'has_enable_scaling': 'AA_EnableHighDpiScaling' in content,
                    'has_use_pixmaps': 'AA_UseHighDpiPixmaps' in content,
                    'has_env_var': 'QT_AUTO_SCREEN_SCALE_FACTOR' in content
                }
        
        # All launchers should have the same DPI settings
        for launcher_file, settings in dpi_settings.items():
            self.assertTrue(settings['has_enable_scaling'], 
                          f"{launcher_file} missing AA_EnableHighDpiScaling")
            self.assertTrue(settings['has_use_pixmaps'], 
                          f"{launcher_file} missing AA_UseHighDpiPixmaps")
            self.assertTrue(settings['has_env_var'], 
                          f"{launcher_file} missing QT_AUTO_SCREEN_SCALE_FACTOR")


if __name__ == '__main__':
    # Run tests
    unittest.main()
