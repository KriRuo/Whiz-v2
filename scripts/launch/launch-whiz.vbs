Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
launchDir  = fso.GetParentFolderName(WScript.ScriptFullName)
scriptsDir = fso.GetParentFolderName(launchDir)
rootPath   = fso.GetParentFolderName(scriptsDir)
WshShell.CurrentDirectory = rootPath
ffmpegBin = rootPath & "\ffmpeg\bin"
If fso.FileExists(ffmpegBin & "\ffmpeg.exe") Then
    WshShell.Environment("Process")("PATH") = ffmpegBin & ";" & WshShell.Environment("Process")("PATH")
End If
pythonw = rootPath & "\whiz_env_311\Scripts\pythonw.exe"
mainPy  = rootPath & "\main.py"
WshShell.Run Chr(34) & pythonw & Chr(34) & " " & Chr(34) & mainPy & Chr(34), 0, False
