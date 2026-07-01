import os
import json
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

print("=== LLM MODULE LOADED ===")

def get_api_key():
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        genai.configure(api_key=key)
        return key
    return None

def is_ai_available():
    return bool(get_api_key())

def analyze_resume_with_llm(resume_text):
    """
    Passes the raw resume text to Gemini to extract a structured JSON object.
    Requires GEMINI_API_KEY to be set in environment.
    """
    if not is_ai_available():
        print("=== GEMINI ERROR === API KEY MISSING")
        raise Exception("LLM NOT WORKING: GEMINI_API_KEY is missing")
        
    system_instruction = """You are an expert ATS (Applicant Tracking System) and Technical Recruiter.
Your job is to read the provided Resume Text and strictly extract the following data.
Return ONLY valid JSON. No markdown, no code blocks, no comments, no extra text.
Your entire response must be a single valid JSON object structured exactly like this:
{
  "detected_domain": "Software / IT",
  "technical_skills": ["Java", "Python", "SQL"],
  "soft_skills": ["Leadership", "Agile"],
  "tools": ["Git", "Docker", "AWS"],
  "experience_level": "Fresher",
  "education_level": "Bachelors",
  "sections_found": ["Education", "Experience", "Projects", "Skills"],
  "strengths": ["Strong technical skill diversity."],
  "weaknesses": ["Missing a dedicated Certifications section."],
  "suggestions": ["Add more action verbs to older experience bullets."]
}"""
    
    import re
    try:
        model = genai.GenerativeModel(
            'gemini-2.5-flash',
            system_instruction=system_instruction,
            generation_config=GenerationConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )
        print("=== CALLING GEMINI FOR RESUME ANALYSIS ===")
        
        response = model.generate_content(
            f"Analyze this resume text:\\n\\n{resume_text}"
        )
        print("=== GEMINI RESPONSE RECEIVED ===")
        
        response_text = response.text.strip()
        
        # Robust JSON extraction: Find the first '{' and last '}'
        json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)
            
        data = json.loads(response_text.strip())
        print("[LLM] JSON parsed successfully.")
        return data

    except json.JSONDecodeError as e:
        print("=== GEMINI JSON PARSE ERROR ===", e)
        raise Exception("LLM response was not valid JSON") from e
    except Exception as e:
        print("=== GEMINI ERROR ===", e)
        raise Exception("LLM NOT WORKING") from e

def chat_with_resume_context(message, context_data):
    """
    Allows the user to talk directly to Gemini with their Resume JSON data passed as context.
    """
    if not is_ai_available():
        raise ValueError("GEMINI_API_KEY is not configured.")
        
    system_instruction = f"""
    You are an expert Career Assistant.
    The user has just had their resume evaluated by your system.
    Here is their resume's Extracted Context JSON:
    {json.dumps(context_data)}
    
    Answer their career question logically related to this context. 
    Be encouraging, concise, and professional. 
    Limit your response to 2-3 short paragraphs maximum.
    """
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_instruction)
        response = model.generate_content(message)
        return response.text.replace('\n', '<br>')
    except Exception as e:
        print(f"Error calling Gemini Chat: {str(e)}")
        raise e
