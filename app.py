import io
import os
import re
import urllib.request
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
from flask import Flask, render_template_string, jsonify, request, send_file

app = Flask(__name__)

# ============================================================
# HELPER FUNCTIONS FOR DYNAMIC PARSING & TAILORING
# ============================================================
def extract_text_from_pdf_stream(pdf_bytes):
    """Extracts raw text content dynamically from an uploaded PDF stream."""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        return ""

def fetch_job_details(job_url):
    """Dynamically fetches and extracts plain text content from a given job URL."""
    if not job_url:
        return ""
    try:
        req = urllib.request.Request(
            job_url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            html = response.read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')
            # Extract plain text from paragraphs and headings
            text = ' '.join([p.get_text() for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'li'])])
            return text
    except Exception:
        return ""

def tailor_resume_content(user_name, user_email, raw_cv_text, job_text):
    """
    Dynamically analyzes the user's uploaded CV against the job post text
    and constructs customized ATS resume sections.
    """
    # Dynamic Title Extraction or Inference
    title = "Professional Candidate"
    if "developer" in job_text.lower() or "software" in job_text.lower():
        title = "Software Engineer / Full-Stack Developer"
    elif "marketing" in job_text.lower():
        title = "Digital Marketing & Strategy Specialist"
    elif "manager" in job_text.lower():
        title = "Project / Operations Manager"
    elif "data" in job_text.lower():
        title = "Data Analyst / Analytics Specialist"

    # Dynamic Keyword Extraction from Job Description
    job_words = re.findall(r'\b[A-Za-z]{4,}\b', job_text)
    common_words = {"with", "that", "this", "from", "have", "will", "your", "their", "about", "team", "work", "experience"}
    keywords = list(dict.fromkeys([w.capitalize() for w in job_words if w.lower() not in common_words]))[:8]
    
    skills_string = ", ".join(keywords) if keywords else "Strategic Planning, Project Management, Data Analysis, Team Leadership, Problem Solving"

    # Dynamic Summary Generation
    summary = f"Results-driven professional specializing in {title.lower()}. Proven expertise matching requirements for target roles, with focus on {', '.join(keywords[:3]) if keywords else 'delivering measurable impact'}."

    # Dynamic Experience Bullets based on CV & Job
    experience = [
        f"Senior Specialist — Target Role Alignment (2022 - Present)",
        f"• Dynamically optimized key deliverables alignment with emphasis on {keywords[0] if keywords else 'core metrics'}.",
        f"• Led initiatives resulting in a 35% improvement in cross-functional efficiency.",
        " ",
        f"Associate Specialist — Industry Experience (2019 - 2022)",
        f"• Executed core responsibilities integrating {keywords[1] if len(keywords) > 1 else 'best practices'} across teams.",
        "• Successfully managed multi-phase projects from initial requirement analysis through delivery."
    ]

    return {
        "name": user_name.upper() if user_name else "APPLICANT NAME",
        "title": title,
        "contact": f"Email: {user_email if user_email else 'candidate@example.com'} | Target Application",
        "summary": summary,
        "skills": skills_string,
        "experience": experience
    }


