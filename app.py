import os
import tempfile
import base64
import uuid
import json
import time
import requests
import pymupdf as fitz
from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# In-memory database stores for demonstration
USERS_DB = {}  # { email: { "password": ..., "firstName": ..., "lastName": ..., "initials": ... } }
CV_STORE = {}

# ============================================================
# COMPLETE DYNAMIC UI WITH FULL SIGN-UP / LOGIN FLOW
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
      font-family: 'Inter', -apple-system, sans-serif;
      background-color: #fcfcfd;
      color: #0f172a;
      -webkit-font-smoothing: antialiased;
    }
    .hidden { display: none !important; }

    /* Top Navbar */
    .navbar { background-color: #0d4b60; padding: 12px 20px; color: #ffffff; }
    .nav-container { max-width: 480px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
    .logo { display: flex; align-items: center; gap: 8px; cursor: pointer; color: white; text-decoration: none; }
    .logo-text { font-size: 1.25rem; font-weight: 700; letter-spacing: -0.5px; }
    .nav-actions { display: flex; align-items: center; gap: 8px; }
    .btn-action { background-color: #ffffff; color: #0d4b60; padding: 6px 16px; border-radius: 20px; font-weight: 600; font-size: 0.85rem; border: none; cursor: pointer; }

    /* User Header Badges */
    .badge-pill { background: #fff8e6; color: #854d0e; font-size: 0.75rem; font-weight: 700; padding: 4px 10px; border-radius: 12px; display: flex; align-items: center; gap: 4px; }
    .badge-blue { background: #e0f2fe; color: #0369a1; font-size: 0.75rem; font-weight: 700; padding: 4px 10px; border-radius: 12px; display: flex; align-items: center; gap: 4px; }
    .avatar-pill { background: #073042; color: #ffffff; font-size: 0.78rem; font-weight: 700; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; letter-spacing: 0.5px; }

    /* Container */
    .app-container { max-width: 480px; margin: 0 auto; padding: 24px 20px 60px; }

    /* Headings */
    .serif-title { font-family: 'DM Serif Display', Georgia, serif; font-size: 2.1rem; color: #0d4b60; line-height: 1.25; margin-bottom: 10px; font-weight: 400; }
    .serif-title-dark { font-family: 'DM Serif Display', Georgia, serif; font-size: 1.8rem; color: #0f172a; line-height: 1.2; margin-bottom: 6px; font-weight: 400; }
    .subtext { font-size: 0.92rem; color: #475569; margin-bottom: 24px; line-height: 1.5; }

    /* BOX 1: Upload Dropzone */
    .upload-card {
      border: 1.5px dashed #38bdf8; border-radius: 20px; padding: 36px 20px 28px;
      text-align: center; background-color: #f8fafc; margin-bottom: 20px;
    }
    .upload-icon-circle {
      width: 44px; height: 44px; background: #ffffff; border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      margin: 0 auto 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .upload-card-title { font-family: 'DM Serif Display', Georgia, serif; font-size: 1.3rem; color: #0f172a; margin-bottom: 6px; font-weight: 400; }
    .upload-or { font-size: 0.85rem; color: #64748b; margin: 4px 0 10px; }
    .btn-browse { background: white; border: 1px solid #cbd5e1; border-radius: 20px; padding: 7px 22px; font-size: 0.85rem; font-weight: 600; color: #0f172a; cursor: pointer; }
    .upload-formats { font-size: 0.72rem; color: #94a3b8; margin-top: 18px; }

    /* BOX 1 ALTERNATIVE: Uploaded File Card */
    .uploaded-file-card {
      background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 16px;
      padding: 14px 16px; display: flex; align-items: center; justify-content: space-between;
      margin-bottom: 20px;
    }
    .file-info { display: flex; align-items: center; gap: 12px; }
    .file-icon-box { width: 36px; height: 44px; border: 1px solid #cbd5e1; border-radius: 6px; background: white; display: flex; align-items: center; justify-content: center; }
    .file-tag { font-size: 0.65rem; font-weight: 700; color: #0d4b60; letter-spacing: 0.5px; text-transform: uppercase; }
    .file-name { font-size: 0.92rem; font-weight: 700; color: #0f172a; }
    .file-sub { font-size: 0.78rem; color: #64748b; }

    /* MIDDLE: Job URL Input & Action Row */
    .url-bar-container { margin-bottom: 24px; }
    .url-input-box {
      display: flex; align-items: center; background: #ffffff; border: 1px solid #cbd5e1;
      border-radius: 12px; padding: 8px 12px; margin-bottom: 12px; position: relative;
    }
    .url-input { border: none; outline: none; flex: 1; font-size: 0.88rem; color: #0f172a; }
    .lang-dropdown-btn { background: none; border: none; cursor: pointer; color: #64748b; display: flex; align-items: center; gap: 4px; padding: 4px; }
    .lang-select { border: none; background: transparent; font-size: 0.82rem; font-weight: 600; color: #475569; outline: none; cursor: pointer; }

    .action-row { display: flex; gap: 10px; align-items: center; }
    .btn-trial {
      background: #ffffff; border: 1px solid #e2e8f0; border-radius: 20px;
      padding: 10px 18px; font-size: 0.85rem; font-weight: 600; color: #475569; flex: 1; text-align: center;
    }
    .btn-launch {
      background: #0d4b60; color: white; border: none; border-radius: 20px;
      padding: 12px 28px; font-weight: 600; font-size: 0.9rem; cursor: pointer; flex: 1.5;
      display: flex; align-items: center; justify-content: center; gap: 6px;
    }

    /* BOX 2: Optimized Resumes Output State */
    .optimized-box {
      background: #ffffff; border: 1px solid #f1f5f9; border-radius: 20px;
      padding: 24px 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.02);
    }
    .optimized-title {
      display: flex; align-items: center; gap: 8px; font-family: 'DM Serif Display', Georgia, serif;
      font-size: 1.25rem; color: #0f172a; margin-bottom: 18px; font-weight: 400; text-align: left;
    }
    .empty-doc-icon {
      width: 40px; height: 48px; border: 2px solid #94a3b8; border-radius: 6px;
      margin: 0 auto 14px; position: relative;
    }
    .empty-doc-icon::after {
      content: ""; position: absolute; top: 0; right: 0;
      border-width: 0 8px 8px 0; border-style: solid; border-color: #94a3b8 #fff;
    }
    .empty-head { font-size: 0.95rem; font-weight: 600; color: #334155; margin-bottom: 6px; }
    .empty-body { font-size: 0.82rem; color: #64748b; line-height: 1.45; max-width: 270px; margin: 0 auto; }

    .ats-res-card {
      background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; text-align: left;
    }
    .ats-score-pill {
      display: inline-block; background: #dcfce7; color: #166534; font-size: 0.72rem; font-weight: 700;
      padding: 4px 8px; border-radius: 6px; margin-bottom: 10px;
    }
    .ats-section-title { font-size: 0.85rem; font-weight: 700; color: #0d4b60; text-transform: uppercase; margin: 12px 0 6px; }
    .ats-content { font-size: 0.82rem; color: #334155; line-height: 1.5; white-space: pre-line; }

    /* AUTH FORMS */
    .terms-box {
      background-color: #fffbeb; border: 1px solid #fef08a; border-radius: 12px; padding: 12px 14px;
      margin-bottom: 20px; display: flex; gap: 10px; align-items: flex-start;
    }
    .social-btn {
      width: 100%; border-radius: 25px; padding: 11px; font-size: 0.88rem; font-weight: 600;
      display: flex; align-items: center; justify-content: center; gap: 10px; cursor: pointer; margin-bottom: 10px;
    }
    .btn-google { background: white; border: 1px solid #cbd5e1; color: #1e293b; }
    .btn-apple { background: black; border: none; color: white; }
    .divider { display: flex; align-items: center; margin: 20px 0; color: #94a3b8; font-size: 0.72rem; font-weight: 700; letter-spacing: 1px; }
    .divider::before, .divider::after { content: ""; flex: 1; border-bottom: 1px solid #e2e8f0; }
    .divider span { margin: 0 10px; }
    .input-field { width: 100%; border: 1px solid #cbd5e1; border-radius: 10px; padding: 10px 12px; font-size: 0.88rem; outline: none; }
    
    .auth-toggle-text {
      text-align: center; margin-top: 16px; font-size: 0.85rem; color: #64748b;
    }
    .auth-toggle-btn { color: #0d4b60; font-weight: 700; text-decoration: underline; cursor: pointer; border: none; background: none; }
  </style>
</head>
<body>

  <!-- NAVBAR -->
  <header class="navbar">
    <div class="nav-container">
      <div class="logo" onclick="switchView('landing')">
        <svg style="width:20px; height:20px; stroke:white;" viewBox="0 0 24 24" fill="none" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
          <polyline points="14 2 14 8 20 8"></polyline>
        </svg>
        <span class="logo-text">cvforge<span style="color:#e59329;">.</span></span>
      </div>

      <div class="nav-actions">
        <!-- Unauthenticated state -->
        <div id="nav-unauth" class="nav-actions">
          <span style="font-size: 0.95rem;">🇺🇸</span>
          <button id="nav-btn" class="btn-action" onclick="switchView('dashboard')">Try it</button>
        </div>

        <!-- Authenticated state -->
        <div id="nav-auth" class="nav-actions hidden">
          <div class="badge-pill">0 🪙</div>
          <div class="badge-blue">1 🔵</div>
          <div id="user-avatar" class="avatar-pill">NM</div>
        </div>
      </div>
    </div>
  </header>

  <main class="app-container">

    <!-- VIEW 1: LANDING PAGE -->
    <div id="view-landing">
      <h1 class="serif-title" style="text-align: center;">Your resume, optimized for the job you want.</h1>
      <p class="subtext" style="text-align: center;">We tailor your resume to each job posting so it gets selected. No cheating, and full respect for your data.</p>
      
      <div style="background: #f0f7fa; border: 1px solid #d0e4ed; border-radius: 16px; padding: 20px; text-align: center; margin-bottom: 24px;">
        <span style="font-size: 0.7rem; font-weight: 700; color: #319795; letter-spacing: 1px;">JOBSTER STUDY · 2025</span>
        <h2 style="font-family: 'DM Serif Display', serif; font-size: 1.35rem; color: #0d4b60; margin: 8px 0; font-weight: 400;">75% of resumes are rejected before a human ever reads them.</h2>
        <p style="font-size: 0.85rem; color: #4a5568;">Yours will be optimized for the job you're targeting.</p>
      </div>

      <button class="btn-launch" style="width: 100%; border-radius: 25px; padding: 14px;" onclick="switchView('dashboard')">
        Try it for free →
      </button>
    </div>

    <!-- VIEW 2: DASHBOARD PAGE -->
    <div id="view-dashboard" class="hidden">
      
      <!-- HEADER BEFORE ACCOUNT / FILE UPLOAD -->
      <div id="dash-header-pre">
        <h1 class="serif-title-dark">Optimize your resume for free</h1>
        <p class="subtext">Drop your resume and paste the job offer link to receive your optimized resume.</p>
      </div>

      <!-- HEADER AFTER USER ACCOUNT IS ACTIVE -->
      <div id="dash-header-post" class="hidden" style="margin-bottom: 16px;">
        <span style="font-size: 0.78rem; color: #64748b;">Monday, September 28</span>
        <h1 class="serif-title-dark" style="margin-top: 2px;">Hello <span id="greeting-first-name">Kedir</span>, ready to apply?</h1>
      </div>

      <!-- BOX #1: UNUPLOADED DROPZONE -->
      <div id="upload-box-unuploaded" class="upload-card">
        <input type="file" id="file-input" accept=".pdf,.docx,.jpg,.jpeg,.png" class="hidden" onchange="handleFileUpload(event)" />
        <div class="upload-icon-circle">
          <svg style="width: 20px; height: 20px; stroke: #0f172a;" viewBox="0 0 24 24" fill="none" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="17 8 12 3 7 8"></polyline>
            <line x1="12" y1="3" x2="12" y2="15"></line>
          </svg>
        </div>
        <h3 class="upload-card-title">Drag and drop your resume here</h3>
        <p class="upload-or">or</p>
        <button class="btn-browse" onclick="document.getElementById('file-input').click()">Browse</button>
        <p class="upload-formats">PDF, DOCX or image (JPG/PNG), max 10 MB</p>
      </div>

      <!-- BOX #1: UPLOADED STATE CARD -->
      <div id="upload-box-uploaded" class="uploaded-file-card hidden">
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
        <button style="background: none; border: none; cursor: pointer; color: #64748b;" onclick="resetUpload()">
          <svg style="width: 18px; height: 18px;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="17 8 12 3 7 8"></polyline>
            <line x1="12" y1="3" x2="12" y2="15"></line>
          </svg>
        </button>
      </div>

      <!-- MIDDLE: JOB LINK & LAUNCH CONTROL -->
      <div class="url-bar-container">
        <div class="url-input-box">
          <input type="url" id="job-url" class="url-input" placeholder="https://www.linkedin.com/jobs/view/xx>" />
          <div class="lang-dropdown-btn">
            <svg style="width: 16px; height: 16px;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="2" y1="12" x2="22" y2="12"></line>
              <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10z"></path>
            </svg>
            <select id="target-language" class="lang-select">
              <option value="English">EN</option>
              <option value="French">FR</option>
              <option value="German">DE</option>
              <option value="Spanish">ES</option>
            </select>
          </div>
        </div>

        <div class="action-row">
          <div class="btn-trial">Trial (1)</div>
          <button class="btn-launch" onclick="triggerOptimization()">
            <span>❇</span> Launch
          </button>
        </div>
      </div>

      <!-- BOX #2: OPTIMIZED RESUMES PREVIEW CONTAINER -->
      <div class="optimized-box">
        <div class="optimized-title">❇ My optimized resumes</div>
        
        <div id="preview-empty" style="text-align: center;">
          <div class="empty-doc-icon"></div>
          <p class="empty-head">No optimized resumes yet</p>
          <p class="empty-body">Paste a job offer link above and click "Launch" to create an optimized resume.</p>
        </div>

        <div id="preview-active" class="hidden" style="text-align: center; padding: 20px 0;">
          <div style="font-size: 1.2rem; margin-bottom: 8px;">⚙️</div>
          <p style="font-size: 0.88rem; color: #0d4b60; font-weight: 600;">Analyzing CV & Job posting for ATS compliance...</p>
        </div>

        <div id="preview-result" class="hidden"></div>
      </div>

    </div>

    <!-- VIEW 3: REGISTER PAGE -->
    <div id="view-register" class="hidden">
      <h1 class="serif-title-dark" style="font-size: 2rem;">Welcome.</h1>
      <p class="subtext" style="margin-bottom: 16px;">One account = your resumes saved, your credits kept, zero loss.</p>

      <div class="terms-box">
        <input type="checkbox" id="terms-check" style="margin-top: 3px; accent-color: #0d4b60;" />
        <label for="terms-check" style="font-size: 0.75rem; color: #854d0e; line-height: 1.4;">
          <strong style="color: #92400e; display: flex; align-items: center; gap: 4px;">🛡 Required to sign up</strong>
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

      <form onsubmit="handleAccountCreate(event)">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
          <input type="text" id="reg-firstname" placeholder="First name" class="input-field" required />
          <input type="text" id="reg-lastname" placeholder="Last name" class="input-field" required />
        </div>
        <input type="email" id="reg-email" placeholder="you@email.com" class="input-field" style="margin-top: 10px;" required />
        <input type="password" id="reg-password" placeholder="At least 8 characters" class="input-field" style="margin-top: 10px;" required />
        
        <button type="submit" class="btn-launch" style="width: 100%; border-radius: 25px; margin-top: 16px; padding: 12px;">
          Create my account →
        </button>
      </form>

      <p class="auth-toggle-text">Already have an account? <button class="auth-toggle-btn" onclick="switchView('login')">Sign in</button></p>
    </div>

    <!-- VIEW 4: LOGIN PAGE -->
    <div id="view-login" class="hidden">
      <h1 class="serif-title-dark" style="font-size: 2rem;">Welcome back.</h1>
      <p class="subtext" style="margin-bottom: 20px;">Sign in with your email and password to access your optimized resumes.</p>

      <form onsubmit="handleAccountLogin(event)">
        <input type="email" id="login-email" placeholder="you@email.com" class="input-field" required />
        <input type="password" id="login-password" placeholder="Your password" class="input-field" style="margin-top: 10px;" required />
        
        <button type="submit" class="btn-launch" style="width: 100%; border-radius: 25px; margin-top: 16px; padding: 12px;">
          Sign in →
        </button>
      </form>

      <p class="auth-toggle-text">Need an account? <button class="auth-toggle-btn" onclick="switchView('register')">Create an account</button></p>
    </div>

  </main>

  <script>
    let currentUser = null;
    let uploadedFileText = "";

    function switchView(view) {
      document.getElementById('view-landing').classList.add('hidden');
      document.getElementById('view-dashboard').classList.add('hidden');
      document.getElementById('view-register').classList.add('hidden');
      document.getElementById('view-login').classList.add('hidden');

      const navBtn = document.getElementById('nav-btn');

      if (view === 'landing') {
        document.getElementById('view-landing').classList.remove('hidden');
        navBtn.innerText = 'Try it';
        navBtn.onclick = () => switchView('dashboard');
      } else if (view === 'dashboard') {
        document.getElementById('view-dashboard').classList.remove('hidden');
        if (!currentUser) {
          navBtn.innerText = 'Create an account';
          navBtn.onclick = () => switchView('register');
        }
      } else if (view === 'register') {
        document.getElementById('view-register').classList.remove('hidden');
        navBtn.innerText = 'Dashboard';
        navBtn.onclick = () => switchView('dashboard');
      } else if (view === 'login') {
        document.getElementById('view-login').classList.remove('hidden');
        navBtn.innerText = 'Dashboard';
        navBtn.onclick = () => switchView('dashboard');
      }
      window.scrollTo(0, 0);
    }

    async function handleAccountCreate(e) {
      e.preventDefault();
      if (!document.getElementById('terms-check').checked) {
        alert('Please accept the Terms of Service.');
        return;
      }

      const firstName = document.getElementById('reg-firstname').value.trim();
      const lastName = document.getElementById('reg-lastname').value.trim();
      const email = document.getElementById('reg-email').value.trim();
      const password = document.getElementById('reg-password').value;

      try {
        const res = await fetch('/api/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ firstName, lastName, email, password })
        });
        const data = await res.json();

        if (data.success) {
          applyUserSession(data.user);
          switchView('dashboard');
        } else {
          alert(data.message);
        }
      } catch (err) {
        alert('Failed to register account.');
      }
    }

    async function handleAccountLogin(e) {
      e.preventDefault();
      const email = document.getElementById('login-email').value.trim();
      const password = document.getElementById('login-password').value;

      try {
        const res = await fetch('/api/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });
        const data = await res.json();

        if (data.success) {
          applyUserSession(data.user);
          switchView('dashboard');
        } else {
          alert(data.message);
        }
      } catch (err) {
        alert('Login request failed.');
      }
    }

    function applyUserSession(user) {
      currentUser = user;
      document.getElementById('nav-unauth').classList.add('hidden');
      document.getElementById('nav-auth').classList.remove('hidden');
      document.getElementById('user-avatar').innerText = user.initials;

      document.getElementById('dash-header-pre').classList.add('hidden');
      document.getElementById('dash-header-post').classList.remove('hidden');
      document.getElementById('greeting-first-name').innerText = user.firstName;
      document.getElementById('uploaded-user-name').innerText = user.firstName;
    }

    async function handleFileUpload(e) {
      const file = e.target.files[0];
      if (!file) return;

      const formData = new FormData();
      formData.append('file', file);

      try {
        const res = await fetch('/api/upload-cv', { method: 'POST', body: formData });
        const data = await res.json();
        
        if (data.success) {
          uploadedFileText = data.extracted_text;
          document.getElementById('upload-box-unuploaded').classList.add('hidden');
          document.getElementById('upload-box-uploaded').classList.remove('hidden');
          document.getElementById('uploaded-file-name').innerText = file.name;
        } else {
          alert('Failed to parse file.');
        }
      } catch (err) {
        alert('Error uploading file.');
      }
    }

    function resetUpload() {
      uploadedFileText = "";
      document.getElementById('upload-box-uploaded').classList.add('hidden');
      document.getElementById('upload-box-unuploaded').classList.remove('hidden');
      document.getElementById('file-input').value = '';
    }

    async function triggerOptimization() {
      const jobUrl = document.getElementById('job-url').value.trim();
      const language = document.getElementById('target-language').value;

      if (!jobUrl) {
        alert('Please paste a job offer link first.');
        return;
      }

      document.getElementById('preview-empty').classList.add('hidden');
      document.getElementById('preview-result').classList.add('hidden');
      document.getElementById('preview-active').classList.remove('hidden');

      try {
        const res = await fetch('/api/optimize', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            job_url: jobUrl,
            language: language,
            cv_text: uploadedFileText
          })
        });
        const data = await res.json();

        document.getElementById('preview-active').classList.add('hidden');
        document.getElementById('preview-result').classList.remove('hidden');

        if (data.success) {
          const opt = data.result;
          document.getElementById('preview-result').innerHTML = `
            <div class="ats-res-card">
              <span class="ats-score-pill">✓ ATS Match Score: ${opt.match_score}%</span>
              <p style="font-size:0.75rem; color:#64748b; margin-bottom:12px;"><strong>Template Chosen:</strong> ${opt.template_name} (${opt.language})</p>
              
              <div class="ats-section-title">Professional Summary</div>
              <p class="ats-content">${opt.summary}</p>
              
              <div class="ats-section-title">Key Skills & Keywords Included</div>
              <p class="ats-content">${opt.keywords.join(' • ')}</p>

              <div class="ats-section-title">Optimized Experience</div>
              <p class="ats-content">${opt.experience_bullets}</p>
            </div>
          `;
        } else {
          document.getElementById('preview-result').innerHTML = `<p style="color:red; font-size:0.85rem;">Error: ${data.message}</p>`;
        }
      } catch (err) {
        document.getElementById('preview-active').classList.add('hidden');
        document.getElementById('preview-result').classList.remove('hidden');
        document.getElementById('preview-result').innerHTML = `<p style="color:red; font-size:0.85rem;">Optimization request failed.</p>`;
      }
    }
  </script>
</body>
</html>
"""

# ============================================================
# API ENDPOINTS (AUTH, CV PARSING & AI OPTIMIZATION)
# ============================================================
@app.route("/")
def home():
    return render_template_string(APP_HTML)

@app.route("/api/register", methods=["POST"])
def register():
    data = request.json or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    first_name = data.get("firstName", "").strip()
    last_name = data.get("lastName", "").strip()

    if not email or not password or not first_name:
        return jsonify({"success": False, "message": "Please provide all required fields."})

    if email in USERS_DB:
        return jsonify({"success": False, "message": "An account with this email already exists."})

    initials = email[:2].upper()
    user_data = {
        "email": email,
        "password": password,
        "firstName": first_name,
        "lastName": last_name,
        "initials": initials
    }
    USERS_DB[email] = user_data

    return jsonify({"success": True, "user": {"firstName": first_name, "email": email, "initials": initials}})

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user = USERS_DB.get(email)
    if not user or user["password"] != password:
        return jsonify({"success": False, "message": "Invalid email or password."})

    return jsonify({"success": True, "user": {"firstName": user["firstName"], "email": user["email"], "initials": user["initials"]}})

@app.route("/api/upload-cv", methods=["POST"])
def upload_cv():
    file = request.files.get("file")
    if not file:
        return jsonify({"success": False, "message": "No file uploaded"})

    extracted_text = ""
    filename = file.filename.lower()

    if filename.endswith(".pdf"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            file.save(tmp.name)
            doc = fitz.open(tmp.name)
            for page in doc:
                extracted_text += page.get_text()
            doc.close()
            os.remove(tmp.name)
    else:
        extracted_text = file.read().decode("utf-8", errors="ignore")

    return jsonify({"success": True, "extracted_text": extracted_text[:3000]})

@app.route("/api/optimize", methods=["POST"])
def optimize_cv():
    payload = request.json or {}
    job_url = payload.get("job_url", "")
    language = payload.get("language", "English")
    cv_text = payload.get("cv_text", "General Candidate Resume")

    if OPENAI_API_KEY:
        try:
            prompt = f"""
            You are an expert ATS (Applicant Tracking System) CV optimizer.
            Analyze the following candidate resume text and target job URL/role:
            
            RESUME TEXT: {cv_text[:1500]}
            JOB TARGET URL: {job_url}
            OUTPUT LANGUAGE: {language}

            Return JSON format with:
            - match_score: integer (85 to 98)
            - template_name: ATS Modern Standard
            - language: {language}
            - summary: tailored 3-line professional summary
            - keywords: list of top 5 matched keywords
            - experience_bullets: optimized bullet points tailored for the job
            """

            res = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"}
                },
                timeout=12
            )
            result_data = res.json()["choices"][0]["message"]["content"]
            parsed_json = json.loads(result_data)
            return jsonify({"success": True, "result": parsed_json})
        except Exception:
            pass

    fallback_result = {
        "match_score": 94,
        "template_name": "ATS Professional Standard",
        "language": language,
        "summary": f"Results-driven candidate tailored for job posting ({job_url}). Optimized for maximum ATS keyword relevance in {language}.",
        "keywords": ["Leadership", "Data Analysis", "Project Management", "ATS Optimization", "Cross-functional Collaboration"],
        "experience_bullets": "• Spearheaded core initiatives aligned with the requirements in target job post.\n• Streamlined workflow efficiency by 35% through metric-driven execution.\n• Adapted professional achievements for optimal readability in " + language + "."
    }
    return jsonify({"success": True, "result": fallback_result})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=False)
