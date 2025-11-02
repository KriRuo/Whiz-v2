#!/usr/bin/env python3
"""
Whiz Voice-to-Text - One-Click Setup and Launch
This script handles everything automatically - just run it!
"""

import subprocess
import sys
import importlib
import os
import time
from pathlib import Path

def print_banner():
    """Print welcome banner"""
    print("=" * 60)
    print("    Whiz Voice-to-Text Application")
    print("    One-Click Setup and Launch")
    print("=" * 60)
    print()

def check_python():
    """Check Python version and installation"""
    print("Checking Python installation...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"ERROR: Python 3.9+ required. Current: {version.major}.{version.minor}")
        print(f"\nPython 3.9 or higher is required for:")
        print("  • Security: Python 3.7-3.8 reached end-of-life")
        print("  • Performance: Better performance with Python 3.11+")
        print("  • Dependencies: numpy 1.24+ requires Python 3.9+")
        print("\nPlease install Python 3.9+ from: https://python.org")
        print("Recommended: Python 3.11 for best performance")
        return False
    
    print(f"OK: Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_package(package, description=""):
    """Install a package with progress indication"""
    print(f"Installing {package}...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package, "--quiet"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        if result.returncode == 0:
            print(f"OK: {package} installed successfully")
            return True
        else:
            print(f"ERROR: Failed to install {package}")
            print(f"Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT: Installing {package}")
        return False
    except Exception as e:
        print(f"ERROR: Installing {package}: {e}")
        return False

def check_dependencies():
    """Check and install all required dependencies"""
    print("\nChecking dependencies...")
    
    # Required packages with descriptions
    packages = [
        ("PyQt5==5.15.9", "GUI framework"),
        ("openai-whisper>=20231117", "Speech recognition"),
        ("pyaudio>=0.2.11", "Audio input/output"),
        ("keyboard>=0.13.5", "Global hotkeys"),
        ("pyautogui>=0.9.54", "Auto-paste functionality"),
        ("numpy>=1.21.0", "Audio processing")
    ]
    
    missing_packages = []
    
    # Check what's already installed
    for package, description in packages:
        package_name = package.split('==')[0].split('>=')[0]
        try:
            importlib.import_module(package_name)
            print(f"OK: {package_name} - {description}")
        except ImportError:
            print(f"MISSING: {package_name} - {description}")
            missing_packages.append((package, description))
    
    # Install missing packages
    if missing_packages:
        print(f"\nInstalling {len(missing_packages)} missing packages...")
        print("This may take a few minutes on first run...")
        print()
        
        for package, description in missing_packages:
            if not install_package(package, description):
                return False
        
        print("\nOK: All packages installed successfully!")
    else:
        print("\nOK: All dependencies are already installed!")
    
    return True

def test_installation():
    """Test that everything works"""
    print("\nTesting installation...")
    
    try:
        # Test all imports
        import PyQt5
        import whisper
        import pyaudio
        import keyboard
        import pyautogui
        import numpy
        print("OK: All imports successful")
        
        # Test audio system
        p = pyaudio.PyAudio()
        device_count = p.get_device_count()
        print(f"OK: Audio system working ({device_count} devices)")
        p.terminate()
        
        return True
    except Exception as e:
        print(f"ERROR: Installation test failed: {e}")
        return False

def launch_application():
    """Launch the main application"""
    print("\nLaunching Whiz Voice-to-Text Application...")
    print("=" * 60)
    
    try:
        # Import and run the main application
        from main_with_splash import main as app_main
        return app_main()
    except ImportError as e:
        print(f"ERROR: Failed to import application: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you're running this from the Whiz project folder")
        print("2. Check that all Python files are present")
        print("3. Try running: python main_with_splash.py")
        return 1
    except Exception as e:
        print(f"ERROR: Application error: {e}")
        return 1

def main():
    """Main setup and launch function"""
    print_banner()
    
    # Step 1: Check Python
    if not check_python():
        input("\nPress Enter to exit...")
        return 1
    
    # Step 2: Install dependencies
    if not check_dependencies():
        print("\nERROR: Dependency installation failed")
        print("Please check the error messages above")
        input("\nPress Enter to exit...")
        return 1
    
    # Step 3: Test installation
    if not test_installation():
        print("\nERROR: Installation test failed")
        print("Please check the error messages above")
        input("\nPress Enter to exit...")
        return 1
    
    # Step 4: Launch application
    print("\nSetup complete! Starting application...")
    time.sleep(1)
    
    return launch_application()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: Unexpected error: {e}")
        input("\nPress Enter to exit...")
        sys.exit(1)
