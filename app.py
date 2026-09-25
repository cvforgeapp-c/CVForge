import os
import tempfile
import base64
import uuid
from flask import Flask, request, render_template_string, send_file

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, FrameBreak, NextPageTemplate
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ============================================================
# 1. FONT CONFIGURATION & SAFE FALLBACKS
# ============================================================

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
MONTSERRAT_EXTRA_BOLD = os.path.join(FONT_DIR, "Montserrat-ExtraBold.ttf")
DANCING_SCRIPT = os.path.join(FONT_DIR, "DancingScript-Regular.ttf")

FONT_TITLE = "Helvetica-Bold"
FONT_SIG = "Helvetica-BoldOblique"

if os.path.exists(MONTSERRAT_EXTRA_BOLD):
    try:
        pdfmetrics.registerFont(TTFont("Montserrat-ExtraBold", MONTSERRAT_EXTRA_BOLD))
        FONT_TITLE = "Montserrat-ExtraBold"
    except Exception:
        pass

if os.path.exists(DANCING_SCRIPT):
    try:
        pdfmetrics.registerFont(TTFont("DancingScript", DANCING_SCRIPT))
        FONT_SIG = "DancingScript"
    except Exception:
        pass

app = Flask(__name__)

# ============================================================
# 2. PLATYPUS FLOWABLE CV GENERATOR
# ============================================================

