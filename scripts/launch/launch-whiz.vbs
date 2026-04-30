Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
scriptPath = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = fso.GetParentFolderName(scriptPath)
WshShell.Run "whiz_env\Scripts\pythonw.exe main.py", 0, False
