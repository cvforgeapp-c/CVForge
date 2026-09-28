import os
import tempfile
import json
import io
import pymupdf as fitz  # PyMuPDF
from flask import Flask, request, render_template_string, jsonify, send_file

app = Flask(__name__)

# ============================================================
# MULTI-PAGE ATS CV PDF GENERATOR (PyMuPDF)
# ============================================================
def generate_ats_pdf(data, watermark=False):
    doc = fitz.open()
    
    # Page setup (A4 standard)
    page_width, page_height = 595, 842
    margin = 40
    content_width = page_width - (2 * margin)
    
    def create_page():
        page = doc.new_page(width=page_width, height=page_height)
        return page, margin

    page, y = create_page()
    
    # Styling helpers
    def check_page_break(current_page, current_y, needed_height):
        if current_y + needed_height > page_height - margin:
            new_page, new_y = create_page()
            return new_page, new_y
        return current_page, current_y

    # --- HEADER SECTION ---
    name = data.get("name", "KEDIR ABDELA").upper()
    title = data.get("title", "Digital Marketing Specialist (5 yrs exp)")
    contact = data.get("contact", "0908706534 | nmtullah86@gmail.com | Los Angeles")
    links = data.get("links", "linkedin.com/in/kedirmohammed | Availability: 1 month")

    page.insert_text((margin, y + 18), name, fontsize=18, fontname="helv-bold", color=(0.05, 0.1, 0.2))
    y += 28
    page.insert_text((margin, y + 12), title, fontsize=12, fontname="helv-bold", color=(0.1, 0.3, 0.4))
    y += 20
    page.insert_text((margin, y + 10), contact, fontsize=9, fontname="helv", color=(0.3, 0.3, 0.3))
    y += 14
    page.insert_text((margin, y + 10), links, fontsize=9, fontname="helv", color=(0.3, 0.3, 0.3))
    y += 24

    # Separator Line
    page.draw_line((margin, y), (page_width - margin, y), color=(0.8, 0.8, 0.8), width=0.8)
    y += 16

    # --- SECTIONS RENDERER ---
    sections = [
        ("PROFESSIONAL SUMMARY", [
            "Results-driven Digital Marketing Specialist with 5+ years of experience designing data-driven campaigns across Google, Meta, and LinkedIn. Proven track record in SEO, paid advertising, and content strategy, with measurable impact on traffic growth and audience engagement. Adept at managing budgets, analyzing performance metrics, and collaborating cross-functionally to deliver retail-focused marketing outcomes."
        ]),
        ("KEY SKILLS", [
            "Digital Marketing: SEO, Social Media Marketing (Google, Instagram, Facebook, LinkedIn), Paid Advertising (Google Ads), Content Marketing, Email Marketing, Campaign Performance Analysis, Customer Acquisition, Budget Management, Data-Driven Strategy",
            "Tools & Analytics: Google Analytics (Certified), Google Ads Search, HubSpot Content Marketing, Performance Reporting & Dashboards",
            "Soft Skills: Project Management, Cross-functional Collaboration, Analytical Thinking, Adaptability, Results Orientation"
        ]),
        ("PROFESSIONAL EXPERIENCE", [
            "Digital Marketing Specialist — BrightWave Media (2022 - Present)",
            "• Developed and managed multi-channel campaigns across Google, Instagram, Facebook, and LinkedIn, aligning with core growth goals.",
            "• Increased website traffic by 45% through targeted SEO strategies and content marketing initiatives.",
            "• Managed advertising budgets and conducted campaign performance analysis to produce high-impact marketing materials.",
            " ",
            "Marketing Associate — NovaTech Solutions (2019 - 2022)",
            "• Supported digital marketing and social media operations, contributing to measurable user acquisition.",
            "• Improved social media engagement by 30% within one year through optimized content scheduling.",
            "• Created weekly performance reports using Google Analytics; assisted with targeted email campaigns."
        ]),
        ("EDUCATION & CERTIFICATIONS", [
            "Bachelor of Business Administration | New York University",
            "• Google Analytics Certification | Google",
            "• Google Ads Search Certification | Google",
            "• HubSpot Content Marketing Certification | HubSpot Academy"
        ]),
        ("LANGUAGES & INTERESTS", [
            "Languages: English (Native), Spanish (Professional Working Proficiency), French (Basic)",
            "Interests & Projects: Technology, AI Automation, Photography, Digital Publishing, Entrepreneurship"
        ])
    ]

    for sec_title, items in sections:
        page, y = check_page_break(page, y, 40)
        
        # Section Header
        page.insert_text((margin, y + 12), sec_title, fontsize=11, fontname="helv-bold", color=(0.05, 0.1, 0.2))
        y += 18
        page.draw_line((margin, y), (page_width - margin, y), color=(0.85, 0.85, 0.85), width=0.5)
        y += 12

        # Section Content
        for item in items:
            # Simple text wrap approximation
            words = item.split(" ")
            line = ""
            for word in words:
                test_line = line + word + " "
                if len(test_line) * 4.8 > content_width:
                    page, y = check_page_break(page, y, 14)
                    page.insert_text((margin, y + 10), line, fontsize=9.5, fontname="helv", color=(0.2, 0.2, 0.2))
                    y += 13
                    line = word + " "
                else:
                    line = test_line
            
            if line:
                page, y = check_page_break(page, y, 14)
                page.insert_text((margin, y + 10), line, fontsize=9.5, fontname="helv", color=(0.2, 0.2, 0.2))
                y += 14
        y += 10

    # --- WATERMARK OVERLAY ---
    if watermark:
        for p in doc:
            p.insert_text(
                (margin, page_height - 20),
                "CVforge.co — Free ATS Template",
                fontsize=9,
                fontname="helv-bold",
                color=(0.6, 0.6, 0.6)
            )

    pdf_buffer = io.BytesIO()
    doc.save(pdf_buffer)
    doc.close()
    pdf_buffer.seek(0)
    return pdf_buffer


