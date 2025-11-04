#!/bin/bash
# run_tests.sh
# Linux/macOS test runner for Whiz

# Change to project root directory
cd "$(dirname "$0")/.."

echo "========================================"
echo "Whiz Test Runner (Linux/macOS)"
echo "========================================"
echo

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found!"
    echo "Please install Python 3 from https://python.org"
    exit 1
fi

# Check if pytest is available
echo "Checking pytest..."
if ! python3 -c "import pytest" 2>/dev/null; then
    echo "Installing pytest..."
    pip3 install pytest
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install pytest!"
        exit 1
    fi
fi

# Check if PyQt5 is available (required for some tests)
echo "Checking PyQt5..."
if ! python3 -c "import PyQt5" 2>/dev/null; then
    echo "WARNING: PyQt5 not found, some tests may be skipped"
    echo "Install with: pip3 install PyQt5"
fi

# Run tests
echo "Running Whiz tests..."
echo
python3 -m pytest tests/ -v --tb=short --color=yes

# Check test results
if [ $? -eq 0 ]; then
    echo
    echo "========================================"
    echo "ALL TESTS PASSED!"
    echo "========================================"
    echo
    echo "Test summary:"
    echo "- Cross-platform compatibility tests"
    echo "- Splash screen functionality tests"
    echo "- Core module tests"
    echo "- Integration tests"
    echo
else
    echo
    echo "========================================"
    echo "SOME TESTS FAILED!"
    echo "========================================"
    echo
    echo "Check the output above for details."
    echo "Common issues:"
    echo "- Missing dependencies"
    echo "- Platform-specific failures"
    echo "- Import errors"
    echo "- Missing system libraries"
    echo
fi

echo
read -p "Press Enter to continue..."