def generate_pdf(data, output_filename):
    # Colors
    sidebar_bg = colors.HexColor(data.get("sidebar_color") or "#02353C")
    gold_accent = colors.HexColor(data.get("accent_color") or "#E5A93C")
    title_dark = colors.HexColor("#0D3B4C")
    body_muted = colors.HexColor("#334E58")
    white = colors.white

    # Dimensions
    PAGE_W, PAGE_H = A4
    sidebar_w = 72 * mm
    main_w = PAGE_W - sidebar_w

    doc = BaseDocTemplate(
        output_filename,
        pagesize=A4,
        leftMargin=0,
        rightMargin=0,
        topMargin=0,
        bottomMargin=0
    )

    # Frame definitions for two-column flow
    # Sidebar frame: padded slightly inside the colored panel
    frame_sidebar = Frame(
        8 * mm, 10 * mm, sidebar_w - 14 * mm, PAGE_H - 20 * mm,
        id='sidebar_frame', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0
    )
    # Main frame: right column
    frame_main = Frame(
        sidebar_w + 8 * mm, 10 * mm, main_w - 16 * mm, PAGE_H - 20 * mm,
        id='main_frame', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0
    )

    # Background canvas background callback for multi-page support
    def draw_background(canvas, document):
        canvas.saveState()
        # Main background
        canvas.setFillColor(colors.HexColor("#FAFCFB"))
        canvas.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
        # Left sidebar panel background
        canvas.setFillColor(sidebar_bg)
        canvas.rect(0, 0, sidebar_w, PAGE_H, stroke=0, fill=1)
        canvas.restoreState()

    # Register Page Template
    two_col_template = PageTemplate(
        id='TwoCol',
        frames=[frame_sidebar, frame_main],
        onPage=draw_background
    )
    doc.addPageTemplates([two_col_template])

    # Styles
    base_styles = getSampleStyleSheet()
    
    # Sidebar Paragraph Styles
    style_sb_heading = ParagraphStyle(
        'SBHeading', parent=base_styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10, leading=13,
        textColor=gold_accent, spaceAfter=2
    )
    style_sb_text = ParagraphStyle(
        'SBText', parent=base_styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=11,
        textColor=white, spaceAfter=3
    )

    # Main Area Paragraph Styles
    style_main_name = ParagraphStyle(
        'MainName', parent=base_styles['Normal'],
        fontName=FONT_TITLE, fontSize=20, leading=22,
        textColor=title_dark, spaceAfter=2
    )
    style_main_title = ParagraphStyle(
        'MainTitle', parent=base_styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11, leading=13,
        textColor=gold_accent, spaceAfter=8
    )
    style_main_summary = ParagraphStyle(
        'MainSummary', parent=base_styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=11.5,
        textColor=body_muted, spaceAfter=10
    )
    style_sec_heading = ParagraphStyle(
        'SecHeading', parent=base_styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11, leading=13,
        textColor=title_dark, spaceAfter=0
    )
    style_item_title = ParagraphStyle(
        'ItemTitle', parent=base_styles['Normal'],
        fontName='Helvetica-Bold', fontSize=9.5, leading=12,
        textColor=title_dark
    )
    style_item_sub = ParagraphStyle(
        'ItemSub', parent=base_styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=8.5, leading=11,
        textColor=body_muted, spaceAfter=3
    )
    style_bullet = ParagraphStyle(
        'BulletText', parent=base_styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=11.5,
        textColor=body_muted, spaceAfter=2
    )
    style_sig = ParagraphStyle(
        'SigText', parent=base_styles['Normal'],
        fontName=FONT_SIG, fontSize=16 if FONT_SIG == "DancingScript" else 11, leading=18,
        textColor=title_dark, spaceBefore=8
    )

    story = []

    # ----------------------------------------------------
    # SIDEBAR FLOWABLES (Fills Sidebar Frame)
    # ----------------------------------------------------

    def add_sb_header(title):
        story.append(Paragraph(title.upper(), style_sb_heading))
        # Divider line
        t = Table([['']], colWidths=[sidebar_w - 14 * mm], rowHeights=[1 * mm])
        t.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 1, gold_accent),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(t)
        story.append(Spacer(1, 4 * mm))

    # Contact Details
    add_sb_header("Contact")
    for key, label in [("phone", "Phone"), ("email", "Email"), ("location", "Location"), ("linkedin", "LinkedIn"), ("website", "Website")]:
        val = data.get(key)
        if val and str(val).strip():
            story.append(Paragraph(f"<b>{label}:</b> {val.strip()}", style_sb_text))
    story.append(Spacer(1, 4 * mm))

    # Skills Details
    if data.get("skills"):
        add_sb_header("Skills")
        for skill in data["skills"].splitlines():
            if skill.strip():
                story.append(Paragraph(f"• {skill.strip().lstrip('• ')}", style_sb_text))
        story.append(Spacer(1, 4 * mm))

    # Languages
    if data.get("languages"):
        add_sb_header("Languages")
        for lang in data["languages"].splitlines():
            if lang.strip():
                story.append(Paragraph(f"• {lang.strip().lstrip('• ')}", style_sb_text))
        story.append(Spacer(1, 4 * mm))

    # Interests & Hobbies
    if data.get("hobbies"):
        add_sb_header("Interests")
        for hobby in data["hobbies"].splitlines():
            if hobby.strip():
                story.append(Paragraph(f"• {hobby.strip().lstrip('• ')}", style_sb_text))

    # BREAK TO MAIN COLUMN
    story.append(FrameBreak())

    # ----------------------------------------------------
    # MAIN COLUMN FLOWABLES (Fills Main Frame)
    # ----------------------------------------------------

    # Name & Title Header
    name_str = (data.get("name") or "KEDIR ABDELA").upper()
    title_str = (data.get("title") or "BUSINESS MARKETING").upper()
    story.append(Paragraph(name_str, style_main_name))
    story.append(Paragraph(title_str, style_main_title))

    # Summary Section
    if data.get("summary"):
        story.append(Paragraph(data["summary"], style_main_summary))

    def add_main_header(title):
        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph(title.upper(), style_sec_heading))
        t = Table([['']], colWidths=[main_w - 16 * mm], rowHeights=[1 * mm])
        t.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 1, gold_accent),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(t)
        story.append(Spacer(1, 4 * mm))

    # Work Experience Section
    if data.get("experience"):
        add_main_header("Experience")
        blocks = data["experience"].split("\n\n")
        for block in blocks:
            lines = [l.strip() for l in block.splitlines() if l.strip()]
            if not lines:
                continue
            
            header_parts = [p.strip() for p in lines[0].split("|")]
            role = header_parts[0]
            sub = header_parts[1] if len(header_parts) > 1 else ""
            date_str = header_parts[2] if len(header_parts) > 2 else ""

            # Use Table for header line to keep Role left aligned and Date right aligned
            p_role = Paragraph(f"<b>{role}</b>", style_item_title)
            p_date = Paragraph(f"<font color='{body_muted.hexval()}'>{date_str}</font>", style_item_title)
            t_hdr = Table([[p_role, p_date]], colWidths=[(main_w - 16 * mm) * 0.7, (main_w - 16 * mm) * 0.3])
            t_hdr.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            story.append(t_hdr)

            if sub:
                story.append(Paragraph(sub, style_item_sub))

            for bline in lines[1:]:
                clean_line = bline.lstrip("• ").strip()
                story.append(Paragraph(f"• {clean_line}", style_bullet))
            story.append(Spacer(1, 3 * mm))

    # Education Section
    if data.get("education"):
        add_main_header("Education")
        blocks = data["education"].split("\n\n")
        for block in blocks:
            lines = [l.strip() for l in block.splitlines() if l.strip()]
            if not lines:
                continue
            header_parts = [p.strip() for p in lines[0].split("|")]
            degree = header_parts[0]
            school = header_parts[1] if len(header_parts) > 1 else ""
            date_str = header_parts[2] if len(header_parts) > 2 else ""

            p_deg = Paragraph(f"<b>{degree}</b>", style_item_title)
            p_date = Paragraph(f"<font color='{body_muted.hexval()}'>{date_str}</font>", style_item_title)
            t_hdr = Table([[p_deg, p_date]], colWidths=[(main_w - 16 * mm) * 0.7, (main_w - 16 * mm) * 0.3])
            t_hdr.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            story.append(t_hdr)

            if school:
                story.append(Paragraph(school, style_item_sub))
            story.append(Spacer(1, 2 * mm))

    # Certificates Section
    if data.get("certificates"):
        add_main_header("Certificates")
        for line in data["certificates"].splitlines():
            if not line.strip():
                continue
            parts = [p.strip() for p in line.split("|")]
            cert_name = parts[0].lstrip("• ")
            issuer = parts[1] if len(parts) > 1 else ""
            date_str = parts[2] if len(parts) > 2 else ""

            p_cert = Paragraph(f"• <b>{cert_name}</b>" + (f" - <i>{issuer}</i>" if issuer else ""), style_bullet)
            p_date = Paragraph(f"<font color='{body_muted.hexval()}'>{date_str}</font>", style_bullet)
            t_cert = Table([[p_cert, p_date]], colWidths=[(main_w - 16 * mm) * 0.75, (main_w - 16 * mm) * 0.25])
            t_cert.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            story.append(t_cert)

    # References Section
    if data.get("references"):
        add_main_header("References")
        for line in data["references"].splitlines():
            if not line.strip():
                continue
            parts = [p.strip() for p in line.split("|")]
            ref_name = parts[0].lstrip("• ")
            ref_title = parts[1] if len(parts) > 1 else ""
            ref_contact = " | ".join(parts[2:]) if len(parts) > 2 else ""

            story.append(Paragraph(f"• <b>{ref_name}</b>", style_bullet))
            if ref_title:
                story.append(Paragraph(f"&nbsp;&nbsp;{ref_title}", style_item_sub))
            if ref_contact:
                story.append(Paragraph(f"&nbsp;&nbsp;{ref_contact}", style_item_sub))

    # Signature Block
    sig_name = data.get("signature_name") or "Kedir Abdela"
    if sig_name:
        story.append(Spacer(1, 4 * mm))
        story.append(Paragraph(sig_name, style_sig))

    # Build Document
    doc.build(story)