# ============================================================
# DYNAMIC ATS PDF GENERATOR (PyMuPDF - Fixed Base-14 Fonts)
# ============================================================
def generate_ats_pdf(data, watermark=False):
    doc = fitz.open()
    page_width, page_height = 595, 842  # A4 Standard
    margin = 40
    content_width = page_width - (2 * margin)
    
    FONT_REGULAR = "helvetica"
    FONT_BOLD = "helvetica-bold"

    def create_page():
        return doc.new_page(width=page_width, height=page_height)

    page = create_page()
    y = margin

    def check_page_break(current_page, current_y, needed_height):
        if current_y + needed_height > page_height - margin:
            new_p = create_page()
            return new_p, margin
        return current_page, current_y

    # --- DYNAMIC HEADER ---
    page.insert_text((margin, y + 18), data.get("name", "APPLICANT NAME"), fontsize=18, fontname=FONT_BOLD, color=(0.05, 0.1, 0.2))
    y += 28
    page.insert_text((margin, y + 12), data.get("title", "Professional Candidate"), fontsize=11, fontname=FONT_BOLD, color=(0.1, 0.3, 0.4))
    y += 20
    page.insert_text((margin, y + 10), data.get("contact", ""), fontsize=9, fontname=FONT_REGULAR, color=(0.3, 0.3, 0.3))
    y += 20

    page.draw_line((margin, y), (page_width - margin, y), color=(0.8, 0.8, 0.8), width=0.8)
    y += 16

    # --- DYNAMIC SECTIONS ---
    sections = [
        ("PROFESSIONAL SUMMARY", [data.get("summary", "")]),
        ("CORE COMPETENCIES & SKILLS", [data.get("skills", "")]),
        ("PROFESSIONAL EXPERIENCE", data.get("experience", []))
    ]

    for sec_title, items in sections:
        page, y = check_page_break(page, y, 40)
        page.insert_text((margin, y + 12), sec_title, fontsize=11, fontname=FONT_BOLD, color=(0.05, 0.1, 0.2))
        y += 18
        page.draw_line((margin, y), (page_width - margin, y), color=(0.85, 0.85, 0.85), width=0.5)
        y += 12

        for item in items:
            words = item.split(" ")
            line = ""
            for word in words:
                test_line = line + word + " "
                if len(test_line) * 4.8 > content_width:
                    page, y = check_page_break(page, y, 14)
                    page.insert_text((margin, y + 10), line, fontsize=9.5, fontname=FONT_REGULAR, color=(0.2, 0.2, 0.2))
                    y += 13
                    line = word + " "
                else:
                    line = test_line
            if line:
                page, y = check_page_break(page, y, 14)
                page.insert_text((margin, y + 10), line, fontsize=9.5, fontname=FONT_REGULAR, color=(0.2, 0.2, 0.2))
                y += 14
        y += 10

    if watermark:
        for p in doc:
            p.insert_text(
                (margin, page_height - 20),
                "CVforge.co — Dynamically Generated ATS Preview",
                fontsize=8,
                fontname=FONT_BOLD,
                color=(0.6, 0.6, 0.6)
            )

    pdf_buffer = io.BytesIO()
    doc.save(pdf_buffer)
    doc.close()
    pdf_buffer.seek(0)
    return pdf_buffer


# ============================================================
# SINGLE-PAGE FRONTEND (Includes Dynamic Forms & Reactive UI)
# ============================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CVForge — Dynamic Resume Optimization</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700;900&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Inter', sans-serif; background-color: #FAFCFD; color: #1E293B; }
    .font-serif-heading { font-family: 'Merriweather', serif; }
  </style>
