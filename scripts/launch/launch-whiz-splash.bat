@echo off
REM launch-whiz-splash.bat
REM Launch Whiz with splash screen (minimized console)
REM This script launches Whiz with a splash screen for better user experience

REM Change to project root directory
cd /d "%~dp0..\.."

REM Add ffmpeg to PATH if it exists
if exist "%~dp0..\..\ffmpeg\bin\ffmpeg.exe" (
    set "PATH=%~dp0..\..\ffmpeg\bin;%PATH%"
)

whiz_env_311\Scripts\pythonw.exe main_with_splash.py

if %ERRORLEVEL% == 0 (
    REM Whiz closed successfully
) else (
    REM Whiz encountered an error (Exit code: %ERRORLEVEL%)
    pause
)