# ============================================================
# COMPLETE FRONTEND & APP LAYOUT
# ============================================================
APP_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>cvforge - Resume Optimizer</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Inter', -apple-system, sans-serif; background-color: #f8fafc; color: #0f172a; }
    .hidden { display: none !important; }

    .navbar { background-color: #ffffff; padding: 12px 20px; border-bottom: 1px solid #e2e8f0; }
    .nav-container { max-width: 480px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
    .logo { font-size: 1.25rem; font-weight: 700; color: #0f172a; text-decoration: none; }
    .logo-dot { color: #d97706; }
    .nav-actions { display: flex; align-items: center; gap: 8px; }
    .badge-pill { background: #fff8e6; color: #854d0e; font-size: 0.75rem; font-weight: 700; padding: 4px 10px; border-radius: 12px; }
    .badge-blue { background: #e0f2fe; color: #0369a1; font-size: 0.75rem; font-weight: 700; padding: 4px 10px; border-radius: 12px; }
    .avatar-pill { background: #073042; color: #ffffff; font-size: 0.78rem; font-weight: 700; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }

    .app-container { max-width: 480px; margin: 0 auto; padding: 20px 16px 60px; }
    .serif-title-dark { font-family: 'DM Serif Display', Georgia, serif; font-size: 1.85rem; color: #0f172a; margin-bottom: 16px; font-weight: 400; }

    .upload-card { border: 1.5px dashed #38bdf8; border-radius: 16px; padding: 30px 20px; text-align: center; background-color: #ffffff; margin-bottom: 16px; }
    .btn-browse { background: #ffffff; border: 1px solid #cbd5e1; border-radius: 20px; padding: 8px 24px; font-size: 0.85rem; font-weight: 600; cursor: pointer; }

    .uploaded-file-card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 14px 16px; display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
    .file-info { display: flex; align-items: center; gap: 12px; }
    .file-icon-box { width: 38px; height: 46px; border: 1px solid #cbd5e1; border-radius: 6px; display: flex; align-items: center; justify-content: center; }
    .file-tag { font-size: 0.65rem; font-weight: 700; color: #0d4b60; letter-spacing: 0.5px; }
    .file-name { font-size: 0.95rem; font-weight: 700; color: #0f172a; }
    .file-sub { font-size: 0.78rem; color: #64748b; }
    .upload-btn-link { background: none; border: none; cursor: pointer; color: #64748b; padding: 6px; border-radius: 50%; }

    .url-bar-container { margin-bottom: 24px; }
    .url-input-box { display: flex; align-items: center; background: #ffffff; border: 1px solid #cbd5e1; border-radius: 14px; padding: 10px 14px; margin-bottom: 12px; }
    .url-input { border: none; outline: none; flex: 1; font-size: 0.88rem; }

    .action-row { display: flex; gap: 10px; align-items: center; }
    .btn-trial { background: #ffffff; border: 1px solid #cbd5e1; border-radius: 25px; padding: 12px; font-size: 0.9rem; font-weight: 600; color: #0f172a; flex: 1; border: none; cursor: pointer; }
    .btn-trial.disabled { opacity: 0.4; filter: blur(0.4px); cursor: not-allowed; background: #e2e8f0; color: #94a3b8; }
    .btn-launch-disabled { background: #8da4b0; color: #ffffff; border: none; border-radius: 25px; padding: 12px; font-weight: 600; font-size: 0.9rem; flex: 1.2; display: flex; align-items: center; justify-content: center; gap: 6px; cursor: not-allowed; opacity: 0.7; }

    .optimized-box { background: #ffffff; border-radius: 20px; padding: 20px; border: 1px solid #f1f5f9; }
    .optimized-title { font-family: 'DM Serif Display', Georgia, serif; font-size: 1.3rem; color: #0f172a; margin-bottom: 16px; font-weight: 400; display: flex; align-items: center; gap: 8px; }
    
    .step-card { background: #f8fafc; border-radius: 16px; padding: 24px; text-align: center; }
    .step-title { font-family: 'DM Serif Display', Georgia, serif; font-size: 1.4rem; color: #0f172a; margin-bottom: 20px; font-weight: 400; }
    .step-list { text-align: left; max-width: 300px; margin: 0 auto; display: flex; flex-direction: column; gap: 14px; }
    .step-item { display: flex; align-items: center; gap: 12px; font-size: 0.88rem; color: #94a3b8; }
    .step-item.active { color: #0f172a; font-weight: 600; }
    .step-item.done { color: #0f172a; }
    
    .status-icon { width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
    .icon-pending { background: #f1f5f9; }
    .icon-active { border: 2.5px solid #0d4b60; border-top-color: transparent; animation: spin 0.8s linear infinite; }
    .icon-done { background: #16a34a; color: white; }
    @keyframes spin { 100% { transform: rotate(360deg); } }

    .result-card { background: #ffffff; border-radius: 16px; padding: 16px; text-align: left; }
    .job-header { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
    .company-logo { width: 44px; height: 44px; background: #ea580c; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 0.8rem; }
    .job-company { font-weight: 700; font-size: 1rem; color: #0f172a; }
    .job-title-text { font-family: 'DM Serif Display', Georgia, serif; font-size: 1.25rem; color: #0f172a; margin-top: 4px; }
    .job-date { font-size: 0.78rem; color: #64748b; margin-top: 2px; }
    .view-link { font-size: 0.82rem; color: #0d4b60; text-decoration: none; font-weight: 600; display: inline-flex; align-items: center; gap: 4px; margin: 10px 0 16px; }

    .result-actions { display: flex; flex-direction: column; gap: 8px; }
    .btn-action-main { background: #0d4b60; color: white; border: none; border-radius: 20px; padding: 12px; font-weight: 600; font-size: 0.9rem; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 6px; width: 100%; }
    .btn-action-sec { background: #ffffff; color: #0f172a; border: 1px solid #cbd5e1; border-radius: 20px; padding: 10px; font-weight: 600; font-size: 0.88rem; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 6px; width: 100%; }
    .btn-action-danger { background: #ef4444; color: white; border: none; border-radius: 20px; padding: 10px; font-weight: 600; font-size: 0.88rem; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 6px; width: 100%; }

    .modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(4px); display: flex; align-items: flex-end; justify-content: center; z-index: 100; }
    .modal-card { background: #ffffff; border-radius: 24px 24px 0 0; width: 100%; max-width: 480px; padding: 24px; text-align: center; }

    .modal-top-bar { display: flex; justify-content: space-between; align-items: center; background: #0d4b60; color: white; margin: -24px -24px 20px; padding: 16px 20px; border-radius: 24px 24px 0 0; }
    .modal-title { font-family: 'DM Serif Display', Georgia, serif; font-size: 1.4rem; font-weight: 400; display: flex; align-items: center; gap: 6px; }
    .modal-close { background: rgba(255,255,255,0.2); border: none; color: white; width: 28px; height: 28px; border-radius: 50%; font-size: 1rem; cursor: pointer; }

    .modal-banner { background: #f0f7fa; border: 1px solid #e0f2fe; border-radius: 14px; padding: 14px; text-align: left; margin-bottom: 20px; display: flex; gap: 10px; }
    .modal-btn-primary { background: #0d4b60; color: white; border: none; border-radius: 25px; padding: 12px; font-size: 0.9rem; font-weight: 600; width: 100%; margin-bottom: 10px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 6px; }
    .modal-btn-orange { background: #ea580c; color: white; border: none; border-radius: 25px; padding: 12px; font-size: 0.9rem; font-weight: 600; width: 100%; margin-bottom: 12px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 6px; }
    .modal-link-sub { font-size: 0.82rem; color: #64748b; text-decoration: underline; cursor: pointer; }
  </style>
</head>
<body>

  <input type="file" id="global-file-input" accept=".pdf,.docx" class="hidden" onchange="handleFileUpload(event)" />

  <header class="navbar">
    <div class="nav-container">
      <a class="logo" href="#">cvforge<span class="logo-dot">.</span></a>
      <div class="nav-actions">
        <div class="badge-pill">0 🪙</div>
        <div class="badge-blue">1 🔵</div>
        <div id="user-avatar" class="avatar-pill">K</div>
      </div>
    </div>
  </header>

  <main class="app-container">
    <div id="view-dashboard">
      <div style="margin-bottom: 16px;">
        <span style="font-size: 0.78rem; color: #64748b;">Monday, September 28</span>
        <h1 id="greeting-title" class="serif-title-dark" style="margin-top: 2px;">Hello Kedir, ready to apply?</h1>
      </div>

      <div id="upload-box-unuploaded" class="upload-card">
        <h3 style="font-family: 'DM Serif Display', Georgia, serif; font-size: 1.3rem; margin-bottom: 8px;">Upload your baseline CV</h3>
        <button class="btn-browse" onclick="triggerFilePicker()">Browse file</button>
      </div>

      <div id="upload-box-uploaded" class="uploaded-file-card">
        <div class="file-info">
          <div class="file-icon-box">
            <svg style="width: 18px; height: 18px; stroke: #0d4b60;" viewBox="0 0 24 24" fill="none" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
            </svg>
          </div>
          <div>
            <div class="file-tag">VOTRE CV DE BASE</div>
            <div id="uploaded-user-name" class="file-name">Kedir</div>
            <div id="uploaded-file-name" class="file-sub">Kedir_Alemayehu_CV.pdf</div>
          </div>
        </div>
        <button class="upload-btn-link" title="Upload new CV" onclick="triggerFilePicker()">
          <svg style="width: 18px; height: 18px;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="17 8 12 3 7 8"></polyline>
            <line x1="12" y1="3" x2="12" y2="15"></line>
          </svg>
        </button>
      </div>

      <div class="url-bar-container">
        <div class="url-input-box">
          <input type="url" id="job-url" class="url-input" placeholder="https://www.linkedin.com/jobs/view/xx>" oninput="validateJobUrl()" />
        </div>

        <div class="action-row">
          <button id="btn-trial" class="btn-trial disabled" disabled onclick="startOptimizationProcess()">Trial (1)</button>
          <button id="btn-launch" class="btn-launch-disabled" disabled><span>❇</span> Launch</button>
        </div>
      </div>

      <div class="optimized-box">
        <div class="optimized-title"><span>❇</span> My optimized resumes</div>

        <div id="preview-empty" style="text-align: center; padding: 20px 0; color: #64748b; font-size: 0.85rem;">
          Paste a job offer link above and click "Trial (1)" to begin.
        </div>

        <div id="preview-stepwise" class="step-card hidden">
          <h3 class="step-title">We're working on it.</h3>
          <div class="step-list">
            <div id="step-1" class="step-item active"><div class="status-icon icon-active" id="icon-1"></div><span>Reading your resume...</span></div>
            <div id="step-2" class="step-item"><div class="status-icon icon-pending" id="icon-2"></div><span>Analyzing the job offer...</span></div>
            <div id="step-3" class="step-item"><div class="status-icon icon-pending" id="icon-3"></div><span>Detecting ATS keywords...</span></div>
            <div id="step-4" class="step-item"><div class="status-icon icon-pending" id="icon-4"></div><span>Rewriting your experiences...</span></div>
            <div id="step-5" class="step-item"><div class="status-icon icon-pending" id="icon-5"></div><span>Calculating the score...</span></div>
          </div>
        </div>

        <div id="preview-result" class="result-card hidden">
          <div class="job-header">
            <div class="company-logo">HOME</div>
            <div>
              <div class="job-company">LinkedIn</div>
              <div class="job-title-text">The Home Depot</div>
              <div class="job-date">Sep 28, 2026 at 11:34 PM</div>
            </div>
          </div>
          <a href="#" class="view-link" target="_blank">View job posting</a>

          <div class="result-actions">
            <button class="btn-action-main" onclick="openDownloadModal()">Download</button>
            <button class="btn-action-sec" onclick="alert('Editing...')">✏️ Edit</button>
            <button class="btn-action-sec" onclick="alert('Rated!')">⭐ Rate</button>
            <button class="btn-action-danger" onclick="resetOptimizationView()">🗑 Delete</button>
          </div>
        </div>
      </div>
    </div>
  </main>

  <div id="download-modal" class="modal-overlay hidden">
    <div class="modal-card">
      <div class="modal-top-bar">
        <div class="modal-title"><span>✨</span> Congratulations!</div>
        <button class="modal-close" onclick="closeDownloadModal()">✕</button>
      </div>

      <p style="font-size: 0.92rem; color: #334155; margin-bottom: 16px; text-align: left;">
        Your resume tailored for <strong>The Home Depot</strong> at <strong>LinkedIn</strong> is ready.
      </p>

      <div class="modal-banner">
        <p style="font-size: 0.78rem; color: #0369a1; text-align: left;">
          A resume tailored to the job posting increases your chances <strong>3×</strong> compared to a generic resume.
        </p>
      </div>

      <button class="modal-btn-primary" onclick="downloadPdf(false)">
        <span>✦</span> Download without watermark
      </button>

      <button class="modal-btn-orange" onclick="alert('Redirecting to Premium...')">
        <span>👑</span> Go Premium
      </button>

      <div style="margin-top: 12px;">
        <span class="modal-link-sub" onclick="downloadPdf(true)">Download with watermark</span>
      </div>
    </div>
  </div>

  <script>
    function triggerFilePicker() { document.getElementById('global-file-input').click(); }

    async function handleFileUpload(e) {
      const file = e.target.files[0];
      if (!file) return;
      document.getElementById('uploaded-file-name').innerText = file.name;
      const rawName = file.name.split('_')[0].split('.')[0];
      const name = rawName.charAt(0).toUpperCase() + rawName.slice(1);
      document.getElementById('uploaded-user-name').innerText = name;
      document.getElementById('greeting-title').innerText = `Hello ${name}, ready to apply?`;
      document.getElementById('upload-box-unuploaded').classList.add('hidden');
      document.getElementById('upload-box-uploaded').classList.remove('hidden');
    }

    function validateJobUrl() {
      const val = document.getElementById('job-url').value.trim();
      const trialBtn = document.getElementById('btn-trial');
      if (val.length > 5) {
        trialBtn.classList.remove('disabled');
        trialBtn.removeAttribute('disabled');
      } else {
        trialBtn.classList.add('disabled');
        trialBtn.setAttribute('disabled', 'true');
      }
    }

    async function startOptimizationProcess() {
      document.getElementById('preview-empty').classList.add('hidden');
      document.getElementById('preview-result').classList.add('hidden');
      document.getElementById('preview-stepwise').classList.remove('hidden');

      for (let i = 1; i <= 5; i++) {
        const stepEl = document.getElementById(`step-${i}`);
        const iconEl = document.getElementById(`icon-${i}`);
        stepEl.className = 'step-item active';
        iconEl.className = 'status-icon icon-active';
        await new Promise(r => setTimeout(r, 750));
        stepEl.className = 'step-item done';
        iconEl.className = 'status-icon icon-done';
        iconEl.innerHTML = '✓';
      }

      document.getElementById('preview-stepwise').classList.add('hidden');
      document.getElementById('preview-result').classList.remove('hidden');
    }

    function resetOptimizationView() {
      document.getElementById('preview-result').classList.add('hidden');
      document.getElementById('preview-empty').classList.remove('hidden');
    }

    function openDownloadModal() { document.getElementById('download-modal').classList.remove('hidden'); }
    function closeDownloadModal() { document.getElementById('download-modal').classList.add('hidden'); }

    // Download dynamic multi-page ATS CV PDF
    function downloadPdf(watermark) {
      const name = document.getElementById('uploaded-user-name').innerText;
      window.location.href = `/api/download-cv?name=${encodeURIComponent(name)}&watermark=${watermark}`;
      closeDownloadModal();
    }
  </script>
</body>
</html>
"""

# ============================================================
# API ENDPOINTS
# ============================================================
@app.route("/")
def home():
    return render_template_string(APP_HTML)

@app.route("/api/download-cv", methods=["GET"])
def download_cv():
    name = request.args.get("name", "KEDIR ABDELA")
    watermark_flag = request.args.get("watermark", "false").lower() == "true"

    cv_data = {
        "name": name,
        "title": "Digital Marketing Specialist (5 yrs exp)",
        "contact": "0908706534 | nmtullah86@gmail.com | Los Angeles",
        "links": "linkedin.com/in/kedirmohammed | Availability: 1 month"
    }

    pdf_stream = generate_ats_pdf(cv_data, watermark=watermark_flag)
    
    filename = f"{name.replace(' ', '_')}_Optimized_ATS_CV.pdf"
    return send_file(
        pdf_stream,
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=False)
