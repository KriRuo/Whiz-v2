Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
scriptPath = fso.GetParentFolderName(WScript.ScriptFullName)
rootPath = fso.GetParentFolderName(scriptPath)
WshShell.CurrentDirectory = rootPath
ffmpegBin = rootPath & "\ffmpeg\bin"
If fso.FileExists(ffmpegBin & "\ffmpeg.exe") Then
    WshShell.Environment("Process")("PATH") = ffmpegBin & ";" & WshShell.Environment("Process")("PATH")
End If
WshShell.Run ".venv\Scripts\pythonw.exe main.py", 0, False
