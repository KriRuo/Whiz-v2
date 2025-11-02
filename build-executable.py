#!/usr/bin/env python3
"""
build-executable.py
-------------------
Cross-platform build script for creating standalone Whiz executable.

This script builds a standalone executable using PyInstaller with cross-platform
compatibility. It handles dependency checking, platform detection, and provides
detailed build information.

Features:
    - Cross-platform support (Windows, macOS, Linux)
    - Dependency validation (sounddevice, pynput, PyQt5, whisper)
    - Automatic PyInstaller installation
    - Build optimization and cleanup
    - Detailed error reporting

Dependencies:
    - PyInstaller: Executable packaging
    - sounddevice: Cross-platform audio
    - pynput: Cross-platform input handling
    - PyQt5: GUI framework
    - whisper: Speech recognition

Example:
    Basic build:
        python build-executable.py
    
    With cleanup:
        python build-executable.py --clean

Author: Whiz Development Team
Last Updated: October 10, 2025
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"[BUILD] {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"[OK] {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} failed:")
        print(f"   Command: {cmd}")
        print(f"   Error: {e.stderr}")
        return False

def check_dependencies():
    """
    Check for required dependencies and platform compatibility.
    
    Returns:
        bool: True if all dependencies are available, False otherwise
    """
    print("Checking dependencies...")
    
    # Required packages
    required_packages = {
        'PyInstaller': 'pyinstaller',
        'PyQt5': 'PyQt5',
        'sounddevice': 'sounddevice',
        'pynput': 'pynput',
        'whisper': 'openai-whisper',
        'numpy': 'numpy',
        'pyautogui': 'pyautogui'
    }
    
    missing_packages = []
    
    for package_name, pip_name in required_packages.items():
        try:
            if package_name == 'PyInstaller':
                import PyInstaller
                print(f"[OK] {package_name} {PyInstaller.__version__} found")
            elif package_name == 'PyQt5':
                import PyQt5
                print(f"[OK] {package_name} found")
            elif package_name == 'sounddevice':
                import sounddevice
                print(f"[OK] {package_name} found")
            elif package_name == 'pynput':
                import pynput
                print(f"[OK] {package_name} found")
            elif package_name == 'whisper':
                import whisper
                print(f"[OK] {package_name} found")
            elif package_name == 'numpy':
                import numpy
                print(f"[OK] {package_name} found")
            elif package_name == 'pyautogui':
                import pyautogui
                print(f"[OK] {package_name} found")
        except ImportError:
            print(f"[ERROR] {package_name} not found")
            missing_packages.append(pip_name)
    
    if missing_packages:
        print(f"\n[ERROR] Missing packages: {', '.join(missing_packages)}")
        print("Please install missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    # Platform detection
    current_platform = platform.system()
    print(f"Platform detected: {current_platform}")
    
    if current_platform not in ['Windows', 'Darwin', 'Linux']:
        print(f"Platform {current_platform} may not be fully supported")
    
    return True

def build_executable():
    """
    Build standalone executable using PyInstaller.
    
    Returns:
        bool: True if build successful, False otherwise
    """
    print("Whiz Cross-Platform Executable Builder")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"[OK] PyInstaller {PyInstaller.__version__} found")
    except ImportError:
        print("[ERROR] PyInstaller not found")
        print("Installing PyInstaller...")
        if not run_command("pip install pyinstaller", "Installing PyInstaller"):
            return False
    
    # Check if main.py exists
    if not os.path.exists("main.py"):
        print("[ERROR] main.py not found")
        print("Please run this script from the Whiz application directory")
        return False
    
    # Check if whiz.spec exists
    spec_file = "whiz.spec"
    if not os.path.exists(spec_file):
        print(f"[ERROR] {spec_file} not found")
        print("Please ensure whiz.spec exists in the current directory")
        return False
    
    # Clean previous builds
    print("Cleaning previous builds...")
    for dir_name in ["build", "dist"]:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}/")
    
    # Build the executable
    build_cmd = f"pyinstaller {spec_file}"
    if not run_command(build_cmd, "Building executable"):
        return False
    
    # Check if build was successful
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("[ERROR] Build failed - dist directory not created")
        return False
    
    # Find the executable
    executables = list(dist_dir.glob("**/*.exe")) if sys.platform == "win32" else list(dist_dir.glob("**/whiz"))
    
    if not executables:
        print("[ERROR] No executable found in dist directory")
        return False
    
    executable_path = executables[0]
    print(f"[OK] Executable created: {executable_path}")
    
    # Get file size
    size_mb = executable_path.stat().st_size / (1024 * 1024)
    print(f"   Size: {size_mb:.1f} MB")
    
    # Create a simple launcher script
    if sys.platform == "win32":
        launcher_content = f'''@echo off
echo Starting Whiz...
"{executable_path}"
pause
'''
        launcher_path = dist_dir / "Launch-Whiz.bat"
    else:
        launcher_content = f'''#!/bin/bash
echo "Starting Whiz..."
"{executable_path}"
'''
        launcher_path = dist_dir / "launch-whiz.sh"
    
    with open(launcher_path, 'w') as f:
        f.write(launcher_content)
    
    if sys.platform != "win32":
        os.chmod(launcher_path, 0o755)
    
    print(f"[OK] Launcher created: {launcher_path}")
    
    print("\n🎉 Build completed successfully!")
    print(f"📁 Output directory: {dist_dir.absolute()}")
    print(f"🚀 Executable: {executable_path.absolute()}")
    print(f"🎯 Launcher: {launcher_path.absolute()}")
    
    return True

def main():
    """Main function"""
    try:
        success = build_executable()
        if success:
            print("\nReady to distribute!")
            print("You can now copy the dist/ directory to other machines.")
            sys.exit(0)
        else:
            print("\nBuild failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nBuild cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
