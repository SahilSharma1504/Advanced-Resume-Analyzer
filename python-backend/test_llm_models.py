import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("API KEY MISSING")
else:
    genai.configure(api_key=api_key)
    try:
        # Test 1.5-flash
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello")
        print("gemini-1.5-flash success:", response.text)
    except Exception as e:
        print("gemini-1.5-flash failed:", e)

    try:
        # Test 2.5-flash (from code)
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content("Hello")
        print("gemini-2.5-flash success:", response.text)
    except Exception as e:
        print("gemini-2.5-flash failed:", e)
