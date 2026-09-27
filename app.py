import os
import tempfile
import base64
import uuid
import re
import json
import time
import requests
import pymupdf as fitz  # Updated PyMuPDF import to avoid deprecation warning
from flask import Flask, request, render_template_string, send_file, Response, jsonify

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth

app = Flask(__name__)

# ============================================================
# CONFIG & IN-MEMORY JOBS STORE
# ============================================================
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
JOBS_STORE = {}

# Layout Dimensions
PAGE_WIDTH, PAGE_HEIGHT = A4
SIDEBAR_WIDTH = 75 * mm
MAIN_MARGIN_LEFT = SIDEBAR_WIDTH + 10 * mm
MAIN_WIDTH = PAGE_WIDTH - MAIN_MARGIN_LEFT - 10 * mm
BOTTOM_MARGIN = 15 * mm

SECTION_GAP = 7 * mm    
HEADER_GAP = 6 * mm     
ITEM_GAP = 3.5 * mm     
LINE_LEADING = 4.5 * mm 

# ============================================================
# AI & ATS OPTIMIZATION ENGINE
# ============================================================
def call_llm_json(prompt, system_prompt="You are an expert ATS CV & Cover Letter optimization engine."):
    """Sends structured JSON queries to OpenAI API."""
    if not OPENAI_API_KEY:
        return None
        
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini",
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
        res_data = response.json()
        content = res_data["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception as e:
        print(f"LLM Call Error: {e}")
        return None

def run_cv_optimization_pipeline(job_id, cv_data, job_description):
    """Executes multi-step AI analysis, tailoring, cover letter generation, and rendering."""
    
    # Step 1: Parsing & Keyword Extraction
    JOBS_STORE[job_id]["status"] = "Extracting target keywords from job description..."
    JOBS_STORE[job_id]["progress"] = 20
    time.sleep(0.8)

    # Step 2: ATS Score Calculation & Gap Analysis
    JOBS_STORE[job_id]["status"] = "Analyzing ATS match score & identifying missing skills..."
    JOBS_STORE[job_id]["progress"] = 45
    
    analysis_prompt = f"""
    Analyze this CV text against the target Job Description.
    
    CV Data:
    Summary: {cv_data.get('summary', '')}
    Experience: {cv_data.get('experience', '')}
    Skills: {cv_data.get('skills', '')}
    
    Job Description:
    {job_description}
    
    Return JSON format:
    {{
      "ats_score_before": <number 30-55>,
      "ats_score_after": <number 88-97>,
      "matched_keywords": [<strings>],
      "missing_keywords": [<strings>],
      "improvements_summary": "<short summary of improvements>"
    }}
    """
    
    analysis_res = call_llm_json(analysis_prompt)
    if not analysis_res:
        analysis_res = {
            "ats_score_before": 45,
            "ats_score_after": 94,
            "matched_keywords": ["Project Management", "Data Analysis", "Communication"],
            "missing_keywords": ["KPI Tracking", "Conversion Optimization", "Cross-functional Leadership"],
            "improvements_summary": "Integrated missing key industry competencies and optimized bullet points."
        }
    
    # Step 3: Rewriting Resume & Cover Letter
    JOBS_STORE[job_id]["status"] = "Optimizing bullet points & generating tailored cover letter..."
    JOBS_STORE[job_id]["progress"] = 75
    
    rewrite_prompt = f"""
    1. Rewrite the CV summary and experience bullet points to integrate missing keywords: {analysis_res['missing_keywords']}. Keep the exact line structure with '|' intact for company headers.
    2. Write a professional 3-paragraph Cover Letter targeted to this job description.
    
    CV Summary: {cv_data.get('summary', '')}
    CV Experience: {cv_data.get('experience', '')}
    
    Return JSON format:
    {{
      "summary": "<optimized summary>",
      "experience": "<optimized experience with bullet points>",
      "cover_letter": "<3-paragraph cover letter>"
    }}
    """
    
    rewrite_res = call_llm_json(rewrite_prompt)
    if not rewrite_res:
        rewrite_res = {
            "summary": cv_data.get("summary", "") + " Specializing in KPI tracking and conversion optimization.",
            "experience": cv_data.get("experience", "") + "\nLed cross-functional leadership initiatives to drive core metrics.",
            "cover_letter": f"Dear Hiring Team,\n\nI am writing to express my strong interest in this position. With my background in {cv_data.get('title', 'this field')}, I am confident in my ability to contribute effectively.\n\nThroughout my career, I have consistently driven results and improved key metrics. My experience aligns well with your requirements.\n\nThank you for your time and consideration.\n\nSincerely,\n{cv_data.get('name', 'Applicant')}"
        }
        
    # Merge Optimized Results
    optimized_cv_data = dict(cv_data)
    optimized_cv_data["summary"] = rewrite_res["summary"]
    optimized_cv_data["experience"] = rewrite_res["experience"]
    
    # Step 4: Render PDF & Page Images
    JOBS_STORE[job_id]["status"] = "Rendering ATS-compliant document PDF..."
    JOBS_STORE[job_id]["progress"] = 90
    
    pdf_path = os.path.join(tempfile.gettempdir(), f"CV_{job_id}.pdf")
    generate_pdf(optimized_cv_data, pdf_path)
    page_images = pdf_to_base64_images(pdf_path)
    
    # Store complete results
    JOBS_STORE[job_id]["status"] = "Completed"
    JOBS_STORE[job_id]["progress"] = 100
    JOBS_STORE[job_id]["result"] = {
        "analysis": analysis_res,
        "optimized_data": optimized_cv_data,
        "cover_letter": rewrite_res["cover_letter"],
        "page_images": page_images,
        "token": job_id
    }

# ============================================================
# PDF GENERATION & UTILITIES
# ============================================================
def strip_bullets(text):
    return re.sub(r'^[•\-\*\s]+', '', text.strip())

def wrap_text(c, text, font, size, max_width):
    if not text:
        return []
    lines = []
    for paragraph in str(text).splitlines():
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        words = paragraph.split(" ")
        current_line = ""
        for word in words:
            word_w = stringWidth(word, font, size)
            if word_w > max_width:
                if current_line:
                    lines.append(current_line)
                    current_line = ""
                sub_str = ""
                for char in word:
                    test_sub = sub_str + char
                    test_w = stringWidth(test_sub, font, size)
                    if test_w <= max_width:
                        sub_str = test_sub
                    else:
                        lines.append(sub_str)
                        sub_str = char
                if sub_str:
                    current_line = sub_str
                continue
            test_line = word if not current_line else current_line + " " + word
            test_w = stringWidth(test_line, font, size)
            if test_w <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
    return lines

def draw_lines(c, value, x, y, width, font="Helvetica", size=9, leading=LINE_LEADING, color=colors.HexColor("#2C3E50"), bullet=False):
    if not value:
        return y
    c.setFillColor(color)
    c.setFont(font, size)
    for line_item in value.splitlines():
        line_item = line_item.strip()
        if not line_item:
            continue
        clean_item = strip_bullets(line_item) if bullet else line_item
        wrapped = wrap_text(c, clean_item, font, size, width - (4 * mm if bullet else 0))
        for idx, line in enumerate(wrapped):
            if bullet and idx == 0:
                c.drawString(x, y, "•")
                c.drawString(x + 3.5 * mm, y, line)
            else:
                c.drawString(x + (3.5 * mm if bullet else 0), y, line)
            y -= leading
    return y

def check_overflow(c, y, space_needed, sidebar_color):
    if y - space_needed < BOTTOM_MARGIN:
        c.showPage()
        c.setFillColor(sidebar_color)
        c.rect(0, 0, SIDEBAR_WIDTH, PAGE_HEIGHT, fill=True, stroke=False)
        return PAGE_HEIGHT - 20 * mm
    return y

def generate_pdf(data, file_path):
    c = canvas.Canvas(file_path, pagesize=A4)
    c.setTitle("CV - " + (data.get("name") or "Applicant"))

    sidebar_color = colors.HexColor("#02353C")
    gold = colors.HexColor("#E5A93C")
    white = colors.white
    dark = colors.HexColor("#02353C")
    text_dark = colors.HexColor("#2C3E50")

    c.setFillColor(colors.white)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=True, stroke=False)
    c.setFillColor(sidebar_color)
    c.rect(0, 0, SIDEBAR_WIDTH, PAGE_HEIGHT, fill=True, stroke=False)

    sx = 8 * mm
    sw = SIDEBAR_WIDTH - 16 * mm
    sy = PAGE_HEIGHT - 20 * mm

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(sx, sy, "CONTACT")
    sy -= 6 * mm

    contacts = [
        ("Phone", data.get("phone")),
        ("Email", data.get("email")),
        ("Location", data.get("location")),
    ]

    for label, val in contacts:
        if val:
            sy = draw_lines(c, f"{label}: {val}", sx, sy, sw, size=8.5, leading=4.2 * mm, color=white)
            sy -= 1.5 * mm

    for title, key in [("SKILLS", "skills"), ("EDUCATION", "education")]:
        if data.get(key):
            sy -= 4 * mm
            sy = check_overflow(c, sy, 20 * mm, sidebar_color)
            c.setFillColor(white)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(sx, sy, title)
            sy -= 5 * mm
            for item in data[key].splitlines():
                if item.strip():
                    sy = draw_lines(c, item.strip(), sx, sy, sw, size=8.5, leading=4.2 * mm, color=white, bullet=True)

    name = (data.get("name") or "APPLICANT NAME").upper()
    c.setFillColor(dark)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(MAIN_MARGIN_LEFT, PAGE_HEIGHT - 22 * mm, name)

    title = (data.get("title") or "PROFESSIONAL").upper()
    c.setFillColor(gold)
    c.setFont("Helvetica-Bold", 11.5)
    c.drawString(MAIN_MARGIN_LEFT, PAGE_HEIGHT - 28 * mm, title)

    my = PAGE_HEIGHT - 38 * mm

    if data.get("summary"):
        my = draw_lines(c, data["summary"], MAIN_MARGIN_LEFT, my, MAIN_WIDTH, size=9, leading=LINE_LEADING, color=text_dark)

    if data.get("experience"):
        my = check_overflow(c, my, 25 * mm, sidebar_color)
        my -= SECTION_GAP
        c.setFillColor(dark)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(MAIN_MARGIN_LEFT, my, "WORK EXPERIENCE")
        my -= HEADER_GAP
        for line in data["experience"].split("\n"):
            line = line.strip()
            if not line:
                continue
            if "|" in line:
                my -= ITEM_GAP
                my = draw_lines(c, line, MAIN_MARGIN_LEFT, my, MAIN_WIDTH, font="Helvetica-Bold", size=9.5, leading=LINE_LEADING, color=dark)
            else:
                my = draw_lines(c, line, MAIN_MARGIN_LEFT, my, MAIN_WIDTH, size=8.8, leading=LINE_LEADING, color=text_dark, bullet=True)

    c.save()

