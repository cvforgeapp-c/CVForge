from flask import Flask, request, render_template_string, send_file
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.utils import ImageReader
import os
import tempfile


app = Flask(__name__)


# ============================================================
# HTML FORM
# ============================================================

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>CVForge Professional CV Builder</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            font-family: Arial, sans-serif;
            background: #eef1f2;
            margin: 0;
            padding: 15px;
            color: #222;
        }

        .box {
            max-width: 760px;
            margin: auto;
            background: white;
            padding: 22px;
            border-radius: 14px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }

        h1 {
            margin: 0 0 5px 0;
            color: #173f49;
        }

        .subtitle {
            color: #777;
            margin-bottom: 20px;
        }

        .section {
            margin-top: 25px;
            padding-top: 15px;
            border-top: 2px solid #e3e3e3;
        }

        .section h2 {
            color: #173f49;
            font-size: 19px;
            margin-bottom: 5px;
        }

        label {
            display: block;
            font-weight: bold;
            margin-top: 14px;
            color: #333;
        }

        input,
        textarea {
            width: 100%;
            padding: 12px;
            margin-top: 6px;
            border: 1px solid #ccc;
            border-radius: 8px;
            font-size: 15px;
            font-family: Arial, sans-serif;
        }

        textarea {
            min-height: 100px;
            resize: vertical;
        }

        small {
            display: block;
            color: #777;
            margin-top: 5px;
            line-height: 1.4;
        }

        .button {
            margin-top: 25px;
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 9px;
            background: #173f49;
            color: white;
            font-size: 17px;
            font-weight: bold;
        }

        .button:hover {
            background: #0e3038;
        }

        .example {
            background: #f5f7f7;
            padding: 10px;
            border-radius: 7px;
            margin-top: 7px;
            font-size: 13px;
            color: #555;
        }
    </style>
</head>

<body>

<div class="box">

    <h1>CVForge</h1>
    <div class="subtitle">
        Create a professional, modern CV as a PDF.
    </div>

    <form method="post"
          action="/generate"
          enctype="multipart/form-data">

        <!-- PERSONAL INFORMATION -->

        <div class="section">
            <h2>Personal Information</h2>

            <label>Full Name</label>
            <input name="name"
                   placeholder="John Doe"
                   required>

            <label>Professional Title</label>
            <input name="title"
                   placeholder="Medical Doctor">

            <label>Profile Photo</label>
            <input type="file"
                   name="photo"
                   accept="image/*">

            <small>
                Optional. JPG, PNG or other common image format.
            </small>

            <label>Phone</label>
            <input name="phone"
                   placeholder="+251 9XX XXX XXX">

            <label>Email</label>
            <input name="email"
                   placeholder="you@example.com">

            <label>Location</label>
            <input name="location"
                   placeholder="Addis Ababa, Ethiopia">

            <label>LinkedIn</label>
            <input name="linkedin"
                   placeholder="linkedin.com/in/yourname">

            <label>Website / Portfolio</label>
            <input name="website"
                   placeholder="www.example.com">
        </div>


        <!-- SUMMARY -->

        <div class="section">
            <h2>Professional Summary</h2>

            <textarea name="summary"
                placeholder="Write 3-5 lines describing your professional background, strongest skills, achievements and career goals..."></textarea>
        </div>


        <!-- SKILLS -->

        <div class="section">
            <h2>Skills</h2>

            <label>Skills</label>
            <input name="skills"
                   placeholder="Patient Care, Clinical Assessment, Diagnosis, Leadership">

            <small>
                Separate skills with commas.
            </small>
        </div>


        <!-- LANGUAGES -->

        <div class="section">
            <h2>Languages</h2>

            <textarea name="languages"
                placeholder="English | Fluent
Amharic | Native
Afaan Oromo | Native"></textarea>

            <small>
                One language per line:
                Language | Level
            </small>
        </div>


        <!-- EXPERIENCE -->

        <div class="section">
            <h2>Work Experience</h2>

            <small>
                One job per block. Use this format:
                Job Title | Company | Location | Dates
                followed by responsibilities.
            </small>

            <textarea name="experience"
                style="min-height:220px"
                placeholder="Medical Doctor | ABC General Hospital | Addis Ababa | 2023 - Present
