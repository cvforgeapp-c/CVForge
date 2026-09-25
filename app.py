import os
import tempfile
import base64
import uuid
import math
import re
from flask import Flask, request, render_template_string, send_file, session

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
MONTSERRAT_EXTRA_BOLD = os.path.join(FONT_DIR, "Montserrat-ExtraBold.ttf")
DANCING_SCRIPT = os.path.join(FONT_DIR, "DancingScript-Regular.ttf")

HAS_MONTSERRAT = False
HAS_DANCING = False

if os.path.exists(MONTSERRAT_EXTRA_BOLD):
    try:
        pdfmetrics.registerFont(TTFont("Montserrat-ExtraBold", MONTSERRAT_EXTRA_BOLD))
        HAS_MONTSERRAT = True
    except Exception as e:
        print(f"Font error (Montserrat): {e}")

if os.path.exists(DANCING_SCRIPT):
    try:
        pdfmetrics.registerFont(TTFont("DancingScript", DANCING_SCRIPT))
        HAS_DANCING = True
    except Exception as e:
        print(f"Font error (DancingScript): {e}")

app = Flask(__name__)
app.secret_key = "cv_builder_secret_key"

PAGE_WIDTH, PAGE_HEIGHT = A4
BOTTOM_MARGIN = 15 * mm
LINE_LEADING = 4.5 * mm

# ============================================================
# HELPER WRAPPING FUNCTIONS
# ============================================================
def clean(text):
    return str(text).strip() if text else ""

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
            word_w = c.stringWidth(word, font, size) if c else stringWidth(word, font, size)
            if word_w > max_width:
                if current_line:
                    lines.append(current_line)
                    current_line = ""
                sub_str = ""
                for char in word:
                    test_sub = sub_str + char
                    test_w = c.stringWidth(test_sub, font, size) if c else stringWidth(test_sub, font, size)
                    if test_w <= max_width:
                        sub_str = test_sub
                    else:
                        lines.append(sub_str)
                        sub_str = char
                if sub_str:
                    current_line = sub_str
                continue

            test_line = word if not current_line else current_line + " " + word
            test_w = c.stringWidth(test_line, font, size) if c else stringWidth(test_line, font, size)

            if test_w <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)
    return lines

def draw_wrapped_lines(c, value, x, y, width, font="Helvetica", size=9, leading=LINE_LEADING, color=colors.HexColor("#2C3E50"), bullet=False):
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

# ============================================================
# TEMPLATE 1: CLASSIC (Traditional Single-Column Layout)
# ============================================================
def classic(data, file):
    c = canvas.Canvas(file, pagesize=A4)
    c.setTitle("CV - " + (data.get("name") or "KEDIR ABDELA"))

    left_m = 15 * mm
    right_m = 15 * mm
    content_w = PAGE_WIDTH - left_m - right_m
    y = PAGE_HEIGHT - 18 * mm

    # Name & Title Header (Centered)
    name = (data.get("name") or "KEDIR ABDELA").upper()
    c.setFillColor(colors.HexColor("#1A1A1A"))
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(PAGE_WIDTH / 2, y, name)
    y -= 6 * mm

    title = (data.get("title") or "BUSINESS MARKETING").upper()
    c.setFillColor(colors.HexColor("#555555"))
    c.setFont("Helvetica", 10)
    c.drawCentredString(PAGE_WIDTH / 2, y, title)
    y -= 6 * mm

    # Contact Bar
    contact_info = [data.get("phone"), data.get("email"), data.get("location"), data.get("linkedin"), data.get("website")]
    contact_str = " | ".join([item for item in contact_info if item])
    if contact_str:
        c.setFont("Helvetica", 8.5)
        c.setFillColor(colors.HexColor("#333333"))
        c.drawCentredString(PAGE_WIDTH / 2, y, contact_str)
        y -= 5 * mm

    c.setStrokeColor(colors.HexColor("#333333"))
    c.setLineWidth(1)
    c.line(left_m, y, PAGE_WIDTH - right_m, y)
    y -= 6 * mm

    def section(title):
        nonlocal y
        c.setFillColor(colors.HexColor("#1A1A1A"))
        c.setFont("Helvetica-Bold", 11)
        c.drawString(left_m, y, title.upper())
        y -= 2 * mm
        c.setStrokeColor(colors.HexColor("#888888"))
        c.setLineWidth(0.5)
        c.line(left_m, y, PAGE_WIDTH - right_m, y)
        y -= 5 * mm

    for key, label in [("summary", "Professional Summary"), ("experience", "Work Experience"), ("education", "Education"), ("skills", "Key Skills"), ("certificates", "Certifications"), ("references", "References")]:
        if data.get(key):
            section(label)
            if key in ["experience", "education"]:
                for line in data[key].splitlines():
                    if "|" in line:
                        y -= 2 * mm
                        y = draw_wrapped_lines(c, line, left_m, y, content_w, font="Helvetica-Bold", size=9)
                    else:
                        y = draw_wrapped_lines(c, line, left_m, y, content_w, size=8.5, bullet=True)
            else:
                y = draw_wrapped_lines(c, data[key], left_m, y, content_w, size=8.5, bullet=(key != "summary"))
            y -= 4 * mm

    c.save()

