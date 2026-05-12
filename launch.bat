@echo off
cd /d "C:\Users\krir\Documents\Solutions\Whiz"
if exist ffmpeg\bin\ffmpeg.exe set "PATH=%CD%\ffmpeg\bin;%PATH%"
call whiz_env_311\Scripts\activate.bat
python main.py
pause
