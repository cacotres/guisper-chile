' Iniciar Whisper Flow en segundo plano (Headless) sin consola
Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
sScriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
sPythonScript = sScriptDir & "\whisper_flow.py"

WshShell.CurrentDirectory = sScriptDir
WshShell.Run "pythonw.exe """ & sPythonScript & """", 0, False
