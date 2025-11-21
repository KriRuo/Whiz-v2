@echo off
echo Uninstalling Whiz Voice-to-Text Application...
echo.
if exist "%USERPROFILE%\Desktop\Whiz" (
    rmdir /s /q "%USERPROFILE%\Desktop\Whiz"
    echo Whiz has been removed from your system.
) else (
    echo Whiz is not installed.
)
pause
