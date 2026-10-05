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
        "linkedin": {"type": "STRING"},
        "availability": {"type": "STRING"},
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
                },
                "required": ["category", "items"]
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
                    "summary_line": {"type": "STRING"},
                    "bullets": {"type": "ARRAY", "items": {"type": "STRING"}}
                },
                "required": ["role", "company", "dates", "bullets"]
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
                },
                "required": ["degree", "institution"]
            }
        },
        "languages": {"type": "ARRAY", "items": {"type": "STRING"}},
        "interests": {"type": "ARRAY", "items": {"type": "STRING"}}
    },
    "required": ["candidate_name", "target_title", "summary", "experiences", "skills", "education"]
}

def optimize_resume_data(cv_text: str, job_text: str, tone: str = "Professional") -> dict:
    """Generates structured ATS-optimized multi-page resume JSON strictly matching target job post."""
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": RESUME_SCHEMA,
            "temperature": 0.2
        }
    )

    prompt = f"""
    You are an elite ATS Resume Optimizer and AI Executive Coach.
    Transform the candidate's raw CV text to align with the provided Target Job Description.
    Tone target: {tone}.

    Candidate CV:
    {cv_text}

    Target Job Description:
    {job_text}

    Optimization Instructions:
    1. Header & Contact: Extract candidate_name, target_title (e.g. "Digital Marketing Specialist (5+ yrs exp)"), phone, email, location, linkedin URL, and availability if present.
    2. Professional Summary: Write a compelling 3-4 sentence paragraph highlighting core value proposition, key tech stack, and direct keyword alignment with the job position.
    3. Categorized Skills: Break skills down into distinct categories such as "Digital Marketing / Core Skills", "Tools & Analytics", and "Soft Skills".
    4. Work Experience:
       - Ensure job bullet points begin with strong action verbs (e.g. Led, Developed, Managed, Increased, Optimized).
       - Seamlessly integrate primary technical and domain keywords from the target job description.
       - Quantify accomplishments wherever possible with realistic percentages, budgets, or metrics.
       - Include a brief scope summary line per position describing overall responsibility.
    5. Cleanup: Omit irrelevant text, filler content, or corrupted characters.
    6. Match Scores: Provide exact integer estimates for match_score_before and match_score_after based on job requirement overlap.
    """

    response = model.generate_content(prompt)
    return json.loads(response.text)