Provided clinical assessment, diagnosis and treatment for patients.
Managed emergency cases and coordinated patient follow-up.
Worked collaboratively with nurses and other healthcare professionals.

Intern Doctor | XYZ Teaching Hospital | Addis Ababa | 2022 - 2023
Assisted with patient assessment and clinical procedures.
Participated in emergency care and medical documentation."></textarea>
        </div>


        <!-- EDUCATION -->

        <div class="section">
            <h2>Education</h2>

            <textarea name="education"
                placeholder="Doctor of Medicine (MD) | XYZ University | 2022
High School Diploma | ABC School | 2016"></textarea>

            <small>
                One qualification per line:
                Degree | Institution | Year
            </small>
        </div>


        <!-- CERTIFICATES -->

        <div class="section">
            <h2>Certificates & Training</h2>

            <textarea name="certificates"
                placeholder="Basic Life Support (BLS) | 2023
Advanced Cardiac Life Support (ACLS) | 2024
First Aid Training | 2023"></textarea>

            <small>
                One certificate per line:
                Certificate | Year
            </small>
        </div>


        <!-- HOBBIES -->

        <div class="section">
            <h2>Hobbies & Interests</h2>

            <input name="hobbies"
                   placeholder="Reading, Volunteering, Research, Photography">

            <small>
                Separate hobbies with commas.
            </small>
        </div>


        <!-- REFERENCES -->

        <div class="section">
            <h2>References</h2>

            <textarea name="references"
                placeholder="Dr. John Smith | ABC Hospital | john@example.com | +251 9XX XXX XXX
Dr. Jane Doe | XYZ University | jane@example.com | +251 9XX XXX XXX"></textarea>

            <small>
                One reference per line:
                Name | Organization | Email | Phone
            </small>
        </div>


        <button class="button" type="submit">
            GENERATE PROFESSIONAL PDF CV
        </button>

    </form>

</div>

