"""
pytest configuration file
Automatically configures test environment for all tests
"""

import os
import sys
from pathlib import Path

def pytest_configure(config):
    """
    Configure pytest before test collection.
    Sets up FFmpeg PATH and other environment variables.
    """
    # Add project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # Add FFmpeg to PATH if it exists locally
    ffmpeg_bin = project_root / "ffmpeg" / "bin"
    if ffmpeg_bin.exists():
        current_path = os.environ.get("PATH", "")
        if str(ffmpeg_bin) not in current_path:
            os.environ["PATH"] = f"{ffmpeg_bin}{os.pathsep}{current_path}"
            print(f"[PYTEST] Added FFmpeg to PATH: {ffmpeg_bin}")
    else:
        print(f"[PYTEST] FFmpeg not found at: {ffmpeg_bin}")
        print("[PYTEST] E2E tests requiring FFmpeg will be skipped")


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to add markers.
    """
    import pytest
    
    for item in items:
        # Add integration marker to integration test classes
        if "Integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Add e2e marker to end-to-end tests
        if "RealAudioWorkflow" in item.nodeid:
            item.add_marker(pytest.mark.e2e)
        
        # Add unit marker to non-integration tests
        if "Integration" not in item.nodeid and "e2e" not in item.keywords:
            item.add_marker(pytest.mark.unit)


def pytest_runtest_setup(item):
    """
    Reset test isolation state before each test.
    This ensures tests don't interfere with each other.
    """
    # Reset the global cleanup manager before each test to allow re-registration
    try:
        from core.cleanup_manager import reset_cleanup_manager
        reset_cleanup_manager()
    except (ImportError, Exception):
        pass  # Not available in all test contexts


def pytest_runtest_teardown(item, nextitem):
    """
    Clean up after each test run.
    """
    # Reset cleanup manager after test completion too
    try:
        from core.cleanup_manager import reset_cleanup_manager
        reset_cleanup_manager()
    except (ImportError, Exception):
        pass  # Not available in all test contexts


