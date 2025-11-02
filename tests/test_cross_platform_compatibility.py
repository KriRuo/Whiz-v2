"""
Cross-Platform Compatibility Test Suite

This test suite verifies that Whiz works correctly across different platforms
and gracefully handles platform-specific limitations.
"""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import logging

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.platform_utils import PlatformUtils, PlatformType
from core.platform_features import PlatformFeatures, FeatureStatus
from core.audio_manager import AudioManager
from core.hotkey_manager import HotkeyManager
from core.logging_config import LoggingConfig, initialize_logging, get_logger

class TestPlatformUtils(unittest.TestCase):
    """Test platform utility functions"""
    
    def setUp(self):
        """Set up test environment"""
        self.logger = get_logger(__name__)
    
    def test_platform_detection(self):
        """Test platform detection"""
        platform = PlatformUtils.get_platform()
        self.assertIn(platform, [PlatformType.WINDOWS, PlatformType.LINUX, PlatformType.MACOS, PlatformType.UNKNOWN])
        
        # Test platform-specific checks
        if platform == PlatformType.WINDOWS:
            self.assertTrue(PlatformUtils.is_windows())
            self.assertFalse(PlatformUtils.is_linux())
            self.assertFalse(PlatformUtils.is_macos())
        elif platform == PlatformType.LINUX:
            self.assertFalse(PlatformUtils.is_windows())
            self.assertTrue(PlatformUtils.is_linux())
            self.assertFalse(PlatformUtils.is_macos())
        elif platform == PlatformType.MACOS:
            self.assertFalse(PlatformUtils.is_windows())
            self.assertFalse(PlatformUtils.is_linux())
            self.assertTrue(PlatformUtils.is_macos())
    
    def test_platform_info(self):
        """Test platform information gathering"""
        info = PlatformUtils.get_platform_info()
        
        self.assertIn('platform', info)
        self.assertIn('system', info)
        self.assertIn('release', info)
        self.assertIn('python_version', info)
        
        self.assertEqual(info['platform'], PlatformUtils.get_platform())
    
    def test_config_directory(self):
        """Test configuration directory creation"""
        config_dir = PlatformUtils.get_config_dir()
        
        self.assertTrue(config_dir.exists())
        self.assertTrue(config_dir.is_dir())
        
        # Test that it's platform-appropriate
        platform = PlatformUtils.get_platform()
        if platform == PlatformType.WINDOWS:
            self.assertIn('AppData', str(config_dir))
        elif platform == PlatformType.MACOS:
            self.assertIn('Library', str(config_dir))
        elif platform == PlatformType.LINUX:
            self.assertIn('.config', str(config_dir))
    
    def test_temp_directory(self):
        """Test temporary directory creation"""
        temp_dir = PlatformUtils.get_temp_dir()
        
        self.assertTrue(temp_dir.exists())
        self.assertTrue(temp_dir.is_dir())
        self.assertIn('whiz', str(temp_dir))
    
    def test_log_directory(self):
        """Test log directory creation"""
        log_dir = PlatformUtils.get_log_dir()
        
        self.assertTrue(log_dir.exists())
        self.assertTrue(log_dir.is_dir())
    
    def test_path_normalization(self):
        """Test path normalization"""
        test_path = "test/path/file.txt"
        normalized = PlatformUtils.normalize_path(test_path)
        
        self.assertIsInstance(normalized, str)
        self.assertTrue(len(normalized) > 0)
    
    def test_admin_check(self):
        """Test administrator privilege checking"""
        is_admin = PlatformUtils.is_admin()
        self.assertIsInstance(is_admin, bool)
    
    def test_system_language(self):
        """Test system language detection"""
        lang = PlatformUtils.get_system_language()
        
        self.assertIsInstance(lang, str)
        self.assertTrue(len(lang) >= 2)
        self.assertTrue(len(lang) <= 5)  # Should be language code
    
    def test_display_info(self):
        """Test display information gathering"""
        display_info = PlatformUtils.get_display_info()
        
        self.assertIn('platform', display_info)
        self.assertIn('dpi_aware', display_info)
        self.assertIn('high_dpi', display_info)
        self.assertIn('screen_width', display_info)
        self.assertIn('screen_height', display_info)
        
        self.assertIsInstance(display_info['screen_width'], int)
        self.assertIsInstance(display_info['screen_height'], int)
        self.assertGreater(display_info['screen_width'], 0)
        self.assertGreater(display_info['screen_height'], 0)

