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

# Change to project root directory (parent of scripts/tools/)
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
os.chdir(project_root)
sys.path.insert(0, str(project_root))

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
    """Check and install all required dependencies from requirements.txt"""
    print("\nChecking dependencies...")
    
    # Check if requirements.txt exists
    requirements_file = project_root / "requirements.txt"
    if not requirements_file.exists():
        print(f"ERROR: requirements.txt not found at {requirements_file}")
        return False
    
    print(f"Installing dependencies from requirements.txt...")
    print("This may take a few minutes on first run...")
    print()
    
    try:
        # Install all dependencies from requirements.txt
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout for large packages like torch
        )
        
        if result.returncode == 0:
            print("\nOK: All dependencies installed successfully!")
            
            # Verify critical imports
            print("\nVerifying critical packages...")
            critical_packages = {
                "PyQt5": "GUI framework",
                "whisper": "Speech recognition (openai-whisper)",
                "faster_whisper": "Optimized speech recognition",
                "sounddevice": "Audio input/output",
                "pynput": "Keyboard/mouse control",
                "pyautogui": "Auto-paste functionality",
                "numpy": "Audio processing",
                "psutil": "Process management"
            }
            
            # Add Windows-specific packages
            if sys.platform == "win32":
                critical_packages["win32gui"] = "Windows window management (pywin32)"
            
            all_ok = True
            for package_name, description in critical_packages.items():
                try:
                    if package_name == "whisper":
                        importlib.import_module("whisper")
                    else:
                        importlib.import_module(package_name)
                    print(f"  ✓ {package_name} - {description}")
                except ImportError:
                    print(f"  ✗ {package_name} - {description} (MISSING)")
                    all_ok = False
            
            if not all_ok:
                print("\nWARNING: Some packages failed to import. See above for details.")
                return False
            
            return True
        else:
            print(f"\nERROR: Failed to install dependencies")
            print(f"Exit code: {result.returncode}")
            if result.stderr:
                print(f"Error output:\n{result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("\nERROR: Installation timed out (>10 minutes)")
        print("This may indicate a network issue or very slow download speeds")
        return False
    except Exception as e:
        print(f"\nERROR: Unexpected error during installation: {e}")
        return False

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
