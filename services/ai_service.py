import json
import os
import google.generativeai as genai

# Initialize Gemini Client
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

RESUME_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "candidate_name": {"type": "STRING"},
        "target_title": {"type": "STRING"},
        "email": {"type": "STRING"},
        "phone": {"type": "STRING"},
        "location": {"type": "STRING"},
        "summary": {"type": "STRING"},
        "match_score_before": {"type": "INTEGER"},
        "match_score_after": {"type": "INTEGER"},
        "skills": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "category": {"type": "STRING"},
                    "items": {"type": "ARRAY", "items": {"type": "STRING"}}
                }
            }
        },
        "experiences": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "role": {"type": "STRING"},
                    "company": {"type": "STRING"},
                    "dates": {"type": "STRING"},
                    "bullets": {"type": "ARRAY", "items": {"type": "STRING"}}
                }
            }
        },
        "education": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "degree": {"type": "STRING"},
                    "institution": {"type": "STRING"},
                    "year": {"type": "STRING"}
                }
            }
        }
    },
    "required": ["candidate_name", "target_title", "summary", "experiences", "skills"]
}

def optimize_resume_data(cv_text: str, job_text: str, tone: str = "Professional") -> dict:
    """Generates structured ATS-optimized resume JSON."""
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": RESUME_SCHEMA,
            "temperature": 0.2
        }
    )

    prompt = f"""
    You are an expert ATS Resume Optimizer.
    Tailor the candidate's CV text to match the target job description requirements.
    Tone: {tone}.

    Candidate CV:
    {cv_text}

    Target Job Description:
    {job_text}

    Instructions:
    1. Extract contact metadata correctly.
    2. Rewrite experience bullet points using high-impact action verbs and quantified achievements matching job keywords.
    3. Eliminate any gibberish or unformatted placeholder text.
    4. Calculate genuine ATS match percentage scores before and after optimization.
    """

    response = model.generate_content(prompt)
    return json.loads(response.text)
