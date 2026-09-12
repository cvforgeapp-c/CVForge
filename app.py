from flask import Flask, request, render_template_string, send_file, redirect, url_for
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os
import tempfile
import base64
import uuid

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CVForge - Professional CV Builder</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f4f7f7;
    color: #173f3f;
}

.container {
    max-width: 760px;
    margin: auto;
    padding: 20px;
}

.card {
    background: white;
    border-radius: 18px;
    padding: 25px;
    box-shadow: 0 5px 25px rgba(0,0,0,.08);
}

.logo {
    text-align: center;
    font-size: 30px;
    font-weight: bold;
    color: #0d4f4f;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    color: #777;
    margin-bottom: 25px;
}

.step {
    display: none;
}

.step.active {
    display: block;
}

.progress {
    display: flex;
    gap: 5px;
    margin-bottom: 25px;
}

.progress div {
    flex: 1;
    height: 6px;
    background: #d9e3e3;
    border-radius: 10px;
}

.progress div.active {
    background: #c9a227;
}

h2 {
    margin-top: 0;
    color: #0d4f4f;
}

label {
    display: block;
    margin-top: 15px;
    margin-bottom: 6px;
    font-weight: bold;
}

input,
textarea,
select {
    width: 100%;
    padding: 13px;
    border: 1px solid #ccd8d8;
    border-radius: 10px;
    font-size: 16px;
    font-family: Arial, sans-serif;
}

textarea {
    min-height: 120px;
    resize: vertical;
}

input:focus,
textarea:focus,
select:focus {
    outline: none;
    border-color: #0d4f4f;
}

.buttons {
    display: flex;
    gap: 10px;
    margin-top: 25px;
}

button {
    flex: 1;
    padding: 14px;
    border: none;
    border-radius: 10px;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
}

.next {
    background: #0d4f4f;
    color: white;
}

.back {
    background: #e7eeee;
    color: #173f3f;
}

.generate {
    background: #c9a227;
    color: white;
}

.small {
    color: #777;
    font-size: 13px;
    margin-top: 5px;
}

@media(max-width:600px) {
    .container {
        padding: 10px;
    }

    .card {
        padding: 18px;
    }

    .buttons {
        flex-direction: column;
    }
}
</style>
</head>

<body>

<div class="container">
<div class="card">

<div class="logo">CVForge</div>
<div class="subtitle">Build a professional CV in minutes</div>

<div class="progress">
<div class="p active"></div>
<div class="p"></div>
<div class="p"></div>
<div class="p"></div>
<div class="p"></div>
<div class="p"></div>
<div class="p"></div>
<div class="p"></div>
<div class="p"></div>
<div class="p"></div>
<div class="p"></div>
</div>

<form method="POST" action="/generate" enctype="multipart/form-data">

<div class="step active">
<h2>1. Personal Information</h2>

<label>Full Name *</label>
<input name="name" required>

<label>Professional Title</label>
<input name="title" placeholder="e.g. Software Developer">

<label>Profile Photo</label>
<input type="file" name="photo" accept="image/*">

<label>Phone</label>
<input name="phone">

<label>Email</label>
<input name="email">

<label>Location</label>
<input name="location" placeholder="City, Country">

<label>LinkedIn</label>
<input name="linkedin">

<label>Website</label>
<input name="website">

<div class="buttons">
<button type="button" class="next" onclick="nextStep()">Next →</button>
</div>
</div>

<div class="step">
<h2>2. Professional Summary</h2>

<label>Summary</label>
<textarea name="summary" placeholder="Write a short professional summary about yourself..."></textarea>

<div class="buttons">
<button type="button" class="back" onclick="prevStep()">← Back</button>
<button type="button" class="next" onclick="nextStep()">Next →</button>
</div>
</div>

<div class="step">
<h2>3. Work Experience</h2>

<label>Experience</label>
<textarea name="experience" placeholder="Job Title - Company - Dates

Describe your responsibilities and achievements.

Add another position below if needed."></textarea>

<div class="buttons">
<button type="button" class="back" onclick="prevStep()">← Back</button>
<button type="button" class="next" onclick="nextStep()">Next →</button>
</div>
</div>

<div class="step">
<h2>4. Education</h2>

<label>Education</label>
<textarea name="education" placeholder="Degree - Institution - Year

