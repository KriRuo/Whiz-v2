@echo off
REM launch-whiz.bat — Launch Whiz Voice-to-Text

cd /d "%~dp0..\.."

if exist "%~dp0..\..\ffmpeg\bin\ffmpeg.exe" (
    set "PATH=%~dp0..\..\ffmpeg\bin;%PATH%"
)

whiz_env_311\Scripts\pythonw.exe main.py

if %ERRORLEVEL% NEQ 0 (
    echo Whiz exited with error code %ERRORLEVEL%
    pause
)
