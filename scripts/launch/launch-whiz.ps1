# launch-whiz.ps1
# Launch Whiz without showing any console window
# This PowerShell script runs the application silently

# Change to project root directory
Set-Location (Split-Path -Parent $PSScriptRoot)

Start-Process -FilePath "whiz_env\Scripts\pythonw.exe" -ArgumentList "main_with_splash.py" -WindowStyle Hidden
