import os
from flask import Flask, request, jsonify, Response, send_from_directory
from dotenv import load_dotenv


# --- Import Core Utility Modules ---
from scraper import scrape_job_url
from pdf_parser import extract_text_from_pdf_stream

# --- Import Phase 2 Modules ---
from models import db, User, Resume, Transaction
from ai_engine import generate_tailored_resume
from stream import stream_optimization_process

load_dotenv()

app = Flask(__name__, static_folder='out', static_url_path='')

# --- App & Database Configuration ---
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-dev-key')
# Uses Render/Neon PostgreSQL URL if provided; falls back to local SQLite for quick testing
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///cvforge.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with app
db.init_app(app)

# Automatically create all SQL tables (users, resumes, transactions) on server start
with app.app_context():
    db.create_all()


@app.route('/api/parse', methods=['POST'])
def parse_inputs():
    """Extracts raw text from uploaded resume PDF and/or job URL."""
    job_url = request.form.get('job_url', '')
    pdf_file = request.files.get('file')

    job_text = scrape_job_url(job_url) if job_url else ""
    cv_text = ""
    
    if pdf_file and pdf_file.filename.endswith('.pdf'):
        cv_text = extract_text_from_pdf_stream(pdf_file.read())

    if not cv_text and not job_text:
        return jsonify({'error': 'Please provide a valid CV PDF or Job URL'}), 400

    return jsonify({
        'status': 'success',
        'cv_text': cv_text,
        'job_text': job_text
    })

@app.route('/api/optimize/stream', methods=['GET'])
def optimize_stream():
    """SSE Endpoint for live UI progress updates."""
    return stream_optimization_process("", "")

@app.route('/api/optimize', methods=['POST'])
def run_optimization():
    """Triggers GPT-4o-mini optimization and saves the result."""
    data = request.get_json() or {}
    cv_text = data.get('cv_text', '')
    job_text = data.get('job_text', '')

    if not cv_text or not job_text:
        return jsonify({'error': 'Missing cv_text or job_text'}), 400

    # Call AI Engine to optimize resume
    result = generate_tailored_resume(cv_text, job_text)
    
    # If the engine returned an error dictionary
    if "error" in result:
        return jsonify({'status': 'error', 'message': result['error']}), 500

    return jsonify({
        'status': 'success',
        'data': result
    })

# --- Static File Serving Routes ---

@app.route('/')
def serve_index():
    return send_from_directory('out', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join('out', path)):
        return send_from_directory('out', path)
    return send_from_directory('out', 'index.html')

if __name__ == '__main__':
    # Render assigns dynamic ports via the PORT environment variable
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

