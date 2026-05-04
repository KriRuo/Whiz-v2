@echo off
REM launch-whiz.bat — Launch Whiz Voice-to-Text (no terminal window)

cd /d "%~dp0..\.."

if exist "%~dp0..\..\ffmpeg\bin\ffmpeg.exe" (
    set "PATH=%~dp0..\..\ffmpeg\bin;%PATH%"
)

start "" .venv\Scripts\pythonw.exe main.py
