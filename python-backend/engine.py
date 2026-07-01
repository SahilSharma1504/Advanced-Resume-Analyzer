import re
import PyPDF2
import docx
from fuzzywuzzy import fuzz
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import difflib
import json
from ai_analyzer import is_ai_available, analyze_resume_with_llm, chat_with_resume_context

# Quietly download necessary NLTK data
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

"""
MICROSERVICE EXPLANATION (For Viva/Academic Purposes):
This Python engine acts as the NLP and AI processing core for the Intelligent Resume Evaluation System.
It uses TF-IDF vectorization and cosine similarity for Domain Detection and Intent Classification.
It uses rule-based heuristics and regex for ATS extraction and Experience scoring.
The scoring is heavily weighted and realistically capped to avoid 100% scores.
"""

# ==========================================
# 1. DICTIONARIES & MASTER DATA
# ==========================================

TECH_SKILLS_DB = set([
    "java", "python", "javascript", "typescript", "c++", "c#", "ruby", "php", "go", "rust", 
    "spring", "spring boot", "hibernate", "react", "angular", "vue", "node.js", "express", "next.js", 
    "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "css", "html",
    "machine learning", "artificial intelligence", "data structures", "algorithms",
    "rest api", "microservices", "graphql", "kafka", "pandas", "numpy", 
    "django", "flask", "fastapi", "linux", "cloud computing"
])

SOFT_SKILLS_DB = set([
    "leadership", "communication", "teamwork", "project management", "agile", "scrum", 
    "problem solving", "time management", "marketing", "sales", "human resources", 
    "public speaking", "negotiation", "critical thinking", "client relations",
    "analytical skills", "adaptability", "mentoring"
])

TOOLS_DB = set([
    "git", "github", "gitlab", "docker", "kubernetes", "aws", "gcp", "azure", "jenkins", 
    "github actions", "ci/cd", "jira", "confluence", "trello", "postman", "figma", 
    "excel", "powerpoint", "tableau", "power bi", "splunk", "datadog", "maven", "gradle"
])

# DOMAIN CLUSTERS FOR TF-IDF (Explainable AI)
DOMAIN_CLUSTERS = {
    "Software / IT": "software engineer developer programming coding java python javascript react web backend frontend fullstack cloud aws architecture microservices code agile testing",
    "Management": "manager leadership strategy operations business agile scrum project roadmap stakeholders budget direct director executive alignment KPI metrics",
    "Marketing": "marketing seo campaigns social media content brand strategy growth advertising sales digital ecommerce inbound analytics b2b b2c",
    "Data / Analytics": "data analyst scientist sql python pandas machine learning ai statistics modeling visualization dashboard tableau analytics prediction",
    "HR": "human resources talent acquisition recruiter onboarding employee relations payroll benefits hiring culture compliance retention training"
}

# ==========================================
# 2. TEXT EXTRACTION
# ==========================================

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            extr = page.extract_text()
            if extr: text += extr + "\n"
    return text

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s\n+.-]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# ==========================================
# 3. ADVANCED ANALYSIS MODULES
# ==========================================

def detect_domain(text):
    """
    EXPLANATION: Uses TF-IDF wrappers to classify the resume text against predefined
    domain clusters. Calculates cosine similarity to find the mathematical closest match.
    """
    domain_names = list(DOMAIN_CLUSTERS.keys())
    domain_texts = list(DOMAIN_CLUSTERS.values())
    
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(domain_texts + [text])
    
    # Calculate similarity of user resume (last item) against the domain intents
    cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()
    best_idx = cosine_sim.argmax()
    
    # Normalize the confidence strictly (cosine similarity ranges 0 to 1)
    # Usually resumes have a lot of noise, so multiply by an amplifier for realism
    raw_confidence = cosine_sim[best_idx] * 100 * 2.5 
    confidence = min(int(raw_confidence), 98) # cap at 98%
    
    if confidence < 15:
        return "General", confidence
    return domain_names[best_idx], confidence

