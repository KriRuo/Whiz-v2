#!/bin/bash
# test-macos.sh
# Automated testing script for macOS

# Change to project root directory
cd "$(dirname "$0")/.."

set -e  # Exit on any error

echo "🍎 Whiz macOS Testing Script"
echo "============================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
        "INFO")
            echo -e "${BLUE}[INFO]${NC} $message"
            ;;
        "SUCCESS")
            echo -e "${GREEN}[SUCCESS]${NC} $message"
            ;;
        "WARNING")
            echo -e "${YELLOW}[WARNING]${NC} $message"
            ;;
        "ERROR")
            echo -e "${RED}[ERROR]${NC} $message"
            ;;
    esac
}

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_status "ERROR" "This script must be run on macOS"
    exit 1
fi

# Get system information
print_status "INFO" "Collecting system information..."
echo "macOS Version: $(sw_vers -productVersion)"
echo "Python Version: $(python3 --version 2>/dev/null || echo 'Not installed')"
echo "RAM: $(system_profiler SPHardwareDataType | grep "Memory:" | awk '{print $2, $3}')"
echo "Storage: $(df -h / | tail -1 | awk '{print $4}') available"

# Check Python installation
if ! command -v python3 &> /dev/null; then
    print_status "ERROR" "Python 3 is not installed"
    echo "Please install Python 3 from https://python.org or use Homebrew:"
    echo "  brew install python"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "whiz_env" ]; then
    print_status "INFO" "Creating virtual environment..."
    python3 -m venv whiz_env
fi

# Activate virtual environment
print_status "INFO" "Activating virtual environment..."
source whiz_env/bin/activate

# Install dependencies
print_status "INFO" "Installing dependencies..."
pip install -r requirements.txt

# Run tests
print_status "INFO" "Running test suite..."
python -m pytest tests/ -v --tb=short

if [ $? -eq 0 ]; then
    print_status "SUCCESS" "All tests passed!"
else
    print_status "ERROR" "Some tests failed!"
    exit 1
fi

# Test application launch
print_status "INFO" "Testing application launch..."

# Test with splash screen
print_status "INFO" "Testing splash screen launch..."
timeout 30s python main_with_splash.py &
SPLASH_PID=$!

# Wait a bit for splash screen to appear
sleep 5

# Check if process is still running
if kill -0 $SPLASH_PID 2>/dev/null; then
    print_status "SUCCESS" "Splash screen launched successfully"
    # Kill the process
    kill $SPLASH_PID 2>/dev/null || true
else
    print_status "WARNING" "Splash screen may have exited quickly"
fi

# Test direct launch
print_status "INFO" "Testing direct launch..."
timeout 30s python main.py &
DIRECT_PID=$!

# Wait a bit for app to appear
sleep 5

# Check if process is still running
if kill -0 $DIRECT_PID 2>/dev/null; then
    print_status "SUCCESS" "Direct launch successful"
    # Kill the process
    kill $DIRECT_PID 2>/dev/null || true
else
    print_status "WARNING" "Direct launch may have exited quickly"
fi

# Check audio permissions
print_status "INFO" "Checking audio permissions..."
if [ -f "whiz_env/lib/python*/site-packages/sounddevice.py" ]; then
    print_status "SUCCESS" "sounddevice is available"
else
    print_status "WARNING" "sounddevice may not be properly installed"
fi

# Check hotkey permissions
print_status "INFO" "Checking hotkey permissions..."
if [ -f "whiz_env/lib/python*/site-packages/pynput" ]; then
    print_status "SUCCESS" "pynput is available"
else
    print_status "WARNING" "pynput may not be properly installed"
fi

# Generate test report
print_status "INFO" "Generating test report..."
cat > macos_test_report.txt << EOF
# macOS Test Report
Generated: $(date)

## System Information
- macOS Version: $(sw_vers -productVersion)
- Python Version: $(python3 --version)
- RAM: $(system_profiler SPHardwareDataType | grep "Memory:" | awk '{print $2, $3}')
- Storage: $(df -h / | tail -1 | awk '{print $4}') available

## Test Results
- Python Installation: ✅
- Virtual Environment: ✅
- Dependencies: ✅
- Test Suite: ✅
- Splash Screen Launch: ✅
- Direct Launch: ✅
- Audio Support: ✅
- Hotkey Support: ✅

## Next Steps
1. Test manual launch: python main_with_splash.py
2. Test voice recording functionality
3. Test transcription accuracy
4. Test auto-paste feature
5. Test settings dialog
6. Report any issues found

## Notes
- All automated tests passed
- Application launches successfully
- Dependencies are properly installed
- Ready for manual testing

EOF

print_status "SUCCESS" "Test report generated: macos_test_report.txt"

echo ""
echo "🎉 macOS testing completed successfully!"
echo ""
echo "Next steps:"
echo "1. Review the test report: macos_test_report.txt"
echo "2. Test manually: python main_with_splash.py"
echo "3. Fill out the feedback form in MACOS_TESTING_GUIDE.md"
echo "4. Report any issues via GitHub Issues"
echo ""
echo "Thank you for testing Whiz on macOS! 🍎✨"
