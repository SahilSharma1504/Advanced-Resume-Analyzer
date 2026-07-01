@echo off
echo ====================================================
echo Starting Resume Analyzer System...
echo ====================================================
echo.

echo Cleaning up old background processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000') do (
    if NOT "%%a"=="0" taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080') do (
    if NOT "%%a"=="0" taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8081') do (
    if NOT "%%a"=="0" taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    if NOT "%%a"=="0" taskkill /F /PID %%a >nul 2>&1
)
echo Ports successfully freed!
echo.
REM Start Python Backend
echo Starting Python backend...
cd /d "%~dp0python-backend"
echo Installing Python dependencies...
pip install -r requirements.txt
start "Python Backend" cmd /k "python app.py || py app.py || echo Failed to start Python! && pause"

REM Wait for Python to start
timeout /t 8

REM Start Java Backend
echo Starting Java backend...
cd /d "%~dp0java-backend"
if exist mvnw.cmd (
    start "Java Backend" cmd /k "call mvnw.cmd spring-boot:run || echo Failed to start Java backend! && pause"
) else (
    start "Java Backend" cmd /k "call mvn spring-boot:run || echo Failed to start Java backend! && pause"
)

REM Wait for Java to start
timeout /t 20

REM Open Frontend
echo Opening frontend...
cd /d "%~dp0frontend"
    echo Starting local web server...
    start "Frontend Server" cmd /k "python -m http.server 8000"
    
    REM Wait 2 seconds for server to bind
    timeout /t 2
    
    echo Launching browser...
    start http://localhost:8000

echo System launched successfully!
pause
