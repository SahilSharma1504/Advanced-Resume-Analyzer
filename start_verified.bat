@echo off
set "PYTHON_EXE=C:\Users\Robin Singh\AppData\Local\Microsoft\WindowsApps\python.exe"
set "JAVA_EXE=C:\Program Files\Java\jdk-23\bin\java.exe"
set "MVN_CMD=C:\Program Files\apache-maven-3.9.9-bin\bin\mvn.cmd"

echo --- DIAGNOSTICS ---
"%PYTHON_EXE%" --version
"%JAVA_EXE%" -version
call "%MVN_CMD%" -version

echo.
echo --- STARTING SERVICES ---

echo [1/3] Starting Python Backend...
cd /d "c:\Users\Robin Singh\OneDrive\Desktop\project1\ResumeAnalyzer\python-backend"
start /b "" "%PYTHON_EXE%" app.py > start_python.log 2>&1

echo [2/3] Starting Java Backend...
cd /d "c:\Users\Robin Singh\OneDrive\Desktop\project1\ResumeAnalyzer\java-backend"
start /b "" cmd /c "set JAVA_HOME=C:\Program Files\Java\jdk-23 && call \"%MVN_CMD%\" spring-boot:run > start_java.log 2>&1"

echo [3/3] Starting Frontend...
cd /d "c:\Users\Robin Singh\OneDrive\Desktop\project1\ResumeAnalyzer\frontend"
start /b "" "%PYTHON_EXE%" -m http.server 8000 > start_frontend.log 2>&1

echo Services launched in background.
echo Waiting 15 seconds for startup logs to populate...
timeout /t 15 /nobreak > nul

echo.
echo --- RECENT LOGS ---
echo [PYTHON LOG]
type "c:\Users\Robin Singh\OneDrive\Desktop\project1\ResumeAnalyzer\python-backend\start_python.log"
echo.
echo [JAVA LOG]
type "c:\Users\Robin Singh\OneDrive\Desktop\project1\ResumeAnalyzer\java-backend\start_java.log"
echo.
echo [FRONTEND LOG]
type "c:\Users\Robin Singh\OneDrive\Desktop\project1\ResumeAnalyzer\frontend\start_frontend.log"
