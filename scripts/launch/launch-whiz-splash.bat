@echo off
REM launch-whiz-splash.bat — Launch Whiz with animated splash screen

cd /d "%~dp0..\.."

if exist "%~dp0..\..\ffmpeg\bin\ffmpeg.exe" (
    set "PATH=%~dp0..\..\ffmpeg\bin;%PATH%"
)

REM Try venv in this directory, then 3 levels up (main repo), then system Python.
if exist "whiz_env_311\Scripts\pythonw.exe" (
    start "" "whiz_env_311\Scripts\pythonw.exe" main_with_splash.py
) else if exist "..\..\..\whiz_env_311\Scripts\pythonw.exe" (
    start "" "..\..\..\whiz_env_311\Scripts\pythonw.exe" main_with_splash.py
) else (
    start "" pythonw main_with_splash.py
)