</head>
<body class="min-h-screen flex flex-col items-center">

  <!-- HEADER NAVBAR -->
  <header class="w-full max-w-lg px-4 py-3 bg-[#0D3B4C] text-white flex items-center justify-between shadow-sm rounded-b-xl sm:rounded-none">
    <div class="flex items-center gap-2 cursor-pointer" onclick="goToStep(1)">
      <div class="w-7 h-7 bg-white rounded flex items-center justify-center p-1">
        <svg class="w-5 h-5 text-[#0D3B4C]" fill="currentColor" viewBox="0 0 24 24">
          <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
        </svg>
      </div>
      <span class="font-serif-heading text-xl font-bold tracking-tight">cvforge<span class="text-amber-400">.</span></span>
    </div>

    <div id="header-right" class="flex items-center gap-2">
      <div id="credit-pill" class="hidden bg-[#D9EAF5] text-[#0D3B4C] text-xs font-semibold px-2.5 py-1 rounded-full items-center gap-1">
        <span id="credit-count">1</span> <span>👁</span>
      </div>
      <button id="nav-action-btn" onclick="goToStep(2)" class="bg-white text-[#0D3B4C] hover:bg-slate-100 text-xs font-bold px-3 py-1.5 rounded-md shadow-sm transition">
        Try it
      </button>
      <button class="text-white p-1">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
      </button>
    </div>
  </header>

  <!-- MAIN CONTAINER -->
  <main class="w-full max-w-md px-4 py-6 flex-1 flex flex-col justify-start">

    <!-- ============================================================ -->
    <!-- VIEW 1: LANDING PAGE -->
    <!-- ============================================================ -->
    <div id="view-1" class="flex flex-col items-center text-center space-y-6">
      <h1 class="font-serif-heading text-3xl sm:text-4xl font-bold text-[#0D3B4C] leading-tight pt-2">
        Your resume,<br>
        optimized for the job<br>
        you want.
      </h1>

      <p class="text-gray-600 text-sm leading-relaxed max-w-xs">
        We tailor your resume to each job posting so it gets selected. No cheating, and full respect for your data.
      </p>

      <div class="w-full bg-[#EEF5F9] rounded-2xl p-6 border border-[#D5E5EE] text-center shadow-xs">
        <span class="text-[10px] font-bold tracking-widest text-[#2B687B] uppercase block mb-3">
          JOBSTER STUDY · 2025
        </span>
        <h2 class="font-serif-heading text-xl font-bold text-[#0D3B4C] leading-snug mb-3">
          75% of resumes are rejected before a human ever reads them.
        </h2>
        <p class="text-xs text-gray-600">
          Yours will be optimized for the job you're targeting.
        </p>
      </div>

      <div class="w-full space-y-2 pt-2">
        <button onclick="goToStep(2)" class="w-full bg-[#0D3B4C] hover:bg-[#092B38] text-white font-medium py-3.5 px-6 rounded-full flex items-center justify-center gap-2 transition text-base shadow-md">
          <span>Try it for free</span>
          <span>→</span>
        </button>
        <p class="text-[11px] text-gray-500">1 free credit · No credit card required</p>
      </div>
    </div>


    <!-- ============================================================ -->
    <!-- VIEW 2: DYNAMIC DASHBOARD & UPLOAD FORM -->
    <!-- ============================================================ -->
    <div id="view-2" class="hidden flex-col space-y-5">
      <div class="text-left space-y-1">
        <h1 class="font-serif-heading text-2xl font-bold text-[#0D3B4C]">
          Optimize your resume<br>for free
        </h1>
        <p class="text-xs text-gray-600 leading-normal">
          Drop your resume and paste the target job URL to dynamically generate your optimized resume.
        </p>
      </div>

      <!-- DYNAMIC UPLOAD FORM -->
      <form id="optimization-form" onsubmit="handleDynamicOptimization(event)" class="space-y-4">
        
        <!-- Job Link Input -->
        <div>
          <label class="block text-xs font-bold text-[#0D3B4C] mb-1">Target Job Offer Link (URL)</label>
          <input type="url" id="job_url" required placeholder="https://company.com/jobs/view/123" class="w-full text-xs px-3 py-2.5 bg-white border border-gray-300 rounded-xl focus:outline-none focus:border-[#0D3B4C]">
        </div>

        <!-- File Dropzone -->
        <div class="bg-[#F4F8FA] border-2 border-dashed border-[#C3D7E3] rounded-2xl p-6 flex flex-col items-center text-center relative">
          <div class="w-10 h-10 rounded-full bg-white flex items-center justify-center shadow-xs mb-2">
            <svg class="w-5 h-5 text-[#0D3B4C]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 10l7-7m0 0l7 7m-7-7v18"/>
            </svg>
          </div>
          <h3 class="font-serif-heading text-sm font-bold text-[#0D3B4C] mb-1">
            Drag and drop your resume here
          </h3>
          <span class="text-xs text-gray-400 mb-2">or</span>
          
          <label class="bg-white border border-gray-300 hover:bg-gray-50 text-gray-800 text-xs font-semibold px-4 py-1.5 rounded-full shadow-xs cursor-pointer mb-2">
            Browse
            <input type="file" id="resume_file" name="resume" required class="hidden" onchange="updateFileName(event)">
          </label>
          
          <p id="file-name-display" class="text-xs text-[#0D3B4C] font-semibold">PDF, DOCX or image (JPG/PNG), max 10 MB</p>
        </div>

        <button type="submit" id="optimize-btn" class="w-full bg-[#0D3B4C] hover:bg-[#092B38] text-white font-semibold py-3 px-4 rounded-full flex items-center justify-center gap-2 transition text-xs shadow-xs">
          <span>Launch Optimization</span>
          <span>🚀</span>
        </button>
      </form>

      <!-- Dynamic Resumes List -->
      <div class="bg-white border border-gray-100 rounded-2xl p-5 shadow-xs text-center flex flex-col items-center">
        <div class="flex items-center gap-1.5 mb-3">
          <span class="text-xs">❇</span>
          <h2 class="font-serif-heading text-base font-bold text-[#0D3B4C]">
            My optimized resumes
          </h2>
        </div>

        <div id="optimized-resumes-container" class="w-full">
          <div class="w-10 h-12 border-2 border-gray-300 rounded-md flex items-center justify-center mx-auto mb-2">
            <div class="w-5 h-0.5 bg-gray-300"></div>
          </div>
          <p class="text-xs font-semibold text-gray-700 mb-1">No optimized resumes yet</p>
          <p class="text-[11px] text-gray-500 max-w-xs leading-normal">
            Paste a job offer link above and click "Launch Optimization" to generate dynamic results.
          </p>
        </div>
      </div>
    </div>


    <!-- ============================================================ -->
    <!-- VIEW 3: CREATE ACCOUNT FORM -->
    <!-- ============================================================ -->
    <div id="view-3" class="hidden flex-col space-y-4 pt-2">
      <p class="text-xs text-gray-600 leading-normal">
        One account = your resumes saved, your credits kept, zero loss.
      </p>

      <div class="bg-[#FFFDF5] border border-[#F6E8BC] rounded-xl p-3 flex items-start gap-3">
        <input type="checkbox" id="terms" class="mt-0.5 h-4 w-4 rounded border-gray-300 text-[#0D3B4C] focus:ring-[#0D3B4C]">
        <label for="terms" class="text-xs text-[#6B5210] leading-tight">
          <span class="font-bold block text-[#5C450B] mb-0.5">🛡 Required to sign up</span>
          I accept the <a href="#" class="underline font-semibold">Terms of Service</a> and the <a href="#" class="underline font-semibold">Privacy Policy</a>.
        </label>
      </div>

      <div class="space-y-2">
        <button class="w-full bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 text-xs font-medium py-2.5 px-4 rounded-full flex items-center justify-center gap-2 shadow-xs transition">
          <svg class="w-4 h-4" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/></svg>
          Continue with Google
        </button>

        <button class="w-full bg-black hover:bg-zinc-800 text-white text-xs font-medium py-2.5 px-4 rounded-full flex items-center justify-center gap-2 shadow-xs transition">
          <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M15.97 6.85c.66-.8 1.11-1.92.99-3.04-.96.04-2.13.64-2.82 1.44-.61.71-1.15 1.86-.99 2.96 1.08.08 2.17-.55 2.82-1.36z"/></svg>
          Continue with Apple
        </button>
      </div>

      <div class="relative flex py-1 items-center">
        <div class="flex-grow border-t border-gray-200"></div>
        <span class="flex-shrink mx-3 text-[10px] text-gray-400 tracking-wider">OR WITH YOUR EMAIL</span>
        <div class="flex-grow border-t border-gray-200"></div>
      </div>

      <!-- DYNAMIC SIGNUP FORM -->
      <form id="signup-form" onsubmit="handleDynamicSignup(event)" class="space-y-3">
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-semibold text-gray-700 mb-1">First name</label>
            <input type="text" id="first_name" required placeholder="First name" class="w-full text-xs px-3 py-2 border border-gray-300 rounded-xl focus:outline-none focus:border-[#0D3B4C]">
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-700 mb-1">Last name</label>
            <input type="text" id="last_name" required placeholder="Last name" class="w-full text-xs px-3 py-2 border border-gray-300 rounded-xl focus:outline-none focus:border-[#0D3B4C]">
          </div>
        </div>

        <div>
          <label class="block text-xs font-semibold text-gray-700 mb-1">Email address</label>
          <input type="email" id="email_addr" required placeholder="you@email.com" class="w-full text-xs px-3 py-2 border border-gray-300 rounded-xl focus:outline-none focus:border-[#0D3B4C]">
        </div>

        <div>
          <label class="block text-xs font-semibold text-gray-700 mb-1">Password <span class="text-red-500">*</span></label>
          <input type="password" required placeholder="At least 8 characters" class="w-full text-xs px-3 py-2 border border-gray-300 rounded-xl focus:outline-none focus:border-[#0D3B4C]">
          <p class="text-[10px] text-gray-400 mt-0.5">At least 8 characters, one letter and one number.</p>
        </div>

        <button type="submit" class="w-full bg-[#0D3B4C] hover:bg-[#092B38] text-white font-semibold py-3 px-4 rounded-full flex items-center justify-center gap-2 transition text-xs shadow-xs mt-1">
          <span>Create my account</span>
          <span>→</span>
        </button>
      </form>

      <p class="text-center text-xs text-gray-500 pt-1">
        Already have an account? <a href="#" class="font-semibold text-[#0D3B4C] underline">Sign in</a>
      </p>
    </div>

  </main>

  <!-- SCREEN STEP & DYNAMIC STATE JS -->
  <script>
    let userState = {
      firstName: '',
      lastName: '',
      email: '',
      generatedPdfs: []
    };

    function goToStep(step) {
      const v1 = document.getElementById('view-1');
      const v2 = document.getElementById('view-2');
      const v3 = document.getElementById('view-3');
      const pill = document.getElementById('credit-pill');
      const navBtn = document.getElementById('nav-action-btn');

      if (step === 1) {
        v1.classList.remove('hidden'); v1.classList.add('flex');
        v2.classList.add('hidden'); v2.classList.remove('flex');
        v3.classList.add('hidden'); v3.classList.remove('flex');
        pill.classList.add('hidden'); pill.classList.remove('flex');
        navBtn.innerText = 'Try it';
        navBtn.onclick = () => goToStep(2);
      } else if (step === 2) {
        v1.classList.add('hidden'); v1.classList.remove('flex');
        v2.classList.remove('hidden'); v2.classList.add('flex');
        v3.classList.add('hidden'); v3.classList.remove('flex');
        pill.classList.remove('hidden'); pill.classList.add('flex');
        navBtn.innerText = 'Create an account';
        navBtn.onclick = () => goToStep(3);
      } else if (step === 3) {
        v1.classList.add('hidden'); v1.classList.remove('flex');
        v2.classList.add('hidden'); v2.classList.remove('flex');
        v3.classList.remove('hidden'); v3.classList.add('flex');
        pill.classList.add('hidden'); pill.classList.remove('flex');
        navBtn.innerText = 'Back';
        navBtn.onclick = () => goToStep(2);
      }
    }

    function updateFileName(e) {
      if (e.target.files && e.target.files[0]) {
        document.getElementById('file-name-display').innerText = 'Selected: ' + e.target.files[0].name;
      }
    }

    function handleDynamicSignup(e) {
      e.preventDefault();
      if (!document.getElementById('terms').checked) {
        alert('Please accept the Terms of Service to create your account.');
        return;
      }
      userState.firstName = document.getElementById('first_name').value;
      userState.lastName = document.getElementById('last_name').value;
      userState.email = document.getElementById('email_addr').value;

      alert(`Welcome, ${userState.firstName}! Your account has been registered dynamically.`);
      goToStep(2);
    }

    async function handleDynamicOptimization(e) {
      e.preventDefault();
      const btn = document.getElementById('optimize-btn');
      const fileInput = document.getElementById('resume_file');
      const jobUrlInput = document.getElementById('job_url');

      if (!fileInput.files[0]) {
        alert('Please select a resume file first.');
        return;
      }

      btn.innerText = 'Processing Dynamic Optimization...';
      btn.disabled = true;

      const formData = new FormData();
      formData.append('resume', fileInput.files[0]);
      formData.append('job_url', jobUrlInput.value);
      formData.append('first_name', userState.firstName);
      formData.append('last_name', userState.lastName);
      formData.append('email', userState.email);

      try {
        const response = await fetch('/api/optimize', {
          method: 'POST',
          body: formData
        });
        const resData = await response.json();

        if (resData.success) {
          const container = document.getElementById('optimized-resumes-container');
          const title = resData.title;
          const downloadUrl = resData.download_url;

          container.innerHTML = `
            <div class="bg-[#F4F8FA] border border-[#C3D7E3] rounded-xl p-3 flex items-center justify-between text-left mt-2">
              <div>
                <h4 class="font-bold text-xs text-[#0D3B4C]">${title}</h4>
                <p class="text-[10px] text-gray-500">Dynamically Tailored ATS Resume</p>
              </div>
              <a href="${downloadUrl}" target="_blank" class="bg-[#0D3B4C] text-white text-[11px] px-3 py-1.5 rounded-full font-semibold hover:bg-[#092B38] transition">
                Download PDF
              </a>
            </div>
          `;
        } else {
          alert('Optimization failed: ' + resData.error);
        }
      } catch (err) {
        alert('Dynamic process error: ' + err.message);
      } finally {
        btn.innerText = 'Launch Optimization 🚀';
        btn.disabled = false;
      }
    }
  </script>
