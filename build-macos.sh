#!/bin/bash
# build-macos.sh
# Build Whiz for macOS using PyInstaller

set -e  # Exit on any error

echo "🍎 Building Whiz for macOS..."
echo "================================"

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Error: This script must be run on macOS"
    exit 1
fi

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3 from https://python.org"
    exit 1
fi

# Check PyInstaller
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "📦 Installing PyInstaller..."
    pip3 install PyInstaller
fi

# Check dependencies
echo "🔍 Checking dependencies..."
python3 -c "
import sys
required_packages = [
    'PyQt5', 'sounddevice', 'pynput', 'whisper', 'numpy', 'pyautogui'
]
missing = []
for pkg in required_packages:
    try:
        __import__(pkg)
    except ImportError:
        missing.append(pkg)

if missing:
    print(f'❌ Missing packages: {missing}')
    print('Please install with: pip3 install -r requirements.txt')
    sys.exit(1)
else:
    print('✅ All dependencies available')
"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ *.spec

# Build the application
echo "🔨 Building application..."
python3 -m PyInstaller whiz.spec --clean --noconfirm

# Check if build was successful
if [ -d "dist/Whiz.app" ]; then
    echo ""
    echo "✅ [SUCCESS] macOS application created!"
    echo "📁 Location: dist/Whiz.app"
    echo "📏 Size: $(du -sh dist/Whiz.app | cut -f1)"
    echo ""
    echo "🚀 To test the application:"
    echo "   open dist/Whiz.app"
    echo ""
    echo "📦 To create DMG installer:"
    echo "   ./create-dmg-macos.sh"
else
    echo "❌ [ERROR] Build failed!"
    echo "Check the output above for error messages"
    exit 1
fi