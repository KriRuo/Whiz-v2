#!/bin/bash
# Whiz Voice-to-Text Application Installer and Launcher for macOS

# Change to project root directory
cd "$(dirname "$0")/.."

set -e  # Exit on any error

echo "🎤 Whiz Voice-to-Text Application Installer for macOS"
echo "=================================================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3.9+ is available
print_status "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    PYTHON_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
    PYTHON_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")
    
    if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 9 ]; then
        print_success "Python $PYTHON_VERSION found"
        PYTHON_CMD="python3"
    else
        print_error "Python 3.9+ required, found $PYTHON_VERSION"
        echo "Please install Python 3.9+ from https://python.org or using Homebrew:"
        echo "  brew install python"
        exit 1
    fi
else
    print_error "Python 3 not found"
    echo "Please install Python 3.9+ from https://python.org or using Homebrew:"
    echo "  brew install python"
    exit 1
fi

# Check if pip is available
print_status "Checking pip installation..."
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    print_error "pip not found"
    echo "Please install pip or reinstall Python"
    exit 1
fi

print_success "pip found"

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    print_error "main.py not found"
    echo "Please run this script from the Whiz application directory"
    exit 1
fi

# Install dependencies
print_status "Installing Python dependencies..."
$PYTHON_CMD -m pip install --user -r requirements.txt

if [ $? -eq 0 ]; then
    print_success "Dependencies installed successfully"
else
    print_error "Failed to install dependencies"
    echo "You may need to install system dependencies first:"
    echo "  brew install portaudio"
    exit 1
fi

# Check for accessibility permissions (for hotkeys)
print_status "Checking accessibility permissions..."
print_warning "macOS requires accessibility permissions for global hotkeys"
echo "If hotkeys don't work, please:"
echo "1. Open System Preferences > Security & Privacy > Privacy"
echo "2. Select 'Accessibility' from the left sidebar"
echo "3. Click the lock to make changes"
echo "4. Add 'Terminal' or 'Python' to the list"
echo "5. Check the box to enable it"
echo

# Launch the application
print_status "Launching Whiz Voice-to-Text Application..."
echo "=================================================="
echo

$PYTHON_CMD main.py

# Check exit status
if [ $? -eq 0 ]; then
    print_success "Application closed successfully"
else
    print_error "Application exited with an error"
    echo "Check the output above for error details"
fi

echo
echo "Thank you for using Whiz!"
