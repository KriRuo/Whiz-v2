@echo off
echo Installing Whiz Voice-to-Text Application...
echo.
if not exist "%USERPROFILE%\Desktop\Whiz" mkdir "%USERPROFILE%\Desktop\Whiz"
copy "Whiz.exe" "%USERPROFILE%\Desktop\Whiz\"
xcopy "assets" "%USERPROFILE%\Desktop\Whiz\assets\" /E /Y
echo.
echo Installation complete!
echo You can find Whiz at: %USERPROFILE%\Desktop\Whiz\Whiz.exe
pause
