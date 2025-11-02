#!/usr/bin/env python3
"""
run_tests.py
------------
Test runner for Whiz Voice-to-Text Application.

This script runs all tests and generates a comprehensive report.
It supports different test modes and provides detailed output.

Features:
    - Runs all test suites
    - Verbose output with colors
    - Performance timing
    - Coverage reporting (if available)
    - Cross-platform compatibility

Usage:
    Basic test run:
        python run_tests.py
    
    With specific options:
        python run_tests.py --verbose --coverage

Author: Whiz Development Team
Last Updated: October 10, 2025
"""

import pytest
import sys
import os
import argparse
from pathlib import Path


def main():
    """
    Main test runner function.
    
    Parses command line arguments and runs the test suite with
    appropriate options.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(description='Run Whiz test suite')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--coverage', '-c', action='store_true',
                       help='Run with coverage reporting')
    parser.add_argument('--fast', '-f', action='store_true',
                       help='Skip slow tests')
    parser.add_argument('--splash-only', action='store_true',
                       help='Run only splash screen tests')
    parser.add_argument('--cross-platform-only', action='store_true',
                       help='Run only cross-platform compatibility tests')
    
    args = parser.parse_args()
    
    # Build pytest arguments
    pytest_args = ['tests/']
    
    if args.verbose:
        pytest_args.append('-v')
    else:
        pytest_args.append('-q')
    
    # Add common options
    pytest_args.extend([
        '--tb=short',
        '--color=yes',
        '--durations=10'
    ])
    
    # Add coverage if requested
    if args.coverage:
        try:
            import coverage
            pytest_args.extend([
                '--cov=.',
                '--cov-report=html',
                '--cov-report=term-missing'
            ])
        except ImportError:
            print("WARNING: coverage package not installed, skipping coverage reporting")
    
    # Add test filtering
    if args.splash_only:
        pytest_args.extend(['-k', 'splash'])
    elif args.cross_platform_only:
        pytest_args.extend(['-k', 'cross_platform'])
    
    # Add fast mode
    if args.fast:
        pytest_args.extend(['-m', 'not slow'])
    
    # Print test configuration
    print("🧪 Whiz Test Runner")
    print("=" * 50)
    print(f"Test directory: tests/")
    print(f"Verbose: {args.verbose}")
    print(f"Coverage: {args.coverage}")
    print(f"Fast mode: {args.fast}")
    print(f"Filter: {'splash' if args.splash_only else 'cross-platform' if args.cross_platform_only else 'all'}")
    print("=" * 50)
    print()
    
    # Run tests
    try:
        exit_code = pytest.main(pytest_args)
        
        if exit_code == 0:
            print("\n✅ All tests passed!")
        else:
            print(f"\n❌ {exit_code} test(s) failed!")
            
        return exit_code
        
    except Exception as e:
        print(f"\n💥 Test runner error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
