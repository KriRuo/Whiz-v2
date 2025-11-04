#!/usr/bin/env python3
"""
Runtime test for single instance enforcement.

This script tests the actual application behavior by attempting
to start multiple instances and verifying only one can run.
"""

import sys
import time
import subprocess
import os
from pathlib import Path

# Add parent directory to path (go up two levels: integration -> tests -> root)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.single_instance_manager import SingleInstanceManager

def test_single_instance_runtime():
    """Test single instance enforcement at runtime."""
    print("=" * 60)
    print("Single Instance Runtime Test")
    print("=" * 60)
    print()
    
    # Test 1: First instance should acquire lock
    print("Test 1: First instance lock acquisition")
    print("-" * 60)
    manager1 = SingleInstanceManager(app_name="test_whiz_runtime")
    
    try:
        success1, message1 = manager1.try_acquire_lock()
        print(f"✓ First instance: success={success1}, message={message1}")
        print(f"✓ Lock acquired: {manager1.lock_acquired}")
        print(f"✓ Lock file exists: {manager1.lock_file_path.exists()}")
        
        if manager1.shared_memory:
            print(f"✓ Qt shared memory attached: {manager1.shared_memory.isAttached()}")
        
        assert success1 == True, "First instance should acquire lock"
        assert manager1.lock_acquired == True, "Lock should be acquired"
        print("✓ PASSED\n")
        
    except Exception as e:
        print(f"✗ FAILED: {e}\n")
        manager1.force_release_lock()
        return False
    
    # Test 2: Second instance should detect existing instance
    print("Test 2: Second instance detection")
    print("-" * 60)
    manager2 = SingleInstanceManager(app_name="test_whiz_runtime")
    
    try:
        success2, message2 = manager2.try_acquire_lock()
        print(f"✓ Second instance: success={success2}, message={message2}")
        print(f"✓ Lock acquired: {manager2.lock_acquired}")
        
        assert success2 == True, "Second instance should return success (activation)"
        assert manager2.lock_acquired == False, "Second instance should NOT acquire lock"
        assert message2 is not None, "Should have activation message"
        print("✓ PASSED\n")
        
    except Exception as e:
        print(f"✗ FAILED: {e}\n")
        manager1.force_release_lock()
        return False
    
    # Test 3: Release lock and verify it can be reacquired
    print("Test 3: Lock release and reacquisition")
    print("-" * 60)
    try:
        result = manager1.release_lock()
        print(f"✓ Release result: {result}")
        print(f"✓ Lock acquired after release: {manager1.lock_acquired}")
        print(f"✓ Lock file exists after release: {manager1.lock_file_path.exists()}")
        
        assert result == True, "Release should succeed"
        assert manager1.lock_acquired == False, "Lock should be released"
        assert not manager1.lock_file_path.exists(), "Lock file should be removed"
        print("✓ PASSED\n")
        
        # Now second instance should be able to acquire
        success3, message3 = manager2.try_acquire_lock()
        print(f"✓ After release, second instance: success={success3}, message={message3}")
        print(f"✓ Lock acquired: {manager2.lock_acquired}")
        
        assert success3 == True, "Should acquire lock after release"
        assert manager2.lock_acquired == True, "Lock should be acquired"
        assert message3 is None, "Should be first instance (no message)"
        print("✓ PASSED\n")
        
        # Cleanup
        manager2.release_lock()
        
    except Exception as e:
        print(f"✗ FAILED: {e}\n")
        manager1.force_release_lock()
        manager2.force_release_lock()
        return False
    
    # Test 4: Status reporting
    print("Test 4: Status reporting")
    print("-" * 60)
    manager3 = SingleInstanceManager(app_name="test_whiz_runtime")
    manager3.try_acquire_lock()
    
    try:
        status = manager3.get_status()
        print(f"✓ Status keys: {list(status.keys())}")
        print(f"✓ Lock acquired: {status['lock_acquired']}")
        print(f"✓ PID: {status['pid']}")
        print(f"✓ Qt available: {status['qt_available']}")
        
        assert 'lock_acquired' in status
        assert 'pid' in status
        assert 'qt_available' in status
        assert status['pid'] == os.getpid()
        print("✓ PASSED\n")
        
        manager3.release_lock()
        
    except Exception as e:
        print(f"✗ FAILED: {e}\n")
        manager3.force_release_lock()
        return False
    
    print("=" * 60)
    print("ALL TESTS PASSED! ✓")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_single_instance_runtime()
    sys.exit(0 if success else 1)

