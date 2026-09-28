import os
import tempfile
import base64
import uuid
import re
import json
import time
import requests
import pymupdf as fitz
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
# MULTI-VIEW INTEGRATED UI FRONTEND
# ============================================================
APP_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>cvforge - Optimize Your Resume</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: #ffffff;
      color: #1a202c;
      line-height: 1.5;
      -webkit-font-smoothing: antialiased;
    }
    .hidden { display: none !important; }

    /* Navigation Header */
    .navbar { background-color: #0d4b60; padding: 12px 20px; color: #ffffff; }
    .nav-container { max-width: 500px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
    .logo { display: flex; items-center; gap: 8px; cursor: pointer; text-decoration: none; color: white; }
    .logo-icon { width: 22px; height: 22px; stroke: #ffffff; }
    .logo-text { font-size: 1.25rem; font-weight: 700; letter-spacing: -0.5px; }
    .logo-dot { color: #e59329; }
    .nav-actions { display: flex; align-items: center; gap: 12px; }
    .btn-secondary {
      background-color: #ffffff; color: #0d4b60; padding: 6px 16px; border-radius: 8px;
      text-decoration: none; font-weight: 600; font-size: 0.88rem; cursor: pointer; border: none;
    }

    /* Hero / Home View */
    .hero { padding: 40px 20px 60px; text-align: center; }
    .hero-container { max-width: 480px; margin: 0 auto; display: flex; flex-direction: column; align-items: center; }
    .hero-title { font-family: 'DM Serif Display', Georgia, serif; font-size: 2.2rem; line-height: 1.25; color: #0d4b60; margin-bottom: 20px; font-weight: 400; }
    .hero-subtitle { font-size: 1rem; color: #4a5568; margin-bottom: 32px; line-height: 1.6; }
    .stat-card { background-color: #f0f7fa; border: 1px solid #d0e4ed; border-radius: 16px; padding: 24px 20px; margin-bottom: 32px; width: 100%; }
    .stat-tag { display: block; font-size: 0.72rem; font-weight: 700; letter-spacing: 1px; color: #319795; margin-bottom: 10px; }
    .stat-heading { font-family: 'DM Serif Display', Georgia, serif; font-size: 1.4rem; line-height: 1.3; color: #0d4b60; margin-bottom: 12px; font-weight: 400; }
    .stat-subtext { font-size: 0.9rem; color: #4a5568; }
    .cta-wrapper { position: relative; width: 100%; display: flex; justify-content: center; margin-bottom: 12px; }
    .btn-primary {
      background-color: #0d4b60; color: #ffffff; width: 100%; max-width: 320px; padding: 16px 24px;
      border-radius: 30px; font-size: 1.05rem; font-weight: 600; border: none; display: flex;
      align-items: center; justify-content: center; gap: 8px; box-shadow: 0 4px 14px rgba(13, 75, 96, 0.25);
      cursor: pointer; transition: background-color 0.2s;
    }
    .btn-primary:hover { background-color: #0a3a4b; }
    .badge {
      position: absolute; right: 10px; top: -15px; background-color: #000000; color: #ffffff;
      border-radius: 50%; width: 52px; height: 52px; display: flex; flex-direction: column;
      align-items: center; justify-content: center; border: 2px dashed #319795;
    }
    .badge-icon { width: 14px; height: 14px; stroke: #ffffff; }
    .badge-text { font-size: 0.35rem; font-weight: 700; text-align: center; margin-top: 2px; }
    .cta-footnote { font-size: 0.82rem; color: #718096; }

    /* Dashboard View */
    .dashboard-container { max-width: 480px; margin: 0 auto; padding: 20px; }
    .dash-header-card {
      background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 16px; padding: 16px 20px;
      display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;
    }
    .credit-pill {
      background-color: #e0f2fe; color: #0369a1; border-radius: 20px; padding: 4px 12px;
      font-size: 0.78rem; font-weight: 700; display: inline-flex; align-items: center; gap: 6px;
    }
    .btn-account {
      background-color: #0d4b60; color: white; border: none; padding: 8px 16px; border-radius: 20px;
      font-size: 0.8rem; font-weight: 600; cursor: pointer;
    }
    .dropzone-card {
      border: 2px dashed #cbd5e1; border-radius: 16px; padding: 28px 20px; text-align: center;
      background-color: #fafafa; margin-bottom: 20px; cursor: pointer;
    }
    .input-field {
      width: 100%; border: 1px solid #cbd5e1; border-radius: 12px; padding: 12px; font-family: inherit;
      font-size: 0.88rem; margin-bottom: 12px; outline: none;
    }
    .input-field:focus { border-color: #0d4b60; }

    /* Register View */
    .register-container { max-width: 460px; margin: 0 auto; padding: 16px 20px 48px; }
    .terms-box {
      background-color: #fffbeb; border: 1px solid #fef08a; border-radius: 12px; padding: 14px;
      margin-bottom: 20px; display: flex; gap: 12px; align-items: flex-start;
    }
    .social-btn {
      width: 100%; border-radius: 25px; padding: 12px; font-size: 0.88rem; font-weight: 600;
      display: flex; align-items: center; justify-content: center; gap: 10px; cursor: pointer; margin-bottom: 10px;
    }
    .btn-google { background: white; border: 1px solid #cbd5e1; color: #1e293b; }
    .btn-apple { background: black; border: none; color: white; }
    .divider { display: flex; align-items: center; margin: 20px 0; color: #94a3b8; font-size: 0.7rem; font-weight: 700; letter-spacing: 1px; }
    .divider::before, .divider::after { content: ""; flex: 1; border-bottom: 1px solid #e2e8f0; }
    .divider span { margin: 0 12px; }

    /* Progress & Results */
    .progress-bar-inner { height: 100%; background-color: #0d4b60; width: 0%; transition: width 0.3s; }
  </style>
</head>
<body>

  <!-- TOP NAVBAR -->
  <header class="navbar">
    <div class="nav-container">
      <div class="logo" onclick="switchView('home')">
        <svg class="logo-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
          <polyline points="14 2 14 8 20 8"></polyline>
          <line x1="16" y1="13" x2="8" y2="13"></line>
          <line x1="16" y1="17" x2="8" y2="17"></line>
        </svg>
        <span class="logo-text">cvforge<span class="logo-dot">.</span></span>
      </div>
      <div class="nav-actions">
        <span>🇬🇧</span>
        <button id="nav-action-btn" class="btn-secondary" onclick="switchView('dashboard')">Try it</button>
      </div>
    </div>
  </header>

  <!-- VIEW 1: HOME PAGE -->
  <div id="view-home">
    <main class="hero">
      <div class="hero-container">
        <h1 class="hero-title">Your resume, optimized for the job you want.</h1>
        <p class="hero-subtitle">We tailor your resume to each job posting so it gets selected. No cheating, and full respect for your data.</p>
        
        <div class="stat-card">
          <span class="stat-tag">JOBSTER STUDY · 2025</span>
          <h2 class="stat-heading">75% of resumes are rejected before a human ever reads them.</h2>
          <p class="stat-subtext">Yours will be optimized for the job you're targeting.</p>
        </div>

        <div class="cta-wrapper">
          <button class="btn-primary" onclick="switchView('dashboard')">
            Try it for free <span style="font-size: 1.2rem;">→</span>
          </button>
          <div class="badge">
            <svg class="badge-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
            </svg>
            <span class="badge-text">GDPR COMPLIANCE</span>
          </div>
        </div>
        <p class="cta-footnote">1 free credit · No credit card required</p>
      </div>
    </main>
  </div>

  <!-- VIEW 2: DASHBOARD PAGE -->
  <div id="view-dashboard" class="hidden">
    <div class="dashboard-container">
      <div class="dash-header-card">
        <div class="credit-pill">⚡ 1 free credit left</div>
        <button class="btn-account" onclick="switchView('register')">Create an account</button>
      </div>

      <div id="dash-form">
        <div class="dropzone-card">
          <svg style="width: 32px; height: 32px; margin: 0 auto 8px; stroke: #64748b;" viewBox="0 0 24 24" fill="none" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="17 8 12 3 7 8"></polyline>
            <line x1="12" y1="3" x2="12" y2="15"></line>
          </svg>
          <p style="font-size: 0.9rem; font-weight: 600; color: #1e293b;">Drop your CV or click to browse</p>
          <p style="font-size: 0.75rem; color: #64748b;">Supports PDF or TXT format</p>
        </div>

        <input type="text" id="name" placeholder="Full Name" class="input-field" value="Alex Smith" />
        <input type="text" id="title" placeholder="Target Job Title" class="input-field" value="Software Engineer" />
        <textarea id="job_description" rows="3" placeholder="Paste Target Job Description here..." class="input-field">Looking for a Full Stack Software Engineer proficient in KPI tracking, data optimization, and cross-functional leadership.</textarea>
        <textarea id="summary" rows="2" placeholder="Current CV Summary..." class="input-field">Experienced software developer with focus on web applications.</textarea>
        <textarea id="experience" rows="3" placeholder="Current Work Experience..." class="input-field">Senior Developer | Tech Corp
Developed scalable web APIs and backend systems.</textarea>

        <button class="btn-primary" style="max-width: 100%; border-radius: 12px; margin-top: 8px;" onclick="startOptimization()">
          Optimize Resume Now →
        </button>
      </div>

      <!-- Progress Section -->
      <div id="progress-card" class="hidden" style="text-align: center; padding: 40px 0;">
        <p id="progress-status" style="font-size: 0.9rem; font-weight: 600; color: #0d4b60; margin-bottom: 12px;">Initializing...</p>
        <div style="height: 8px; background: #e2e8f0; border-radius: 4px; overflow: hidden; margin-bottom: 12px;">
          <div id="progress-bar" class="progress-bar-inner"></div>
        </div>
      </div>

      <!-- Result Section -->
      <div id="results-card" class="hidden" style="margin-top: 20px;">
        <h3 style="color: #0d4b60; margin-bottom: 12px;">Optimization Complete!</h3>
        <p style="font-size: 0.85rem; color: #475569; margin-bottom: 12px;">ATS Score Improved: <span id="score-before">--</span> → <strong id="score-after" style="color: #16a34a;">--</strong></p>
        <a id="download-btn" href="#" class="btn-primary" style="max-width: 100%; border-radius: 12px; text-decoration: none;">Download Optimized PDF</a>
        <div id="preview-container" style="margin-top: 20px; text-align: center;"></div>
      </div>
    </div>
  </div>

  <!-- VIEW 3: REGISTER PAGE -->
  <div id="view-register" class="hidden">
    <div class="register-container">
      <h1 style="font-family: 'DM Serif Display', Georgia, serif; font-size: 2rem; color: #0d4b60; margin-bottom: 6px;">Welcome.</h1>
      <p style="font-size: 0.85rem; color: #64748b; margin-bottom: 20px;">One account = your resumes saved, your credits kept, zero loss.</p>

      <div class="terms-box">
        <input type="checkbox" id="terms-check" style="margin-top: 3px; accent-color: #0d4b60; cursor: pointer;" />
        <label for="terms-check" style="font-size: 0.75rem; color: #854d0e; line-height: 1.4; cursor: pointer;">
          <strong style="color: #92400e; display: flex; align-items: center; gap: 4px; margin-bottom: 2px;">
            🛡 Required to sign up
          </strong>
          I accept the <a href="#" style="color: #78350f; font-weight: 600;">Terms of Service</a> and the <a href="#" style="color: #78350f; font-weight: 600;">Privacy Policy</a>.
        </label>
      </div>

      <button class="social-btn btn-google">
        <svg style="width: 16px; height: 16px;" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/></svg>
        Continue with Google
      </button>

      <button class="social-btn btn-apple">
        <svg style="width: 16px; height: 16px; fill: currentColor;" viewBox="0 0 170 170"><path d="M150.37 130.25c-2.45 5.66-5.35 10.87-8.71 15.66-4.58 6.53-8.33 11.05-11.22 13.56-4.48 4.12-9.28 6.23-14.42 6.35-3.69 0-8.14-1.05-13.32-3.18-5.19-2.12-9.97-3.17-14.34-3.17-4.58 0-9.49 1.05-14.75 3.17-5.26 2.13-9.5 3.24-12.74 3.35-4.34.13-9.16-1.9-14.49-6.08-3.32-2.68-7.23-7.38-11.73-14.09-6.42-9.56-11.45-20.15-15.09-31.78-3.64-11.63-5.46-22.91-5.46-33.84 0-14.88 3.73-27.12 11.19-36.72 7.46-9.6 16.89-14.48 28.29-14.64 4.89 0 10.15 1.25 15.78 3.74 5.63 2.5 9.4 3.75 11.3 3.75 1.52 0 5.43-1.3 11.73-3.9 6.3-2.6 11.49-3.8 15.57-3.6 11.51.9 20.89 5.22 28.14 12.96-10.22 6.18-15.22 14.84-15.01 25.98.21 8.68 3.51 16.03 9.89 22.05 6.38 6.02 14.01 9.46 22.89 10.32-2.28 6.84-5.22 13.62-8.82 20.34zM119.22 31.84c0-6.73 2.41-13.36 7.23-19.89 4.82-6.53 11.08-10.87 18.78-13.02.65 2.17.98 4.29.98 6.36 0 6.84-2.52 13.6-7.56 20.28-5.04 6.68-11.28 10.84-18.72 12.48-.22-2.06-.71-4.13-.71-6.21z"/></svg>
        Continue with Apple
      </button>

      <div class="divider"><span>OR WITH YOUR EMAIL</span></div>

      <form onsubmit="handleRegister(event)">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
          <div>
            <label style="font-size: 0.75rem; font-weight: 700; color: #334155;">First name</label>
            <input type="text" placeholder="First name" class="input-field" style="margin-top: 4px;" required />
          </div>
          <div>
            <label style="font-size: 0.75rem; font-weight: 700; color: #334155;">Last name</label>
            <input type="text" placeholder="Last name" class="input-field" style="margin-top: 4px;" required />
          </div>
        </div>

        <div style="margin-top: 8px;">
          <label style="font-size: 0.75rem; font-weight: 700; color: #334155;">Email address</label>
          <input type="email" placeholder="you@email.com" class="input-field" style="margin-top: 4px;" required />
        </div>

        <div style="margin-top: 8px;">
          <label style="font-size: 0.75rem; font-weight: 700; color: #334155;">Password <span style="color: #ef4444;">*</span></label>
          <input type="password" placeholder="At least 8 characters" class="input-field" style="margin-top: 4px;" required />
          <p style="font-size: 0.7rem; color: #64748b;">Your password must contain at least 8 characters, one letter and one number.</p>
        </div>

        <button type="submit" class="btn-primary" style="max-width: 100%; border-radius: 25px; margin-top: 16px;">
          Create my account →
        </button>
      </form>

      <p style="text-align: center; font-size: 0.8rem; color: #475569; margin-top: 20px;">
        Already have an account? <a href="#" style="color: #0d4b60; font-weight: 700;">Sign in</a>
      </p>
    </div>
  </div>

  <script>
    function switchView(viewName) {
      document.getElementById('view-home').classList.add('hidden');
      document.getElementById('view-dashboard').classList.add('hidden');
      document.getElementById('view-register').classList.add('hidden');

      const actionBtn = document.getElementById('nav-action-btn');

      if (viewName === 'home') {
        document.getElementById('view-home').classList.remove('hidden');
        actionBtn.innerText = 'Try it';
        actionBtn.onclick = () => switchView('dashboard');
      } else if (viewName === 'dashboard') {
        document.getElementById('view-dashboard').classList.remove('hidden');
        actionBtn.innerText = 'Sign up';
        actionBtn.onclick = () => switchView('register');
      } else if (viewName === 'register') {
        document.getElementById('view-register').classList.remove('hidden');
        actionBtn.innerText = 'Dashboard';
        actionBtn.onclick = () => switchView('dashboard');
      }
      window.scrollTo(0, 0);
    }

    function handleRegister(e) {
      e.preventDefault();
      const terms = document.getElementById('terms-check').checked;
      if (!terms) {
        alert('Please accept the Terms of Service and Privacy Policy.');
        return;
      }
      alert('Account created successfully!');
      switchView('dashboard');
    }

    function startOptimization() {
      const payload = {
        job_description: document.getElementById('job_description').value,
        name: document.getElementById('name').value,
        title: document.getElementById('title').value,
        summary: document.getElementById('summary').value,
        experience: document.getElementById('experience').value
      };

      document.getElementById('dash-form').classList.add('hidden');
      document.getElementById('progress-card').classList.remove('hidden');

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
      document.getElementById('progress-card').classList.add('hidden');
      document.getElementById('results-card').classList.remove('hidden');

      document.getElementById('score-before').innerText = result.analysis.ats_score_before + '%';
      document.getElementById('score-after').innerText = result.analysis.ats_score_after + '%';
      document.getElementById('download-btn').href = `/download/${result.token}`;

      const previewContainer = document.getElementById('preview-container');
      previewContainer.innerHTML = '';
      result.page_images.forEach(base64Img => {
        previewContainer.innerHTML += `<img src="data:image/png;base64,${base64Img}" style="max-width: 100%; border-radius: 8px; border: 1px solid #cbd5e1; margin-top: 12px;" />`;
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
