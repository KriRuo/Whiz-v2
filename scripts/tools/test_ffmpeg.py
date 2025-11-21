#!/usr/bin/env python3
"""Test if FFmpeg is properly installed and accessible."""

import subprocess
import sys
import os

def test_ffmpeg():
    """Test if ffmpeg is available in PATH."""
    print("=" * 50)
    print("Testing FFmpeg Installation")
    print("=" * 50)
    print()
    
    # Test 1: Check if ffmpeg is in PATH
    print("Test 1: Checking if ffmpeg is in PATH...")
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print("[OK] FFmpeg found in PATH")
            # Print first line of version info
            version_line = result.stdout.split('\n')[0]
            print(f"  Version: {version_line}")
        else:
            print("[FAIL] FFmpeg command failed")
            print(f"  Error: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("[FAIL] FFmpeg not found in PATH")
        print()
        print("To fix this issue:")
        print("1. Run 'install_ffmpeg.bat' in the project root")
        print("2. Or download FFmpeg from: https://www.gyan.dev/ffmpeg/builds/")
        print("3. Add ffmpeg to your system PATH")
        return False
    except subprocess.TimeoutExpired:
        print("[FAIL] FFmpeg command timed out")
        return False
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False
    
    print()
    
    # Test 2: Check if Whisper can import (which uses ffmpeg)
    print("Test 2: Checking Whisper audio module...")
    try:
        import whisper
        print("[OK] Whisper module imported successfully")
        print(f"  Whisper location: {whisper.__file__}")
    except ImportError as e:
        print(f"[FAIL] Failed to import Whisper: {e}")
        return False
    
    print()
    
    # Test 3: Test audio loading capability
    print("Test 3: Testing Whisper audio loading capability...")
    try:
        from whisper.audio import load_audio
        print("[OK] Whisper audio module can be imported")
        print("  (Actual audio file test would require a sample file)")
    except ImportError as e:
        print(f"[FAIL] Failed to import Whisper audio module: {e}")
        return False
    
    print()
    print("=" * 50)
    print("All tests passed!")
    print("=" * 50)
    print()
    print("FFmpeg is properly installed and ready to use with Whiz.")
    return True


if __name__ == "__main__":
    success = test_ffmpeg()
    sys.exit(0 if success else 1)

