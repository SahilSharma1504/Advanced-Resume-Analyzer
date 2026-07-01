Set WshShell = CreateObject("WScript.Shell")

' Kill old processes on ports
WshShell.Run "cmd /c for /f ""tokens=5"" %a in ('netstat -ano ^| findstr "":5000 :8000 :8081"" ^| findstr LISTENING') do taskkill /F /PID %a", 0, True

WScript.Sleep 1000

' Start Python Backend
WshShell.Run "cmd /k ""cd /d C:\Users\Robin Singh\OneDrive\Desktop\Project\ResumeAnalyzer\python-backend && python app.py""", 1, False

WScript.Sleep 8000

' Start Java Backend
WshShell.Run "cmd /k ""cd /d C:\Users\Robin Singh\OneDrive\Desktop\Project\ResumeAnalyzer\java-backend && run_mvn.cmd""", 1, False

WScript.Sleep 2000

' Start Frontend
WshShell.Run "cmd /k ""cd /d C:\Users\Robin Singh\OneDrive\Desktop\Project\ResumeAnalyzer\frontend && python -m http.server 8000""", 1, False

WScript.Sleep 3000

' Open browser
WshShell.Run "http://localhost:8000", 1, False

WScript.Echo "All services launched!"
