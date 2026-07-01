@echo off
set "JAVA_HOME=C:\Program Files\Java\jdk-23"
set "PYTHON=C:\Users\Robin Singh\AppData\Local\Python\pythoncore-3.14-64\python.exe"

echo Launching Python...
cd /d "c:\Users\Robin Singh\OneDrive\Desktop\project1\ResumeAnalyzer\python-backend"
start /b "" "%PYTHON%" app.py

echo Launching Java...
cd /d "c:\Users\Robin Singh\OneDrive\Desktop\project1\ResumeAnalyzer\java-backend"
start /b "" cmd /c "set JAVA_HOME=C:\Program Files\Java\jdk-23 && apache-maven-3.9.6\bin\mvn.cmd spring-boot:run"

echo Launching Frontend...
cd /d "c:\Users\Robin Singh\OneDrive\Desktop\project1\ResumeAnalyzer\frontend"
start /b "" "%PYTHON%" -m http.server 8000

echo All services launched in background.
