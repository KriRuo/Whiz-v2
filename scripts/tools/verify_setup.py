#!/usr/bin/env python3
"""
Whiz Setup Verification Script
This script verifies that all dependencies are properly installed and configured.
Run this after installation to ensure everything is working correctly.
"""

import sys
import importlib
import subprocess
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_status(check_name, passed, details=""):
    """Print check status with consistent formatting"""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status:8} | {check_name}")
    if details:
        print(f"         | {details}")

def check_python_version():
    """Verify Python version is compatible"""
    print_header("Python Version Check")
    
    version = sys.version_info
    required_major = 3
    required_minor = 9
    
    compatible = version.major == required_major and version.minor >= required_minor
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    print_status(
        "Python Version",
        compatible,
        f"Current: {version_str} | Required: {required_major}.{required_minor}+"
    )
    
    return compatible

def check_pip():
    """Verify pip is available"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        pip_version = result.stdout.strip() if result.returncode == 0 else "Unknown"
        print_status("pip Available", result.returncode == 0, pip_version)
        return result.returncode == 0
    except Exception as e:
        print_status("pip Available", False, str(e))
        return False

def check_package(package_name, import_name=None, description=""):
    """Check if a package is installed and importable"""
    if import_name is None:
        import_name = package_name
    
    try:
        module = importlib.import_module(import_name)
        version = getattr(module, "__version__", "unknown")
        print_status(
            package_name,
            True,
            f"{description} | Version: {version}" if description else f"Version: {version}"
        )
        return True
    except ImportError:
        print_status(package_name, False, f"{description} | NOT INSTALLED" if description else "NOT INSTALLED")
        return False
    except Exception as e:
        print_status(package_name, False, f"Import error: {str(e)}")
        return False

def check_core_dependencies():
    """Check all core dependencies"""
    print_header("Core Dependencies Check")
    
    packages = [
        ("PyQt5", "PyQt5", "GUI framework"),
        ("openai-whisper", "whisper", "Speech recognition"),
        ("faster-whisper", "faster_whisper", "Optimized speech recognition"),
        ("sounddevice", "sounddevice", "Audio input/output"),
        ("pynput", "pynput", "Keyboard/mouse control"),
        ("pyautogui", "pyautogui", "Auto-paste functionality"),
        ("numpy", "numpy", "Numerical processing"),
        ("psutil", "psutil", "Process management"),
        ("torch", "torch", "Machine learning backend"),
    ]
    
    results = []
    for package_name, import_name, description in packages:
        results.append(check_package(package_name, import_name, description))
    
    return all(results)

def check_platform_dependencies():
    """Check platform-specific dependencies"""
    print_header("Platform-Specific Dependencies")
    
    if sys.platform == "win32":
        print("Platform: Windows")
        return check_package("pywin32", "win32gui", "Windows window management")
    elif sys.platform == "darwin":
        print("Platform: macOS")
        print_status("macOS Support", True, "No additional packages required")
        return True
    elif sys.platform.startswith("linux"):
        print("Platform: Linux")
        print_status("Linux Support", True, "No additional packages required")
        return True
    else:
        print(f"Platform: {sys.platform}")
        print_status("Platform Support", False, "Unsupported platform")
        return False

def check_audio_system():
    """Verify audio system is working"""
    print_header("Audio System Check")
    
    try:
        import sounddevice as sd
        
        # Check for audio devices
        devices = sd.query_devices()
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        output_devices = [d for d in devices if d['max_output_channels'] > 0]
        
        print_status(
            "Audio Devices",
            len(input_devices) > 0 and len(output_devices) > 0,
            f"Input: {len(input_devices)}, Output: {len(output_devices)}"
        )
        
        # Check default input device
        try:
            default_input = sd.query_devices(kind='input')
            print_status(
                "Default Input",
                True,
                f"{default_input['name']} ({default_input['max_input_channels']} channels)"
            )
            has_default = True
        except Exception as e:
            print_status("Default Input", False, str(e))
            has_default = False
        
        return len(input_devices) > 0 and has_default
        
    except Exception as e:
        print_status("Audio System", False, str(e))
        return False

def check_whisper_models():
    """Check if Whisper models can be loaded"""
    print_header("Whisper Model Check")
    
    try:
        import whisper
        
        # Try to list available models
        available_models = whisper.available_models()
        print_status(
            "Whisper Models",
            len(available_models) > 0,
            f"Available: {', '.join(available_models)}"
        )
        
        # Note: We don't actually load a model here to avoid long load times
        print("         | Note: Models will be downloaded on first use")
        
        return True
    except Exception as e:
        print_status("Whisper Models", False, str(e))
        return False

def check_ffmpeg():
    """Check if FFmpeg is available"""
    print_header("FFmpeg Check")
    
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # Extract version from first line
            version_line = result.stdout.split('\n')[0]
            print_status("FFmpeg", True, version_line)
            return True
        else:
            print_status("FFmpeg", False, "Command failed")
            return False
    except FileNotFoundError:
        print_status("FFmpeg", False, "Not found in PATH")
        print("         | FFmpeg is required for audio processing")
        print("         | Run install_ffmpeg.bat (Windows) or install via package manager")
        return False
    except Exception as e:
        print_status("FFmpeg", False, str(e))
        return False

def check_project_structure():
    """Verify project files are in place"""
    print_header("Project Structure Check")
    
    critical_files = [
        "main.py",
        "main_with_splash.py",
        "speech_controller.py",
        "speech_ui.py",
        "requirements.txt",
        "core/audio_manager.py",
        "core/settings_manager.py",
        "ui/main_window.py",
    ]
    
    all_exist = True
    for file_path in critical_files:
        exists = Path(file_path).exists()
        print_status(file_path, exists, "Found" if exists else "MISSING")
        all_exist = all_exist and exists
    
    return all_exist

def print_summary(results):
    """Print summary of all checks"""
    print_header("Verification Summary")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed
    
    print(f"\nTotal Checks: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n✓ ALL CHECKS PASSED - Setup is complete and ready to use!")
        print("\nYou can now run Whiz with:")
        print("  python main.py")
        print("  or")
        print("  python main_with_splash.py")
    else:
        print("\n✗ SOME CHECKS FAILED - Please fix the issues above")
        print("\nCommon fixes:")
        print("  • Install missing dependencies: pip install -r requirements.txt")
        print("  • Install FFmpeg: run install_ffmpeg.bat (Windows)")
        print("  • Verify you're in the correct directory")
    
    return failed == 0

def main():
    """Run all verification checks"""
    print("\n" + "=" * 60)
    print("  Whiz Voice-to-Text Setup Verification")
    print("  Checking your installation...")
    print("=" * 60)
    
    results = {
        "Python Version": check_python_version(),
        "pip": check_pip(),
        "Core Dependencies": check_core_dependencies(),
        "Platform Dependencies": check_platform_dependencies(),
        "Audio System": check_audio_system(),
        "Whisper": check_whisper_models(),
        "FFmpeg": check_ffmpeg(),
        "Project Files": check_project_structure(),
    }
    
    success = print_summary(results)
    
    return 0 if success else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nVerification cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: Unexpected error during verification: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

