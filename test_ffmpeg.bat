@echo off
REM Test FFmpeg installation for Whiz
echo Testing FFmpeg installation...
echo.

REM Add local ffmpeg to PATH if it exists
if exist "%~dp0ffmpeg\bin\ffmpeg.exe" (
    set "PATH=%~dp0ffmpeg\bin;%PATH%"
    echo Note: Using local FFmpeg installation
    echo.
)

whiz_env_311\Scripts\python.exe scripts\tools\test_ffmpeg.py

echo.
pause

