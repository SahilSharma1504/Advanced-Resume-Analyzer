import sys
import os

# add python-backend to path
sys.path.append('c:/Users/Robin Singh/OneDrive/Desktop/Project/ResumeAnalyzer/python-backend')

from dotenv import load_dotenv
load_dotenv('c:/Users/Robin Singh/OneDrive/Desktop/Project/ResumeAnalyzer/python-backend/.env')

from ai_analyzer import analyze_resume_with_llm

try:
    res = analyze_resume_with_llm("Software Engineer with 5 years of experience in Python and Java. Built scalable microservices.")
    print("SUCCESS")
    print(res)
except Exception as e:
    print("FAILED")
    print(str(e))
