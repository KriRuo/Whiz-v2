#!/bin/bash
# build-linux.sh
# Build Whiz for Linux using PyInstaller

set -e  # Exit on any error

echo "🐧 Building Whiz for Linux..."
echo "=============================="

# Check if we're on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ Error: This script must be run on Linux"
    exit 1
fi

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "  Arch: sudo pacman -S python python-pip"
    exit 1
fi

# Check PyInstaller
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "📦 Installing PyInstaller..."
    pip3 install PyInstaller
fi

# Check system dependencies
echo "🔍 Checking system dependencies..."
missing_deps=()

# Check for audio libraries
if ! pkg-config --exists alsa 2>/dev/null; then
    missing_deps+=("libasound2-dev")
fi

# Check for X11 libraries
if ! pkg-config --exists x11 2>/dev/null; then
    missing_deps+=("libx11-dev")
fi

# Check for Qt5 libraries
if ! pkg-config --exists Qt5Core 2>/dev/null; then
    missing_deps+=("qt5-default")
fi

if [ ${#missing_deps[@]} -ne 0 ]; then
    echo "⚠️  Missing system dependencies: ${missing_deps[*]}"
    echo "Please install them:"
    echo "  Ubuntu/Debian: sudo apt install ${missing_deps[*]}"
    echo "  CentOS/RHEL: sudo yum install ${missing_deps[*]}"
    echo "  Arch: sudo pacman -S ${missing_deps[*]}"
    echo ""
    echo "Continuing anyway..."
fi

# Check Python dependencies
echo "🔍 Checking Python dependencies..."
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
    print('✅ All Python dependencies available')
"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ *.spec

# Build the application
echo "🔨 Building application..."
python3 -m PyInstaller whiz.spec --clean --noconfirm

# Check if build was successful
if [ -f "dist/Whiz" ]; then
    echo ""
    echo "✅ [SUCCESS] Linux executable created!"
    echo "📁 Location: dist/Whiz"
    echo "📏 Size: $(du -sh dist/Whiz | cut -f1)"
    echo ""
    echo "🚀 To test the application:"
    echo "   ./dist/Whiz"
    echo ""
    echo "📦 To create AppImage:"
    echo "   ./create-appimage-linux.sh"
    echo ""
    echo "📦 To create DEB package:"
    echo "   ./create-deb-linux.sh"
else
    echo "❌ [ERROR] Build failed!"
    echo "Check the output above for error messages"
    exit 1
fi