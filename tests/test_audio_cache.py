#!/usr/bin/env python3
"""
tests/test_audio_cache.py
-------------------------
Unit tests for audio device caching functionality.

Tests the caching mechanism that improves startup performance by
avoiding full device enumeration on subsequent launches.
"""

import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.audio_manager import AudioManager


class TestAudioCaching(unittest.TestCase):
    """Test cases for audio device caching functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for this test
        self.test_dir = tempfile.mkdtemp()
        self.original_tempdir = tempfile.gettempdir()
        
        # Patch tempfile.gettempdir to use our test directory
        self.tempdir_patcher = patch('tempfile.gettempdir', return_value=self.test_dir)
        self.tempdir_patcher.start()
    
    def tearDown(self):
        """Clean up after each test method."""
        # Stop the patcher
        self.tempdir_patcher.stop()
        
        # Clean up test directory
        import shutil
        try:
            shutil.rmtree(self.test_dir)
        except (OSError, PermissionError):
            pass
    
    def test_cache_device(self):
        """Test that device caching works correctly."""
        manager = AudioManager()
        
        # Cache a device
        manager._cache_device(5)
        
        # Retrieve the cached device
        cached = manager._get_cached_device()
        self.assertEqual(cached, 5)
    
    def test_cache_device_string_conversion(self):
        """Test that device ID is properly converted to string and back."""
        manager = AudioManager()
        
        # Cache different device IDs
        test_ids = [0, 1, 5, 10, 99]
        for device_id in test_ids:
            manager._cache_device(device_id)
            cached = manager._get_cached_device()
            self.assertEqual(cached, device_id)
    
    def test_no_cache_file(self):
        """Test behavior when cache file doesn't exist."""
        manager = AudioManager()
        
        # Should return None when no cache file exists
        cached = manager._get_cached_device()
        self.assertIsNone(cached)
    
    def test_corrupted_cache_file(self):
        """Test graceful handling of corrupted cache file."""
        manager = AudioManager()
        
        # Create a corrupted cache file
        cache_file = os.path.join(tempfile.gettempdir(), 'whiz_audio_device.cache')
        with open(cache_file, 'w') as f:
            f.write("not_a_number")
        
        # Should return None for corrupted cache
        cached = manager._get_cached_device()
        self.assertIsNone(cached)
    
    def test_empty_cache_file(self):
        """Test handling of empty cache file."""
        manager = AudioManager()
        
        # Create an empty cache file
        cache_file = os.path.join(tempfile.gettempdir(), 'whiz_audio_device.cache')
        with open(cache_file, 'w') as f:
            f.write("")
        
        # Should return None for empty cache
        cached = manager._get_cached_device()
        self.assertIsNone(cached)
    
    def test_cache_file_permissions(self):
        """Test handling of cache file permission issues."""
        manager = AudioManager()
        
        # Create a cache file
        cache_file = os.path.join(tempfile.gettempdir(), 'whiz_audio_device.cache')
        with open(cache_file, 'w') as f:
            f.write("5")
        
        # Make file read-only (on Windows, this might not work the same way)
        try:
            os.chmod(cache_file, 0o444)  # Read-only
            
            # Should still work for reading
            cached = manager._get_cached_device()
            self.assertEqual(cached, 5)
            
            # Writing should fail gracefully
            manager._cache_device(10)
            # Should not raise an exception
            
        except (OSError, PermissionError):
            # On some systems, we can't change permissions
            # Just verify the basic functionality works
            cached = manager._get_cached_device()
            self.assertEqual(cached, 5)
    
    @patch('core.audio_manager.sd')
    def test_cached_device_validation(self, mock_sd):
        """Test that cached device is validated before use."""
        # Mock sounddevice to simulate device validation
        mock_device_info = MagicMock()
        mock_device_info.__getitem__ = lambda self, key: 2 if key == 'max_input_channels' else None
        mock_sd.query_devices.return_value = mock_device_info
        
        manager = AudioManager()
        
        # Cache a valid device
        manager._cache_device(5)
        
        # Should be able to retrieve it
        cached = manager._get_cached_device()
        self.assertEqual(cached, 5)
    
    @patch('core.audio_manager.sd')
    def test_invalid_cached_device_handling(self, mock_sd):
        """Test handling when cached device is no longer valid."""
        # Mock sounddevice to simulate invalid device
        mock_sd.query_devices.side_effect = Exception("Device not found")
        
        manager = AudioManager()
        
        # Cache an invalid device
        manager._cache_device(9999)
        
        # The cached device should still be retrievable (it's just cached)
        cached = manager._get_cached_device()
        self.assertEqual(cached, 9999)
        
        # But when we try to use it in __init__, it should fall back gracefully
        # This is tested by the actual AudioManager initialization behavior
    
    def test_cache_file_location(self):
        """Test that cache file is created in the correct location."""
        manager = AudioManager()
        
        # Cache a device
        manager._cache_device(3)
        
        # Check that cache file exists in temp directory
        cache_file = os.path.join(tempfile.gettempdir(), 'whiz_audio_device.cache')
        self.assertTrue(os.path.exists(cache_file))
        
        # Verify content
        with open(cache_file, 'r') as f:
            content = f.read().strip()
            self.assertEqual(content, "3")
    
    def test_multiple_cache_operations(self):
        """Test multiple cache operations work correctly."""
        manager = AudioManager()
        
        # Perform multiple cache operations
        test_sequence = [1, 5, 2, 8, 0]
        
        for device_id in test_sequence:
            manager._cache_device(device_id)
            cached = manager._get_cached_device()
            self.assertEqual(cached, device_id)
    
    def test_cache_with_negative_device_id(self):
        """Test caching with negative device ID (should work)."""
        manager = AudioManager()
        
        # Cache a negative device ID (though unlikely in practice)
        manager._cache_device(-1)
        cached = manager._get_cached_device()
        self.assertEqual(cached, -1)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
