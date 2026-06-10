Dim fso, shell, dir
Set fso   = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
dir = fso.GetParentFolderName(WScript.ScriptFullName)

' Launch Streamlit with no visible window (0 = hidden, False = don't wait)
shell.Run "cmd /c cd /d """ & dir & """ && "".venv\Scripts\streamlit.exe"" run app.py", 0, False
