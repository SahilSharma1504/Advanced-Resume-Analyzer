# AI Resume Analyzer Pro

A powerful Resume Analyzer tool built with a **Java Spring Boot backend**, a **Python Flask AI Engine**, and a **Beautiful Glassmorphic UI**.

## Project Structure
- `python-backend/`: Contains text extraction, skill matching, and AI suggestions logic.
- `java-backend/`: Acts as the API gateway and interacts with the Python engine.
- `frontend/`: A premium Vanilla HTML/CSS/JS frontend to interact with the analyzer.

## Prerequisites
- Java 17+
- Maven
- Python 3.8+
- pip

## How to Run

### Automatic Startup (Recommended)
To start the entire system:
1. Double-click `run_project.bat`
This will launch the Frontend, Java Backend, Python API, and Gemini integration automatically.

### Manual Startup
#### Step 1: Start the Python AI Engine
1. Open a new terminal and navigate to: `ResumeAnalyzer/python-backend`
2. *(Optional but Highly Recommended)* Create an `.env` file in this directory and add your Google Gemini Key to activate the **Hybrid LLM Module**:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```
   *Note: If this key is missing, the system will seamlessly run in its **Offline TF-IDF Fallback Mode**.*
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the Flask server:
   ```bash
   python app.py
   ```
*(The Python server will run on `http://localhost:5000`)*

### Step 2: Start the Java Backend
1. Open another terminal and navigate to: `ResumeAnalyzer/java-backend`
2. Run the Spring Boot application using Maven:
   ```bash
   mvn spring-boot:run
   ```
*(The Java server will run on `http://localhost:8080`)*

### Step 3: Open the Frontend Dashboard
1. Simply go to the `ResumeAnalyzer/frontend` folder.
2. Double-click on `index.html` to open it in your browser.
3. Upload a **PDF** or **DOCX** resume, select a role or paste a Job Description, and click **Analyze Resume**!

## Features Implemented
✅ Deep text extraction from PDFs and DOCX files
✅ Skill Keyword Database mapping
✅ Interactive Resume Strength Meter & Scoring Algorithm
✅ Matched & Missing Skills Analysis
✅ Auto-generated AI Suggestions for improvement
✅ Seamless Java <-> Python Integration via REST Hooks
✅ Premium, dynamic glassmorphic interface

Enjoy analyzing!
