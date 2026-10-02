import json
import time
from flask import Blueprint, Response, stream_with_context

stream_bp = Blueprint('stream', __name__)

@stream_bp.route('/api/stream/optimize', methods=['GET'])
def stream_optimization():
    """Streams live step progress events to Next.js EventSource."""
    def event_generator():
        steps = [
            {"step": 1, "message": "Reading your resume..."},
            {"step": 2, "message": "Scraping target job posting..."},
            {"step": 3, "message": "Detecting ATS keywords and skill gaps..."},
            {"step": 4, "message": "Rewriting experiences with Gemini AI..."},
            {"step": 5, "message": "Generating ATS-compliant PyMuPDF file..."},
            {"step": 6, "message": "Complete!"}
        ]

        for s in steps:
            time.sleep(1.0)  # Simulates real async worker progress
            yield f"data: {json.dumps(s)}\n\n"

    return Response(stream_with_context(event_generator()), mimetype="text/event-stream")
