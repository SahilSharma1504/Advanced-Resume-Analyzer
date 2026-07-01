import os
import json
import google.generativeai as genai

# Configure Gemini API
API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-2.5-flash', system_instruction="Respond with a joke")
response = model.generate_content("hello")
print(response.text)
