@echo off
REM build-windows.bat
REM Windows build script for Whiz executable
REM Creates a standalone .exe file using PyInstaller

echo ========================================
echo Whiz Windows Build Script
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

REM Check if PyInstaller is available
echo Checking PyInstaller...
whiz_env\Scripts\python.exe -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    whiz_env\Scripts\pip.exe install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller!
        pause
        exit /b 1
    )
)

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Build executable
echo Building Whiz for Windows...
echo This may take several minutes...
echo.
whiz_env\Scripts\python.exe -m PyInstaller whiz.spec --clean --noconfirm

REM Check build result
if %ERRORLEVEL% == 0 (
    echo.
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Executable created: dist\Whiz.exe
    echo.
    echo You can now:
    echo 1. Test the executable: dist\Whiz.exe
    echo 2. Create installer using installer-windows.iss
    echo 3. Distribute the standalone executable
    echo.
    
    REM Show file size
    if exist "dist\Whiz.exe" (
        for %%A in ("dist\Whiz.exe") do echo File size: %%~zA bytes
    )
    
) else (
    echo.
    echo ========================================
    echo BUILD FAILED!
    echo ========================================
    echo.
    echo Check the error messages above for details.
    echo Common issues:
    echo - Missing dependencies
    echo - PyInstaller configuration errors
    echo - File permissions
    echo.
)

echo.
pause