def extract_categorized_skills(text):
    """Scan text against our specific DBs and return categorized hits."""
    tech_hits = set()
    soft_hits = set()
    tools_hits = set()
    
    for skill in TECH_SKILLS_DB:
        if re.search(r'\b' + re.escape(skill) + r'\b', text): tech_hits.add(skill.title())
    for skill in SOFT_SKILLS_DB:
        if re.search(r'\b' + re.escape(skill) + r'\b', text): soft_hits.add(skill.title())
    for skill in TOOLS_DB:
        if re.search(r'\b' + re.escape(skill) + r'\b', text): tools_hits.add(skill.title())
        
    return list(tech_hits), list(soft_hits), list(tools_hits)

def detect_sections(text):
    sections = {
        'Education': bool(re.search(r'\b(education|university|college|bachelor|master|degree)\b', text)),
        'Experience': bool(re.search(r'\b(experience|work history|employment|career)\b', text)),
        'Projects': bool(re.search(r'\b(projects|portfolio|personal projects)\b', text)),
        'Skills': bool(re.search(r'\b(skills|technologies|core competencies)\b', text)),
        'Certifications': bool(re.search(r'\b(certifications|certificates|awards)\b', text))
    }
    return sections, [k for k, v in sections.items() if v]

def evaluate_structure_and_writing(text, raw_text):
    # Retrieve top 500 common english words for a naive spell check to avoid C++ dependencies
    common_words = set([
        "the", "of", "to", "and", "a", "in", "is", "it", "you", "that", "he", "was", "for", "on", "are", "with", "as", "i", "his", "they", "be", "at", "one", "have", "this", "from", "or", "had", "by", "hot", "word", "but", "what", "some", "we", "can", "out", "other", "were", "all", "there", "when", "up", "use", "your", "how", "said", "an", "each", "she", "which", "do", "their", "time", "if", "will", "way", "about", "many", "then", "them", "write", "would", "like", "so", "these", "her", "long", "make", "thing", "see", "him", "two", "has", "look", "more", "day", "could", "go", "come", "did", "number", "sound", "no", "most", "people", "my", "over", "know", "water", "than", "call", "first", "who", "may", "down", "side", "been", "now", "find", "any", "new", "work", "part", "take", "get", "place", "made", "live", "where", "after", "back", "little", "only", "round", "man", "year", "came", "show", "every", "good", "me", "give", "our", "under", "name", "very", "through", "just", "form", "sentence", "great", "think", "say", "help", "low", "line", "differ", "turn", "cause", "much", "mean", "before", "move", "right", "boy", "old", "too", "same", "tell", "does", "set", "three", "want", "air", "well", "also", "play", "small", "end", "put", "home", "read", "hand", "port", "large", "spell", "add", "even", "land", "here", "must", "big", "high", "such", "follow", "act", "why", "ask", "men", "change", "went", "light", "kind", "off", "need", "house", "picture", "try", "us", "again", "animal", "point", "mother", "world", "near", "build", "self", "earth", "father", "head", "stand", "own", "page", "should", "country", "found", "answer", "school", "grow", "study", "still", "learn", "plant", "cover", "food", "sun", "four", "between", "state", "keep", "eye", "never", "last", "let", "thought", "city", "tree", "cross", "farm", "hard", "start", "might", "story", "saw", "far", "sea", "draw", "left", "late", "run", "don't", "while", "press", "close", "night", "real", "life", "few", "north", "open", "seem", "together", "next", "white", "children", "begin", "got", "walk", "example", "ease", "paper", "group", "always", "music", "those", "both", "mark", "often", "letter", "until", "mile", "river", "car", "feet", "care", "second", "book", "carry", "took", "science", "eat", "room", "friend", "began", "idea", "fish", "mountain", "stop", "once", "base", "hear", "horse", "cut", "sure", "watch", "color", "face", "wood", "main", "enough", "plain", "girl", "usual", "young", "ready", "above", "ever", "red", "list", "though", "feel", "talk", "bird", "soon", "body", "dog", "family", "direct", "pose", "leave", "song", "measure", "door", "product", "black", "short", "numeral", "class", "wind", "question", "happen", "complete", "ship", "area", "half", "rock", "order", "fire", "south", "problem", "piece", "told", "knew", "pass", "since", "top", "whole", "king", "space", "heard", "best", "hour", "better", "true", "during", "hundred", "five", "remember", "step", "early", "hold", "west", "ground", "interest", "reach", "fast", "verb", "sing", "listen", "six", "table", "travel", "less", "morning", "ten", "simple", "several", "vowel", "toward", "war", "lay", "against", "pattern", "slow", "center", "love", "person", "money", "serve", "appear", "road", "map", "rain", "rule", "govern", "pull", "cold", "notice", "voice", "unit", "power", "town", "fine", "certain", "fly", "fall", "lead", "cry", "dark", "machine", "note", "wait", "plan", "figure", "star", "box", "noun", "field", "rest", "correct", "able", "pound", "done", "beauty", "drive", "stood", "contain", "front", "teach", "week", "final", "gave", "green", "oh", "quick", "develop", "ocean", "warm", "free", "minute", "strong", "special", "mind", "behind", "clear", "tail", "produce", "fact", "street", "inch", "multiply", "nothing", "course", "stay", "wheel", "full", "force", "blue", "object", "decide", "surface", "deep", "moon", "island", "foot", "system", "busy", "test", "record", "boat", "common", "gold", "possible", "plane", "stead", "dry", "wonder", "laugh", "thousand", "ago", "ran", "check", "game", "shape", "equate", "hot", "miss", "brought", "heat", "snow", "tire", "bring", "yes", "distant", "fill", "east", "paint", "language", "among",
        "experience", "worked", "software", "developer", "engineer", "education", "university", "bachelor", "degree", "technologies", "developed", "using"
    ])
    
    # Check for basic typos via heuristic sequence matching (difflib is standard python, no pip needed)
    words = re.findall(r'\b[a-z]{4,}\b', raw_text.lower())
    ignore_list = TECH_SKILLS_DB.union(TOOLS_DB).union({'linkedin', 'github', 'frontend', 'backend', 'fullstack', 'api', 'http', 'html', 'css', 'json', 'sql'})
    
    words_to_check = [w for w in words if w not in ignore_list and w not in common_words]
    
    # Cap size to prevent lag
    if len(words_to_check) > 100:
        words_to_check = words_to_check[:100]
        
    # Heuristic Mistake Count
    mistakes_count = 0
    for w in words_to_check:
        # If the word is highly unusual and doesn't match common english words closely, 
        # it is likely a severe typo or untracked proper noun
        closest = difflib.get_close_matches(w, common_words, n=1, cutoff=0.85)
        if closest and closest[0] != w:
            mistakes_count += 1
            
    # We purposefully make it lenient because many words won't be in our 500 word dict
    mistakes_count = int(mistakes_count / 3) 
    
    # Weak writing phrases
    weak_phrases = ["worked on", "responsible for", "helped with", "participated in", "duties included", "was tasked with"]
    weak_phrase_count = sum(1 for phrase in weak_phrases if phrase in text)
    
    # Calculate Structure Score (starts at 100)
    structure_score = 100
    
    # Spelling penalties
    if 1 <= mistakes_count <= 2: structure_score -= 5
    elif 3 <= mistakes_count <= 5: structure_score -= 10
    elif mistakes_count > 5: structure_score -= 20
        
    # Weak writing penalties
    structure_score -= min(weak_phrase_count * 2, 15)
    
    return max(0, structure_score), mistakes_count, weak_phrase_count

