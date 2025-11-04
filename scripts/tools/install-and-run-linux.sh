#!/bin/bash
# Whiz Voice-to-Text Application Installer and Launcher for Linux

# Change to project root directory
cd "$(dirname "$0")/.."

set -e  # Exit on any error

echo "🎤 Whiz Voice-to-Text Application Installer for Linux"
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

# Detect Linux distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
    elif [ -f /etc/redhat-release ]; then
        DISTRO="rhel"
    elif [ -f /etc/debian_version ]; then
        DISTRO="debian"
    else
        DISTRO="unknown"
    fi
    echo $DISTRO
}

# Install system dependencies
install_system_deps() {
    local distro=$1
    print_status "Installing system dependencies for $distro..."
    
    case $distro in
        ubuntu|debian)
            sudo apt update
            sudo apt install -y python3 python3-pip python3-venv portaudio19-dev python3-dev
            ;;
        fedora|rhel|centos)
            sudo dnf install -y python3 python3-pip python3-devel portaudio-devel
            ;;
        arch|manjaro)
            sudo pacman -S --noconfirm python python-pip portaudio
            ;;
        opensuse*)
            sudo zypper install -y python3 python3-pip python3-devel portaudio-devel
            ;;
        *)
            print_warning "Unknown distribution: $distro"
            echo "Please install the following packages manually:"
            echo "  - python3 (3.7+)"
            echo "  - python3-pip"
            echo "  - portaudio development libraries"
            echo "  - python3 development headers"
            ;;
    esac
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
        DISTRO=$(detect_distro)
        install_system_deps $DISTRO
        exit 1
    fi
else
    print_error "Python 3 not found"
    DISTRO=$(detect_distro)
    install_system_deps $DISTRO
    exit 1
fi

# Check if pip is available
print_status "Checking pip installation..."
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    print_error "pip not found"
    DISTRO=$(detect_distro)
    install_system_deps $DISTRO
    exit 1
fi

print_success "pip found"

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    print_error "main.py not found"
    echo "Please run this script from the Whiz application directory"
    exit 1
fi

# Check for display server
print_status "Checking display server..."
if [ -z "$DISPLAY" ] && [ -z "$WAYLAND_DISPLAY" ]; then
    print_warning "No display server detected"
    echo "Whiz requires a display server (X11 or Wayland) to run"
    echo "Please ensure you're running in a graphical environment"
fi

# Install dependencies
print_status "Installing Python dependencies..."
$PYTHON_CMD -m pip install --user -r requirements.txt

if [ $? -eq 0 ]; then
    print_success "Dependencies installed successfully"
else
    print_error "Failed to install dependencies"
    echo "You may need to install system dependencies first:"
    DISTRO=$(detect_distro)
    case $distro in
        ubuntu|debian)
            echo "  sudo apt install portaudio19-dev python3-dev"
            ;;
        fedora|rhel|centos)
            echo "  sudo dnf install portaudio-devel python3-devel"
            ;;
        arch|manjaro)
            echo "  sudo pacman -S portaudio"
            ;;
    esac
    exit 1
fi

# Check for audio permissions
print_status "Checking audio permissions..."
if ! $PYTHON_CMD -c "import sounddevice; print('Audio devices:', len(sounddevice.query_devices()))" 2>/dev/null; then
    print_warning "Audio system check failed"
    echo "You may need to:"
    echo "1. Add your user to the audio group: sudo usermod -a -G audio \$USER"
    echo "2. Log out and log back in"
    echo "3. Check that your microphone is working"
fi

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
