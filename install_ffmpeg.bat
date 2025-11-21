@echo off
REM Install FFmpeg for Whiz
echo Installing FFmpeg...
powershell.exe -ExecutionPolicy Bypass -File "scripts\tools\install_ffmpeg.ps1"
if %ERRORLEVEL% EQU 0 (
    echo.
    echo FFmpeg installed successfully!
    echo You can now run Whiz with proper audio support.
) else (
    echo.
    echo FFmpeg installation failed. Please check the error messages above.
)
pause