Add your education history here."></textarea>

<div class="buttons">
<button type="button" class="back" onclick="prevStep()">← Back</button>
<button type="button" class="next" onclick="nextStep()">Next →</button>
</div>
</div>

<div class="step">
<h2>5. Skills</h2>

<label>Skills</label>
<textarea name="skills" placeholder="Python
Flask
Microsoft Office
Communication
Leadership"></textarea>

<div class="buttons">
<button type="button" class="back" onclick="prevStep()">← Back</button>
<button type="button" class="next" onclick="nextStep()">Next →</button>
</div>
</div>

<div class="step">
<h2>6. Certificates & Training</h2>

<label>Certificates</label>
<textarea name="certificates" placeholder="Certificate Name - Organization - Year"></textarea>

<div class="buttons">
<button type="button" class="back" onclick="prevStep()">← Back</button>
<button type="button" class="next" onclick="nextStep()">Next →</button>
</div>
</div>

<div class="step">
<h2>7. Languages</h2>

<label>Languages</label>
<textarea name="languages" placeholder="English - Fluent
Amharic - Native"></textarea>

<div class="buttons">
<button type="button" class="back" onclick="prevStep()">← Back</button>
<button type="button" class="next" onclick="nextStep()">Next →</button>
</div>
</div>

<div class="step">
<h2>8. Interests</h2>

<label>Interests & Hobbies</label>
<textarea name="hobbies" placeholder="Technology
Reading
Travel
Sports"></textarea>

<div class="buttons">
<button type="button" class="back" onclick="prevStep()">← Back</button>
<button type="button" class="next" onclick="nextStep()">Next →</button>
</div>
</div>

<div class="step">
<h2>9. References</h2>

<label>References</label>
<textarea name="references" placeholder="Name - Position - Company
Email / Phone"></textarea>

<div class="buttons">
<button type="button" class="back" onclick="prevStep()">← Back</button>
<button type="button" class="next" onclick="nextStep()">Next →</button>
</div>
</div>

<div class="step">
<h2>10. Choose Template</h2>

<label>CV Template</label>

<select name="template">
<option value="modern">Modern Professional</option>
<option value="classic">Classic Professional</option>
<option value="ats">ATS Friendly</option>
</select>

<p class="small">
Choose the design that best matches your job application.
</p>

<div class="buttons">
<button type="button" class="back" onclick="prevStep()">← Back</button>
<button type="button" class="next" onclick="nextStep()">Next →</button>
</div>
</div>

<div class="step">
<h2>11. Generate Your CV</h2>

<p>
Your information is ready. Click the button below to create your professional CV.
</p>

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
    steps.forEach((step, i) => {
        step.classList.toggle("active", i === index);
    });

    progress.forEach((bar, i) => {
        bar.classList.toggle("active", i <= index);
    });

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}

function nextStep() {
    if (currentStep < steps.length - 1) {
        currentStep++;
        showStep(currentStep);
    }
}

