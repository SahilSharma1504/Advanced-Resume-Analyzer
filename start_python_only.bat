@echo off
echo Starting Python Backend...
cd /d "c:\Users\Robin Singh\OneDrive\Desktop\project1\ResumeAnalyzer\python-backend"
echo Python version:
python --version
echo Starting app...
python app.py > start_python.log 2>&1
echo If we reach here, Python exited.
