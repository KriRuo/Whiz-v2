@echo off
REM create-installer.bat
REM Create Windows installer for Whiz
REM This script creates a simple installer without Inno Setup

echo Creating Windows installer for Whiz...

REM Create installer directory
if not exist "installers" mkdir installers

REM Copy executable and assets
echo Copying files...
xcopy "dist\Whiz.exe" "installers\" /Y
xcopy "assets\*" "installers\assets\" /E /Y
copy "app_icon_transparent.ico" "installers\"

REM Create a simple batch installer
echo Creating installer script...
(
echo @echo off
echo echo Installing Whiz Voice-to-Text Application...
echo echo.
echo if not exist "%%USERPROFILE%%\Desktop\Whiz" mkdir "%%USERPROFILE%%\Desktop\Whiz"
echo copy "Whiz.exe" "%%USERPROFILE%%\Desktop\Whiz\"
echo copy "assets" "%%USERPROFILE%%\Desktop\Whiz\assets\" /E /Y
echo echo.
echo echo Installation complete!
echo echo You can find Whiz at: %%USERPROFILE%%\Desktop\Whiz\Whiz.exe
echo pause
) > "installers\install-whiz.bat"

REM Create uninstaller
(
echo @echo off
echo echo Uninstalling Whiz Voice-to-Text Application...
echo echo.
echo if exist "%%USERPROFILE%%\Desktop\Whiz" (
echo     rmdir /s /q "%%USERPROFILE%%\Desktop\Whiz"
echo     echo Whiz has been removed from your system.
echo ^) else (
echo     echo Whiz is not installed.
echo ^)
echo pause
) > "installers\uninstall-whiz.bat"

REM Create README for installer
(
echo Whiz Voice-to-Text Application
echo =============================
echo.
echo Installation Instructions:
echo 1. Run install-whiz.bat as Administrator
echo 2. The application will be installed to your Desktop
echo 3. Run Whiz.exe to start the application
echo.
echo Uninstallation:
echo 1. Run uninstall-whiz.bat as Administrator
echo.
echo System Requirements:
echo - Windows 10/11
echo - Microphone for voice input
echo - 4GB RAM minimum
echo.
echo For support, visit: https://github.com/your-repo/whiz
) > "installers\README.txt"

echo.
echo [SUCCESS] Installer created in installers\ directory
echo.
echo Files created:
echo - Whiz.exe (main application)
echo - assets\ (application resources)
echo - install-whiz.bat (installer script)
echo - uninstall-whiz.bat (uninstaller script)
echo - README.txt (instructions)
echo.
echo To distribute: Zip the entire installers\ directory
echo.
pause