function prevStep() {
    if (currentStep > 0) {
        currentStep--;
        showStep(currentStep);
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
<title>CVForge Preview</title>

<style>
body {
    margin: 0;
    background: #eef3f3;
    font-family: Arial, sans-serif;
    color: #173f3f;
}

.container {
    max-width: 900px;
    margin: auto;
    padding: 20px;
}

.card {
    background: white;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 5px 25px rgba(0,0,0,.08);
}

h1 {
    text-align: center;
    color: #0d4f4f;
}

.preview {
    width: 100%;
    height: 700px;
    border: 1px solid #ddd;
    border-radius: 10px;
}

.buttons {
    display: flex;
    gap: 10px;
    margin-top: 20px;
}

a {
    flex: 1;
    text-align: center;
    text-decoration: none;
    padding: 14px;
    border-radius: 10px;
    font-weight: bold;
}

.edit {
    background: #e7eeee;
    color: #173f3f;
}

.download {
    background: #c9a227;
    color: white;
}

@media(max-width:600px) {
    .buttons {
        flex-direction: column;
    }

    .preview {
        height: 600px;
    }
}
</style>
</head>

<body>

<div class="container">
<div class="card">

<h1>Your CV Preview</h1>

<iframe
class="preview"
src="data:application/pdf;base64,{{ pdf_data }}">
</iframe>

<div class="buttons">
<a class="edit" href="/">← Edit CV</a>
<a class="download" href="/download/{{ token }}">DOWNLOAD CV</a>
</div>

</div>
</div>

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

    c.setFont(font, size)

    for word in words:
        test = word if not current else current + " " + word

        if c.stringWidth(test, font, size) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def draw_wrapped(c, text, x, y, width,
                 font="Helvetica",
                 size=9,
                 leading=12,
                 color=colors.black):

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


def draw_sidebar_title(c, title, x, y):
    c.setFillColor(colors.HexColor("#C9A227"))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y, title.upper())

    return y - 15


def draw_sidebar_list(c, text, x, y, width):
    if not text:
        return y

    items = [
        item.strip()
        for item in text.replace(",", "\n").splitlines()
        if item.strip()
    ]

    c.setFillColor(colors.white)
    c.setFont("Helvetica", 8.5)

    for item in items:
        lines = wrap_text(
            c,
            "• " + item,
            "Helvetica",
            8.5,
            width
        )

        for line in lines:
            c.drawString(x, y, line)
            y -= 12

        y -= 3

    return y


def draw_header(c, data, sidebar_width):
    page_width, page_height = A4

    header_height = 55 * mm

    c.setFillColor(colors.HexColor("#0D4F4F"))
    c.rect(
        0,
        page_height - header_height,
        page_width,
        header_height,
        fill=1,
        stroke=0
    )

    c.setFillColor(colors.HexColor("#C9A227"))
    c.rect(
        0,
        page_height - header_height,
        7 * mm,
        header_height,
        fill=1,
        stroke=0
    )

    name = clean(data.get("name")) or "Your Name"
    title = clean(data.get("title"))

    x = sidebar_width + 12 * mm

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(x, page_height - 23 * mm, name)

    if title:
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.HexColor("#E6EEEE"))
        c.drawString(x, page_height - 32 * mm, title)

    summary = clean(data.get("summary"))

    if summary:
        draw_wrapped(
            c,
            summary,
            x,
            page_height - 39 * mm,
            page_width - x - 12 * mm,
            "Helvetica",
            8.5,
            11,
            colors.HexColor("#E6EEEE")
        )


def draw_sidebar(c, data, sidebar_width):
    page_width, page_height = A4

    c.setFillColor(colors.HexColor("#123E3E"))
    c.rect(
        0,
        0,
        sidebar_width,
        page_height,
        fill=1,
        stroke=0
    )

    x = 9 * mm
    width = sidebar_width - 18 * mm

    y = page_height - 68 * mm

    c.setFillColor(colors.HexColor("#C9A227"))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y, "CONTACT")

    y -= 15

    contact_items = [
        data.get("phone"),
        data.get("email"),
        data.get("location"),
        data.get("linkedin"),
        data.get("website")
    ]

    c.setFillColor(colors.white)
    c.setFont("Helvetica", 8)

    for item in contact_items:
        item = clean(item)

        if not item:
            continue

        for line in wrap_text(
            c,
            item,
            "Helvetica",
            8,
            width
        ):
            c.drawString(x, y, line)
            y -= 11

        y -= 3

    y -= 8

    if clean(data.get("skills")):
        y = draw_sidebar_title(
            c,
            "Skills",
            x,
            y
        )

        y = draw_sidebar_list(
            c,
            data.get("skills"),
            x,
            y,
            width
        )

        y -= 8

    if clean(data.get("languages")):
        y = draw_sidebar_title(
            c,
            "Languages",
            x,
            y
        )

        y = draw_sidebar_list(
            c,
            data.get("languages"),
            x,
            y,
            width
        )

        y -= 8

    if clean(data.get("hobbies")):
        y = draw_sidebar_title(
            c,
            "Interests",
            x,
            y
        )

        y = draw_sidebar_list(
            c,
            data.get("hobbies"),
            x,
            y,
            width
        )


