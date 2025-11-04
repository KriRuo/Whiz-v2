#!/usr/bin/env python3
"""
Test QSettings timing and sync issues.

This script will test if there are timing issues with QSettings
sync that could cause settings to not persist properly.
"""

import sys
import os
import time

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.settings_manager import SettingsManager
from core.logging_config import get_logger

logger = get_logger(__name__)

def test_qsettings_timing():
    """Test QSettings timing and sync issues."""
    print("Testing QSettings Timing and Sync")
    print("=" * 40)
    
    # Test 1: Test immediate sync
    print("1. Testing immediate sync...")
    settings_manager = SettingsManager()
    
    # Set hotkey
    settings_manager.set("behavior/hotkey", "F8")
    print(f"   Set hotkey to: F8")
    
    # Check immediately
    immediate = settings_manager.get("behavior/hotkey")
    print(f"   Immediate check: {immediate}")
    
    # Test 2: Test with new instance immediately
    print("\n2. Testing with new instance immediately...")
    new_manager = SettingsManager()
    new_hotkey = new_manager.get("behavior/hotkey")
    print(f"   New manager hotkey: {new_hotkey}")
    
    # Test 3: Test QSettings directly
    print("\n3. Testing QSettings directly...")
    try:
        from PyQt5.QtCore import QSettings
        qsettings = QSettings("Whiz", "VoiceToText")
        qsettings_hotkey = qsettings.value("behavior/hotkey")
        print(f"   QSettings hotkey: {qsettings_hotkey}")
    except Exception as e:
        print(f"   Error checking QSettings: {e}")
    
    # Test 4: Test rapid changes
    print("\n4. Testing rapid changes...")
    
    for i in range(5):
        hotkey = f"F{i+1}"
        settings_manager.set("behavior/hotkey", hotkey)
        print(f"   Set hotkey to: {hotkey}")
        
        # Check immediately
        immediate = settings_manager.get("behavior/hotkey")
        print(f"   Immediate: {immediate}")
        
        # Check with new manager
        new_mgr = SettingsManager()
        new_hotkey = new_mgr.get("behavior/hotkey")
        print(f"   New manager: {new_hotkey}")
        
        # Small delay
        time.sleep(0.01)
    
    # Test 5: Test apply_all timing
    print("\n5. Testing apply_all timing...")
    
    # Set hotkey
    settings_manager.set("behavior/hotkey", "alt gr")
    print(f"   Set hotkey to: alt gr")
    
    # Check immediately
    immediate = settings_manager.get("behavior/hotkey")
    print(f"   Immediate: {immediate}")
    
    # Create mock window and call apply_all
    class MockMainWindow:
        def __init__(self):
            self.controller = None
    
    mock_window = MockMainWindow()
    
    # Call apply_all (this might be causing the issue)
    print("   Calling apply_all...")
    settings_manager.apply_all(mock_window)
    
    # Check after apply_all
    after_apply = settings_manager.get("behavior/hotkey")
    print(f"   After apply_all: {after_apply}")
    
    # Test 6: Test load_all timing
    print("\n6. Testing load_all timing...")
    
    # Set hotkey
    settings_manager.set("behavior/hotkey", "caps lock")
    print(f"   Set hotkey to: caps lock")
    
    # Check immediately
    immediate = settings_manager.get("behavior/hotkey")
    print(f"   Immediate: {immediate}")
    
    # Call load_all
    print("   Calling load_all...")
    loaded_settings = settings_manager.load_all()
    loaded_hotkey = loaded_settings.get("behavior/hotkey")
    print(f"   Load all result: {loaded_hotkey}")
    
    # Check with new manager
    new_mgr = SettingsManager()
    new_hotkey = new_mgr.get("behavior/hotkey")
    print(f"   New manager: {new_hotkey}")
    
    print("\n✅ QSettings timing test completed!")
    return True

if __name__ == "__main__":
    try:
        success = test_qsettings_timing()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        logger.exception("QSettings timing test failed")
        sys.exit(1)
