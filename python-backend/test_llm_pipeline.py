import engine

weak_resume = "I worked at a company. I did something there. Programming is fun. " * 30
medium_resume = "Java Developer with 3 years experience. Worked on Spring Boot backend and React frontend. Good communication skills. " * 15
strong_resume = """
John Doe | johndoe@email.com | (555) 123-4567

Senior Full Stack Engineer
- Spearheaded the migration of the core monolithic architecture to AWS microservices, achieving a 45% increase in load capacity and reducing downtime.
- Engineered 15+ REST APIs using Python FastAPI and Node.js.
- Deployed highly scalable solutions leveraging Docker and Kubernetes (K8s).
- Increased sales retention by 20% through targeted data analytics via Pandas and SQL.
- Mentored a team of 4 junior developers in Agile methodologies.
Education: Bachelors in Computer Science
Skills: Python, Java, AWS, Docker, Kubernetes, SQL, Pandas, React
Projects: Built an incredible AI platform using Javascript and Machine Learning.
""" + ("We love computing and system architecture heavily. " * 50)

def test_resume_realism(name, text, min_score, max_score):
    print(f"\n--- Testing {name} ---")
    
    # We will simulate the raw extracted text as arriving
    try:
        cleaned_text = engine.clean_text(text)
        
        # Check rule fallback pipeline
        ats_score, word_count, has_bullets = engine.check_ats_compatibility(cleaned_text, text)
        tech_skills, soft_skills, tools = engine.extract_categorized_skills(cleaned_text)
        exp_score, has_metrics, action_verb_score = engine.evaluate_experience_strength(cleaned_text)
        section_map, sections_detected = engine.detect_sections(cleaned_text)
        
        quality_score = min(int(((len(tech_skills) + len(soft_skills) + len(tools)) / 15) * 100), 100)
        sectional_score = int((len(sections_detected) / 5) * 100)
        
        overall_score = int((quality_score * 0.3) + (exp_score * 0.35) + (ats_score * 0.20) + (sectional_score * 0.15))
        
        if word_count < 250: overall_score = min(overall_score, 70)
        elif not section_map.get('Experience'): overall_score = min(overall_score, 80)
        
        if overall_score > 90:
            if ats_score < 90 or len(sections_detected) < 4: overall_score = 90
            else: overall_score = min(overall_score, 92)
            
        print(f"Fallback Calculated Score: {overall_score}")
        
        if min_score <= overall_score <= max_score:
            print("✅ Score Realism Check Passed")
        else:
            print(f"❌ Score Realism Check Failed: Expected {min_score}-{max_score}, got {overall_score}")
            
    except Exception as e:
        print("Error during test:", e)

if __name__ == "__main__":
    print("RUNNING AUTOMATED REALISM TEST SCRIPT")
    test_resume_realism("Weak Resume", weak_resume, 40, 60)
    test_resume_realism("Medium Resume", medium_resume, 60, 78)
    test_resume_realism("Strong Resume", strong_resume, 78, 92)
