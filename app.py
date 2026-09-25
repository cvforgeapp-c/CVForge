import os
import tempfile
import base64
import uuid
import math
from io import BytesIO
from PIL import Image
from flask import Flask, request, render_template_string, send_file

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth

# ============================================================
# SAFE CUSTOM FONT REGISTRATION WITH FALLBACKS
# ============================================================

FONT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "fonts"
)

MONTSERRAT_EXTRA_BOLD = os.path.join(FONT_DIR, "Montserrat-ExtraBold.ttf")
DANCING_SCRIPT = os.path.join(FONT_DIR, "DancingScript-Regular.ttf")

if os.path.exists(MONTSERRAT_EXTRA_BOLD):
    try:
        pdfmetrics.registerFont(TTFont("Montserrat-ExtraBold", MONTSERRAT_EXTRA_BOLD))
    except Exception as e:
        print(f"Warning: Could not register Montserrat font: {e}")

if os.path.exists(DANCING_SCRIPT):
    try:
        pdfmetrics.registerFont(TTFont("DancingScript", DANCING_SCRIPT))
    except Exception as e:
        print(f"Warning: Could not register DancingScript font: {e}")

app = Flask(__name__)

# Global canvas reference for text wrapping helper
_modern_canvas = None

PAGE_HEIGHT = 297 * mm  # A4 Height
PAGE_WIDTH = 210 * mm   # A4 Width
BOTTOM_MARGIN = 20 * mm

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CVForge - Professional CV Builder</title>
<style>
* { box-sizing: border-box; }
body { margin: 0; font-family: Arial, sans-serif; background: #f4f7f7; color: #173f3f; }
.container { max-width: 760px; margin: auto; padding: 20px; }
.card { background: white; border-radius: 18px; padding: 25px; box-shadow: 0 5px 25px rgba(0,0,0,.08); }
.logo { text-align: center; font-size: 30px; font-weight: bold; color: #0d4f4f; }
.subtitle { text-align: center; color: #777; margin-bottom: 25px; }
.progress { display: flex; gap: 5px; margin-bottom: 25px; }
.progress div { flex: 1; height: 6px; background: #d9e3e3; border-radius: 10px; }
.progress div.active { background: #c9a227; }
.step { display: none; }
.step.active { display: block; }
h2 { margin-top: 0; color: #0d4f4f; }
label { display: block; margin-top: 15px; margin-bottom: 6px; font-weight: bold; }
input, textarea, select { width: 100%; padding: 13px; border: 1px solid #ccd8d8; border-radius: 10px; font-size: 16px; font-family: Arial, sans-serif; }
textarea { min-height: 120px; resize: vertical; }
.buttons { display: flex; gap: 10px; margin-top: 25px; }
button { flex: 1; padding: 14px; border: none; border-radius: 10px; font-size: 16px; font-weight: bold; }
.next { background: #0d4f4f; color: white; }
.back { background: #e7eeee; color: #173f3f; }
.generate { background: #c9a227; color: white; }
.small { color: #777; font-size: 13px; }
.template-grid { display: grid; gap: 15px; margin-top: 18px; }
.template-option { width: 100%; text-align: left; background: #ffffff; border: 2px solid #d9e0e0; border-radius: 16px; padding: 20px; cursor: pointer; transition: all 0.2s ease; }
.template-option:hover { border-color: #0d4f4f; transform: translateY(-2px); }
.template-option.selected { border-color: #c9a227; background: #f8f5e9; box-shadow: 0 4px 15px rgba(201,162,39,.18); }
.template-name { font-size: 20px; font-weight: bold; color: #173f3f; margin-bottom: 8px; }
.template-description { color: #777; font-size: 15px; line-height: 1.5; }
.template-badge { display: inline-block; margin-top: 12px; padding: 7px 12px; border-radius: 20px; background: #e7eeee; color: #173f3f; font-size: 13px; font-weight: bold; }
.template-option.selected .template-badge { background: #c9a227; color: white; }
.checkmark { float: right; display: none; color: #c9a227; font-size: 24px; font-weight: bold; }
.template-option.selected .checkmark { display: block; }
.color-section { margin-top: 25px; padding: 18px; background: #f7f9f9; border-radius: 14px; }
.color-section h3 { margin: 0 0 6px; color: #173f3f; }
.color-grid { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 15px; }
.color-option { width: 42px; height: 42px; border-radius: 50%; border: 4px solid white; box-shadow: 0 0 0 1px #ccd8d8; cursor: pointer; padding: 0; flex: none; }
.color-option.selected { box-shadow: 0 0 0 2px #222, 0 3px 10px rgba(0,0,0,.18); transform: scale(1.08); }
@media(max-width:600px) { .container { padding: 10px; } .card { padding: 18px; } .buttons { flex-direction: column; } }
.char-counter { text-align: right; margin-top: 5px; font-size: 12px; color: #777; }
.char-counter.warning { color: #b07a00; }
.char-counter.limit { color: #b00020; font-weight: bold; }
</style>
</head>
<body>
<div class="container">
<div class="card">
<div class="logo">CVForge</div>
<div class="subtitle">Build a professional CV in minutes</div>
<div class="progress">
<div class="p active"></div><div class="p"></div><div class="p"></div><div class="p"></div><div class="p"></div><div class="p"></div><div class="p"></div><div class="p"></div><div class="p"></div><div class="p"></div><div class="p"></div>
</div>
<form method="POST" action="/generate" enctype="multipart/form-data">

<div class="step active">
<h2>1. Personal Information</h2>
<label>Full Name *</label><input name="name" required>
<label>Professional Title</label><input name="title" maxlength="70" placeholder="e.g. Software Developer">
<label>Profile Photo</label><input type="file" name="photo" accept="image/*">
<label>Phone</label><input name="phone">
<label>Email</label><input name="email">
<label>Location</label><input name="location" placeholder="City, Country">
<label>LinkedIn</label><input name="linkedin">
<label>Website</label><input name="website">
<div class="buttons"><button type="button" class="next" onclick="nextStep()">Next →</button></div>
</div>

<div class="step">
<h2>2. Professional Summary</h2>
<label>Summary</label><textarea id="summary" name="summary" maxlength="500" placeholder="Write a short professional summary..."></textarea>
<div class="buttons"><button type="button" class="back" onclick="prevStep()">← Back</button><button type="button" class="next" onclick="nextStep()">Next →</button></div>
</div>

<div class="step">
<h2>3. Work Experience</h2>
<label>Experience</label><textarea name="experience" maxlength="1200" placeholder="Job Title - Company - Dates..."></textarea>
<div class="buttons"><button type="button" class="back" onclick="prevStep()">← Back</button><button type="button" class="next" onclick="nextStep()">Next →</button></div>
</div>

<div class="step">
<h2>4. Education</h2>
<label>Education</label><textarea name="education" maxlength="600" placeholder="Degree - Institution - Year"></textarea>
<div class="buttons"><button type="button" class="back" onclick="prevStep()">← Back</button><button type="button" class="next" onclick="nextStep()">Next →</button></div>
</div>

<div class="step">
<h2>5. Skills</h2>
<label>Skills</label><textarea name="skills" maxlength="400" placeholder="Python&#10;Flask&#10;Communication"></textarea>
<div class="buttons"><button type="button" class="back" onclick="prevStep()">← Back</button><button type="button" class="next" onclick="nextStep()">Next →</button></div>
</div>

<div class="step">
<h2>6. Certificates & Training</h2>
<label>Certificates</label><textarea name="certificates" maxlength="500" placeholder="Certificate Name - Organization - Year"></textarea>
<div class="buttons"><button type="button" class="back" onclick="prevStep()">← Back</button><button type="button" class="next" onclick="nextStep()">Next →</button></div>
</div>

<div class="step">
<h2>7. Languages</h2>
<label>Languages</label><textarea name="languages" maxlength="250" placeholder="English - Fluent"></textarea>
<div class="buttons"><button type="button" class="back" onclick="prevStep()">← Back</button><button type="button" class="next" onclick="nextStep()">Next →</button></div>
</div>

<div class="step">
<h2>8. Interests</h2>
<label>Interests & Hobbies</label><textarea name="hobbies" maxlength="250" placeholder="Technology&#10;Reading"></textarea>
<div class="buttons"><button type="button" class="back" onclick="prevStep()">← Back</button><button type="button" class="next" onclick="nextStep()">Next →</button></div>
</div>

<div class="step">
<h2>9. References</h2>
<label>References</label><textarea name="references" maxlength="500" placeholder="Name - Position - Company"></textarea>
<label>Signature (optional)</label><input type="file" name="signature" accept="image/png,image/jpeg,image/jpg">
<div class="buttons"><button type="button" class="back" onclick="prevStep()">← Back</button><button type="button" class="next" onclick="nextStep()">Next →</button></div>
</div>

<div class="step">
<h2>10. Choose Template</h2>
<input type="hidden" name="template" id="templateInput" value="modern">
<div class="template-grid">
<button type="button" class="template-option selected" data-template="modern" onclick="selectTemplate(this)">
    <span class="checkmark">✓</span><div class="template-name">Modern Professional</div>
    <div class="template-description">Premium visual design with photo & clean layout.</div>
    <span class="template-badge">✓ Selected</span>
</button>
<button type="button" class="template-option" data-template="classic" onclick="selectTemplate(this)">
    <span class="checkmark">✓</span><div class="template-name">Classic Professional</div>
    <div class="template-description">Traditional design with full-width header.</div>
    <span class="template-badge">Select</span>
</button>
<button type="button" class="template-option" data-template="ats" onclick="selectTemplate(this)">
    <span class="checkmark">✓</span><div class="template-name">ATS Friendly</div>
    <div class="template-description">Single-column text design.</div>
    <span class="template-badge">Select</span>
</button>
</div>

<div class="color-section">
<h3>Choose Accent Color</h3>
<input type="hidden" name="accent_color" id="accentColorInput" value="#F2B632">
<div class="color-grid">
<button type="button" class="color-option selected" data-color="#F2B632" style="background:#F2B632" onclick="selectColor(this)"></button>
<button type="button" class="color-option" data-color="#1599A8" style="background:#1599A8" onclick="selectColor(this)"></button>
<button type="button" class="color-option" data-color="#1769AA" style="background:#1769AA" onclick="selectColor(this)"></button>
<button type="button" class="color-option" data-color="#8B2F3B" style="background:#8B2F3B" onclick="selectColor(this)"></button>
</div>
</div>

<div class="color-section">
<h3>Choose Sidebar Color</h3>
<input type="hidden" name="sidebar_color" id="sidebarColorInput" value="#173F49">
<div class="color-grid">
<button type="button" class="color-option selected" data-sidebar-color="#173F49" style="background:#173F49" onclick="selectSidebarColor(this)"></button>
<button type="button" class="color-option" data-sidebar-color="#1F2937" style="background:#1F2937" onclick="selectSidebarColor(this)"></button>
<button type="button" class="color-option" data-sidebar-color="#123B2A" style="background:#123B2A" onclick="selectSidebarColor(this)"></button>
</div>
</div>

<div class="buttons">
<button type="button" class="back" onclick="prevStep()">← Back</button>
<button type="button" class="next" onclick="nextStep()">Next →</button>
</div>
</div>

<div class="step">
<h2>11. Generate Your CV</h2>
<p>Your information is ready.</p>
<div class="buttons">
<button type="button" class="back" onclick="prevStep()">← Back</button>
<button type="submit" class="generate">GENERATE & PREVIEW CV</button>
</div>
</div>

</form>
</div>
</div>

<script>
let currentStep = 0;
const steps = document.querySelectorAll(".step");
const progress = document.querySelectorAll(".progress .p");

function showStep(index) {
    steps.forEach((step, i) => step.classList.toggle("active", i === index));
    progress.forEach((bar, i) => bar.classList.toggle("active", i <= index));
    window.scrollTo({ top: 0, behavior: "smooth" });
}

function selectTemplate(button) {
    document.querySelectorAll(".template-option").forEach(opt => {
        opt.classList.remove("selected");
        const b = opt.querySelector(".template-badge");
        if (b) b.textContent = "Select";
    });
    button.classList.add("selected");
    const badge = button.querySelector(".template-badge");
    if (badge) badge.textContent = "✓ Selected";
    document.getElementById("templateInput").value = button.dataset.template;
}

function selectColor(button) {
    document.querySelectorAll(".color-option[data-color]").forEach(opt => opt.classList.remove("selected"));
    button.classList.add("selected");
    document.getElementById("accentColorInput").value = button.dataset.color;
}

function selectSidebarColor(button) {
    document.querySelectorAll(".color-option[data-sidebar-color]").forEach(opt => opt.classList.remove("selected"));
    button.classList.add("selected");
    document.getElementById("sidebarColorInput").value = button.dataset.sidebarColor;
}

function nextStep() { if (currentStep < steps.length - 1) { currentStep++; showStep(currentStep); } }
function prevStep() { if (currentStep > 0) { currentStep--; showStep(currentStep); } }
</script>
</body>
</html>
"""

PREVIEW_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CVForge Preview</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
<style>
* { box-sizing: border-box; }
body { margin: 0; background: #eef3f3; font-family: Arial, sans-serif; color: #173f3f; }
.container { max-width: 900px; margin: auto; padding: 20px; }
.card { background: white; border-radius: 16px; padding: 20px; box-shadow: 0 5px 25px rgba(0,0,0,.08); }
h1 { text-align: center; color: #0d4f4f; margin-bottom: 8px; }
.subtitle { text-align: center; color: #777; margin-bottom: 20px; }
.preview-box { width: 100%; background: #dfe7e7; padding: 10px; border-radius: 12px; }
.pdf-page { width: 100%; height: auto; display: block; background: white; margin-bottom: 15px; border-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,.12); }
.loading { text-align: center; padding: 30px; color: #777; font-weight: bold; }
.error { text-align: center; padding: 30px; color: #b00020; font-weight: bold; }
.buttons { display: flex; gap: 12px; margin-top: 20px; }
a { flex: 1; text-align: center; text-decoration: none; padding: 15px; border-radius: 10px; font-weight: bold; font-size: 16px; }
.edit { background: #e7eeee; color: #173f3f; }
.download { background: #c9a227; color: white; }
@media(max-width:600px) { .container { padding: 8px; } .card { padding: 12px; } .buttons { flex-direction: column; } }
</style>
</head>
<body>
<div class="container">
<div class="card">
<h1>Your CV Preview</h1>
<div class="subtitle">Your professional CV is ready</div>
<div class="preview-box" id="previewBox"><div class="loading" id="loading">Preparing your CV preview...</div></div>
<div class="buttons">
<a class="edit" href="/">← Edit CV</a>
<a class="download" href="/download/{{ token }}">⬇ DOWNLOAD CV</a>
</div>
</div>
</div>

<script>
pdfjsLib.GlobalWorkerOptions.workerSrc = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";
const pdfBase64 = "{{ pdf_data }}";
const previewBox = document.getElementById("previewBox");
const loading = document.getElementById("loading");

async function renderPDF() {
    try {
        const binaryString = atob(pdfBase64);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }
        const pdf = await pdfjsLib.getDocument({ data: bytes }).promise;
        loading.remove();

        for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber++) {
            const page = await pdf.getPage(pageNumber);
            const containerWidth = previewBox.clientWidth - 20;
            const originalViewport = page.getViewport({ scale: 1 });
            const scale = containerWidth / originalViewport.width;
            const viewport = page.getViewport({ scale: scale });

            const canvas = document.createElement("canvas");
            canvas.className = "pdf-page";
            const context = canvas.getContext("2d");
            canvas.width = viewport.width;
            canvas.height = viewport.height;

            previewBox.appendChild(canvas);
            await page.render({ canvasContext: context, viewport: viewport }).promise;
        }
    } catch (error) {
        loading.remove();
        const errorMessage = document.createElement("div");
        errorMessage.className = "error";
        errorMessage.textContent = "Unable to display the CV preview. Please try again.";
        previewBox.appendChild(errorMessage);
        console.error(error);
    }
}
renderPDF();
</script>
</body>
</html>
"""

def clean(text):
    if not text:
        return ""
    return str(text).strip()

def wrap_text(c, text, font, size, max_width):
    words = clean(text).split()
    lines = []
    current = ""

    if c:
        c.setFont(font, size)

    for word in words:
        test = word if not current else current + " " + word
        width = c.stringWidth(test, font, size) if c else stringWidth(test, font, size)
        if width <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines

def wrap(text, font, size, width):
    if not text:
        return []
    return wrap_text(_modern_canvas, text, font, size, width)

def draw_wrapped(c, text, x, y, width, font="Helvetica", size=9, leading=12, color=colors.black):
    c.setFillColor(color)
    for line in wrap_text(c, text, font, size, width):
        c.setFont(font, size)
        c.drawString(x, y, line)
        y -= leading
    return y

def draw_section_title(c, title, x, y, width):
    c.setFillColor(colors.HexColor("#0D4F4F"))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, title.upper())
    c.setStrokeColor(colors.HexColor("#C9A227"))
    c.setLineWidth(1)
    c.line(x, y - 4, x + width, y - 4)
    return y - 20

def check_page_overflow(c, y, required_space, template_type, sidebar_color, accent_color):
    if y - required_space < BOTTOM_MARGIN:
        c.showPage()
        new_y = PAGE_HEIGHT - 20 * mm
        if template_type == "modern":
            c.setFillColor(sidebar_color)
            c.rect(0, 0, 78 * mm, PAGE_HEIGHT, fill=True, stroke=False)
        elif template_type == "classic":
            c.setFillColor(accent_color)
            c.rect(0, PAGE_HEIGHT - 8 * mm, PAGE_WIDTH, 8 * mm, fill=True, stroke=False)
        return new_y
    return y

# ============================================================
# MODERN PROFESSIONAL CV TEMPLATE
# ============================================================

def modern(data, file):
    W, H = A4
    c = canvas.Canvas(file, pagesize=A4)
    global _modern_canvas
    _modern_canvas = c
    c.setTitle("CV - " + (data.get("name") or "My CV"))

    teal = colors.HexColor("#053D47")
    sidebar_color = colors.HexColor(data.get("sidebar_color") or "#173F49")
    gold = colors.HexColor(data.get("accent_color") or "#F2B632")
    white = colors.white
    dark = colors.HexColor("#123F4A")
    muted = colors.HexColor("#5E6F73")

    sidebar_w = 78 * mm
    main_x = sidebar_w + 14 * mm
    main_w = W - main_x - 13 * mm

    c.setFillColor(colors.HexColor("#FAFCFB"))
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(sidebar_color)
    c.rect(0, 0, sidebar_w, H, stroke=0, fill=1)

    photo = data.get("photo")
    if photo and os.path.exists(photo):
        try:
            photo_size = 48 * mm
            photo_x = (sidebar_w - photo_size) / 2
            photo_y = H - 63 * mm

            c.setFillColor(gold)
            c.circle(photo_x + photo_size / 2, photo_y + photo_size / 2, photo_size / 2 + 2.2 * mm, stroke=0, fill=1)

            c.setFillColor(colors.white)
            c.circle(photo_x + photo_size / 2, photo_y + photo_size / 2, photo_size / 2 + 0.8 * mm, stroke=0, fill=1)

            c.saveState()
            path = c.beginPath()
            path.circle(photo_x + photo_size / 2, photo_y + photo_size / 2, photo_size / 2)
            c.clipPath(path, stroke=0, fill=0)

            c.drawImage(ImageReader(photo), photo_x, photo_y, width=photo_size, height=photo_size, preserveAspectRatio=True, anchor="c", mask="auto")
            c.restoreState()
        except Exception as e:
            print(f"Error drawing photo: {e}")

    def draw_lines(value, x, y, width, font="Helvetica", size=8.8, leading=4.6 * mm, color=dark, bullet=False):
        if not value:
            return y
        c.setFillColor(color)
        c.setFont(font, size)

        for paragraph in value.splitlines():
            paragraph = paragraph.strip()
            if not paragraph:
                y -= leading * 0.55
                continue

            lines = wrap(paragraph, font, size, width)
            for index, line in enumerate(lines):
                prefix = "• " if (bullet and index == 0) else ("  " if bullet else "")
                c.drawString(x, y, prefix + line)
                y -= leading
        return y

    def main_section(title, x, y, width):
        c.setFillColor(teal)
        c.circle(x + 5 * mm, y + 1 * mm, 5.2 * mm, stroke=0, fill=1)
        
        c.setFillColor(dark)
        c.setFont("Helvetica-Bold", 11.5)
        c.drawString(x + 14 * mm, y, title.upper())
        
        c.setStrokeColor(gold)
        c.setLineWidth(1.1)
        c.line(x + 12 * mm, y - 4.5 * mm, x + width, y - 4.5 * mm)
        return y - 11.5 * mm

    def sidebar_section(title, x, y, width):
        c.setFillColor(gold)
        c.setFont("Helvetica-Bold", 10.5)
        title_x = x + 2 * mm
        c.drawString(title_x, y, title.upper())

        c.setStrokeColor(gold)
        c.setLineWidth(1)
        c.line(title_x, y - 2.2 * mm, x + width, y - 2.2 * mm)
        return y - 9 * mm

    # Sidebar Content
    sx = 10 * mm
    sw = sidebar_w - 20 * mm
    sy = H - 78 * mm

    sy = check_page_overflow(c, sy, 6 * mm, "modern", sidebar_color, gold)
    sy = sidebar_section("Contact", sx, sy, sw)

    contact_items = [
        data.get("phone"),
        data.get("email"),
        data.get("location"),
        data.get("linkedin"),
        data.get("website")
    ]

    for val in contact_items:
        if val:
            sy = draw_lines(val, sx + 2 * mm, sy, sw - 2 * mm, size=8.2, leading=4.8 * mm, color=white)
    sy -= 2.0 * mm

    if data.get("skills"):
        sy = check_page_overflow(c, sy, 6 * mm, "modern", sidebar_color, gold)
        sy -= 4 * mm
        sy = sidebar_section("Skills", sx, sy, sw)
        for skill in data["skills"].splitlines():
            if skill.strip():
                sy = draw_lines(skill.strip(), sx, sy, sw, size=9, leading=5 * mm, color=white, bullet=True)

    if data.get("languages"):
        sy = check_page_overflow(c, sy, 6 * mm, "modern", sidebar_color, gold)
        sy -= 4 * mm
        sy = sidebar_section("Languages", sx, sy, sw)
        for lang in data["languages"].splitlines():
            if lang.strip():
                sy = draw_lines(lang.strip(), sx, sy, sw, size=9, leading=5 * mm, color=white, bullet=True)

    # Main Column Content
    name = (data.get("name") or "My CV").upper()
    c.setFillColor(dark)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(main_x, H - 23 * mm, name[:45])

    title = data.get("title") or ""
    if title:
        c.setFillColor(gold)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(main_x, H - 31 * mm, title[:70].upper())

    y = H - 43 * mm

    if data.get("summary"):
        y = draw_lines(data["summary"], main_x, y, main_w, size=9.5, leading=4.8 * mm, color=muted)
        y -= 7 * mm

    if data.get("experience"):
        y = check_page_overflow(c, y, 15 * mm, "modern", sidebar_color, gold)
        y = main_section("Experience", main_x, y, main_w)
        y = draw_lines(data["experience"], main_x, y, main_w, size=8.8, leading=5.0 * mm, color=muted)
        y -= 5 * mm

    if data.get("education"):
        y = check_page_overflow(c, y, 15 * mm, "modern", sidebar_color, gold)
        y = main_section("Education", main_x, y, main_w)
        y = draw_lines(data["education"], main_x, y, main_w, size=8.8, leading=5.0 * mm, color=muted)
        y -= 5 * mm

    if data.get("certificates"):
        y = check_page_overflow(c, y, 15 * mm, "modern", sidebar_color, gold)
        y = main_section("Certificates", main_x, y, main_w)
        y = draw_lines(data["certificates"], main_x, y, main_w, size=8.8, leading=5.0 * mm, color=muted)
        y -= 5 * mm

    if data.get("references"):
        y = check_page_overflow(c, y, 15 * mm, "modern", sidebar_color, gold)
        y = main_section("References", main_x, y, main_w)
        y = draw_lines(data["references"], main_x, y, main_w, size=8.8, leading=5.0 * mm, color=muted)

    c.save()

# ============================================================
# PDF GENERATION DISPATCHER
# ============================================================

def generate_pdf(data, filename):
    template = clean(data.get("template")).lower()

    if template == "modern":
        modern(data, filename)
        return

    c = canvas.Canvas(filename, pagesize=A4)
    # Default fallbacks for other templates
    modern(data, filename)

# ============================================================
# FLASK ROUTES
# ============================================================

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/generate", methods=["POST"])
def generate():
    photo = request.files.get("photo")
    signature = request.files.get("signature")

    def form_limit(name, maximum):
        return request.form.get(name, "")[:maximum]

    data = {
        "name": form_limit("name", 100),
        "title": form_limit("title", 70),
        "phone": form_limit("phone", 50),
        "email": form_limit("email", 100),
        "location": form_limit("location", 100),
        "linkedin": form_limit("linkedin", 200),
        "website": form_limit("website", 200),
        "summary": form_limit("summary", 500),
        "experience": form_limit("experience", 1200),
        "education": form_limit("education", 600),
        "skills": form_limit("skills", 400),
        "certificates": form_limit("certificates", 500),
        "languages": form_limit("languages", 250),
        "hobbies": form_limit("hobbies", 250),
        "references": form_limit("references", 500),
        "template": request.form.get("template", "modern"),
        "accent_color": request.form.get("accent_color", "#F2B632"),
        "sidebar_color": request.form.get("sidebar_color", "#173F49"),
    }

    if photo and photo.filename:
        photo_path = os.path.join(tempfile.gettempdir(), "CVForge_" + photo.filename)
        photo.save(photo_path)
        data["photo"] = photo_path
    else:
        data["photo"] = ""

    filename = os.path.join(tempfile.gettempdir(), "CVForge_" + uuid.uuid4().hex + ".pdf")
    generate_pdf(data, filename)

    with open(filename, "rb") as pdf_file:
        pdf_data = base64.b64encode(pdf_file.read()).decode("utf-8")

    token = str(uuid.uuid4())
    preview_file = os.path.join(tempfile.gettempdir(), "CVForge_" + token + ".pdf")

    with open(preview_file, "wb") as output:
        with open(filename, "rb") as source:
            output.write(source.read())

    return render_template_string(PREVIEW_HTML, pdf_data=pdf_data, token=token)

@app.route("/download/<token>")
def download_pdf(token):
    filename = os.path.join(tempfile.gettempdir(), "CVForge_" + token + ".pdf")
    if not os.path.exists(filename):
        return "CV not found.", 404
    return send_file(filename, as_attachment=True, download_name="CVForge_Professional_CV.pdf", mimetype="application/pdf")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
