import os
from openai import OpenAI
from pydantic import BaseModel, Field

class BulletPoint(BaseModel):
    original: str
    optimized: str
    impact_metric: str

class ResumeOptimizationResponse(BaseModel):
    match_score: int = Field(description="ATS match score from 0 to 100")
    missing_keywords: list[str]
    strengths: list[str]
    optimized_bullets: list[BulletPoint]

def generate_tailored_resume(cv_text: str, job_text: str) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[AI Engine Error]: OPENAI_API_KEY environment variable is not set.")
        return {"error": "OpenAI API key missing from server environment."}

    client = OpenAI(api_key=api_key)

    prompt = f"""
    You are an expert ATS Resume Optimizer.
    Analyze the candidate's CV against the target Job Description.
    Extract missing keywords, compute a match score (0-100), and rewrite bullet points 
    using strong active verbs and quantifiable metrics.

    CV TEXT:
    {cv_text[:3000]}

    JOB DESCRIPTION:
    {job_text[:3000]}
    """

    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional ATS resume strategist."},
                {"role": "user", "content": prompt}
            ],
            response_format=ResumeOptimizationResponse,
            temperature=0.3
        )
        return response.choices[0].message.parsed.model_dump()
    except Exception as e:
        print(f"[AI Engine Error]: {str(e)}")
        return {}