# ============================================================
# TEMPLATE 2: ALS / EXECUTIVE MINIMALIST
# ============================================================
def als(data, file):
    c = canvas.Canvas(file, pagesize=A4)
    c.setTitle("CV - " + (data.get("name") or "KEDIR ABDELA"))

    left_m = 18 * mm
    right_m = 18 * mm
    content_w = PAGE_WIDTH - left_m - right_m
    y = PAGE_HEIGHT - 20 * mm

    # Left-aligned Header with Accent Block
    name = (data.get("name") or "KEDIR ABDELA").upper()
    c.setFillColor(colors.HexColor("#2B3E50"))
    c.setFont("Helvetica-Bold", 22)
    c.drawString(left_m, y, name)
    y -= 6 * mm

    title = (data.get("title") or "BUSINESS MARKETING").upper()
    c.setFillColor(colors.HexColor("#E74C3C"))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_m, y, title)
    y -= 6 * mm

    contacts = [data.get("email"), data.get("phone"), data.get("location"), data.get("linkedin")]
    contact_str = " • ".join([c for c in contacts if c])
    if contact_str:
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.HexColor("#7F8C8D"))
        c.drawString(left_m, y, contact_str)
        y -= 6 * mm

    def section(title):
        nonlocal y
        c.setFillColor(colors.HexColor("#2B3E50"))
        c.setFont("Helvetica-Bold", 11)
        c.drawString(left_m, y, title.upper())
        y -= 2 * mm
        c.setStrokeColor(colors.HexColor("#E74C3C"))
        c.setLineWidth(1.5)
        c.line(left_m, y, left_m + 25 * mm, y)
        c.setStrokeColor(colors.HexColor("#BDC3C7"))
        c.setLineWidth(0.5)
        c.line(left_m + 25 * mm, y, PAGE_WIDTH - right_m, y)
        y -= 5 * mm

    for key, label in [("summary", "Summary"), ("experience", "Experience"), ("education", "Education"), ("skills", "Core Competencies"), ("certificates", "Certifications")]:
        if data.get(key):
            section(label)
            if key in ["experience", "education"]:
                for line in data[key].splitlines():
                    if "|" in line:
                        y -= 2 * mm
                        y = draw_wrapped_lines(c, line, left_m, y, content_w, font="Helvetica-Bold", size=9, color=colors.HexColor("#2B3E50"))
                    else:
                        y = draw_wrapped_lines(c, line, left_m, y, content_w, size=8.5, bullet=True)
            else:
                y = draw_wrapped_lines(c, data[key], left_m, y, content_w, size=8.5, bullet=(key != "summary"))
            y -= 4 * mm

    c.save()

# ============================================================
# TEMPLATE 3: MODERN (Imported from modern code)
# ============================================================
def modern(data, file):
    # Your existing modern implementation
    classic(data, file) # Fallback to classic if not overriding

# ============================================================
# HTML FORM WITH TEMPLATE SELECTOR
# ============================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CV Builder</title>
    <style>
        body { font-family: Arial, sans-serif; background: #F4F7F6; padding: 30px; }
        .container { max-width: 650px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
        .form-group { margin-bottom: 15px; }
        label { font-weight: bold; display: block; margin-bottom: 5px; }
        input, select, textarea { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; }
        button { background: #02353C; color: white; padding: 12px 20px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h2>CV Builder</h2>
        <form action="/generate" method="POST">
            <div class="form-group">
                <label>Select Template Layout</label>
                <select name="template">
                    <option value="modern" {% if data.get('template') == 'modern' %}selected{% endif %}>Modern (Sidebar + Icons)</option>
                    <option value="classic" {% if data.get('template') == 'classic' %}selected{% endif %}>Classic (Traditional Single Column)</option>
                    <option value="als" {% if data.get('template') == 'als' %}selected{% endif %}>ALS / Executive Minimalist</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>Full Name</label>
                <input type="text" name="name" value="{{ data.get('name', '') }}">
            </div>
            
            <div class="form-group">
                <label>Job Title</label>
                <input type="text" name="title" value="{{ data.get('title', '') }}">
            </div>

            <div class="form-group">
                <label>Work Experience</label>
                <textarea name="experience">{{ data.get('experience', '') }}</textarea>
            </div>

            <button type="submit">Generate CV</button>
        </form>
    </div>
</body>
</html>
"""

# ============================================================
# FLASK ROUTER
# ============================================================
@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE, data=session.get("cv_data", {}))

@app.route("/generate", methods=["POST"])
def generate():
    data = request.form.to_dict()
    session["cv_data"] = data

    selected_template = data.get("template", "modern")
    pdf_path = os.path.join(tempfile.gettempdir(), f"CV_{uuid.uuid4().hex}.pdf")

    # Route request based on selected template
    if selected_template == "classic":
        classic(data, pdf_path)
    elif selected_template == "als":
        als(data, pdf_path)
    else:
        modern(data, pdf_path)

    return send_file(pdf_path, as_attachment=True, download_name=f"CV_{selected_template}.pdf")

if __name__ == "__main__":
    app.run(debug=True)
