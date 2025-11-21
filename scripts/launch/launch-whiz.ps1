# launch-whiz.ps1
# Launch Whiz without showing any console window
# This PowerShell script runs the application silently

# Change to project root directory
Set-Location (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))

# Add ffmpeg to PATH if it exists
$ffmpegPath = Join-Path $PSScriptRoot "..\..\ffmpeg\bin"
if (Test-Path (Join-Path $ffmpegPath "ffmpeg.exe")) {
    $env:PATH = "$ffmpegPath;$env:PATH"
}

Start-Process -FilePath "whiz_env_311\Scripts\pythonw.exe" -ArgumentList "main_with_splash.py" -WindowStyle Hidden
