import os
import tempfile
from flask import Blueprint, request, jsonify, send_file
from utils.auth_middleware import token_required
from services.pdf_parser import parse_resume_stream
from services.scraper_service import scrape_job_posting
from services.ai_service import optimize_resume_data
from services.pdf_engine import generate_ats_pdf

optimize_bp = Blueprint('optimize', __name__)

@optimize_bp.route('/parse', methods=['POST'])
def parse_cv():
    """Parses raw text from an uploaded resume file (PDF/DOCX)."""
    if 'file' not in request.files:
        return jsonify({'error': 'No resume file uploaded.'}), 400

    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return jsonify({'error': 'Empty filename.'}), 400

    try:
        parsed_data = parse_resume_stream(uploaded_file.stream, uploaded_file.filename)
        return jsonify({
            'message': 'File parsed successfully',
            'data': parsed_data
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to parse file: {str(e)}'}), 500


@optimize_bp.route('/optimize', methods=['POST'])
@token_required
def optimize_cv(current_user_id):
    """
    Accepts uploaded CV text along with either a target job URL or direct job description text.
    Runs Gemini AI ATS tailoring and generates the multi-page PDF output.
    """
    data = request.get_json() or {}
    cv_text = data.get('cv_text', '')
    job_url = data.get('job_url', '')
    job_text_input = data.get('job_text', '')
    tone = data.get('tone', 'Professional')

    if not cv_text:
        return jsonify({'error': 'Candidate CV text is required.'}), 400

    if not job_url and not job_text_input:
        return jsonify({'error': 'Either job_url or direct job_text is required.'}), 400

    try:
        # 1. Obtain Target Job Description
        target_job_description = ""
        job_title = "Target Position"

        if job_url:
            job_data = scrape_job_posting(job_url)
            target_job_description = job_data.get('description', '')
            job_title = job_data.get('title', job_title)
        else:
            target_job_description = job_text_input

        if not target_job_description.strip():
            return jsonify({'error': 'Failed to extract job description.'}), 400

        # 2. Run Gemini AI optimization with structured JSON schema matching reference layout
        optimized_json = optimize_resume_data(
            cv_text=cv_text, 
            job_text=target_job_description, 
            tone=tone
        )

        # 3. Generate ATS-optimized multi-page PDF in temp directory
        temp_dir = tempfile.gettempdir()
        pdf_path = os.path.join(temp_dir, f"cvforge_{current_user_id}.pdf")
        
        # Free preview receives watermark; premium accounts receive unwatermarked PDF
        watermark = data.get('watermark', True)
        generate_ats_pdf(optimized_json, pdf_path, watermarked=watermark)

        return jsonify({
            'message': 'Resume optimized successfully!',
            'job_title': optimized_json.get('target_title', job_title),
            'match_score_before': optimized_json.get('match_score_before'),
            'match_score_after': optimized_json.get('match_score_after'),
            'optimized_data': optimized_json,
            'pdf_path': pdf_path
        }), 200

    except Exception as e:
        return jsonify({'error': f'Optimization engine failed: {str(e)}'}), 500


@optimize_bp.route('/download/<user_id>', methods=['GET'])
def download_pdf(user_id):
    """Downloads the generated PDF file."""
    temp_dir = tempfile.gettempdir()
    pdf_path = os.path.join(temp_dir, f"cvforge_{user_id}.pdf")

    if not os.path.exists(pdf_path):
        return jsonify({'error': 'Generated PDF not found or expired.'}), 404

    return send_file(
        pdf_path,
        as_attachment=True,
        download_name="Tailored_ATS_Resume.pdf",
        mimetype="application/pdf"
    )
