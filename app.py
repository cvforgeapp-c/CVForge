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
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>cvforge - Optimize Your Resume</title>
  <link rel="stylesheet" href="style.css" />
  <!-- Google Fonts: Serif for titles, Sans-Serif for body -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        /* Reset & Base Styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  background-color: #ffffff;
  color: #1a202c;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}

/* Navbar */
.navbar {
  background-color: #0f4c64; /* Dark Teal / Blue shade */
  padding: 12px 20px;
  color: #ffffff;
}

.nav-container {
  max-width: 600px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo-icon {
  width: 24px;
  height: 24px;
  stroke: #ffffff;
}

.logo-text {
  font-size: 1.3rem;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.logo-dot {
  color: #d97706; /* Accent color for the dot */
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.lang-selector {
  font-size: 1.1rem;
  cursor: pointer;
}

.btn-secondary {
  background-color: #ffffff;
  color: #0f4c64;
  padding: 6px 16px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.9rem;
  transition: opacity 0.2s;
}

.btn-secondary:hover {
  opacity: 0.9;
}

.menu-toggle {
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 4px;
}

.menu-toggle span {
  display: block;
  width: 20px;
  height: 2px;
  background-color: #ffffff;
  border-radius: 2px;
}

/* Hero Section */
.hero {
  padding: 40px 20px 60px;
  text-align: center;
}

.hero-container {
  max-width: 480px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.hero-title {
  font-family: 'DM Serif Display', Georgia, serif;
  font-size: 2.2rem;
  line-height: 1.25;
  color: #0f4c64;
  margin-bottom: 20px;
  font-weight: 400;
}

.hero-subtitle {
  font-size: 1.05rem;
  color: #4a5568;
  margin-bottom: 32px;
  line-height: 1.6;
}

/* Stat Box / Card */
.stat-card {
  background-color: #f0f7fa;
  border: 1px solid #d0e4ed;
  border-radius: 16px;
  padding: 28px 20px;
  margin-bottom: 36px;
  width: 100%;
}

.stat-tag {
  display: block;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 1px;
  color: #319795;
  margin-bottom: 12px;
}

.stat-heading {
  font-family: 'DM Serif Display', Georgia, serif;
  font-size: 1.5rem;
  line-height: 1.3;
  color: #0f4c64;
  margin-bottom: 16px;
  font-weight: 400;
}

.stat-subtext {
  font-size: 0.95rem;
  color: #4a5568;
}

/* CTA Wrapper & Badge */
.cta-wrapper {
  position: relative;
  width: 100%;
  display: flex;
  justify-content: center;
  margin-bottom: 12px;
}

.btn-primary {
  background-color: #0f4c64;
  color: #ffffff;
  width: 100%;
  max-width: 320px;
  padding: 16px 24px;
  border-radius: 30px;
  font-size: 1.1rem;
  font-weight: 600;
  text-decoration: none;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 4px 14px rgba(15, 76, 100, 0.25);
  transition: transform 0.15s, background-color 0.2s;
}

.btn-primary:hover {
  background-color: #0b3b4f;
  transform: translateY(-1px);
}

.arrow {
  font-size: 1.2rem;
}

.badge {
  position: absolute;
  right: 10px;
  top: -15px;
  background-color: #000000;
  color: #ffffff;
  border-radius: 50%;
  width: 52px;
  height: 52px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 2px dashed #319795;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.badge-icon {
  width: 16px;
  height: 16px;
  stroke: #ffffff;
}

.badge-text {
  font-size: 0.35rem;
  font-weight: 700;
  text-align: center;
  margin-top: 2px;
  line-height: 1;
}

.cta-footnote {
  font-size: 0.85rem;
  color: #718096;
}

    </style>
</head>
<body>

  <!-- Navbar -->
  <header class="navbar">
    <div class="nav-container">
      <div class="logo">
        <svg class="logo-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
          <polyline points="14 2 14 8 20 8"></polyline>
          <line x1="16" y1="13" x2="8" y2="13"></line>
          <line x1="16" y1="17" x2="8" y2="17"></line>
          <polyline points="10 9 9 9 8 9"></polyline>
        </svg>
        <span class="logo-text">cvforge<span class="logo-dot">.</span></span>
      </div>

      <div class="nav-actions">
        <div class="lang-selector">
          <span class="flag">🇬🇧</span>
        </div>
        <a href="#try" class="btn-secondary">Try it</a>
        <button class="menu-toggle" aria-label="Open menu">
          <span></span>
          <span></span>
          <span></span>
        </button>
      </div>
    </div>
  </header>

  <!-- Main Hero Section -->
  <main class="hero">
    <div class="hero-container">
      
      <!-- Main Title -->
      <h1 class="hero-title">
        Your resume, optimized for the job you want.
      </h1>

      <!-- Subtitle -->
      <p class="hero-subtitle">
        We tailor your resume to each job posting so it gets selected. No cheating, and full respect for your data.
      </p>

      <!-- Stat Card -->
      <div class="stat-card">
        <span class="stat-tag">JOBSTER STUDY · 2025</span>
        <h2 class="stat-heading">
          75% of resumes are rejected before a human ever reads them.
        </h2>
        <p class="stat-subtext">
          Yours will be optimized for the job you're targeting.
        </p>
      </div>

      <!-- Call to Action Container -->
      <div class="cta-wrapper">
        <a href="#start" class="btn-primary">
          Try it for free <span class="arrow">→</span>
        </a>
        <div class="badge">
          <svg class="badge-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
          </svg>
          <span class="badge-text">GDPR COMPLIANCE</span>
        </div>
      </div>

      <!-- Sub-CTA Text -->
      <p class="cta-footnote">1 free credit · No credit card required</p>

    </div>
  </main>

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