# ============================================================
# 3. HTML INTERFACE, PREVIEW & CONTROLLERS
# ============================================================

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CVForge - Professional Multi-Page CV Builder</title>
<style>
* { box-sizing: border-box; }
body { margin: 0; font-family: 'Segoe UI', Arial, sans-serif; background: #f4f7f7; color: #173f3f; }
.container { max-width: 820px; margin: auto; padding: 20px; }
.card { background: white; border-radius: 18px; padding: 28px; box-shadow: 0 5px 25px rgba(0,0,0,.08); }
.logo { text-align: center; font-size: 32px; font-weight: 800; color: #02353c; }
.subtitle { text-align: center; color: #667; margin-bottom: 25px; font-size: 15px; }

/* Wizard Progress */
.progress { display: flex; gap: 6px; margin-bottom: 25px; }
.progress div { flex: 1; height: 6px; background: #d9e3e3; border-radius: 10px; transition: background 0.3s; }
.progress div.active { background: #e5a93c; }

.step { display: none; }
.step.active { display: block; }
h2 { margin-top: 0; color: #02353c; font-size: 22px; }

label { display: block; margin-top: 15px; margin-bottom: 6px; font-weight: 600; font-size: 14px; }
input, textarea, select { width: 100%; padding: 12px 14px; border: 1px solid #ccd8d8; border-radius: 10px; font-size: 15px; }
textarea { min-height: 100px; resize: vertical; }

.color-group { display: flex; gap: 15px; }
.color-group > div { flex: 1; }
input[type="color"] { padding: 4px; height: 45px; cursor: pointer; }

.buttons { display: flex; gap: 10px; margin-top: 25px; }
button { flex: 1; padding: 14px; border: none; border-radius: 10px; font-size: 16px; font-weight: bold; cursor: pointer; transition: opacity 0.2s; }
button:hover { opacity: 0.9; }
.next { background: #02353c; color: white; }
.back { background: #e7eeee; color: #173f3f; }
.generate { background: #e5a93c; color: white; }
</style>
</head>
<body>
<div class="container">
<div class="card">
<div class="logo">CVForge</div>
<div class="subtitle">Multi-Page Automatic Layout & Pixel-Perfect CV Builder</div>

<div class="progress">
  <div id="p1" class="active"></div>
  <div id="p2"></div>
  <div id="p3"></div>
  <div id="p4"></div>
</div>

<form id="cvForm" method="POST" action="/generate" enctype="multipart/form-data">

<div class="step active" id="step1">
  <h2>1. Personal Details</h2>
  <label>Full Name</label><input name="name" value="KEDIR ABDELA" required>
  <label>Professional Title</label><input name="title" value="BUSINESS MARKETING">
  <label>Phone Number</label><input name="phone" value="0908706534">
  <label>Email Address</label><input name="email" value="nmtullah86@gmail.com">
  <label>Location</label><input name="location" value="Los Angeles, USA">
  <label>LinkedIn URL</label><input name="linkedin" value="linkedin.com/in/kedirmohammed">
  <label>Website / Portfolio</label><input name="website" value="www.kedirmarketing.com">
  
  <div class="buttons">
    <button type="button" class="next" onclick="goToStep(2)">Next: Background</button>
  </div>
</div>

<div class="step" id="step2">
  <h2>2. Professional Background</h2>
  <label>Professional Summary</label>
  <textarea name="summary">Results-driven Digital Marketing Specialist with 5+ years of experience developing data-driven marketing campaigns, increasing online engagement, and improving customer acquisition. Skilled in SEO, social media marketing, content strategy, Google Analytics, and paid advertising.</textarea>
  
  <label>Work Experience (Format: Role | Company | Dates)</label>
  <textarea name="experience">Digital Marketing Specialist | BrightWave Media | New York, NY
• Developed and managed digital marketing campaigns across Google, Instagram, Facebook, and LinkedIn.
• Increased website traffic by 45% through SEO and content marketing strategies.
• Managed monthly advertising budgets and analyzed campaign performance.
• Collaborated with designers and content writers to produce marketing materials.

Marketing Coordinator | NovaTech Solutions | 2019 - 2022
• Supported digital marketing campaigns and social media activities.
• Created weekly performance reports using Google Analytics.
• Improved social media engagement by 30% within one year.</textarea>
  
  <label>Education (Format: Degree | Institution | Dates)</label>
  <textarea name="education">Bachelor of Business Administration | New York University | New York, NY</textarea>
  
  <div class="buttons">
    <button type="button" class="back" onclick="goToStep(1)">Back</button>
    <button type="button" class="next" onclick="goToStep(3)">Next: Skills & Details</button>
  </div>
</div>

<div class="step" id="step3">
  <h2>3. Skills & Additional Details</h2>
  <label>Skills (One per line)</label>
  <textarea name="skills">Digital Marketing
Search Engine Optimization (SEO)
Social Media Marketing
Google Analytics
Content Marketing
Email Marketing
Google Ads
Data Analysis
Project Management</textarea>
  
  <label>Certificates (Format: Name | Issuer | Date)</label>
  <textarea name="certificates">Google Analytics Certification | Google | 2023
Google Ads Search Certification | Google | 2023
HubSpot Content Marketing Certification | HubSpot Academy | 2022</textarea>
  
  <label>Languages</label>
  <textarea name="languages">English - Native
Spanish - Professional Working Proficiency
French - Basic</textarea>
  
  <label>Interests & Hobbies</label>
  <textarea name="hobbies">Technology and AI
Photography
Traveling
Reading
Entrepreneurship</textarea>
  
  <label>References (Format: Name | Role & Company | Contact)</label>
  <textarea name="references">Dr. Mohammad Namaste | Senior Marketing Director | contact@example.com</textarea>
  
  <label>Signature Text</label>
  <input name="signature_name" value="Kedir Abdela">

  <div class="buttons">
    <button type="button" class="back" onclick="goToStep(2)">Back</button>
    <button type="button" class="next" onclick="goToStep(4)">Next: Design & Styling</button>
  </div>
</div>

<div class="step" id="step4">
  <h2>4. Style & Theme Selection</h2>
  
  <label>Select Template Layout</label>
  <select name="template">
    <option value="modern" selected>Modern Flowable Two-Column Layout</option>
  </select>

  <div class="color-group">
    <div>
      <label>Sidebar Color</label>
      <input type="color" name="sidebar_color" value="#02353C">
    </div>
    <div>
      <label>Accent Color</label>
      <input type="color" name="accent_color" value="#E5A93C">
    </div>
  </div>

  <div class="buttons">
    <button type="button" class="back" onclick="goToStep(3)">Back</button>
    <button type="submit" class="generate">GENERATE MULTI-PAGE CV PREVIEW</button>
  </div>
</div>

</form>
</div>
</div>

<script>
function goToStep(stepNum) {
  for (let i = 1; i <= 4; i++) {
    document.getElementById('step' + i).classList.remove('active');
    document.getElementById('p' + i).classList.remove('active');
  }
  document.getElementById('step' + stepNum).classList.add('active');
  for (let i = 1; i <= stepNum; i++) {
    document.getElementById('p' + i).classList.add('active');
  }
}
</script>
</body>
</html>
"""

PREVIEW_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CV Preview & Download</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
<style>
body { margin: 0; background: #eef3f3; font-family: 'Segoe UI', Arial, sans-serif; }
.container { max-width: 900px; margin: auto; padding: 20px; }
.card { background: white; border-radius: 16px; padding: 25px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,.08); }
.pdf-page { width: 100%; margin-bottom: 15px; border-radius: 6px; box-shadow: 0 2px 10px rgba(0,0,0,.15); }
.actions { display: flex; gap: 15px; justify-content: center; margin-top: 20px; }
.btn { display: inline-block; padding: 14px 28px; border-radius: 10px; font-weight: bold; text-decoration: none; font-size: 16px; cursor: pointer; }
.download { background: #e5a93c; color: white; }
.edit { background: #02353c; color: white; }
</style>
</head>
<body>
<div class="container">
<div class="card">
<h2>CV Generated Successfully</h2>
<div id="previewBox"></div>
<div class="actions">
  <a class="btn edit" href="/">← Edit Form Data</a>
  <a class="btn download" href="/download/{{ token }}">DOWNLOAD PDF</a>
</div>
</div>
</div>
<script>
pdfjsLib.GlobalWorkerOptions.workerSrc = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";
const pdfBase64 = "{{ pdf_data }}";
async function render() {
    const bytes = Uint8Array.from(atob(pdfBase64), c => c.charCodeAt(0));
    const pdf = await pdfjsLib.getDocument({ data: bytes }).promise;
    for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const vp = page.getViewport({ scale: 1.5 });
        const canvas = document.createElement("canvas");
        canvas.className = "pdf-page";
        canvas.width = vp.width;
        canvas.height = vp.height;
        document.getElementById("previewBox").appendChild(canvas);
        await page.render({ canvasContext: canvas.getContext("2d"), viewport: vp }).promise;
    }
}
render();
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/generate", methods=["POST"])
def generate():
    data = {
        "name": request.form.get("name", "KEDIR ABDELA"),
        "title": request.form.get("title", "BUSINESS MARKETING"),
        "phone": request.form.get("phone", ""),
        "email": request.form.get("email", ""),
        "location": request.form.get("location", ""),
        "linkedin": request.form.get("linkedin", ""),
        "website": request.form.get("website", ""),
        "summary": request.form.get("summary", ""),
        "experience": request.form.get("experience", ""),
        "education": request.form.get("education", ""),
        "skills": request.form.get("skills", ""),
        "certificates": request.form.get("certificates", ""),
        "languages": request.form.get("languages", ""),
        "hobbies": request.form.get("hobbies", ""),
        "references": request.form.get("references", ""),
        "signature_name": request.form.get("signature_name", ""),
        "accent_color": request.form.get("accent_color", "#E5A93C"),
        "sidebar_color": request.form.get("sidebar_color", "#02353C"),
    }

    token = str(uuid.uuid4())
    filename = os.path.join(tempfile.gettempdir(), "CV_" + token + ".pdf")
    generate_pdf(data, filename)

    with open(filename, "rb") as f:
        pdf_bytes = f.read()

    return render_template_string(PREVIEW_HTML, pdf_data=base64.b64encode(pdf_bytes).decode("utf-8"), token=token)

@app.route("/download/<token>")
def download_pdf(token):
    filename = os.path.join(tempfile.gettempdir(), "CV_" + token + ".pdf")
    if not os.path.exists(filename):
        return "File not found", 404
    return send_file(filename, as_attachment=True, download_name="CV.pdf", mimetype="application/pdf")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