def draw_experience(c, text, x, y, width):
    if not clean(text):
        return y

    blocks = [
        block.strip()
        for block in text.split("\n\n")
        if block.strip()
    ]

    for block in blocks:
        lines = block.splitlines()

        if lines:
            heading = clean(lines[0])

            c.setFillColor(colors.HexColor("#173F3F"))
            c.setFont("Helvetica-Bold", 10)

            c.drawString(x, y, heading)
            y -= 14

            body = " ".join(
                clean(line)
                for line in lines[1:]
                if clean(line)
            )

            if body:
                y = draw_wrapped(
                    c,
                    body,
                    x,
                    y,
                    width,
                    "Helvetica",
                    8.5,
                    11,
                    colors.HexColor("#333333")
                )

            y -= 9

    return y


def draw_education(c, text, x, y, width):
    if not clean(text):
        return y

    blocks = [
        block.strip()
        for block in text.split("\n\n")
        if block.strip()
    ]

    for block in blocks:
        lines = block.splitlines()

        if lines:
            c.setFillColor(colors.HexColor("#173F3F"))
            c.setFont("Helvetica-Bold", 10)

            c.drawString(
                x,
                y,
                clean(lines[0])
            )

            y -= 14

            body = " ".join(
                clean(line)
                for line in lines[1:]
                if clean(line)
            )

            if body:
                y = draw_wrapped(
                    c,
                    body,
                    x,
                    y,
                    width,
                    "Helvetica",
                    8.5,
                    11,
                    colors.HexColor("#333333")
                )

            y -= 9

    return y


def draw_certificates(c, text, x, y, width):
    if not clean(text):
        return y

    items = [
        item.strip()
        for item in text.splitlines()
        if item.strip()
    ]

    c.setFillColor(colors.HexColor("#333333"))
    c.setFont("Helvetica", 8.5)

    for item in items:
        lines = wrap_text(
            c,
            "• " + item,
            "Helvetica",
            8.5,
            width
        )

        for line in lines:
            c.drawString(x, y, line)
            y -= 11

        y -= 3

    return y


def draw_references(c, text, x, y, width):
    if not clean(text):
        return y

    y = draw_wrapped(
        c,
        text,
        x,
        y,
        width,
        "Helvetica",
        8.5,
        11,
        colors.HexColor("#333333")
    )

    return y


def draw_footer(c):
    page_width, page_height = A4

    c.setStrokeColor(colors.HexColor("#D9E3E3"))
    c.setLineWidth(0.5)

    c.line(
        20 * mm,
        12 * mm,
        page_width - 20 * mm,
        12 * mm
    )

    c.setFillColor(colors.HexColor("#777777"))
    c.setFont("Helvetica", 7)

    c.drawCentredString(
        page_width / 2,
        7 * mm,
        "Created with CVForge"
    )

def generate_modern(c, data):
    page_width, page_height = A4

    sidebar_width = 63 * mm
    content_x = sidebar_width + 12 * mm
    content_width = page_width - content_x - 12 * mm

    draw_sidebar(c, data, sidebar_width)
    draw_header(c, data, sidebar_width)

    y = page_height - 68 * mm

    if clean(data.get("experience")):
        y = draw_section_title(
            c,
            "Experience",
            content_x,
            y,
            content_width
        )

        y = draw_experience(
            c,
            data.get("experience"),
            content_x,
            y,
            content_width
        )

    if clean(data.get("education")):
        y -= 5

        y = draw_section_title(
            c,
            "Education",
            content_x,
            y,
            content_width
        )

        y = draw_education(
            c,
            data.get("education"),
            content_x,
            y,
            content_width
        )

    if clean(data.get("certificates")):
        y -= 5

        y = draw_section_title(
            c,
            "Certificates & Training",
            content_x,
            y,
            content_width
        )

        y = draw_certificates(
            c,
            data.get("certificates"),
            content_x,
            y,
            content_width
        )

    if clean(data.get("references")):
        y -= 5

        y = draw_section_title(
            c,
            "References",
            content_x,
            y,
            content_width
        )

        draw_references(
            c,
            data.get("references"),
            content_x,
            y,
            content_width
        )

    draw_footer(c)


