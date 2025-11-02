@echo off
echo Creating Windows installer package...

REM Create installers directory if it doesn't exist
if not exist "installers" mkdir installers

REM Create a simple installer package
echo Creating Whiz-v1.0.0-Windows-Installer.zip...

REM Copy executable and assets to a temporary directory
if not exist "temp_installer" mkdir temp_installer
copy "dist\Whiz.exe" "temp_installer\"
xcopy "assets" "temp_installer\assets\" /E /I /Y
copy "app_icon_transparent.ico" "temp_installer\"
copy "speech_to_text_icon_transparent_middle_white.ico" "temp_installer\"
copy "Icon_Listening.png" "temp_installer\"
copy "Icon_Transcribing.png" "temp_installer\"
copy "README.md" "temp_installer\"
copy "QUICK_START.md" "temp_installer\"

REM Create installation instructions
echo Creating installation instructions...
echo # Whiz v1.0.0 Windows Installation > "temp_installer\INSTALLATION.txt"
echo. >> "temp_installer\INSTALLATION.txt"
echo 1. Extract all files to a folder (e.g., C:\Program Files\Whiz) >> "temp_installer\INSTALLATION.txt"
echo 2. Double-click Whiz.exe to run >> "temp_installer\INSTALLATION.txt"
echo 3. Grant microphone permissions when prompted >> "temp_installer\INSTALLATION.txt"
echo 4. Press Alt+Gr to start/stop recording >> "temp_installer\INSTALLATION.txt"
echo. >> "temp_installer\INSTALLATION.txt"
echo For more information, see README.md >> "temp_installer\INSTALLATION.txt"

REM Create ZIP file using PowerShell
powershell -command "Compress-Archive -Path 'temp_installer\*' -DestinationPath 'installers\Whiz-v1.0.0-Windows-Installer.zip' -Force"

REM Clean up temporary directory
rmdir /S /Q "temp_installer"

REM Create standalone executable copy
copy "dist\Whiz.exe" "installers\Whiz-v1.0.0-Windows-Standalone.exe"

echo.
echo [SUCCESS] Windows installer package created:
echo   - installers\Whiz-v1.0.0-Windows-Installer.zip
echo   - installers\Whiz-v1.0.0-Windows-Standalone.exe
echo.
echo Ready for distribution!
pause
