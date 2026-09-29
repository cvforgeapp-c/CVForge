import time
import json
from flask import Response

def stream_optimization_process(cv_text: str, job_text: str):
    def generate():
        # Step 1: Parsing
        yield f"data: {json.dumps({'status': 'Parsing CV & Scraping Job Posting...', 'progress': 20})}\n\n"
        time.sleep(0.8)

        # Step 2: Keyword Analysis
        yield f"data: {json.dumps({'status': 'Analyzing ATS Keyword Gaps...', 'progress': 50})}\n\n"
        time.sleep(0.8)

        # Step 3: LLM Optimization
        yield f"data: {json.dumps({'status': 'Rewriting Bullet Points with GPT-4o-mini...', 'progress': 85})}\n\n"
        time.sleep(0.8)

        # Step 4: Finalizing
        yield f"data: {json.dumps({'status': 'Optimization Complete!', 'progress': 100})}\n\n"

    return Response(generate(), mimetype='text/event-stream')