def generate_classic(c, data):
    page_width, page_height = A4

    margin = 18 * mm
    content_width = page_width - 2 * margin

    c.setFillColor(colors.HexColor("#173F3F"))
    c.rect(
        0,
        page_height - 42 * mm,
        page_width,
        42 * mm,
        fill=1,
        stroke=0
    )

    name = clean(data.get("name")) or "Your Name"
    title = clean(data.get("title"))

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(
        margin,
        page_height - 18 * mm,
        name
    )

    if title:
        c.setFont("Helvetica", 11)
        c.drawString(
            margin,
            page_height - 27 * mm,
            title
        )

    contact = " • ".join([
        clean(data.get("phone")),
        clean(data.get("email")),
        clean(data.get("location"))
    ])

    contact = contact.strip(" •")

    if contact:
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.HexColor("#E6EEEE"))
        c.drawString(
            margin,
            page_height - 35 * mm,
            contact
        )

    y = page_height - 53 * mm

    summary = clean(data.get("summary"))

    if summary:
        y = draw_section_title(
            c,
            "Professional Summary",
            margin,
            y,
            content_width
        )

        y = draw_wrapped(
            c,
            summary,
            margin,
            y,
            content_width,
            "Helvetica",
            9,
            12,
            colors.HexColor("#333333")
        )

        y -= 10

    if clean(data.get("experience")):
        y = draw_section_title(
            c,
            "Professional Experience",
            margin,
            y,
            content_width
        )

        y = draw_experience(
            c,
            data.get("experience"),
            margin,
            y,
            content_width
        )

    if clean(data.get("education")):
        y -= 5

        y = draw_section_title(
            c,
            "Education",
            margin,
            y,
            content_width
        )

        y = draw_education(
            c,
            data.get("education"),
            margin,
            y,
            content_width
        )

    if clean(data.get("skills")):
        y -= 5

        y = draw_section_title(
            c,
            "Skills",
            margin,
            y,
            content_width
        )

        y = draw_wrapped(
            c,
            data.get("skills"),
            margin,
            y,
            content_width,
            "Helvetica",
            9,
            12,
            colors.HexColor("#333333")
        )

    if clean(data.get("certificates")):
        y -= 5

        y = draw_section_title(
            c,
            "Certificates & Training",
            margin,
            y,
            content_width
        )

        y = draw_certificates(
            c,
            data.get("certificates"),
            margin,
            y,
            content_width
        )

    if clean(data.get("languages")):
        y -= 5

        y = draw_section_title(
            c,
            "Languages",
            margin,
            y,
            content_width
        )

        y = draw_wrapped(
            c,
            data.get("languages"),
            margin,
            y,
            content_width,
            "Helvetica",
            9,
            12,
            colors.HexColor("#333333")
        )

    if clean(data.get("hobbies")):
        y -= 5

        y = draw_section_title(
            c,
            "Interests",
            margin,
            y,
            content_width
        )

        y = draw_wrapped(
            c,
            data.get("hobbies"),
            margin,
            y,
            content_width,
            "Helvetica",
            9,
            12,
            colors.HexColor("#333333")
        )

    if clean(data.get("references")):
        y -= 5

        y = draw_section_title(
            c,
            "References",
            margin,
            y,
            content_width
        )

        draw_references(
            c,
            data.get("references"),
            margin,
            y,
            content_width
        )

    draw_footer(c)


def generate_ats(c, data):
    page_width, page_height = A4

    margin = 18 * mm
    content_width = page_width - 2 * margin

    y = page_height - margin

    name = clean(data.get("name")) or "Your Name"
    title = clean(data.get("title"))

    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 22)

    c.drawString(
        margin,
        y,
        name
    )

    y -= 10 * mm

    if title:
        c.setFont("Helvetica-Bold", 11)

        c.drawString(
            margin,
            y,
            title
        )

        y -= 7 * mm

    contact = " | ".join([
        clean(data.get("phone")),
        clean(data.get("email")),
        clean(data.get("location")),
        clean(data.get("linkedin")),
        clean(data.get("website"))
    ])

    contact = contact.strip(" |")

    if contact:
        c.setFont("Helvetica", 8.5)

        y = draw_wrapped(
            c,
            contact,
            margin,
            y,
            content_width,
            "Helvetica",
            8.5,
            11,
            colors.black
        )

        y -= 5

    summary = clean(data.get("summary"))

    if summary:
        y = draw_section_title(
            c,
            "Professional Summary",
            margin,
            y,
            content_width
        )

        y = draw_wrapped(
            c,
            summary,
            margin,
            y,
            content_width,
            "Helvetica",
            9,
            12,
            colors.black
        )

        y -= 8

    if clean(data.get("experience")):
        y = draw_section_title(
            c,
            "Experience",
            margin,
            y,
            content_width
        )

        y = draw_experience(
            c,
            data.get("experience"),
            margin,
            y,
            content_width
        )

    if clean(data.get("education")):
        y -= 5

        y = draw_section_title(
            c,
            "Education",
            margin,
            y,
            content_width
        )

        y = draw_education(
            c,
            data.get("education"),
            margin,
            y,
            content_width
        )

    if clean(data.get("skills")):
        y -= 5

        y = draw_section_title(
            c,
            "Skills",
            margin,
            y,
            content_width
        )

        y = draw_wrapped(
            c,
            data.get("skills"),
            margin,
            y,
            content_width,
            "Helvetica",
            9,
            12,
            colors.black
        )

    if clean(data.get("certificates")):
        y -= 5

        y = draw_section_title(
            c,
            "Certificates & Training",
            margin,
            y,
            content_width
        )

        y = draw_certificates(
            c,
            data.get("certificates"),
            margin,
            y,
            content_width
        )

    if clean(data.get("languages")):
        y -= 5

        y = draw_section_title(
            c,
            "Languages",
            margin,
            y,
            content_width
        )

        y = draw_wrapped(
            c,
            data.get("languages"),
            margin,
            y,
            content_width,
            "Helvetica",
            9,
            12,
            colors.black
        )

    if clean(data.get("hobbies")):
        y -= 5

        y = draw_section_title(
            c,
            "Interests",
            margin,
            y,
            content_width
        )

        y = draw_wrapped(
            c,
            data.get("hobbies"),
            margin,
            y,
            content_width,
            "Helvetica",
            9,
            12,
            colors.black
        )

    if clean(data.get("references")):
        y -= 5

        y = draw_section_title(
            c,
            "References",
            margin,
            y,
            content_width
        )

        draw_references(
            c,
            data.get("references"),
            margin,
            y,
            content_width
        )

    c.setFillColor(colors.HexColor("#555555"))
    c.setFont("Helvetica", 7)

    c.drawCentredString(
        page_width / 2,
        7 * mm,
        "Created with CVForge"
    )


def generate_pdf(data, filename):
    c = canvas.Canvas(
        filename,
        pagesize=A4
    )

    template = clean(
        data.get("template")
    ).lower()

    if template == "classic":
        generate_classic(c, data)

    elif template == "ats":
        generate_ats(c, data)

    else:
        generate_modern(c, data)

    c.save()
    @app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/generate", methods=["POST"])
def generate():
    data = {
        "name": request.form.get("name", ""),
        "title": request.form.get("title", ""),
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
        "template": request.form.get("template", "modern")
    }

    photo = request.files.get("photo")

    if photo and photo.filename:
        photo_path = os.path.join(
            tempfile.gettempdir(),
            "CVForge_" + photo.filename
        )

        photo.save(photo_path)
        data["photo"] = photo_path

    else:
        data["photo"] = ""

    filename = os.path.join(
        tempfile.gettempdir(),
        "CVForge_CV.pdf"
    )

    generate_pdf(
        data,
        filename
    )

    with open(filename, "rb") as pdf_file:
        pdf_data = base64.b64encode(
            pdf_file.read()
        ).decode("utf-8")

    token = str(uuid.uuid4())

    preview_file = os.path.join(
        tempfile.gettempdir(),
        "CVForge_" + token + ".pdf"
    )

    with open(preview_file, "wb") as output:
        with open(filename, "rb") as source:
            output.write(source.read())

    return render_template_string(
        PREVIEW_HTML,
        pdf_data=pdf_data,
        token=token
    )


@app.route("/pdf/<token>")
def view_pdf(token):
    filename = os.path.join(
        tempfile.gettempdir(),
        "CVForge_" + token + ".pdf"
    )

    if not os.path.exists(filename):
        return "CV not found.", 404

    return send_file(
        filename,
        mimetype="application/pdf"
    )


@app.route("/download/<token>")
def download_pdf(token):
    filename = os.path.join(
        tempfile.gettempdir(),
        "CVForge_" + token + ".pdf"
    )

    if not os.path.exists(filename):
        return "CV not found.", 404

    return send_file(
        filename,
        as_attachment=True,
        download_name="CVForge_Professional_CV.pdf",
        mimetype="application/pdf"
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
  )
