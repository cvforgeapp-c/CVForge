import os
import json
import google.generativeai as genai
from flask import Blueprint, request, jsonify
from utils.auth_middleware import token_required
from services.scraper import scrape_job_posting

cover_letter_bp = Blueprint('cover_letter', __name__)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@cover_letter_bp.route('/api/cover-letter', methods=['POST'])
@token_required
def generate_cover_letter(current_user_id):
    """Drafts a tailored cover letter based on user CV and target job posting URL."""
    data = request.get_json() or {}
    cv_text = data.get('cv_text', '')
    job_url = data.get('job_url', '')

    if not cv_text or not job_url:
        return jsonify({'error': 'cv_text and job_url are required.'}), 400

    try:
        # Scrape job details
        job_data = scrape_job_posting(job_url)

        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
        You are a professional executive career coach.
        Write a compelling, ATS-friendly cover letter pairing the candidate's achievements with the target job requirements.

        Candidate CV Text:
        {cv_text}

        Target Job Description ({job_data.get('title')}):
        {job_data.get('description')}

        Format the output with clear opening hook, 2 impact paragraphs, and a professional closing statement.
        """

        response = model.generate_content(prompt)

        return jsonify({
            'message': 'Cover letter generated successfully!',
            'company_role': job_data.get('title'),
            'cover_letter': response.text
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to generate cover letter: {str(e)}'}), 500
