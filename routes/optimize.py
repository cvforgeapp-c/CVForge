import os
import tempfile
from flask import Blueprint, request, jsonify, send_file
from utils.auth_middleware import token_required
from services.pdf_parser import parse_resume_stream
from services.scraper import scrape_job_posting
from services.ai_engine import optimize_resume_data
from services.pdf_engine import generate_ats_pdf

optimize_bp = Blueprint('optimize', __name__)

@optimize_bp.route('/api/parse', methods=['POST'])
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


@optimize_bp.route('/api/optimize', methods=['POST'])
@token_required
def optimize_cv(current_user_id):
    """Scrapes target job, runs Gemini AI tailoring, and generates the ATS PDF."""
    data = request.get_json() or {}
    cv_text = data.get('cv_text', '')
    job_url = data.get('job_url', '')
    tone = data.get('tone', 'Professional')

    if not cv_text or not job_url:
        return jsonify({'error': 'Both cv_text and job_url are required.'}), 400

    try:
        # 1. Scrape target job posting
        job_data = scrape_job_posting(job_url)

        # 2. Run Gemini AI optimization with structured JSON schema
        optimized_json = optimize_resume_data(cv_text, job_data.get('description', ''), tone=tone)

        # 3. Generate PDF file in a temporary path
        temp_dir = tempfile.gettempdir()
        pdf_path = os.path.join(temp_dir, f"cvforge_{current_user_id}.pdf")
        
        # Free preview gets watermark, premium accounts generate clean PDF
        watermark = data.get('watermark', True)
        generate_ats_pdf(optimized_json, pdf_path, watermarked=watermark)

        return jsonify({
            'message': 'Resume optimized successfully!',
            'job_title': job_data.get('title'),
            'optimized_data': optimized_json,
            'pdf_path': pdf_path
        }), 200

    except Exception as e:
        return jsonify({'error': f'Optimization engine failed: {str(e)}'}), 500


@optimize_bp.route('/api/download/<user_id>', methods=['GET'])
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
