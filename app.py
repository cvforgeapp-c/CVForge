import os
import tempfile
import base64
import uuid
import math
from flask import Flask, request, render_template_string, send_file, redirect, url_for

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth

# ============================================================
# 1. FONT REGISTRATION & FLAGS
# ============================================================

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

_modern_canvas = None
PAGE_HEIGHT = 297 * mm
PAGE_WIDTH = 210 * mm
BOTTOM_MARGIN = 15 * mm

# ============================================================
# 2. HTML TEMPLATES
# ============================================================

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CV Generator</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f6f8; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h1 { text-align: center; color: #02353C; margin-bottom: 20px; }
        label { font-weight: bold; display: block; margin-top: 15px; color: #333; }
        input[type="text"], textarea, input[type="file"], input[type="color"] {
            width: 100%; padding: 10px; margin-top: 5px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box;
        }
        textarea { height: 80px; resize: vertical; }
        .row { display: flex; gap: 15px; }
        .row > div { flex: 1; }
        button { margin-top: 25px; width: 100%; padding: 12px; background: #02353C; color: #fff; border: none; border-radius: 4px; font-size: 16px; cursor: pointer; }
        button:hover { background: #053D47; }
    </style>
</head>
<body>
    <div class="container">
        <h1>CV Builder</h1>
        <form action="/generate" method="POST" enctype="multipart/form-data">
            <div class="row">
                <div>
                    <label>Full Name</label>
                    <input type="text" name="name" value="KEDIR ALEMAYEHU" required>
                </div>
                <div>
                    <label>Job Title</label>
                    <input type="text" name="title" value="SOFTWARE DEVELOPER" required>
                </div>
            </div>

            <div class="row">
                <div>
                    <label>Phone</label>
                    <input type="text" name="phone" value="+251 91 234 5678">
                </div>
                <div>
                    <label>Email</label>
                    <input type="text" name="email" value="kediralemayehu@gmail.com">
                </div>
            </div>

            <div class="row">
                <div>
                    <label>Location</label>
                    <input type="text" name="location" value="Addis Ababa, Ethiopia">
                </div>
                <div>
                    <label>LinkedIn</label>
                    <input type="text" name="linkedin" value="linkedin.com/in/kedir-alemayehu">
                </div>
            </div>

            <label>Website</label>
            <input type="text" name="website" value="www.kedir.dev">

            <label>Profile Photo</label>
            <input type="file" name="photo" accept="image/*">

            <label>Professional Summary</label>
            <textarea name="summary">Passionate and dedicated software developer with a strong foundation in Python, web development, and problem-solving. Eager to contribute to innovative projects and grow in a dynamic tech environment.</textarea>

            <label>Work Experience (One per line)</label>
            <textarea name="experience">Developed web applications using Python and Flask.
Built and maintained small business websites.
Collaborated with clients to deliver quality solutions.</textarea>

            <label>Education</label>
            <textarea name="education">B.Sc. in Computer Science - Addis Ababa University (2019 - 2023)</textarea>

            <label>Skills (One per line)</label>
            <textarea name="skills">Python
Flask
HTML & CSS
JavaScript
Git & GitHub
Problem Solving
Team Collaboration</textarea>

            <label>Certificates (One per line)</label>
            <textarea name="certificates">Python Programming - Udemy (2023)
Web Development with Flask - Coursera (2023)</textarea>

            <label>Languages (One per line)</label>
            <textarea name="languages">Amharic (Native)
English (Fluent)</textarea>

            <label>Interests / Hobbies (One per line)</label>
            <textarea name="hobbies">Technology
Reading
Football
Travel</textarea>

            <label>References (One per line)</label>
            <textarea name="references">Dr. Samuel Tadesse - Senior Software Engineer, EthioTech (+251 91 000 1234)
Mesfin Girma - Lecturer, Addis Ababa University (+251 91 111 2233)</textarea>

            <div class="row">
                <div>
                    <label>Sidebar Color</label>
                    <input type="color" name="sidebar_color" value="#02353C">
                </div>
                <div>
                    <label>Accent Color</label>
                    <input type="color" name="accent_color" value="#E5A93C">
                </div>
            </div>

            <button type="submit">Generate PDF CV</button>
        </form>
    </div>
</body>
</html>
"""

PREVIEW_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CV Preview</title>
    <style>
        body { margin: 0; background: #2b2b2b; display: flex; flex-direction: column; align-items: center; min-height: 100vh; font-family: Arial, sans-serif; }
        .controls { width: 100%; max-width: 900px; padding: 15px; display: flex; justify-content: space-between; box-sizing: border-box; }
        a { text-decoration: none; padding: 10px 20px; border-radius: 4px; font-weight: bold; }
        .btn-back { background: #555; color: #fff; }
        .btn-download { background: #E5A93C; color: #02353C; }
        iframe { width: 100%; max-width: 900px; height: 85vh; border: none; box-shadow: 0 4px 10px rgba(0,0,0,0.5); background: #fff; }
    </style>
</head>
<body>
    <div class="controls">
        <a href="/" class="btn-back">← Edit Details</a>
        <a href="/download/{{ token }}" class="btn-download">Download PDF</a>
    </div>
    <iframe src="data:application/pdf;base64,{{ pdf_data }}"></iframe>
</body>
</html>
"""

# ============================================================
# 3. VECTOR ICON DRAWING HELPERS
# ============================================================

def draw_circle_icon(c, x, y, radius, bg_color, icon_type):
    c.saveState()
    c.setFillColor(bg_color)
    c.circle(x, y, radius, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setStrokeColor(colors.white)
    c.setLineWidth(1)

    r = radius * 0.55

    if icon_type == "experience":
        c.rect(x - r*0.7, y - r*0.5, r*1.4, r*1.0, stroke=1, fill=0)
        c.rect(x - r*0.3, y + r*0.5, r*0.6, r*0.3, stroke=1, fill=0)
        c.line(x - r*0.7, y + r*0.1, x + r*0.7, y + r*0.1)

    elif icon_type == "education":
        p = c.beginPath()
        p.moveTo(x - r*0.9, y)
        p.lineTo(x, y + r*0.6)
        p.lineTo(x + r*0.9, y)
        p.lineTo(x, y - r*0.6)
        p.close()
        c.drawPath(p, stroke=1, fill=1)
        c.rect(x - r*0.5, y - r*0.7, r*1.0, r*0.4, stroke=0, fill=1)

    elif icon_type == "certificates":
        c.rect(x - r*0.6, y - r*0.7, r*1.2, r*1.4, stroke=1, fill=0)
        c.line(x - r*0.3, y + r*0.3, x + r*0.3, y + r*0.3)
        c.line(x - r*0.3, y, x + r*0.3, y)
        c.line(x - r*0.3, y - r*0.3, x + r*0.1, y - r*0.3)

    elif icon_type == "references":
        c.circle(x, y + r*0.3, r*0.35, stroke=1, fill=1)
        p = c.beginPath()
        p.moveTo(x - r*0.6, y - r*0.6)
        p.curveTo(x - r*0.6, y - r*0.1, x + r*0.6, y - r*0.1, x + r*0.6, y - r*0.6)
        c.drawPath(p, stroke=1, fill=1)

    elif icon_type == "contact":
        c.circle(x, y + r*0.2, r*0.4, stroke=1, fill=0)
        p = c.beginPath()
        p.moveTo(x - r*0.3, y + r*0.1)
        p.lineTo(x, y - r*0.7)
        p.lineTo(x + r*0.3, y + r*0.1)
        c.drawPath(p, stroke=1, fill=1)

    elif icon_type == "skills":
        c.circle(x, y, r*0.4, stroke=1, fill=0)
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            c.line(x + r*0.4*math.cos(rad), y + r*0.4*math.sin(rad), x + r*0.75*math.cos(rad), y + r*0.75*math.sin(rad))

    elif icon_type == "languages":
        c.circle(x, y, r*0.7, stroke=1, fill=0)
        c.line(x - r*0.7, y, x + r*0.7, y)
        c.line(x, y - r*0.7, x, y + r*0.7)

    elif icon_type == "interests":
        p = c.beginPath()
        p.moveTo(x, y - r*0.6)
        p.curveTo(x - r*0.8, y, x - r*0.8, y + r*0.6, x, y + r*0.3)
        p.curveTo(x + r*0.8, y + r*0.6, x + r*0.8, y, x, y - r*0.6)
        c.drawPath(p, stroke=1, fill=1)

    c.restoreState()

def draw_sidebar_contact_icon(c, x, y, icon_type, color):
    c.saveState()
    c.setFillColor(color)
    c.setStrokeColor(color)
    c.setLineWidth(1)
    r = 2.2 * mm

    if icon_type == "phone":
        c.rect(x - r*0.4, y - r*0.7, r*0.8, r*1.4, stroke=1, fill=0)
        c.circle(x, y - r*0.4, 0.4, stroke=0, fill=1)

    elif icon_type == "email":
        c.rect(x - r*0.7, y - r*0.5, r*1.4, r*1.0, stroke=1, fill=0)
        p = c.beginPath()
        p.moveTo(x - r*0.7, y + r*0.5)
        p.lineTo(x, y)
        p.lineTo(x + r*0.7, y + r*0.5)
        c.drawPath(p, stroke=1, fill=0)

    elif icon_type == "location":
        c.circle(x, y + r*0.2, r*0.4, stroke=1, fill=0)
        p = c.beginPath()
        p.moveTo(x - r*0.3, y + r*0.1)
        p.lineTo(x, y - r*0.6)
        p.lineTo(x + r*0.3, y + r*0.1)
        c.drawPath(p, stroke=1, fill=1)

    elif icon_type == "linkedin":
        c.rect(x - r*0.6, y - r*0.6, r*1.2, r*1.2, stroke=1, fill=0)
        c.setFont("Helvetica-Bold", 5)
        c.drawString(x - r*0.3, y - r*0.3, "in")

    elif icon_type == "website":
        c.circle(x, y, r*0.6, stroke=1, fill=0)
        c.line(x - r*0.6, y, x + r*0.6, y)
        c.line(x, y - r*0.6, x, y + r*0.6)

    c.restoreState()

# ============================================================
# 4. TEXT WRAPPING & PAGINATION UTILITIES
# ============================================================

def clean(text):
    return str(text).strip() if text else ""

def wrap_text(c, text, font, size, max_width):
    words = clean(text).split()
    lines = []
    current = ""

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

def check_page_overflow(c, y, required_space, sidebar_color):
    if y - required_space < BOTTOM_MARGIN:
        c.showPage()
        c.setFillColor(sidebar_color)
        c.rect(0, 0, 78 * mm, PAGE_HEIGHT, fill=True, stroke=False)
        return PAGE_HEIGHT - 20 * mm
    return y

# ============================================================
# 5. MODERN TEMPLATE GENERATOR
# ============================================================

def modern(data, file):
    W, H = A4
    c = canvas.Canvas(file, pagesize=A4)
    global _modern_canvas
    _modern_canvas = c
    c.setTitle("CV - " + (data.get("name") or "KEDIR ALEMAYEHU"))

    sidebar_color = colors.HexColor(data.get("sidebar_color") or "#02353C")
    gold = colors.HexColor(data.get("accent_color") or "#E5A93C")
    white = colors.white
    dark = colors.HexColor("#02353C")
    muted = colors.HexColor("#334E55")

    sidebar_w = 78 * mm
    main_x = sidebar_w + 12 * mm
    main_w = W - main_x - 12 * mm

    c.setFillColor(colors.HexColor("#FFFFFF"))
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(sidebar_color)
    c.rect(0, 0, sidebar_w, H, stroke=0, fill=1)

    photo = data.get("photo")
    photo_size = 52 * mm
    photo_x = (sidebar_w - photo_size) / 2
    photo_y = H - 65 * mm

    if photo and os.path.exists(photo):
        try:
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
            print(f"Photo render error: {e}")

    def draw_lines(value, x, y, width, font="Helvetica", size=9, leading=4.8 * mm, color=dark, bullet=False):
        if not value:
            return y
        c.setFillColor(color)
        c.setFont(font, size)

        for paragraph in value.splitlines():
            paragraph = paragraph.strip()
            if not paragraph:
                y -= leading * 0.5
                continue

            lines = wrap(paragraph, font, size, width)
            for index, line in enumerate(lines):
                prefix = "• " if (bullet and index == 0) else ("  " if bullet else "")
                c.drawString(x, y, prefix + line)
                y -= leading
        return y

    def main_section(title, icon_type, x, y, width):
        draw_circle_icon(c, x + 5.5 * mm, y + 1.5 * mm, 5.5 * mm, dark, icon_type)
        c.setFillColor(dark)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x + 14 * mm, y, title.upper())
        c.setStrokeColor(gold)
        c.setLineWidth(1.2)
        c.line(x + 13 * mm, y - 3.5 * mm, x + width, y - 3.5 * mm)
        return y - 10 * mm

    def sidebar_section(title, icon_type, x, y, width):
        draw_circle_icon(c, x + 3.5 * mm, y + 1.5 * mm, 4.5 * mm, gold, icon_type)
        c.setFillColor(gold)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x + 10 * mm, y, title.upper())
        c.setStrokeColor(gold)
        c.setLineWidth(1)
        c.line(x, y - 3 * mm, x + width, y - 3 * mm)
        return y - 9 * mm

    sx = 10 * mm
    sw = sidebar_w - 20 * mm
    sy = H - 80 * mm

    sy = sidebar_section("Contact", "contact", sx, sy, sw)
    contacts = [
        ("phone", data.get("phone") or "+251 91 234 5678"),
        ("email", data.get("email") or "kediralemayehu@gmail.com"),
        ("location", data.get("location") or "Addis Ababa, Ethiopia"),
        ("linkedin", data.get("linkedin") or "linkedin.com/in/kedir-alemayehu"),
        ("website", data.get("website") or "www.kedir.dev"),
    ]

    for icon, val in contacts:
        if val:
            draw_sidebar_contact_icon(c, sx + 2 * mm, sy + 1.2 * mm, icon, gold)
            sy = draw_lines(val, sx + 7 * mm, sy, sw - 7 * mm, size=8.2, leading=4.5 * mm, color=white)
            sy -= 1.5 * mm

    if data.get("skills"):
        sy -= 3 * mm
        sy = check_page_overflow(c, sy, 20 * mm, sidebar_color)
        sy = sidebar_section("Skills", "skills", sx, sy, sw)
        for skill in data["skills"].splitlines():
            if skill.strip():
                sy = draw_lines(skill.strip(), sx + 2 * mm, sy, sw - 2 * mm, size=8.8, leading=4.8 * mm, color=white, bullet=True)

    if data.get("languages"):
        sy -= 3 * mm
        sy = check_page_overflow(c, sy, 20 * mm, sidebar_color)
        sy = sidebar_section("Languages", "languages", sx, sy, sw)
        for lang in data["languages"].splitlines():
            if lang.strip():
                sy = draw_lines(lang.strip(), sx + 2 * mm, sy, sw - 2 * mm, size=8.8, leading=4.8 * mm, color=white, bullet=True)

    if data.get("hobbies"):
        sy -= 3 * mm
        sy = check_page_overflow(c, sy, 20 * mm, sidebar_color)
        sy = sidebar_section("Interests", "interests", sx, sy, sw)
        for hobby in data["hobbies"].splitlines():
            if hobby.strip():
                sy = draw_lines(hobby.strip(), sx + 2 * mm, sy, sw - 2 * mm, size=8.8, leading=4.8 * mm, color=white, bullet=True)

    name_font = "Montserrat-ExtraBold" if HAS_MONTSERRAT else "Helvetica-Bold"
    name = (data.get("name") or "KEDIR ALEMAYEHU").upper()

    c.setFillColor(dark)
    c.setFont(name_font, 22)
    c.drawString(main_x, H - 22 * mm, name)

    title = (data.get("title") or "SOFTWARE DEVELOPER").upper()
    c.setFillColor(gold)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(main_x, H - 29 * mm, title)

    y = H - 38 * mm

    summary = data.get("summary") or ""
    y = draw_lines(summary, main_x, y, main_w, size=9, leading=4.8 * mm, color=muted)
    y -= 6 * mm

    if data.get("experience"):
        y = check_page_overflow(c, y, 25 * mm, sidebar_color)
        y = main_section("Experience", "experience", main_x, y, main_w)
        y = draw_lines(data["experience"], main_x, y, main_w, size=8.8, leading=4.8 * mm, color=muted, bullet=True)
        y -= 5 * mm

    if data.get("education"):
        y = check_page_overflow(c, y, 20 * mm, sidebar_color)
        y = main_section("Education", "education", main_x, y, main_w)
        y = draw_lines(data["education"], main_x, y, main_w, size=8.8, leading=4.8 * mm, color=muted, bullet=True)
        y -= 5 * mm

    if data.get("certificates"):
        y = check_page_overflow(c, y, 20 * mm, sidebar_color)
        y = main_section("Certificates", "certificates", main_x, y, main_w)
        y = draw_lines(data["certificates"], main_x, y, main_w, size=8.8, leading=4.8 * mm, color=muted, bullet=True)
        y -= 5 * mm

    if data.get("references"):
        y = check_page_overflow(c, y, 25 * mm, sidebar_color)
        y = main_section("References", "references", main_x, y, main_w)
        y = draw_lines(data["references"], main_x, y, main_w, size=8.8, leading=4.8 * mm, color=muted, bullet=True)
        y -= 6 * mm

    sig_font = "DancingScript" if HAS_DANCING else "Helvetica-Oblique"
    c.setFillColor(dark)
    c.setFont(sig_font, 26)
    c.drawString(main_x, y - 4 * mm, name.title())
    c.setStrokeColor(gold)
    c.setLineWidth(1)
    c.line(main_x, y - 6 * mm, main_x + 65 * mm, y - 6 * mm)

    c.save()

def generate_pdf(data, filename):
    modern(data, filename)

# ============================================================
# 6. FLASK CONTROLLERS & ROUTES
# ============================================================

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/generate", methods=["GET", "POST"])
def generate():
    if request.method == "GET":
        return redirect(url_for("home"))

    photo = request.files.get("photo")

    data = {
        "name": request.form.get("name", "KEDIR ALEMAYEHU"),
        "title": request.form.get("title", "SOFTWARE DEVELOPER"),
        "phone": request.form.get("phone", "+251 91 234 5678"),
        "email": request.form.get("email", "kediralemayehu@gmail.com"),
        "location": request.form.get("location", "Addis Ababa, Ethiopia"),
        "linkedin": request.form.get("linkedin", "linkedin.com/in/kedir-alemayehu"),
        "website": request.form.get("website", "www.kedir.dev"),
        "summary": request.form.get("summary", ""),
        "experience": request.form.get("experience", ""),
        "education": request.form.get("education", ""),
        "skills": request.form.get("skills", ""),
        "certificates": request.form.get("certificates", ""),
        "languages": request.form.get("languages", ""),
        "hobbies": request.form.get("hobbies", ""),
        "references": request.form.get("references", ""),
        "accent_color": request.form.get("accent_color", "#E5A93C"),
        "sidebar_color": request.form.get("sidebar_color", "#02353C"),
    }

    if photo and photo.filename:
        photo_path = os.path.join(tempfile.gettempdir(), "CV_" + uuid.uuid4().hex + "_" + photo.filename)
        photo.save(photo_path)
        data["photo"] = photo_path

    filename = os.path.join(tempfile.gettempdir(), "CV_" + uuid.uuid4().hex + ".pdf")
    generate_pdf(data, filename)

    with open(filename, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()

    pdf_data = base64.b64encode(pdf_bytes).decode("utf-8")
    token = str(uuid.uuid4())
    preview_file = os.path.join(tempfile.gettempdir(), "CV_" + token + ".pdf")

    with open(preview_file, "wb") as output:
        output.write(pdf_bytes)

    return render_template_string(PREVIEW_HTML, pdf_data=pdf_data, token=token)

@app.route("/download/<token>")
def download_pdf(token):
    filename = os.path.join(tempfile.gettempdir(), "CV_" + token + ".pdf")
    if not os.path.exists(filename):
        return "CV not found.", 404
    return send_file(filename, as_attachment=True, download_name="KEDIR_ALEMAYEHU_CV.pdf", mimetype="application/pdf")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=False)