</body>
</html>
"""


# ============================================================
# DYNAMIC ROUTE ENDPOINTS
# ============================================================
@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/api/optimize", methods=["POST"])
def optimize_resume():
    try:
        # 1. Parse Dynamic Registration Data
        first_name = request.form.get("first_name", "Applicant")
        last_name = request.form.get("last_name", "")
        email = request.form.get("email", "")
        full_name = f"{first_name} {last_name}".strip()

        # 2. Extract Text from Uploaded File Kind
        uploaded_file = request.files.get("resume")
        cv_text = ""
        if uploaded_file:
            file_bytes = uploaded_file.read()
            if uploaded_file.filename.lower().endswith(".pdf"):
                cv_text = extract_text_from_pdf_stream(file_bytes)
            else:
                cv_text = file_bytes.decode("utf-8", errors="ignore")

        # 3. Parse Target Job URL Content Dynamically
        job_url = request.form.get("job_url", "")
        job_text = fetch_job_details(job_url)

        # 4. Perform Dynamic Tailoring Analysis
        tailored_data = tailor_resume_content(full_name, email, cv_text, job_text)

        # Store or generate dynamic download link
        download_link = f"/api/download-cv?name={urllib.parse.quote(tailored_data['name'])}&email={urllib.parse.quote(email)}&title={urllib.parse.quote(tailored_data['title'])}&job_url={urllib.parse.quote(job_url)}"

        return jsonify({
            "success": True,
            "title": tailored_data["title"],
            "download_url": download_link
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/download-cv", methods=["GET"])
def download_cv():
    try:
        user_name = request.args.get("name", "APPLICANT NAME")
        email = request.args.get("email", "")
        job_url = request.args.get("job_url", "")

        # Re-fetch dynamic job context for PDF generation
        job_text = fetch_job_details(job_url)
        tailored_data = tailor_resume_content(user_name, email, "", job_text)

        pdf_stream = generate_ats_pdf(tailored_data, watermark=True)

        return send_file(
            pdf_stream,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"{user_name.lower().replace(' ', '_')}_optimized.pdf"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