class TestPlatformFeatures(unittest.TestCase):
    """Test platform feature detection"""
    
    def setUp(self):
        """Set up test environment"""
        self.logger = get_logger(__name__)
        self.platform_features = PlatformFeatures()
    
    def test_feature_detection(self):
        """Test feature detection"""
        features = self.platform_features.detect_all_features()
        
        self.assertIn('audio', features)
        self.assertIn('hotkeys', features)
        self.assertIn('autopaste', features)
        self.assertIn('system_integration', features)
        self.assertIn('permissions', features)
        self.assertIn('ui_features', features)
    
    def test_audio_features(self):
        """Test audio feature detection"""
        features = self.platform_features.detect_all_features()
        audio_features = features['audio']
        
        self.assertIn('recording', audio_features)
        self.assertIn('playback', audio_features)
        self.assertIn('device_selection', audio_features)
        self.assertIn('real_time_levels', audio_features)
        
        # Check that all values are FeatureStatus enums
        for feature, status in audio_features.items():
            self.assertIsInstance(status, FeatureStatus)
    
    def test_hotkey_features(self):
        """Test hotkey feature detection"""
        features = self.platform_features.detect_all_features()
        hotkey_features = features['hotkeys']
        
        self.assertIn('global_hotkeys', hotkey_features)
        self.assertIn('key_combination', hotkey_features)
        self.assertIn('permissions_required', hotkey_features)
        
        # Check that status values are FeatureStatus enums
        for feature, status in hotkey_features.items():
            if feature != 'permissions_required':
                self.assertIsInstance(status, FeatureStatus)
    
    def test_feature_availability_check(self):
        """Test feature availability checking"""
        # Test with valid feature paths
        self.assertIsInstance(
            self.platform_features.is_feature_available('audio.recording'), 
            bool
        )
        self.assertIsInstance(
            self.platform_features.is_feature_available('hotkeys.global_hotkeys'), 
            bool
        )
        
        # Test with invalid feature paths
        self.assertFalse(
            self.platform_features.is_feature_available('nonexistent.feature')
        )
        self.assertFalse(
            self.platform_features.is_feature_available('audio.nonexistent')
        )
    
    def test_feature_status_check(self):
        """Test feature status checking"""
        # Test with valid feature paths
        status = self.platform_features.get_feature_status('audio.recording')
        self.assertIsInstance(status, FeatureStatus)
        
        status = self.platform_features.get_feature_status('hotkeys.global_hotkeys')
        self.assertIsInstance(status, FeatureStatus)
        
        # Test with invalid feature paths
        status = self.platform_features.get_feature_status('nonexistent.feature')
        self.assertEqual(status, FeatureStatus.UNKNOWN)
    
    def test_missing_features(self):
        """Test missing features detection"""
        missing = self.platform_features.get_missing_features()
        
        self.assertIsInstance(missing, dict)
        
        # Check structure of missing features
        for feature_path, info in missing.items():
            self.assertIn('status', info)
            self.assertIn('message', info)
            self.assertIsInstance(info['status'], FeatureStatus)
            self.assertIsInstance(info['message'], str)
    
    def test_recommendations(self):
        """Test recommendations generation"""
        recommendations = self.platform_features.get_recommendations()
        
        self.assertIn('install_packages', recommendations)
        self.assertIn('enable_permissions', recommendations)
        self.assertIn('system_requirements', recommendations)
        self.assertIn('workarounds', recommendations)
        
        self.assertIsInstance(recommendations['install_packages'], list)
        self.assertIsInstance(recommendations['enable_permissions'], list)
        self.assertIsInstance(recommendations['system_requirements'], list)
        self.assertIsInstance(recommendations['workarounds'], list)

