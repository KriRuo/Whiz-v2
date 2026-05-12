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

' Try venv in this directory, then 3 levels up (main repo).
localVenv = rootPath & "\whiz_env_311\Scripts\pythonw.exe"
parentVenv = fso.GetParentFolderName(fso.GetParentFolderName(fso.GetParentFolderName(rootPath))) & "\whiz_env_311\Scripts\pythonw.exe"

If fso.FileExists(localVenv) Then
    pythonw = localVenv
ElseIf fso.FileExists(parentVenv) Then
    pythonw = parentVenv
Else
    pythonw = "pythonw"
End If

mainPy = rootPath & "\main_with_splash.py"
WshShell.Run Chr(34) & pythonw & Chr(34) & " " & Chr(34) & mainPy & Chr(34), 0, False