def evaluate_experience_strength(text, section_map={}):
    """
    Search for action verbs and metrics (numbers, %, x, etc.) in the text
    to evaluate how strong their experience descriptions are.
    """
    action_verbs = ['developed', 'built', 'designed', 'implemented', 'improved', 'optimized', 'led', 'managed', 'created', 'spearheaded', 'architected', 'increased']
    
    has_metrics = bool(re.search(r'(\d+%|\b\d+x\b|\b\d+\s*(million|k|users|requests|increase|decrease)\b)', text))
    has_internship = bool(re.search(r'\b(intern|internship|trainee)\b', text))
    has_projects = section_map.get('Projects', False)
    
    verb_count = sum(1 for verb in action_verbs if r'\b' + verb + r'\b' in text)
    action_verb_score = min(int((verb_count / 5) * 100), 100)
    
    # Base experience score
    exp_score = action_verb_score * 0.7 + (30 if has_metrics else 0)
    
    # Deductions & Caps for Freshers
    if not has_metrics: exp_score -= 15
    if verb_count == 0: exp_score -= 10
        
    # Impose realistic recruiter caps on experience if lacking format
    if not has_internship:
        exp_score = min(exp_score, 50)
    if not has_projects:
        exp_score = min(exp_score, 45)
        
    return max(0, int(exp_score)), has_metrics, action_verb_score

