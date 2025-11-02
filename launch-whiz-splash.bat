@echo off
REM launch-whiz-splash.bat
REM Launch Whiz with splash screen (minimized console)
REM This script launches Whiz with a splash screen for better user experience

whiz_env\Scripts\pythonw.exe main_with_splash.py

if %ERRORLEVEL% == 0 (
    REM Whiz closed successfully
) else (
    REM Whiz encountered an error (Exit code: %ERRORLEVEL%)
    pause
)
