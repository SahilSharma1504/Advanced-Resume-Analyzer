import os
from dotenv import load_dotenv

load_dotenv()
print("ENV KEY FROM APP:", os.getenv("GEMINI_API_KEY"))

from flask import Flask, request, jsonify
from flask_cors import CORS
from engine import run_pure_evaluation_pipeline, improve_bullet, rule_based_chat

"""
MICROSERVICE EXPLANATION:
This Python application acts as an AI/NLP microservice in the overall architecture.
It exposes REST API endpoints that consume and return JSON.
The Java Spring Boot API Gateway calls these endpoints to offload heavy NLP tasks.
"""

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}) # Allow all origins during development

@app.route('/api/analyze-advanced', methods=['POST'])
def analyze_resume_advanced():
    if 'resume' not in request.files:
        return jsonify({'error': 'No resume file provided'}), 400
    
    file = request.files['resume']
    
    if file.filename == '':
        return jsonify({'error': 'Empty file name'}), 400

    import tempfile
    
    # Save the file temporarily
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, file.filename)
    file.save(temp_path)

    try:
        result = run_pure_evaluation_pipeline(temp_path)
    except Exception as e:
        print("--- API ERROR ---", str(e))
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
    return jsonify(result), 200

@app.route('/api/test-llm', methods=['GET'])
def test_llm():
    try:
        from ai_analyzer import is_ai_available
        import google.generativeai as genai
        import os
        
        print("KEY DURING REQUEST:", os.getenv("GEMINI_API_KEY"))
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return jsonify({"status": "error", "message": "LLM NOT WORKING: API Key missing"}), 400
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        print("=== CALLING GEMINI FOR TEST ENDPOINT ===")
        response = model.generate_content("Say LLM is working")
        print("=== GEMINI RESPONSE RECEIVED ===")
        
        return jsonify({"status": "success", "response": response.text}), 200
    except Exception as e:
        print("=== GEMINI ERROR ===", e)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/improve', methods=['POST'])
def improve_resume_bullet():
    data = request.get_json()
    bullet_text = data.get('bullet', '')
    improved_text = improve_bullet(bullet_text)
    return jsonify({'improved_bullet': improved_text}), 200

@app.route('/api/chat', methods=['POST'])
def chat_assistant():
    data = request.get_json()
    message = data.get('message', '')
    context = data.get('context', {})
    reply = rule_based_chat(message, context)
    return jsonify({'reply': reply}), 200

@app.route('/api/quick-score', methods=['POST'])
def quick_score():
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
        
    raw_text = data['text']
    
    try:
        from engine import score_raw_text
        result = score_raw_text(raw_text)
        return jsonify(result), 200
    except Exception as e:
        print("--- QUICK SCORE ERROR ---", str(e))
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
