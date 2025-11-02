# launch-whiz.ps1
# Launch Whiz without showing any console window
# This PowerShell script runs the application silently

Start-Process -FilePath "whiz_env\Scripts\pythonw.exe" -ArgumentList "main_with_splash.py" -WindowStyle Hidden