</body>
</html>
"""


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean(value):
    return (value or "").strip()


def wrap_text(text, font_name, font_size, max_width):
    """
    Wrap text according to actual PDF width.
    """

    if not text:
        return []

    words = text.split()
    lines = []
    current = ""

    for word in words:

        test = word if not current else current + " " + word

        if stringWidth(test, font_name, font_size) <= max_width:
            current = test

        else:
            if current:
                lines.append(current)

            current = word

    if current:
        lines.append(current)

    return lines


def draw_wrapped(
    c,
    text,
    x,
    y,
    max_width,
    font="Helvetica",
    size=10,
    leading=5.2 * mm
):

    if not text:
        return y

    c.setFont(font, size)

    paragraphs = text.splitlines()

    for paragraph in paragraphs:

        paragraph = paragraph.strip()

        if not paragraph:
            y -= leading
            continue

        lines = wrap_text(
            paragraph,
            font,
            size,
            max_width
        )

        for line in lines:

            if y < 25 * mm:
                c.showPage()
                y = A4[1] - 25 * mm
                c.setFont(font, size)

            c.drawString(x, y, line)

            y -= leading

    return y


def draw_sidebar_title(c, title, x, y, width):

    c.setStrokeColor(colors.HexColor("#D6AA4C"))
    c.setLineWidth(1.5)

    c.roundRect(
        x,
        y - 5 * mm,
        width,
        9 * mm,
        4 * mm,
        stroke=1,
        fill=0
    )

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 10.5)

    c.drawCentredString(
        x + width / 2,
        y - 1.5 * mm,
        title.upper()
    )

    return y - 13 * mm


def draw_sidebar_list(
    c,
    items,
    x,
    y,
    width,
    font_size=9.5
):

    c.setFont("Helvetica", font_size)
    c.setFillColor(colors.white)

    for item in items:

        item = item.strip()

        if not item:
            continue

        lines = wrap_text(
            item,
            "Helvetica",
            font_size,
            width - 7 * mm
        )

        for index, line in enumerate(lines):

            if y < 25 * mm:
                return y

            if index == 0:
                c.drawString(
                    x,
                    y,
                    "- " + line
                )
            else:
                c.drawString(
                    x + 4 * mm,
                    y,
                    line
                )

            y -= 5 * mm

        y -= 1.5 * mm

    return y


def draw_section_title(
    c,
    title,
    x,
    y,
    width
):

    c.setFillColor(colors.HexColor("#173F49"))
    c.setFont("Helvetica-Bold", 14)

    c.drawString(
        x,
        y,
        title.upper()
    )

    y -= 2.5 * mm

    c.setStrokeColor(colors.HexColor("#D8D8D8"))
    c.setLineWidth(0.6)

    c.line(
        x,
        y,
        x + width,
        y
    )

    return y - 7 * mm


def draw_header(
    c,
    data,
    page_width,
    page_height,
    sidebar_width
):

    # Header background

    c.setFillColor(colors.HexColor("#173F49"))

    c.rect(
        0,
        page_height - 58 * mm,
        page_width,
        58 * mm,
        stroke=0,
        fill=1
    )

    # Gold accent

    c.setFillColor(colors.HexColor("#D6AA4C"))

    c.rect(
        0,
        page_height - 59 * mm,
        page_width,
        1.5 * mm,
        stroke=0,
        fill=1
    )

    # Photo

    photo = data.get("photo")

    photo_x = 17 * mm
    photo_y = page_height - 47 * mm
    photo_size = 35 * mm

    if photo and os.path.exists(photo):

        try:

            image = ImageReader(photo)

            iw, ih = image.getSize()

            scale = max(
                photo_size / iw,
                photo_size / ih
            )

            dw = iw * scale
            dh = ih * scale

            dx = photo_x + (photo_size - dw) / 2
            dy = photo_y + (photo_size - dh) / 2

            c.saveState()

            path = c.beginPath()

            path.circle(
                photo_x + photo_size / 2,
                photo_y + photo_size / 2,
                photo_size / 2
            )

            c.clipPath(
                path,
                stroke=0,
                fill=0
            )

            c.drawImage(
                image,
                dx,
                dy,
                width=dw,
                height=dh,
                preserveAspectRatio=True,
                mask="auto"
            )

            c.restoreState()

            c.setStrokeColor(colors.HexColor("#D6AA4C"))
            c.setLineWidth(1.2)

            c.circle(
                photo_x + photo_size / 2,
                photo_y + photo_size / 2,
                photo_size / 2,
                stroke=1,
                fill=0
            )

        except Exception:
            pass

    # Header text

    text_x = 60 * mm

    c.setFillColor(colors.HexColor("#D6AA4C"))
    c.setFont("Helvetica-Bold", 23)

    c.drawString(
        text_x,
        page_height - 25 * mm,
        data["name"][:35]
    )

    c.setFillColor(colors.white)
    c.setFont("Helvetica", 11)

    if data["title"]:

        c.drawString(
            text_x,
            page_height - 33 * mm,
            data["title"][:60]
        )

    # Summary in header

    summary = data["summary"]

    if summary:

        summary_lines = wrap_text(
            summary,
            "Helvetica",
            8.5,
            page_width - text_x - 15 * mm
        )

        c.setFillColor(colors.HexColor("#E8EEEE"))
        c.setFont("Helvetica", 8.5)

        sy = page_height - 40 * mm

        for line in summary_lines[:3]:

            c.drawString(
                text_x,
                sy,
                line
            )

            sy -= 4 * mm


# ============================================================
# SIDEBAR
# ============================================================

def draw_sidebar(
    c,
    data,
    page_width,
    page_height
):

    sidebar_width = 63 * mm

    # Sidebar

    c.setFillColor(colors.HexColor("#173F49"))

    c.rect(
        0,
        0,
        sidebar_width,
        page_height - 59.5 * mm,
        stroke=0,
        fill=1
    )

    x = 10 * mm
    content_width = sidebar_width - 20 * mm

    y = page_height - 70 * mm

    # CONTACT

    y = draw_sidebar_title(
        c,
        "CONTACT",
        x,
        y,
        content_width
    )

    c.setFillColor(colors.white)
    c.setFont("Helvetica", 8.8)

    contacts = [
        data["phone"],
        data["email"],
        data["location"],
        data["linkedin"],
        data["website"]
    ]

    for contact in contacts:

        if not contact:
            continue

        lines = wrap_text(
            contact,
            "Helvetica",
            8.8,
            content_width
        )

        for line in lines:

            c.drawString(
                x,
                y,
                line
            )

            y -= 4.5 * mm

        y -= 1.5 * mm

    # SKILLS

    if data["skills"]:

        y -= 3 * mm

        y = draw_sidebar_title(
            c,
            "SKILLS",
            x,
            y,
            content_width
        )

        skills = [
            item.strip()
            for item in data["skills"].split(",")
            if item.strip()
        ]

        y = draw_sidebar_list(
            c,
            skills,
            x,
            y,
            content_width
        )

    # LANGUAGES

    if data["languages"]:

        y -= 3 * mm

        y = draw_sidebar_title(
            c,
            "LANGUAGES",
            x,
            y,
            content_width
        )

        languages = []

        for line in data["languages"].splitlines():

            line = line.strip()

            if not line:
                continue

            parts = [
                p.strip()
                for p in line.split("|")
            ]

            if len(parts) >= 2:
                languages.append(
                    parts[0] + " - " + parts[1]
                )
            else:
                languages.append(parts[0])

        y = draw_sidebar_list(
            c,
            languages,
            x,
            y,
            content_width
        )

    # HOBBIES

    if data["hobbies"]:

        y -= 3 * mm

        y = draw_sidebar_title(
            c,
            "INTERESTS",
            x,
            y,
            content_width
        )

        hobbies = [
            item.strip()
            for item in data["hobbies"].split(",")
            if item.strip()
        ]

        y = draw_sidebar_list(
            c,
            hobbies,
            x,
            y,
            content_width
        )


# ============================================================
# EXPERIENCE
# ============================================================

def draw_experience(
    c,
    experience,
    x,
    y,
    width,
    page_height
):

    blocks = []

    current = []

    for line in experience.splitlines():

        line = line.strip()

        if not line:
            if current:
                blocks.append(current)
                current = []
        else:
            current.append(line)

    if current:
        blocks.append(current)

    for block in blocks:

        if not block:
            continue

        header = block[0]

        parts = [
            p.strip()
            for p in header.split("|")
        ]

        job_title = parts[0] if len(parts) >= 1 else ""
        company = parts[1] if len(parts) >= 2 else ""
        location = parts[2] if len(parts) >= 3 else ""
        dates = parts[3] if len(parts) >= 4 else ""

        if y < 45 * mm:

            c.showPage()

            y = page_height - 25 * mm

        # Job title

        c.setFillColor(colors.HexColor("#222222"))
        c.setFont("Helvetica-Bold", 11.5)

        c.drawString(
            x,
            y,
            job_title[:70]
        )

        y -= 5.5 * mm

        # Company/date

        secondary = " | ".join(
            item
            for item in [
                company,
                location,
                dates
            ]
            if item
        )

        if secondary:

            c.setFillColor(colors.HexColor("#777777"))
            c.setFont(
                "Helvetica-Oblique",
                9
            )

            c.drawString(
                x,
                y,
                secondary[:105]
            )

            y -= 5.5 * mm

        # Responsibilities

        for description in block[1:]:

            description = description.strip()

            if not description:
                continue

            lines = wrap_text(
                description,
                "Helvetica",
                9.5,
                width - 8 * mm
            )

            for index, line in enumerate(lines):

                if y < 28 * mm:

                    c.showPage()

                    y = page_height - 25 * mm

                c.setFillColor(
                    colors.HexColor("#444444")
                )

                c.setFont(
                    "Helvetica",
                    9.5
                )

                prefix = "- " if index == 0 else "  "

                c.drawString(
                    x + 3 * mm,
                    y,
                    prefix + line
                )

                y -= 4.8 * mm

        y -= 4 * mm

    return y


# ============================================================
# EDUCATION
# ============================================================

def draw_education(
    c,
    education,
    x,
    y,
    page_height
):

    for line in education.splitlines():

        line = line.strip()

        if not line:
            continue

        parts = [
            p.strip()
            for p in line.split("|")
        ]

        degree = parts[0] if len(parts) >= 1 else ""
        institution = parts[1] if len(parts) >= 2 else ""
        year = parts[2] if len(parts) >= 3 else ""

        if y < 35 * mm:

            c.showPage()

            y = page_height - 25 * mm

        c.setFillColor(colors.HexColor("#222222"))
        c.setFont("Helvetica-Bold", 10.5)

        c.drawString(
            x,
            y,
            degree[:90]
        )

        y -= 5 * mm

        secondary = " | ".join(
            item
            for item in [
                institution,
                year
            ]
            if item
        )

        if secondary:

            c.setFillColor(colors.HexColor("#666666"))
            c.setFont(
                "Helvetica",
                9
            )

            c.drawString(
                x,
                y,
                secondary[:105]
            )

            y -= 5 * mm

        y -= 3 * mm

    return y


# ============================================================
# CERTIFICATES
# ============================================================

def draw_certificates(
    c,
    certificates,
    x,
    y,
    page_height
):

    for line in certificates.splitlines():

        line = line.strip()

        if not line:
            continue

        parts = [
            p.strip()
            for p in line.split("|")
        ]

        certificate = parts[0] if len(parts) >= 1 else ""
        year = parts[1] if len(parts) >= 2 else ""

        if y < 35 * mm:

            c.showPage()

            y = page_height - 25 * mm

        c.setFillColor(colors.HexColor("#222222"))
        c.setFont(
            "Helvetica-Bold",
            10.5
        )

        c.drawString(
            x,
            y,
            certificate[:90]
        )

        y -= 5 * mm

        if year:

            c.setFillColor(
                colors.HexColor("#666666")
            )

            c.setFont(
                "Helvetica",
                9
            )

            c.drawString(
                x,
                y,
                year
            )

            y -= 5 * mm

        y -= 3 * mm

    return y


# ============================================================
# REFERENCES
# ============================================================

def draw_references(
    c,
    references,
    x,
    y,
    width,
    page_height
):

    for line in references.splitlines():

        line = line.strip()

        if not line:
            continue

        parts = [
            p.strip()
            for p in line.split("|")
        ]

        name = parts[0] if len(parts) >= 1 else ""
        organization = parts[1] if len(parts) >= 2 else ""
        email = parts[2] if len(parts) >= 3 else ""
        phone = parts[3] if len(parts) >= 4 else ""

        if y < 35 * mm:

            c.showPage()

            y = page_height - 25 * mm

        c.setFillColor(
            colors.HexColor("#222222")
        )

        c.setFont(
            "Helvetica-Bold",
            10
        )

        c.drawString(
            x,
            y,
            name[:80]
        )

        y -= 4.5 * mm

        secondary = " | ".join(
            item
            for item in [
                organization,
                email,
                phone
            ]
            if item
        )

        if secondary:

            y = draw_wrapped(
                c,
                secondary,
                x,
                y,
                width,
                "Helvetica",
                8.8,
                4.5 * mm
            )

        y -= 3 * mm

    return y


# ============================================================
# FOOTER
# ============================================================

def draw_footer(
    c,
    page_width
):

    c.setStrokeColor(
        colors.HexColor("#D6AA4C")
    )

    c.setLineWidth(1)

    c.line(
        15 * mm,
        12 * mm,
        page_width - 15 * mm,
        12 * mm
    )

    c.setFillColor(
        colors.HexColor("#888888")
    )

    c.setFont(
        "Helvetica",
        7.5
    )

    c.drawString(
        15 * mm,
        7 * mm,
        "Created with CVForge"
    )


# ============================================================
# PDF GENERATOR
# ============================================================

def generate_pdf(data, filename):

    page_width, page_height = A4

    sidebar_width = 63 * mm

    right_x = sidebar_width + 12 * mm

    right_width = (
        page_width
        - sidebar_width
        - 24 * mm
    )

    c = canvas.Canvas(
        filename,
        pagesize=A4
    )

    c.setTitle(
        "CV - " + data["name"]
    )

    # HEADER

    draw_header(
        c,
        data,
        page_width,
        page_height,
        sidebar_width
    )

    # SIDEBAR

    draw_sidebar(
        c,
        data,
        page_width,
        page_height
    )

    # MAIN CONTENT

    y = page_height - 72 * mm

    # EXPERIENCE

    if data["experience"]:

        y = draw_section_title(
            c,
            "Experience",
            right_x,
            y,
            right_width
        )

        y = draw_experience(
            c,
            data["experience"],
            right_x,
            y,
            right_width,
            page_height
        )

    # EDUCATION

    if data["education"]:

        y -= 2 * mm

        y = draw_section_title(
            c,
            "Education",
            right_x,
            y,
            right_width
        )

        y = draw_education(
            c,
            data["education"],
            right_x,
            y,
            page_height
        )

    # CERTIFICATES

    if data["certificates"]:

        y -= 2 * mm

        y = draw_section_title(
            c,
            "Certificates & Training",
            right_x,
            y,
            right_width
        )

        y = draw_certificates(
            c,
            data["certificates"],
            right_x,
            y,
            page_height
        )

    # REFERENCES

    if data["references"]:

        y -= 2 * mm

        y = draw_section_title(
            c,
            "References",
            right_x,
            y,
            right_width
        )

        y = draw_references(
            c,
            data["references"],
            right_x,
            y,
            right_width,
            page_height
        )

    # FOOTER

    draw_footer(
        c,
        page_width
    )

    c.save()


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/", methods=["GET"])
def home():

    return render_template_string(
        HTML
    )


# ============================================================
# GENERATE ROUTE
# ============================================================

@app.route(
    "/generate",
    methods=["POST"]
)
def generate():

    # --------------------------------------------------------
    # PHOTO
    # --------------------------------------------------------

    photo_path = ""

    photo = request.files.get("photo")

    if photo and photo.filename:

        extension = os.path.splitext(
            photo.filename
        )[1].lower()

        if extension not in [
            ".jpg",
            ".jpeg",
            ".png",
            ".webp"
        ]:

            extension = ".jpg"

        photo_path = os.path.join(
            tempfile.gettempdir(),
            "cvforge_photo" + extension
        )

        photo.save(photo_path)

    # --------------------------------------------------------
    # DATA
    # --------------------------------------------------------

    data = {

        "name":
            clean(
                request.form.get("name")
            ) or "My CV",

        "title":
            clean(
                request.form.get("title")
            ),

        "phone":
            clean(
                request.form.get("phone")
            ),

        "email":
            clean(
                request.form.get("email")
            ),

        "location":
            clean(
                request.form.get("location")
            ),

        "linkedin":
            clean(
                request.form.get("linkedin")
            ),

        "website":
            clean(
                request.form.get("website")
            ),

        "summary":
            clean(
                request.form.get("summary")
            ),

        "skills":
            clean(
                request.form.get("skills")
            ),

        "languages":
            clean(
                request.form.get("languages")
            ),

        "experience":
            clean(
                request.form.get("experience")
            ),

        "education":
            clean(
                request.form.get("education")
            ),

        "certificates":
            clean(
                request.form.get("certificates")
            ),

        "hobbies":
            clean(
                request.form.get("hobbies")
            ),

        "references":
            clean(
                request.form.get("references")
            ),

        "photo":
            photo_path
    }

    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    filename = os.path.join(
        tempfile.gettempdir(),
        "CVForge_CV.pdf"
    )

    generate_pdf(
        data,
        filename
    )

    return send_file(
        filename,
        as_attachment=True,
        download_name="CVForge_Professional_CV.pdf",
        mimetype="application/pdf"
    )


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )