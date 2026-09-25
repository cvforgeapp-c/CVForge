import os
import tempfile
import base64
import uuid
from flask import Flask, request, render_template_string, send_file

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ============================================================
# 1. FONT CONFIGURATION & SAFE FALLBACKS
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
    except Exception:
        pass

if os.path.exists(DANCING_SCRIPT):
    try:
        pdfmetrics.registerFont(TTFont("DancingScript", DANCING_SCRIPT))
        HAS_DANCING = True
    except Exception:
        pass

app = Flask(__name__)

PAGE_HEIGHT = 297 * mm  # A4 Height
PAGE_WIDTH = 210 * mm   # A4 Width
BOTTOM_MARGIN = 15 * mm

# ============================================================
# 2. VECTOR ICON & SECTION BADGE DRAWING FUNCTIONS
# ============================================================

def draw_sidebar_icon(c, x, y, icon_type, color):
    """
    Renders accurate vector line icons matching the reference sidebar.
    """
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1.0)
    
    if icon_type == "phone":
        p = c.beginPath()
        p.moveTo(x - 1.8 * mm, y + 2.2 * mm)
        p.curveTo(x - 2.5 * mm, y + 1.2 * mm, x - 2.5 * mm, y - 1.2 * mm, x - 1.5 * mm, y - 2.2 * mm)
        p.curveTo(x - 0.5 * mm, y - 2.2 * mm, x + 0.5 * mm, y - 1.2 * mm, x + 1.5 * mm, y - 0.2 * mm)
        p.curveTo(x + 2.2 * mm, y + 0.5 * mm, x + 1.2 * mm, y + 1.5 * mm, x + 0.2 * mm, y + 2.2 * mm)
        c.drawPath(p, stroke=1, fill=0)

    elif icon_type == "email":
        c.rect(x - 2.5 * mm, y - 1.8 * mm, 5.0 * mm, 3.6 * mm, stroke=1, fill=0)
        p = c.beginPath()
        p.moveTo(x - 2.5 * mm, y + 1.8 * mm)
        p.lineTo(x, y - 0.2 * mm)
        p.lineTo(x + 2.5 * mm, y + 1.8 * mm)
        c.drawPath(p, stroke=1, fill=0)

    elif icon_type == "location":
        c.circle(x, y + 0.8 * mm, 1.5 * mm, stroke=1, fill=0)
        p = c.beginPath()
        p.moveTo(x - 1.4 * mm, y + 0.2 * mm)
        p.lineTo(x, y - 2.5 * mm)
        p.lineTo(x + 1.4 * mm, y + 0.2 * mm)
        c.drawPath(p, stroke=1, fill=0)

    elif icon_type == "linkedin":
        c.rect(x - 2.2 * mm, y - 2.2 * mm, 4.4 * mm, 4.4 * mm, stroke=1, fill=0)
        c.setFont("Helvetica-Bold", 5)
        c.drawString(x - 1.2 * mm, y - 1.1 * mm, "in")

    elif icon_type == "website":
        c.circle(x, y, 2.2 * mm, stroke=1, fill=0)
        c.line(x - 2.2 * mm, y, x + 2.2 * mm, y)
        c.line(x, y - 2.2 * mm, x, y + 2.2 * mm)

    elif icon_type == "contact_header":
        c.circle(x, y + 1.0 * mm, 1.4 * mm, stroke=1, fill=0)
        c.arc(x - 2.2 * mm, y - 2.2 * mm, x + 2.2 * mm, y + 0.2 * mm, 0, 180)

    elif icon_type == "skills_header":
        c.circle(x, y, 1.8 * mm, stroke=1, fill=0)
        c.line(x, y + 1.8 * mm, x, y + 2.6 * mm)
        c.line(x, y - 1.8 * mm, x, y - 2.6 * mm)
        c.line(x + 1.8 * mm, y, x + 2.6 * mm, y)
        c.line(x - 1.8 * mm, y, x - 2.6 * mm, y)

    elif icon_type == "languages_header":
        c.circle(x, y, 2.3 * mm, stroke=1, fill=0)
        c.ellipse(x - 1.0 * mm, y - 2.3 * mm, x + 1.0 * mm, y + 2.3 * mm, stroke=1, fill=0)

    elif icon_type == "interests_header":
        p = c.beginPath()
        p.moveTo(x, y - 2.0 * mm)
        p.curveTo(x - 2.8 * mm, y + 0.8 * mm, x - 1.4 * mm, y + 2.8 * mm, x, y + 0.8 * mm)
        p.curveTo(x + 1.4 * mm, y + 2.8 * mm, x + 2.8 * mm, y + 0.8 * mm, x, y - 2.0 * mm)
        c.drawPath(p, stroke=1, fill=1)


def draw_section_badge(c, x, y, title, icon_type, badge_bg, icon_gold, text_dark):
    """
    Renders circular badge with golden icon and bold section heading line.
    """
    badge_radius = 5.2 * mm
    c.setFillColor(badge_bg)
    c.circle(x, y, badge_radius, stroke=0, fill=1)

    c.setFillColor(icon_gold)
    c.setStrokeColor(icon_gold)
    c.setLineWidth(1.0)

    if icon_type == "experience":
        c.rect(x - 2.6 * mm, y - 1.8 * mm, 5.2 * mm, 3.6 * mm, stroke=1, fill=0)
        c.rect(x - 1.2 * mm, y + 1.8 * mm, 2.4 * mm, 1.0 * mm, stroke=1, fill=0)

    elif icon_type == "education":
        p = c.beginPath()
        p.moveTo(x, y + 2.4 * mm)
        p.lineTo(x + 3.2 * mm, y)
        p.lineTo(x, y - 2.4 * mm)
        p.lineTo(x - 3.2 * mm, y)
        p.close()
        c.drawPath(p, stroke=1, fill=1)
        c.line(x + 2.2 * mm, y - 0.6 * mm, x + 2.2 * mm, y - 3.0 * mm)

    elif icon_type == "certificates":
        c.rect(x - 2.2 * mm, y - 2.8 * mm, 4.4 * mm, 5.6 * mm, stroke=1, fill=0)
        c.line(x - 1.2 * mm, y + 1.2 * mm, x + 1.2 * mm, y + 1.2 * mm)
        c.line(x - 1.2 * mm, y - 0.2 * mm, x + 1.2 * mm, y - 0.2 * mm)

    elif icon_type == "references":
        c.circle(x - 1.2 * mm, y + 1.2 * mm, 1.2 * mm, stroke=1, fill=0)
        c.circle(x + 1.5 * mm, y + 1.2 * mm, 1.0 * mm, stroke=1, fill=0)
        c.arc(x - 3.2 * mm, y - 2.8 * mm, x + 0.8 * mm, y + 0.6 * mm, 0, 180)

    c.setFillColor(text_dark)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x + 8.5 * mm, y - 1.8 * mm, title.upper())


# ============================================================
# 3. TEXT WRAPPING & PAGE OVERFLOW LOGIC
# ============================================================

def safe_wrap_text(text, font, size, max_width):
    if not text:
        return []
    words = str(text).strip().split(" ")
    wrapped_lines = []
    current_line = ""

    for word in words:
        if not word:
            continue
        word_width = pdfmetrics.stringWidth(word, font, size)
        if word_width > max_width:
            if current_line:
                wrapped_lines.append(current_line)
                current_line = ""
            sub_word = ""
            for char in word:
                if pdfmetrics.stringWidth(sub_word + char, font, size) <= max_width:
                    sub_word += char
                else:
                    wrapped_lines.append(sub_word)
                    sub_word = char
            if sub_word:
                current_line = sub_word
            continue

        test_line = f"{current_line} {word}".strip()
        if pdfmetrics.stringWidth(test_line, font, size) <= max_width:
            current_line = test_line
        else:
            wrapped_lines.append(current_line)
            current_line = word

    if current_line:
        wrapped_lines.append(current_line)
    return wrapped_lines


def check_page_overflow(c, current_y, required_height, sidebar_color):
    if current_y - required_height < BOTTOM_MARGIN:
        c.showPage()
        W, H = A4
        sidebar_w = 78 * mm
        c.setFillColor(colors.HexColor("#FAFCFB"))
        c.rect(0, 0, W, H, stroke=0, fill=1)
        c.setFillColor(sidebar_color)
        c.rect(0, 0, sidebar_w, H, stroke=0, fill=1)
        return PAGE_HEIGHT - 20 * mm
    return current_y


# ============================================================
# 4. MODERN TEMPLATE GENERATOR (REFERENCE REPLICATOR)
# ============================================================

def modern_template(data, file):
    W, H = A4
    c = canvas.Canvas(file, pagesize=A4)
    font_bold = "Montserrat-ExtraBold" if HAS_MONTSERRAT else "Helvetica-Bold"
    c.setTitle("CV - " + (data.get("name") or "Kedir Alemayehu"))

    # Colors matched to exact reference image
    sidebar_bg = colors.HexColor(data.get("sidebar_color") or "#02353C")
    gold_accent = colors.HexColor(data.get("accent_color") or "#E5A93C")
    title_dark = colors.HexColor("#0D3B4C")
    body_muted = colors.HexColor("#334E58")
    white = colors.white

    sidebar_w = 78 * mm
    main_x = sidebar_w + 12 * mm
    main_w = W - main_x - 12 * mm

    # Background canvas
    c.setFillColor(colors.HexColor("#FAFCFB"))
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(sidebar_bg)
    c.rect(0, 0, sidebar_w, H, stroke=0, fill=1)

    # 1. Profile Photo Render
    photo_path = data.get("photo")
    if photo_path and os.path.exists(photo_path):
        try:
            photo_size = 54 * mm
            photo_x = (sidebar_w - photo_size) / 2
            photo_y = H - 64 * mm

            # Outer Gold Circle Frame
            c.setFillColor(gold_accent)
            c.circle(photo_x + photo_size / 2, photo_y + photo_size / 2, photo_size / 2 + 2.5 * mm, stroke=0, fill=1)
            c.setFillColor(white)
            c.circle(photo_x + photo_size / 2, photo_y + photo_size / 2, photo_size / 2 + 0.8 * mm, stroke=0, fill=1)

            # Circular Image Clipping
            c.saveState()
            path = c.beginPath()
            path.circle(photo_x + photo_size / 2, photo_y + photo_size / 2, photo_size / 2)
            c.clipPath(path, stroke=0, fill=0)
            c.drawImage(ImageReader(photo_path), photo_x, photo_y, width=photo_size, height=photo_size, preserveAspectRatio=True, anchor="c", mask="auto")
            c.restoreState()
        except Exception as e:
            print(f"Error rendering profile photo: {e}")

    # Sidebar Render Helper
    def sidebar_heading(title, icon_type, y_pos):
        y_pos = check_page_overflow(c, y_pos, 15 * mm, sidebar_bg)
        draw_sidebar_icon(c, 12 * mm, y_pos + 1.5 * mm, icon_type, gold_accent)
        c.setFillColor(gold_accent)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(18 * mm, y_pos, title.upper())

        c.setStrokeColor(gold_accent)
        c.setLineWidth(1)
        c.line(18 * mm, y_pos - 2.5 * mm, sidebar_w - 10 * mm, y_pos - 2.5 * mm)
        return y_pos - 9 * mm

    sx = 10 * mm
    sw = sidebar_w - 20 * mm
    sy = H - 76 * mm

    # Sidebar Contact Details
    sy = sidebar_heading("Contact", "contact_header", sy)
    contacts = [
        ("phone", data.get("phone")),
        ("email", data.get("email")),
        ("location", data.get("location")),
        ("linkedin", data.get("linkedin")),
        ("website", data.get("website"))
    ]

    for icon_type, val in contacts:
        if val and str(val).strip():
            sy = check_page_overflow(c, sy, 6 * mm, sidebar_bg)
            draw_sidebar_icon(c, sx + 2.5 * mm, sy + 1.5 * mm, icon_type, white)
            c.setFillColor(white)
            c.setFont("Helvetica", 8.5)
            lines = safe_wrap_text(str(val).strip(), "Helvetica", 8.5, sw - 8 * mm)
            for line in lines:
                c.drawString(sx + 8.5 * mm, sy, line)
                sy -= 4.6 * mm
            sy -= 1.8 * mm
    sy -= 3 * mm

    # Sidebar Skills
    if data.get("skills"):
        sy = sidebar_heading("Skills", "skills_header", sy)
        c.setFillColor(white)
        c.setFont("Helvetica", 9)
        for skill in data["skills"].splitlines():
            if skill.strip():
                sy = check_page_overflow(c, sy, 5.2 * mm, sidebar_bg)
                c.drawString(sx + 3 * mm, sy, "• " + skill.strip())
                sy -= 5.2 * mm
        sy -= 3 * mm

    # Sidebar Languages
    if data.get("languages"):
        sy = sidebar_heading("Languages", "languages_header", sy)
        c.setFillColor(white)
        c.setFont("Helvetica", 9)
        for lang in data["languages"].splitlines():
            if lang.strip():
                sy = check_page_overflow(c, sy, 5.2 * mm, sidebar_bg)
                c.drawString(sx + 3 * mm, sy, "• " + lang.strip())
                sy -= 5.2 * mm
        sy -= 3 * mm

    # Sidebar Interests
    if data.get("hobbies"):
        sy = sidebar_heading("Interests", "interests_header", sy)
        c.setFillColor(white)
        c.setFont("Helvetica", 9)
        for hobby in data["hobbies"].splitlines():
            if hobby.strip():
                sy = check_page_overflow(c, sy, 5.2 * mm, sidebar_bg)
                c.drawString(sx + 3 * mm, sy, "• " + hobby.strip())
                sy -= 5.2 * mm

    # Main Header Block
    name = (data.get("name") or "KEDIR ALEMAYEHU").upper()
    c.setFillColor(title_dark)
    c.setFont(font_bold, 24)
    c.drawString(main_x, H - 22 * mm, name[:36])

    title = (data.get("title") or "SOFTWARE DEVELOPER").upper()
    c.setFillColor(gold_accent)
    c.setFont("Helvetica-Bold", 12.5)
    c.drawString(main_x, H - 29 * mm, title)

    my = H - 38 * mm

    # Professional Summary
    if data.get("summary"):
        c.setFillColor(body_muted)
        c.setFont("Helvetica", 9)
        summary_lines = safe_wrap_text(data["summary"], "Helvetica", 9, main_w)
        for line in summary_lines:
            c.drawString(main_x, my, line)
            my -= 4.5 * mm
        my -= 6 * mm

    def main_section_header(title, icon_type, y_pos):
        y_pos = check_page_overflow(c, y_pos, 15 * mm, sidebar_bg)
        draw_section_badge(c, main_x + 3.5 * mm, y_pos + 1 * mm, title, icon_type, sidebar_bg, gold_accent, title_dark)
        c.setStrokeColor(gold_accent)
        c.setLineWidth(1)
        c.line(main_x, y_pos - 4 * mm, main_x + main_w, y_pos - 4 * mm)
        return y_pos - 10 * mm

    # Experience Section
    if data.get("experience"):
        my = main_section_header("Experience", "experience", my)
        blocks = data["experience"].split("\n\n")
        for block in blocks:
            lines = [l.strip() for l in block.splitlines() if l.strip()]
            if not lines:
                continue

            header_parts = [p.strip() for p in lines[0].split("|")]
            role = header_parts[0]
            sub = header_parts[1] if len(header_parts) > 1 else ""
            date_str = header_parts[2] if len(header_parts) > 2 else ""

            my = check_page_overflow(c, my, 12 * mm, sidebar_bg)
            c.setFillColor(title_dark)
            c.setFont("Helvetica-Bold", 10.5)
            c.drawString(main_x, my, role)
            if date_str:
                c.setFillColor(body_muted)
                c.setFont("Helvetica", 9)
                c.drawRightString(main_x + main_w, my, date_str)
            my -= 4.8 * mm

            if sub:
                c.setFillColor(body_muted)
                c.setFont("Helvetica-Oblique", 9)
                c.drawString(main_x, my, sub)
                my -= 5 * mm

            c.setFillColor(body_muted)
            c.setFont("Helvetica", 8.5)
            bullet_lines = lines[1:] if len(header_parts) > 1 else lines[1:]
            for bline in bullet_lines:
                my = check_page_overflow(c, my, 5 * mm, sidebar_bg)
                b_text = bline if bline.startswith("•") else "• " + bline
                wrapped_b = safe_wrap_text(b_text, "Helvetica", 8.5, main_w)
                for wline in wrapped_b:
                    c.drawString(main_x, my, wline)
                    my -= 4.2 * mm
            my -= 3.5 * mm

    # Education Section
    if data.get("education"):
        my = main_section_header("Education", "education", my)
        blocks = data["education"].split("\n\n")
        for block in blocks:
            lines = [l.strip() for l in block.splitlines() if l.strip()]
            if not lines:
                continue
            header_parts = [p.strip() for p in lines[0].split("|")]
            degree = header_parts[0]
            school = header_parts[1] if len(header_parts) > 1 else ""
            date_str = header_parts[2] if len(header_parts) > 2 else ""

            my = check_page_overflow(c, my, 10 * mm, sidebar_bg)
            c.setFillColor(title_dark)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(main_x, my, degree)
            if date_str:
                c.setFillColor(body_muted)
                c.setFont("Helvetica", 9)
                c.drawRightString(main_x + main_w, my, date_str)
            my -= 4.8 * mm

            if school:
                c.setFillColor(body_muted)
                c.setFont("Helvetica", 9)
                c.drawString(main_x, my, school)
                my -= 5 * mm
            my -= 2.5 * mm

    # Certificates Section
    if data.get("certificates"):
        my = main_section_header("Certificates", "certificates", my)
        for line in data["certificates"].splitlines():
            if not line.strip():
                continue
            parts = [p.strip() for p in line.split("|")]
            cert_name = parts[0]
            issuer = parts[1] if len(parts) > 1 else ""
            date_str = parts[2] if len(parts) > 2 else ""

            my = check_page_overflow(c, my, 10 * mm, sidebar_bg)
            c.setFillColor(title_dark)
            c.setFont("Helvetica-Bold", 9.5)
            c.drawString(main_x, my, "• " + cert_name)
            if date_str:
                c.setFillColor(body_muted)
                c.setFont("Helvetica", 8.5)
                c.drawRightString(main_x + main_w, my, date_str)
            my -= 4.2 * mm

            if issuer:
                c.setFillColor(body_muted)
                c.setFont("Helvetica", 8.5)
                c.drawString(main_x + 4 * mm, my, issuer)
                my -= 4.8 * mm

    # References Section
    if data.get("references"):
        my = main_section_header("References", "references", my)
        for line in data["references"].splitlines():
            if not line.strip():
                continue
            parts = [p.strip() for p in line.split("|")]
            ref_name = parts[0]
            ref_title = parts[1] if len(parts) > 1 else ""
            ref_contact = " | ".join(parts[2:]) if len(parts) > 2 else ""

            my = check_page_overflow(c, my, 12 * mm, sidebar_bg)
            c.setFillColor(title_dark)
            c.setFont("Helvetica-Bold", 9.5)
            c.drawString(main_x, my, "• " + ref_name)
            my -= 4.2 * mm

            if ref_title:
                c.setFillColor(body_muted)
                c.setFont("Helvetica", 8.5)
                c.drawString(main_x + 4 * mm, my, ref_title)
                my -= 4.2 * mm
            if ref_contact:
                c.setFillColor(body_muted)
                c.setFont("Helvetica", 8.5)
                c.drawString(main_x + 4 * mm, my, ref_contact)
                my -= 4.8 * mm

    # Digital Cursive Signature Block
    sig_name = data.get("signature_name") or "Kedir Alemayehu"
    if sig_name:
        my = check_page_overflow(c, my, 16 * mm, sidebar_bg)
        my -= 4 * mm
        sig_font = "DancingScript" if HAS_DANCING else "Helvetica-BoldOblique"
        c.setFont(sig_font, 18 if HAS_DANCING else 13)
        c.setFillColor(title_dark)
        c.drawString(main_x, my, sig_name)
        c.setStrokeColor(gold_accent)
        c.setLineWidth(1)
        c.line(main_x, my - 2 * mm, main_x + 60 * mm, my - 2 * mm)

    c.save()


# ============================================================
# 5. FRONTEND HTML & UI ENGINE
# ============================================================

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CVForge - Professional CV Builder</title>
<style>
* { box-sizing: border-box; }
body { margin: 0; font-family: 'Segoe UI', Arial, sans-serif; background: #f4f7f7; color: #173f3f; }
.container { max-width: 780px; margin: auto; padding: 20px; }
.card { background: white; border-radius: 18px; padding: 28px; box-shadow: 0 5px 25px rgba(0,0,0,.08); }
.logo { text-align: center; font-size: 32px; font-weight: 800; color: #02353c; }
.subtitle { text-align: center; color: #667; margin-bottom: 25px; font-size: 15px; }
.progress { display: flex; gap: 4px; margin-bottom: 25px; }
.progress div { flex: 1; height: 6px; background: #d9e3e3; border-radius: 10px; }
.progress div.active { background: #e5a93c; }
.step { display: none; }
.step.active { display: block; }
h2 { margin-top: 0; color: #02353c; font-size: 22px; }
label { display: block; margin-top: 15px; margin-bottom: 6px; font-weight: 600; font-size: 14px; }
input, textarea { width: 100%; padding: 12px 14px; border: 1px solid #ccd8d8; border-radius: 10px; font-size: 15px; }
textarea { min-height: 110px; resize: vertical; }
.buttons { display: flex; gap: 10px; margin-top: 25px; }
button { flex: 1; padding: 14px; border: none; border-radius: 10px; font-size: 16px; font-weight: bold; cursor: pointer; }
.next { background: #02353c; color: white; }
.back { background: #e7eeee; color: #173f3f; }
.generate { background: #e5a93c; color: white; }
</style>
</head>
<body>
<div class="container">
<div class="card">
<div class="logo">CVForge</div>
<div class="subtitle">Pixel-Perfect Professional Resume Engine</div>
<form method="POST" action="/generate" enctype="multipart/form-data">
<h2>Personal Details</h2>
<label>Full Name</label><input name="name" value="KEDIR ALEMAYEHU">
<label>Title</label><input name="title" value="SOFTWARE DEVELOPER">
<label>Profile Picture</label><input type="file" name="photo" accept="image/*">
<label>Phone</label><input name="phone" value="+251 91 234 5678">
<label>Email</label><input name="email" value="kediralemayehu@gmail.com">
<label>Location</label><input name="location" value="Addis Ababa, Ethiopia">
<label>LinkedIn</label><input name="linkedin" value="linkedin.com/in/kedir-alemayehu">
<label>Website</label><input name="website" value="www.kedir.dev">
<label>Summary</label><textarea name="summary">Passionate and dedicated software developer with a strong foundation in Python, web development, and problem-solving. Eager to contribute to innovative projects and grow in a dynamic tech environment.</textarea>
<label>Experience</label><textarea name="experience">Junior Software Developer | Self-Employed / Freelance | 2023 – Present
• Developed web applications using Python and Flask.
• Built and maintained small business websites.
• Collaborated with clients to deliver quality solutions.</textarea>
<label>Education</label><textarea name="education">B.Sc. in Computer Science | Addis Ababa University | 2019 – 2023</textarea>
<label>Skills</label><textarea name="skills">Python
Flask
HTML & CSS
JavaScript
Git & GitHub
Problem Solving
Team Collaboration</textarea>
<label>Certificates</label><textarea name="certificates">Python Programming | Udemy | 2023
Web Development with Flask | Coursera | 2023</textarea>
<label>Languages</label><textarea name="languages">Amharic (Native)
English (Fluent)</textarea>
<label>Interests</label><textarea name="hobbies">Technology
Reading
Football
Travel</textarea>
<label>References</label><textarea name="references">Dr. Samuel Tadesse | Senior Software Engineer, EthioTech | +251 91 000 1234 | samuel@ethiotech.com
Mesfin Girma | Lecturer, Addis Ababa University | +251 91 111 2233 | mesfin@aau.edu.et</textarea>
<label>Signature Text</label><input name="signature_name" value="Kedir Alemayehu">
<div class="buttons"><button type="submit" class="generate">GENERATE CV</button></div>
</form>
</div>
</div>
</body>
</html>
"""

PREVIEW_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CV Preview</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
<style>
body { margin: 0; background: #eef3f3; font-family: sans-serif; }
.container { max-width: 900px; margin: auto; padding: 20px; }
.card { background: white; border-radius: 16px; padding: 20px; text-align: center; }
.pdf-page { width: 100%; margin-bottom: 15px; border-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,.15); }
.download { display: inline-block; padding: 14px 28px; background: #e5a93c; color: white; border-radius: 10px; font-weight: bold; text-decoration: none; margin-top: 15px; }
</style>
</head>
<body>
<div class="container">
<div class="card">
<h2>CV Generated Successfully</h2>
<div id="previewBox"></div>
<a class="download" href="/download/{{ token }}">DOWNLOAD PDF</a>
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

# ============================================================
# 6. FLASK CONTROLLER ROUTES
# ============================================================

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/generate", methods=["POST"])
def generate():
    photo = request.files.get("photo")

    data = {
        "name": request.form.get("name", "KEDIR ALEMAYEHU"),
        "title": request.form.get("title", "SOFTWARE DEVELOPER"),
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
        "accent_color": "#E5A93C",
        "sidebar_color": "#02353C",
    }

    if photo and photo.filename:
        photo_path = os.path.join(tempfile.gettempdir(), "CV_" + uuid.uuid4().hex + "_" + photo.filename)
        photo.save(photo_path)
        data["photo"] = photo_path
    else:
        data["photo"] = ""

    token = str(uuid.uuid4())
    filename = os.path.join(tempfile.gettempdir(), "CV_" + token + ".pdf")
    modern_template(data, filename)

    with open(filename, "rb") as f:
        pdf_bytes = f.read()

    if data["photo"] and os.path.exists(data["photo"]):
        try:
            os.remove(data["photo"])
        except Exception:
            pass

    return render_template_string(PREVIEW_HTML, pdf_data=base64.b64encode(pdf_bytes).decode("utf-8"), token=token)

@app.route("/download/<token>")
def download_pdf(token):
    filename = os.path.join(tempfile.gettempdir(), "CV_" + token + ".pdf")
    if not os.path.exists(filename):
        return "File not found", 404
    return send_file(filename, as_attachment=True, download_name="Kedir_Alemayehu_CV.pdf", mimetype="application/pdf")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