class TestAudioManager(unittest.TestCase):
    """Test audio manager functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.logger = get_logger(__name__)
        self.audio_manager = AudioManager()
    
    def test_initialization(self):
        """Test audio manager initialization"""
        self.assertIsNotNone(self.audio_manager)
        self.assertIsInstance(self.audio_manager.is_available(), bool)
    
    def test_device_discovery(self):
        """Test audio device discovery"""
        if self.audio_manager.is_available():
            devices = self.audio_manager.get_devices()
            self.assertIsInstance(devices, list)
            
            # Check device structure
            for device in devices:
                self.assertIn('index', device)
                self.assertIn('name', device)
                self.assertIn('channels', device)
                self.assertIn('sample_rate', device)
                self.assertIn('is_default', device)
        else:
            self.logger.warning("Audio not available, skipping device discovery test")
    
    def test_device_selection(self):
        """Test audio device selection"""
        if self.audio_manager.is_available():
            # Test default device selection
            result = self.audio_manager.select_device(None)
            self.assertIsInstance(result, bool)
            
            # Test specific device selection (if devices available)
            devices = self.audio_manager.get_devices()
            if devices:
                result = self.audio_manager.select_device(devices[0]['index'])
                self.assertIsInstance(result, bool)
        else:
            self.logger.warning("Audio not available, skipping device selection test")
    
    def test_recording_lifecycle(self):
        """Test recording start/stop lifecycle"""
        if self.audio_manager.is_available():
            # Test start recording
            result = self.audio_manager.start_recording()
            self.assertIsInstance(result, bool)
            
            if result:
                # Test stop recording
                frames = self.audio_manager.stop_recording()
                self.assertIsInstance(frames, list)
            else:
                self.logger.warning("Failed to start recording")
        else:
            self.logger.warning("Audio not available, skipping recording test")
    
    def test_status(self):
        """Test status information"""
        status = self.audio_manager.get_status()
        
        self.assertIn('available', status)
        self.assertIn('recording', status)
        self.assertIn('device_count', status)
        self.assertIn('selected_device', status)
        self.assertIn('sample_rate', status)
        self.assertIn('channels', status)
        self.assertIn('chunk_size', status)
        
        self.assertIsInstance(status['available'], bool)
        self.assertIsInstance(status['recording'], bool)
        self.assertIsInstance(status['device_count'], int)
        self.assertIsInstance(status['sample_rate'], int)
        self.assertIsInstance(status['channels'], int)
        self.assertIsInstance(status['chunk_size'], int)

class TestHotkeyManager(unittest.TestCase):
    """Test hotkey manager functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.logger = get_logger(__name__)
        self.hotkey_manager = HotkeyManager()
    
    def test_initialization(self):
        """Test hotkey manager initialization"""
        self.assertIsNotNone(self.hotkey_manager)
        self.assertIsInstance(self.hotkey_manager.is_available(), bool)
    
    def test_hotkey_setting(self):
        """Test hotkey setting"""
        if self.hotkey_manager.is_available():
            # Test setting a simple hotkey
            result = self.hotkey_manager.set_hotkey('space')
            self.assertIsInstance(result, bool)
        else:
            self.logger.warning("Hotkeys not available, skipping hotkey setting test")
    
    def test_mode_setting(self):
        """Test mode setting"""
        if self.hotkey_manager.is_available():
            from core.hotkey_manager import HotkeyMode
            
            # Test setting modes
            result = self.hotkey_manager.set_mode(HotkeyMode.HOLD)
            self.assertIsInstance(result, bool)
            
            result = self.hotkey_manager.set_mode(HotkeyMode.TOGGLE)
            self.assertIsInstance(result, bool)
        else:
            self.logger.warning("Hotkeys not available, skipping mode setting test")

