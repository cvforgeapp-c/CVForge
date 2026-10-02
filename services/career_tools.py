import os
import json
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_interview_prep(cv_text: str, job_text: str) -> dict:
    """
    Generates role-specific behavioral and technical interview questions with STAR answers.
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = f"""
    You are an expert interview coach. Based on the candidate's CV and target job description, generate 3 interview prep items.
    Return JSON format with structure:
    {{
      "questions": [
        {{
          "category": "Behavioral or Technical",
          "question": "Question text here",
          "star_guide": "Situation, Task, Action, Result coaching tailored to candidate experience"
        }}
      ]
    }}

    Candidate CV: {cv_text[:2000]}
    Job Description: {job_text[:2000]}
    """

    try:
        response = model.generate_content(prompt)
        # Clean JSON markdown quotes if returned
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)
    except Exception as e:
        return {"error": f"Failed to generate interview questions: {str(e)}"}


def generate_linkedin_bio(cv_text: str) -> str:
    """
    Generates an engaging, optimized LinkedIn 'About' section bio.
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"Convert this CV summary into a catchy, professional LinkedIn 'About' bio in first person:\n\n{cv_text[:3000]}"
    response = model.generate_content(prompt)
    return response.text.strip()