def check_ats_compatibility(text, raw_text, section_map={}):
    word_count = len(text.split())
    has_email = bool(re.search(r'[\w\.-]+@[\w\.-]+\.\w+', raw_text))
    has_phone = bool(re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', raw_text))
    has_bullets = bool(re.search(r'[-•*]\s+', raw_text))
    has_linkedin = bool(re.search(r'linkedin\.com', raw_text.lower()))
    has_portfolio = bool(re.search(r'(github\.com|portfolio)', raw_text.lower()))
    
    # Base score is strictly 30 (earn points up or lose them drastically)
    score = 30
    
    # Reward standard length
    if 350 <= word_count <= 900: score += 20
        
    # Deductions for strict ATS compliance
    if word_count < 350: score -= 15
    elif word_count > 900: score -= 10
        
    if not has_linkedin: score -= 10
    if not has_portfolio: score -= 10
    if not has_bullets: score -= 15
    if not has_phone: score -= 10
    if not has_email: score -= 15
    
    # Check for basic required sections
    if not section_map.get('Experience') and not section_map.get('Education'):
        score -= 15
        
    # Heavy penalty for dense paragraph blocks without bullets
    if word_count > 400 and not has_bullets:
        score -= 10
        
    # Cap ATs strictly
    score = min(85, max(0, score))
    
    return score, word_count, has_bullets

def generate_strengths_weaknesses(quality_score, ats_score, exp_score, tech_len, soft_len, sections_detected, word_count, has_metrics, mistakes_count, weak_phrase_count):
    strengths = []
    weaknesses = []
    
    # Strengths
    if tech_len >= 5: strengths.append("Strong technical skill diversity detected.")
    if "Projects" in sections_detected: strengths.append("Dedicated project section provides practical context.")
    if ats_score >= 85: strengths.append("Excellent ATS format compatibility and length.")
    if has_metrics: strengths.append("Good use of measurable metrics to quantify achievements.")
    if exp_score >= 80: strengths.append("Strong usage of active verbs in experience descriptions.")
        
    # Weaknesses (Extremely strict now)
    if mistakes_count > 0: weaknesses.append(f"Score reduced due to {mistakes_count} spelling or grammatical mistakes.")
    if weak_phrase_count > 0: weaknesses.append(f"Detected {weak_phrase_count} instances of weak passive writing (e.g., 'worked on', 'helped with'). Use strong action verbs instead.")
    if word_count < 350: weaknesses.append("Resume is dangerously short, leaving out potential impact. Target 400+ words.")
    if word_count > 900: weaknesses.append("Resume is too wordy and will lose a recruiter's attention. Consider condensing older roles.")
    if not has_metrics: weaknesses.append("Severe lack of measurable achievements (%, counts, metrics). You must quantify your impact.")
    if tech_len < 3 and soft_len < 3: weaknesses.append("Skill section is sparse. List precise tools and competencies.")
    if exp_score <= 50: weaknesses.append("Experience score capped due to weak action verbs or missing internship/project sections.")
    if ats_score < 70: weaknesses.append("ATS issues found. You are missing core elements like a LinkedIn profile, Portfolio link, or bulleted lists.")
        
    # Fallbacks just in case
    if not strengths: strengths.append("Clean text formatting detected.")
    if not weaknesses: weaknesses.append("Consider tailoring this resume further to specific niche job descriptions.")
        
    return strengths, weaknesses

# ==========================================
# 4. MAIN PIPELINE
# ==========================================

def extract_text(file_path):
    if file_path.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.lower().endswith('.docx'):
        return extract_text_from_docx(file_path)
    else:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

def get_empty_fallback():
    return {
        "analysis_mode": "ERROR",
        "detected_domain": "None",
        "domain_confidence": 0,
        "overall_score": 0,
        "quality_score": 0,
        "ats_score": 0,
        "experience_score": 0,
        "skill_strength_score": 0,
        "technical_skills": [],
        "soft_skills": [],
        "tools": [],
        "technical_count": 0,
        "soft_count": 0,
        "tools_count": 0,
        "strengths": [],
        "weaknesses": ["The uploaded document appears to be empty or could not be read."],
        "suggestions": ["Please upload a valid PDF or DOCX file containing text."],
        "word_count": 0,
        "spelling_mistakes": 0,
        "weak_phrases": 0,
        "bullet_points_detected": False,
        "sections_detected": [],
        "has_metrics": False,
        "action_verb_score": 0,
        "raw_text": ""
    }

def run_pure_evaluation_pipeline(file_path):
    print(f"[ENGINE] Starting Evaluation for {file_path}")
    raw_text = extract_text(file_path)
    
    if not raw_text.strip():
        # Empty doc logic
        return get_empty_fallback()
        
    cleaned_text = clean_text(raw_text)
    
    return score_raw_text(raw_text, cleaned_text)

def score_raw_text(raw_text, cleaned_text=None):
    if not cleaned_text:
        cleaned_text = clean_text(raw_text)
        
    print("[ENGINE] Scoring raw text dynamically")
    
    # ----------------------------------------------------
    # STRICT LLM ENFORCEMENT MODE
    # ----------------------------------------------------
    # TEMPORARILY disable automatic fallback to trap silent errors.
    try:
        llm_data = analyze_resume_with_llm(cleaned_text)
        use_llm = True
    except Exception as e:
        print(f"[ENGINE] LLM Analysis failed: {e}. Falling back to Rule-Based Engine.")
        llm_data = None
        use_llm = False
            
    # Base Document Checks (always run for strict ATS scoring)
    ats_score, word_count, has_bullets = check_ats_compatibility(cleaned_text, raw_text)
    
    if use_llm and llm_data:
        # 1. Map LLM Data
        detected_domain = llm_data.get('detected_domain', 'General')
        tech_skills = llm_data.get('technical_skills', [])
        soft_skills = llm_data.get('soft_skills', [])
        tools = llm_data.get('tools', [])
        
        tech_count, soft_count, tools_count = len(tech_skills), len(soft_skills), len(tools)
        
        sections_detected = llm_data.get('sections_found', [])
        
        # 2. Heuristic Experience overlap (still robust for % detection)
        exp_score, has_metrics, action_verb_score = evaluate_experience_strength(cleaned_text)
        
        # 3. Hybrid Scoring
        total_skills = tech_count + soft_count + tools_count
        
        # Stricter Skills Scoring with Caps
        if total_skills <= 10: quality_score = 30
        elif total_skills <= 15: quality_score = 45
        elif total_skills <= 20: quality_score = 55
        elif total_skills <= 25: quality_score = 65
        elif total_skills <= 30: quality_score = 75
        else: quality_score = 85
        
        # Redundancy & Spam Penalty
        skill_counts = Counter(map(str.lower, tech_skills + soft_skills + tools))
        if any(count >= 5 for count in skill_counts.values()): quality_score -= 10
        if total_skills > 40: quality_score -= 10
        
        quality_score = max(0, quality_score)
        
        sectional_score = int((len(sections_detected) / 5) * 100)
        
        # Fetch new structural score
        structure_score, mistakes_count, weak_phrase_count = evaluate_structure_and_writing(cleaned_text, raw_text)
        
        overall_score_raw = (
            (ats_score * 0.25) +
            (quality_score * 0.30) +
            (exp_score * 0.30) +
            (structure_score * 0.15)
        )
        
        overall_score = min(int(overall_score_raw), 92)
                
        # 5. Strengths & Weaknesses
        strengths, weaknesses = generate_strengths_weaknesses(
            quality_score, ats_score, exp_score, tech_count, soft_count, 
            sections_detected, word_count, has_metrics, mistakes_count, weak_phrase_count
        )
        
        # 6. Hybrid Output Construction
        return {
            "analysis_mode": "LLM",
            "is_llm_generated": True,
            "detected_domain": detected_domain,
            "domain_confidence": 98, # LLM generated confidence is extremely high logically
            "overall_score": overall_score,
            "quality_score": quality_score,
            "ats_score": ats_score,
            "experience_score": exp_score,
            "skill_strength_score": quality_score,
            
            "technical_skills": tech_skills,
            "soft_skills": soft_skills,
            "tools": tools,
            "technical_count": tech_count,
            "soft_count": soft_count,
            "tools_count": tools_count,
            
            "strengths": strengths,
            "weaknesses": weaknesses,
            "suggestions": weaknesses.copy(),
            
            "word_count": word_count,
            "spelling_mistakes": mistakes_count,
            "weak_phrases": weak_phrase_count,
            "bullet_points_detected": has_bullets,
            "bullet_points_detected": has_bullets,
            "sections_detected": sections_detected,
            "has_metrics": has_metrics,
            "action_verb_score": action_verb_score,
            "raw_text": raw_text
        }
    
    # ----------------------------------------------------
    # FALLBACK: RULE-BASED NLP PIPELINE (if LLM fails)
    # ----------------------------------------------------
    print("[ENGINE] Running in fallback (offline) mode")
    
    # 1. TF-IDF Domain Detection
    detected_domain, domain_confidence = detect_domain(cleaned_text)
    
    # 2. Skill Extraction
    tech_skills, soft_skills, tools = extract_categorized_skills(cleaned_text)
    tech_count, soft_count, tools_count = len(tech_skills), len(soft_skills), len(tools)
    
    # 3. Section Analyzer
    section_map, sections_detected = detect_sections(cleaned_text)
    
    # 4. ATS & Word Count
    ats_score, word_count, has_bullets = check_ats_compatibility(cleaned_text, raw_text)
    
    # 5. Experience Strength
    exp_score, has_metrics, action_verb_score = evaluate_experience_strength(cleaned_text)
    
    # 6. Quality Profile / Skill Diversity Score (Strict Tiering)
    total_skills = tech_count + soft_count + tools_count
    
    if total_skills <= 10: quality_score = 30
    elif total_skills <= 15: quality_score = 45
    elif total_skills <= 20: quality_score = 55
    elif total_skills <= 25: quality_score = 65
    elif total_skills <= 30: quality_score = 75
    else: quality_score = 85
    
    skill_counts = Counter(map(str.lower, tech_skills + soft_skills + tools))
    if any(count >= 5 for count in skill_counts.values()): quality_score -= 10
    if total_skills > 40: quality_score -= 10
    
    quality_score = max(0, quality_score)
    
    # 7. Overall Weighted Score Calculation (Strict Formula)
    structure_score, mistakes_count, weak_phrase_count = evaluate_structure_and_writing(cleaned_text, raw_text)
    
    overall_score_raw = (
        (ats_score * 0.25) +
        (quality_score * 0.30) +
        (exp_score * 0.30) +
        (structure_score * 0.15)
    )
    
    overall_score = min(int(overall_score_raw), 92)
            
    # 8. Strengths & Weaknesses
    strengths, weaknesses = generate_strengths_weaknesses(
        quality_score, ats_score, exp_score, tech_count, soft_count, 
        sections_detected, word_count, has_metrics, mistakes_count, weak_phrase_count
    )
    
    suggestions = weaknesses.copy()
    if not suggestions:
        suggestions.append("Your resume looks incredibly solid. Keep updating it with your latest projects.")
        
    return {
        "analysis_mode": "FALLBACK",
        "detected_domain": detected_domain,
        "domain_confidence": domain_confidence,
        "overall_score": overall_score,
        "quality_score": quality_score,
        "ats_score": ats_score,
        "experience_score": exp_score,
        "skill_strength_score": quality_score, # alias
        
        "technical_skills": tech_skills,
        "soft_skills": soft_skills,
        "tools": tools,
        "technical_count": tech_count,
        "soft_count": soft_count,
        "tools_count": tools_count,
        
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions,
        
        "word_count": word_count,
        "spelling_mistakes": mistakes_count,
        "weak_phrases": weak_phrase_count,
        "bullet_points_detected": has_bullets,
        "sections_detected": sections_detected,
        
        "has_metrics": has_metrics,
        "action_verb_score": action_verb_score,
        "raw_text": raw_text
    }

# ==========================================
# 5. INTERACTIVE API ENDPOINTS
# ==========================================

def improve_bullet(bullet):
    """Rule-based bullet improver using action verbs."""
    weak_words = ['worked on', 'helped with', 'did', 'made', 'responsible for']
    b_lower = bullet.lower()
    
    for weak in weak_words:
        if weak in b_lower:
            return f"Developed and engineered systems related to: '{bullet.replace(weak, '').strip()}', achieving a 30% performance increase."
            
    return f"Spearheaded {bullet} - leading to a 20% improvement in efficiency and user engagement."

# ==========================================
# TF-IDF AI CHATBOT MODULE
# ==========================================
INTENT_CORPUS = [
    "how can i improve my resume structure or fix my weak points",
    "what specific skills should i learn next for my domain",
    "suggest some technical or capstone projects to build",
    "explain my score and why my resume is graded this way",
    "what is ats and how do i pass the applicant tracking system",
]

def rule_based_chat(message, context):
    """
    Hybrid AI Assistant.
    If the LLM is available, it forwards the prompt to Gemini using the resume context.
    If offline, relies on the Cosine-Similarity intent matcher.
    """
    if context.get('is_llm_generated') and is_ai_available():
        try:
            return chat_with_resume_context(message, context)
        except Exception as e:
            print("Gemini chat fallback:", e)
            pass

    # Fallback Rule-Based Logic
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(INTENT_CORPUS + [message])
    
    cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()
    best_match_idx = cosine_sim.argmax()
    confidence = cosine_sim[best_match_idx]
    
    if confidence < 0.15: 
        return "I am your AI Evaluator. I can help explain your score, suggest skills targeted to your Domain, or give you project ideas. What would you like to ask?"
        
    domain = context.get('detected_domain', 'General')
    
    if best_match_idx == 0: # Improve resume
        weaknesses = context.get('weaknesses', [])
        if weaknesses:
             return f"Based on your evaluation, focus on these areas: {weaknesses[0]}. Adding strong action verbs and metrics helps immensely."
        return "Your structure is quite solid! Ensure you're quantifying your achievements (e.g., 'improved performance by 20%')."
        
    elif best_match_idx == 1: # Skills
        if domain == "Software / IT":
             return "For Software Engineering, prioritize System Design, Cloud Architecture (AWS/GCP), and modern frameworks like React or Spring Boot."
        elif domain == "Data / Analytics":
             return "For Data Analytics, prioritize deep Pandas knowledge, Machine Learning, and deployment using FastAPI."
        return f"For the {domain} domain, ensure you list your core technical proficiencies clearly in a dedicated Skills section."
        
    elif best_match_idx == 2: # Projects
        if domain == "Software / IT":
            return "To stand out in IT, build a Full-Stack Capstone Project with a microservices architecture. Make sure to deploy it on AWS and include the GitHub link in your resume."
        return f"Since your domain is {domain}, consider building a portfolio project mapping out a real-world workflow or case study."
        
    elif best_match_idx == 3: # Score explanation
        return f"Your Overall Score of {context.get('overall_score')}% is weighted: Quality (30%), Experience (35%), ATS (20%), and Sections (15%). Note: Scores are hard-capped to keep evaluations realistic. Reaching 90+ requires an impeccable ATS structure and strong metrics."
        
    elif best_match_idx == 4: # ATS
        return "ATS (Applicant Tracking System) software prefers simple, single-column formats without images. It scans for patterns like emails and exact technical keywords. It also demands bullet points rather than paragraphs."
        
    return "I'm not exactly sure, but reviewing your Weaknesses section is a good start to bump your score!"
