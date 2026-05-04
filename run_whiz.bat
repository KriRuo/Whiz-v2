@echo off
cd /d C:\Users\krir\Documents\Solutions\Whiz
if exist ffmpeg\bin\ffmpeg.exe set "PATH=%CD%\ffmpeg\bin;%PATH%"
call .venv\Scripts\activate.bat
python main.py
pause