# create-shortcut.ps1
# Create a Windows shortcut to launch Whiz without console window

$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$PSScriptRoot\Whiz.lnk")
$Shortcut.TargetPath = "$PSScriptRoot\whiz_env\Scripts\pythonw.exe"
$Shortcut.Arguments = "main_with_splash.py"
$Shortcut.WorkingDirectory = "$PSScriptRoot"
$Shortcut.IconLocation = "$PSScriptRoot\app_icon_transparent.ico"
$Shortcut.Description = "Whiz Voice-to-Text Application"
$Shortcut.Save()

Write-Host "Shortcut created: Whiz.lnk"