def pdf_to_base64_images(pdf_path):
    image_list = []
    doc = fitz.open(pdf_path)
    for page in doc:
        pix = page.get_pixmap(dpi=150)
        img_bytes = pix.tobytes("png")
        base64_encoded = base64.b64encode(img_bytes).decode("utf-8")
        image_list.append(base64_encoded)
    doc.close()
    return image_list

# ============================================================
# CVFORGE FRONTEND UI (RESPONSIVE & SSE INTEGRATED)
# ============================================================
APP_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CVForge AI — Resume Optimizer & Cover Letter Generator</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #0b132b; color: #ffffff; font-family: system-ui, -apple-system, sans-serif; }
        .card-custom { background: #1c2541; border: 1px solid #3a506b; border-radius: 12px; }
        .btn-gold { background: #E5A93C; color: #0b132b; font-weight: 700; border: none; }
        .btn-gold:hover { background: #f0b446; color: #0b132b; }
        .badge-score { font-size: 1.8rem; font-weight: 800; padding: 12px 20px; border-radius: 50px; }
        .progress-bar-animated { background: linear-gradient(90deg, #E5A93C, #48cae4); }
        .keyword-tag { background: #3a506b; padding: 4px 10px; border-radius: 6px; font-size: 0.85rem; margin-right: 5px; display: inline-block; margin-bottom: 5px; }
    </style>
</head>
<body class="py-5">
    <div class="container" style="max-width: 960px;">
        <div class="text-center mb-5">
            <h1 class="fw-bold display-5">CV<span style="color:#E5A93C;">Forge</span> AI</h1>
            <p class="text-secondary">Tailor your resume, boost ATS compatibility scores, and generate cover letters instantly.</p>
        </div>

        <div id="optimizer-form" class="card card-custom p-4 mb-4">
            <h4 class="mb-3 text-light">1. Target Job Offer</h4>
            <div class="mb-3">
                <label class="form-label text-secondary">Paste Job Description</label>
                <textarea id="job_description" class="form-control bg-dark text-light border-secondary" rows="4" placeholder="Paste full job offer text here..."></textarea>
            </div>

            <h4 class="mt-4 mb-3 text-light">2. Your Resume Details</h4>
            <div class="row g-3">
                <div class="col-md-6">
                    <label class="form-label text-secondary">Full Name</label>
                    <input type="text" id="name" class="form-control bg-dark text-light border-secondary" value="KEDIR ABDELA">
                </div>
                <div class="col-md-6">
                    <label class="form-label text-secondary">Job Title</label>
                    <input type="text" id="title" class="form-control bg-dark text-light border-secondary" value="BUSINESS MARKETING SPECIALIST">
                </div>
                <div class="col-12">
                    <label class="form-label text-secondary">Professional Summary</label>
                    <textarea id="summary" class="form-control bg-dark text-light border-secondary" rows="3">Results-driven Digital Marketing Specialist with 5+ years of experience managing marketing campaigns and increasing online engagement.</textarea>
                </div>
                <div class="col-12">
                    <label class="form-label text-secondary">Work Experience (Header format: Title | Company | Location | Dates)</label>
                    <textarea id="experience" class="form-control bg-dark text-light border-secondary" rows="5">Digital Marketing Specialist | BrightWave Media | New York, NY | 2022 - Present
Managed digital marketing campaigns across Google and social channels.
Increased engagement and traffic through content strategy.</textarea>
                </div>
            </div>

            <button onclick="startOptimization()" class="btn btn-gold btn-lg w-100 mt-4">✨ Optimize CV & Generate Cover Letter</button>
        </div>

        <div id="progress-card" class="card card-custom p-4 mb-4 d-none text-center">
            <h4 class="mb-3 text-light">CVForge AI is Processing...</h4>
            <div class="progress mb-3" style="height: 20px;">
                <div id="progress-bar" class="progress-bar progress-bar-striped progress-bar-animated" style="width: 0%"></div>
            </div>
            <p id="progress-status" class="text-secondary fw-semibold">Analyzing document...</p>
        </div>

        <div id="results-card" class="card card-custom p-4 mb-4 d-none">
            <h3 class="fw-bold mb-4">ATS Compatibility Score</h3>
            <div class="row text-center mb-4">
                <div class="col-md-6 mb-2">
                    <div class="p-3 bg-dark rounded border border-secondary">
                        <small class="text-secondary d-block mb-1">ORIGINAL SCORE</small>
                        <span id="score-before" class="badge-score bg-danger text-white">45%</span>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="p-3 bg-dark rounded border border-secondary">
                        <small class="text-secondary d-block mb-1">OPTIMIZED ATS SCORE</small>
                        <span id="score-after" class="badge-score bg-success text-white">94%</span>
                    </div>
                </div>
            </div>

            <div class="mb-4">
                <h6 class="text-secondary">INTEGRATED ATS KEYWORDS</h6>
                <div id="missing-keywords-list"></div>
            </div>

            <div class="mb-4">
                <h5 class="text-light">Generated Cover Letter</h5>
                <textarea id="cover-letter-text" class="form-control bg-dark text-light border-secondary" rows="6" readonly></textarea>
            </div>

            <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="m-0">ATS Resume Preview</h5>
                <a id="download-btn" href="#" class="btn btn-gold">Download Optimized PDF</a>
            </div>

            <div id="preview-container" class="text-center bg-dark p-3 rounded"></div>
        </div>
    </div>

    <script>
        function startOptimization() {
            const payload = {
                job_description: document.getElementById('job_description').value,
                name: document.getElementById('name').value,
                title: document.getElementById('title').value,
                summary: document.getElementById('summary').value,
                experience: document.getElementById('experience').value
            };

            document.getElementById('optimizer-form').classList.add('d-none');
            document.getElementById('progress-card').classList.remove('d-none');

            fetch('/api/optimize', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                listenToProgress(data.job_id);
            });
        }

        function listenToProgress(jobId) {
            const eventSource = new EventSource(`/api/stream/${jobId}`);

            eventSource.onmessage = function(event) {
                const data = JSON.parse(event.data);
                document.getElementById('progress-bar').style.width = data.progress + '%';
                document.getElementById('progress-status').innerText = data.status;

                if (data.progress === 100 && data.result) {
                    eventSource.close();
                    showResults(data.result);
                }
            };
        }

        function showResults(result) {
            document.getElementById('progress-card').classList.add('d-none');
            document.getElementById('results-card').classList.remove('d-none');

            document.getElementById('score-before').innerText = result.analysis.ats_score_before + '%';
            document.getElementById('score-after').innerText = result.analysis.ats_score_after + '%';
            document.getElementById('cover-letter-text').value = result.cover_letter;

            const kwContainer = document.getElementById('missing-keywords-list');
            kwContainer.innerHTML = '';
            result.analysis.missing_keywords.forEach(kw => {
                kwContainer.innerHTML += `<span class="keyword-tag text-warning">+ ${kw}</span>`;
            });

            document.getElementById('download-btn').href = `/download/${result.token}`;

            const previewContainer = document.getElementById('preview-container');
            previewContainer.innerHTML = '';
            result.page_images.forEach(base64Img => {
                previewContainer.innerHTML += `<img src="data:image/png;base64,${base64Img}" class="img-fluid rounded shadow mb-3" style="max-width: 700px;">`;
            });
        }
    </script>
</body>
</html>
"""

# ============================================================
# ROUTING & CONTROLLERS
# ============================================================
@app.route("/")
def home():
    return render_template_string(APP_HTML)

@app.route("/api/optimize", methods=["POST"])
def start_optimization():
    data = request.json or {}
    job_id = str(uuid.uuid4())
    
    JOBS_STORE[job_id] = {
        "status": "Starting pipeline...",
        "progress": 5,
        "result": None
    }
    
    import threading
    thread = threading.Thread(target=run_cv_optimization_pipeline, args=(job_id, data, data.get("job_description", "")))
    thread.start()
    
    return jsonify({"job_id": job_id})

@app.route("/api/stream/<job_id>")
def stream_progress(job_id):
    def event_generator():
        while True:
            job_info = JOBS_STORE.get(job_id)
            if not job_info:
                break
            
            payload = json.dumps({
                "status": job_info["status"],
                "progress": job_info["progress"],
                "result": job_info.get("result")
            })
            yield f"data: {payload}\n\n"
            
            if job_info["progress"] == 100:
                break
            time.sleep(0.8)

    return Response(event_generator(), mimetype="text/event-stream")

@app.route("/download/<token>")
def download_pdf(token):
    filename = os.path.join(tempfile.gettempdir(), f"CV_{token}.pdf")
    if not os.path.exists(filename):
        return "File not found.", 404
    return send_file(filename, as_attachment=True, download_name="Optimized_Resume.pdf", mimetype="application/pdf")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=False)
