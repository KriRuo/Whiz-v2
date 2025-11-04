@echo off
REM run_tests.bat
REM Windows test runner for Whiz

REM Change to project root directory
cd /d "%~dp0.."

echo ========================================
echo Whiz Test Runner (Windows)
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "whiz_env\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please run setup_and_run.py first to create the environment.
    echo.
    pause
    exit /b 1
)

REM Check if pytest is available
echo Checking pytest...
whiz_env\Scripts\python.exe -c "import pytest" 2>nul
if errorlevel 1 (
    echo Installing pytest...
    whiz_env\Scripts\pip.exe install pytest
    if errorlevel 1 (
        echo ERROR: Failed to install pytest!
        pause
        exit /b 1
    )
)

REM Run tests
echo Running Whiz tests...
echo.
whiz_env\Scripts\python.exe -m pytest tests/ -v --tb=short --color=yes

REM Check test results
if %ERRORLEVEL% == 0 (
    echo.
    echo ========================================
    echo ALL TESTS PASSED!
    echo ========================================
    echo.
    echo Test summary:
    echo - Cross-platform compatibility tests
    echo - Splash screen functionality tests
    echo - Core module tests
    echo - Integration tests
    echo.
) else (
    echo.
    echo ========================================
    echo SOME TESTS FAILED!
    echo ========================================
    echo.
    echo Check the output above for details.
    echo Common issues:
    echo - Missing dependencies
    echo - Platform-specific failures
    echo - Import errors
    echo.
)

echo.
pause