class TestLoggingConfig(unittest.TestCase):
    """Test logging configuration"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary directory for test logs
        self.temp_dir = Path(tempfile.mkdtemp())
        self.logging_config = LoggingConfig(
            log_level='DEBUG',
            log_to_file=True,
            log_to_console=False,
            log_dir=self.temp_dir
        )
    
    def tearDown(self):
        """Clean up test environment"""
        # Clean up temporary directory
        if self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir)
            except PermissionError:
                # Windows file locking issue - ignore for tests
                pass
    
    def test_initialization(self):
        """Test logging configuration initialization"""
        self.assertIsNotNone(self.logging_config)
        self.assertEqual(self.logging_config.log_level, 'DEBUG')
        self.assertTrue(self.logging_config.log_to_file)
        self.assertFalse(self.logging_config.log_to_console)
    
    def test_logger_creation(self):
        """Test logger creation"""
        logger = self.logging_config.get_logger('test_module')
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, 'test_module')
    
    def test_log_files(self):
        """Test log file creation"""
        log_files = self.logging_config.get_log_files()
        
        self.assertIn('main', log_files)
        self.assertIn('errors', log_files)
        self.assertIn('debug', log_files)  # Should be present for DEBUG level
        
        # Check that log files exist
        for log_type, log_file in log_files.items():
            self.assertTrue(log_file.exists())
    
    def test_log_info(self):
        """Test log information gathering"""
        log_info = self.logging_config.get_log_info()
        
        self.assertIn('log_level', log_info)
        self.assertIn('log_dir', log_info)
        self.assertIn('log_files', log_info)
        self.assertIn('file_sizes', log_info)
        
        self.assertEqual(log_info['log_level'], 'DEBUG')
        self.assertEqual(log_info['log_dir'], str(self.temp_dir))
    
    def test_level_changing(self):
        """Test log level changing"""
        # Change to INFO level
        self.logging_config.set_level('INFO')
        self.assertEqual(self.logging_config.log_level, 'INFO')
        
        # Change to ERROR level
        self.logging_config.set_level('ERROR')
        self.assertEqual(self.logging_config.log_level, 'ERROR')
    
    def test_debug_toggle(self):
        """Test debug logging toggle"""
        # Enable debug
        self.logging_config.enable_debug()
        self.assertEqual(self.logging_config.log_level, 'DEBUG')
        
        # Disable debug
        self.logging_config.disable_debug()
        self.assertEqual(self.logging_config.log_level, 'INFO')

class TestGlobalLogging(unittest.TestCase):
    """Test global logging functions"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary directory for test logs
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Clean up test environment"""
        # Clean up temporary directory
        if self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir)
            except PermissionError:
                # Windows file locking issue - ignore for tests
                pass
    
    def test_global_initialization(self):
        """Test global logging initialization"""
        config = initialize_logging(
            log_level='INFO',
            log_to_file=True,
            log_to_console=False,
            log_dir=self.temp_dir
        )
        
        self.assertIsNotNone(config)
        self.assertEqual(config.log_level, 'INFO')
    
    def test_global_logger(self):
        """Test global logger creation"""
        initialize_logging(log_dir=self.temp_dir)
        
        logger = get_logger('test_module')
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, 'test_module')
    
    def test_global_level_changing(self):
        """Test global log level changing"""
        initialize_logging(log_dir=self.temp_dir)
        
        # Change level
        from core.logging_config import set_log_level
        set_log_level('ERROR')
        
        # Get config and verify
        from core.logging_config import get_logging_config
        config = get_logging_config()
        self.assertIsNotNone(config)
        self.assertEqual(config.log_level, 'ERROR')

class TestCrossPlatformIntegration(unittest.TestCase):
    """Test cross-platform integration"""
    
    def setUp(self):
        """Set up test environment"""
        self.logger = get_logger(__name__)
    
    def test_platform_consistency(self):
        """Test that platform detection is consistent"""
        platform = PlatformUtils.get_platform()
        platform_info = PlatformUtils.get_platform_info()
        
        self.assertEqual(platform, platform_info['platform'])
    
    def test_feature_consistency(self):
        """Test that feature detection is consistent with platform"""
        platform = PlatformUtils.get_platform()
        features = PlatformFeatures()
        feature_status = features.detect_all_features()
        
        # Check that platform-specific features are detected appropriately
        if platform == PlatformType.WINDOWS:
            # Windows should have good system integration
            self.assertIn('system_integration', feature_status)
        elif platform == PlatformType.MACOS:
            # macOS should require accessibility permissions
            permissions = feature_status.get('permissions', {})
            if 'accessibility_required' in permissions:
                self.assertTrue(permissions['accessibility_required'])
        elif platform == PlatformType.LINUX:
            # Linux should have display server requirements
            self.assertIn('system_integration', feature_status)
    
    def test_graceful_degradation(self):
        """Test graceful degradation when features are unavailable"""
        features = PlatformFeatures()
        missing_features = features.get_missing_features()
        recommendations = features.get_recommendations()
        
        # Should have recommendations for missing features
        if missing_features:
            self.assertTrue(len(recommendations['install_packages']) > 0 or 
                           len(recommendations['enable_permissions']) > 0 or
                           len(recommendations['system_requirements']) > 0)
    
    def test_audio_fallback(self):
        """Test audio manager fallback behavior"""
        audio_manager = AudioManager()
        
        # Should handle unavailability gracefully
        if not audio_manager.is_available():
            self.logger.warning("Audio not available, testing fallback behavior")
            
            # Should return empty lists and False for operations
            devices = audio_manager.get_devices()
            self.assertEqual(devices, [])
            
            result = audio_manager.start_recording()
            self.assertFalse(result)
            
            frames = audio_manager.stop_recording()
            self.assertEqual(frames, [])
    
    def test_hotkey_fallback(self):
        """Test hotkey manager fallback behavior"""
        hotkey_manager = HotkeyManager()
        
        # Should handle unavailability gracefully
        if not hotkey_manager.is_available():
            self.logger.warning("Hotkeys not available, testing fallback behavior")
            
            # Should return False for operations
            result = hotkey_manager.set_hotkey('space')
            self.assertFalse(result)
            
            result = hotkey_manager.register_hotkeys()
            self.assertFalse(result)

def run_compatibility_tests():
    """Run all compatibility tests"""
    # Initialize logging for tests
    initialize_logging(log_level='INFO', log_to_console=True)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestPlatformUtils,
        TestPlatformFeatures,
        TestAudioManager,
        TestHotkeyManager,
        TestLoggingConfig,
        TestGlobalLogging,
        TestCrossPlatformIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_compatibility_tests()
    sys.exit(0 if success else 1)
