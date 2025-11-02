@echo off
REM generate-checksums.bat
REM Generate SHA256 checksums for distribution files

echo Generating SHA256 checksums for Whiz distribution files...

REM Generate checksum for main executable
if exist "dist\Whiz.exe" (
    echo Computing SHA256 for dist\Whiz.exe...
    certutil -hashfile "dist\Whiz.exe" SHA256 > temp_checksum.txt
    for /f "skip=1 tokens=1" %%i in (temp_checksum.txt) do (
        echo dist\Whiz.exe: %%i
        echo dist\Whiz.exe: %%i >> checksums.txt
        goto :done1
    )
    :done1
    del temp_checksum.txt
) else (
    echo ERROR: dist\Whiz.exe not found
)

REM Generate checksum for installer executable
if exist "installers\Whiz.exe" (
    echo Computing SHA256 for installers\Whiz.exe...
    certutil -hashfile "installers\Whiz.exe" SHA256 > temp_checksum.txt
    for /f "skip=1 tokens=1" %%i in (temp_checksum.txt) do (
        echo installers\Whiz.exe: %%i
        echo installers\Whiz.exe: %%i >> checksums.txt
        goto :done2
    )
    :done2
    del temp_checksum.txt
) else (
    echo ERROR: installers\Whiz.exe not found
)

echo.
echo === DISTRIBUTION SUMMARY ===
echo Windows Executable: dist\Whiz.exe
echo Installer Package: installers\ directory
echo Checksums: checksums.txt
echo.
echo Ready for distribution!
pause
