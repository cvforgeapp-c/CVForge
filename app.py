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
    <title>CVForge - Professional CV Builder</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            padding: 15px;
            background: #eef1f2;
            font-family: Arial, sans-serif;
            color: #222;
        }

        .box {
            max-width: 760px;
            margin: auto;
            background: white;
            padding: 22px;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }

        h1 {
            margin: 0;
            color: #173f49;
            font-size: 34px;
        }

        .subtitle {
            color: #777;
            margin-top: 5px;
            margin-bottom: 22px;
        }

        /* PROGRESS */

        .progress-area {
            margin-bottom: 25px;
        }

        .progress-text {
            display: flex;
            justify-content: space-between;
            font-weight: bold;
            color: #173f49;
            margin-bottom: 8px;
        }

        .progress-bg {
            height: 8px;
            background: #e2e6e7;
            border-radius: 20px;
            overflow: hidden;
        }

        .progress-bar {
            height: 100%;
            width: 10%;
            background: #d6aa4c;
            border-radius: 20px;
            transition: width 0.3s;
        }

        /* STEPS */

        .step {
            display: none;
        }

        .step.active {
            display: block;
        }

        .step-title {
            color: #173f49;
            font-size: 24px;
            margin-bottom: 5px;
        }

        .step-description {
            color: #777;
            margin-bottom: 22px;
            line-height: 1.5;
        }

        label {
            display: block;
            font-weight: bold;
            margin-top: 16px;
            color: #333;
        }

        input,
        textarea {
            width: 100%;
            padding: 13px;
            margin-top: 7px;
            border: 1px solid #ccc;
            border-radius: 9px;
            font-size: 16px;
            font-family: Arial, sans-serif;
        }

        input:focus,
        textarea:focus {
            outline: none;
            border-color: #173f49;
        }

        textarea {
            min-height: 140px;
            resize: vertical;
        }

        small {
            display: block;
            color: #777;
            margin-top: 6px;
            line-height: 1.4;
        }

        .example {
            background: #f5f7f7;
            border-left: 4px solid #d6aa4c;
            padding: 12px;
            border-radius: 7px;
            margin-top: 12px;
            color: #555;
            font-size: 14px;
            line-height: 1.5;
        }

        /* NAVIGATION */

        .navigation {
            display: flex;
            gap: 10px;
            margin-top: 28px;
        }

        .nav-button {
            flex: 1;
            padding: 14px;
            border: none;
            border-radius: 9px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
        }

        .back-button {
            background: #e5e8e9;
            color: #173f49;
        }

        .next-button {
            background: #173f49;
            color: white;
        }

        .generate-button {
            width: 100%;
            padding: 17px;
            border: none;
            border-radius: 10px;
            background: #d6aa4c;
            color: #173f49;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 20px;
        }

        /* TEMPLATE CARDS */

        .templates {
            display: grid;
            grid-template-columns: 1fr;
            gap: 14px;
            margin-top: 20px;
        }

        .template-card {
            border: 2px solid #ddd;
            border-radius: 12px;
            padding: 18px;
            cursor: pointer;
            background: white;
        }

        .template-card:hover {
            border-color: #d6aa4c;
        }

        .template-card.selected {
            border-color: #173f49;
            background: #f2f6f7;
        }

        .template-card h3 {
            margin: 0 0 7px 0;
            color: #173f49;
        }

        .template-card p {
            margin: 0;
            color: #777;
            line-height: 1.4;
        }

        .template-badge {
            display: inline-block;
            margin-top: 10px;
            padding: 5px 9px;
            border-radius: 20px;
            background: #d6aa4c;
            color: #173f49;
            font-size: 12px;
            font-weight: bold;
        }

        .success-box {
            text-align: center;
            padding: 25px 10px;
        }

        .success-icon {
            font-size: 55px;
        }

        .success-box h2 {
            color: #173f49;
            font-size: 27px;
        }

        @media (max-width: 500px) {
            body {
                padding: 8px;
            }

            .box {
                padding: 18px;
            }

            h1 {
                font-size: 30px;
            }

            .step-title {
                font-size: 22px;
            }
        }
    </style>
</head>

<body>

<div class="box">

    <h1>CVForge</h1>

    <div class="subtitle">
        Build your professional CV step by step.
    </div>

    <div class="progress-area">
        <div class="progress-text">
            <span id="stepLabel">Step 1 of 10</span>
            <span id="stepName">Personal Information</span>
        </div>

        <div class="progress-bg">
            <div class="progress-bar" id="progressBar"></div>
        </div>
    </div>


    <form method="post"
          action="/generate"
          enctype="multipart/form-data"
          id="cvForm">


        <!-- ================================================= -->
        <!-- STEP 1 -->
        <!-- ================================================= -->

        <div class="step active">

            <div class="step-title">
                1. Personal Information
            </div>

            <div class="step-description">
                Tell us about yourself and how employers can contact you.
            </div>

            <label>Full Name *</label>
            <input
                name="name"
                placeholder="John Doe"
                required>

            <label>Professional Title</label>
            <input
                name="title"
                placeholder="Medical Doctor">

            <label>Profile Photo</label>
            <input
                type="file"
                name="photo"
                accept="image/*">

            <small>
                Optional. JPG, PNG or another common image format.
            </small>

            <label>Phone</label>
            <input
                name="phone"
                placeholder="+251 9XX XXX XXX">

            <label>Email</label>
            <input
                name="email"
                type="email"
                placeholder="you@example.com">

            <label>Location</label>
            <input
                name="location"
                placeholder="Addis Ababa, Ethiopia">

            <label>LinkedIn</label>
            <input
                name="linkedin"
                placeholder="linkedin.com/in/yourname">

            <label>Website / Portfolio</label>
            <input
                name="website"
                placeholder="www.example.com">

        </div>


        <!-- ================================================= -->
        <!-- STEP 2 -->
        <!-- ================================================= -->

        <div class="step">

            <div class="step-title">
                2. Professional Summary
            </div>

            <div class="step-description">
                Write a short introduction that shows your experience,
                strengths and career goals.
            </div>

            <label>Professional Summary</label>

            <textarea
                name="summary"
                placeholder="Medical doctor with experience in patient care, clinical assessment, diagnosis and emergency medicine. Dedicated to providing high-quality patient-centered care."></textarea>

            <div class="example">
                <strong>Tip:</strong>
                Keep your summary around 3–5 sentences.
                Focus on your strongest professional qualities.
            </div>

        </div>


        <!-- ================================================= -->
        <!-- STEP 3 -->
        <!-- ================================================= -->

        <div class="step">

            <div class="step-title">
                3. Experience
            </div>

            <div class="step-description">
                Add your professional work experience, starting with
                your most recent position.
            </div>

            <label>Work Experience</label>

            <textarea
                name="experience"
                style="min-height:260px"
                placeholder="Medical Doctor | ABC General Hospital | Addis Ababa | 2023 - Present
Provided clinical assessment, diagnosis and treatment for patients.
Managed emergency cases and coordinated patient follow-up.
Worked collaboratively with nurses and other healthcare professionals.

Intern Doctor | XYZ Teaching Hospital | Addis Ababa | 2022 - 2023
Assisted with patient assessment and clinical procedures.
Participated in emergency care and medical documentation."></textarea>

            <div class="example">
                <strong>Format:</strong><br>
                Job Title | Company | Location | Dates<br>
                Then write your responsibilities and achievements below.
            </div>

        </div>


        <!-- ================================================= -->
        <!-- STEP 4 -->
        <!-- ================================================= -->

        <div class="step">

            <div class="step-title">
                4. Education
            </div>

            <div class="step-description">
                Add your academic qualifications.
            </div>

            <label>Education</label>

            <textarea
                name="education"
                placeholder="Doctor of Medicine (MD) | XYZ University | 2022
High School Diploma | ABC School | 2016"></textarea>

            <div class="example">
                <strong>Format:</strong><br>
                Degree | Institution | Graduation Year
            </div>

        </div>


        <!-- ================================================= -->
        <!-- STEP 5 -->
        <!-- ================================================= -->

        <div class="step">

            <div class="step-title">
                5. Skills
            </div>

            <div class="step-description">
                Add the skills that best match your profession and target job.
            </div>

            <label>Skills</label>

            <input
                name="skills"
                placeholder="Patient Care, Clinical Assessment, Diagnosis, Leadership, Communication">

            <small>
                Separate each skill with a comma.
            </small>

            <div class="example">
                Example: Leadership, Communication, Teamwork,
                Microsoft Office, Patient Care
            </div>

        </div>


        <!-- ================================================= -->
        <!-- STEP 6 -->
        <!-- ================================================= -->

        <div class="step">

            <div class="step-title">
                6. Certificates
            </div>

            <div class="step-description">
                Add professional certificates, training and courses.
            </div>

            <label>Certificates & Training</label>

            <textarea
                name="certificates"
                placeholder="Basic Life Support (BLS) | 2023
Advanced Cardiac Life Support (ACLS) | 2024
First Aid Training | 2023"></textarea>

            <div class="example">
                <strong>Format:</strong><br>
                Certificate Name | Year
            </div>

        </div>


        <!-- ================================================= -->
        <!-- STEP 7 -->
        <!-- ================================================= -->

        <div class="step">

            <div class="step-title">
                7. Languages
            </div>

            <div class="step-description">
                List the languages you speak and your proficiency level.
            </div>

            <label>Languages</label>

            <textarea
                name="languages"
                placeholder="English | Fluent
Amharic | Native
Afaan Oromo | Native"></textarea>

            <div class="example">
                <strong>Format:</strong><br>
                Language | Proficiency Level
            </div>

        </div>


        <!-- ================================================= -->
        <!-- STEP 8 -->
        <!-- ================================================= -->

        <div class="step">

            <div class="step-title">
                8. References
            </div>

            <div class="step-description">
                Add professional references or choose to provide them later.
            </div>

            <label>References</label>

            <textarea
                name="references"
                placeholder="Dr. John Smith | ABC Hospital | john@example.com | +251 9XX XXX XXX
Dr. Jane Doe | XYZ University | jane@example.com | +251 9XX XXX XXX"></textarea>

            <div class="example">
                <strong>Format:</strong><br>
                Name | Organization | Email | Phone
                <br><br>
                You may also write:
                <strong>References available upon request.</strong>
            </div>

        </div>


        <!-- ================================================= -->
        <!-- STEP 9 -->
        <!-- ================================================= -->

        <div class="step">

            <div class="step-title">
                9. Choose Template
            </div>

            <div class="step-description">
                Choose the style you want for your CV.
            </div>

            <div class="templates">

                <div class="template-card selected"
                     onclick="selectTemplate(this, 'modern')">

                    <h3>Modern Professional</h3>

                    <p>
                        Dark teal and gold design with profile photo,
                        sidebar and professional sections.
                    </p>

                    <span class="template-badge">
                        CURRENT DESIGN
                    </span>

                </div>


                <div class="template-card"
                     onclick="selectTemplate(this, 'classic')">

                    <h3>Classic Professional</h3>

                    <p>
                        Clean and traditional layout suitable for
                        corporate and professional applications.
                    </p>

                    <span class="template-badge">
                        COMING SOON
                    </span>

                </div>


                <div class="template-card"
                     onclick="selectTemplate(this, 'ats')">

                    <h3>ATS Friendly</h3>

                    <p>
                        Simple professional layout designed for
                        applicant tracking systems.
                    </p>

                    <span class="template-badge">
                        COMING SOON
                    </span>

                </div>

            </div>

            <input
                type="hidden"
                name="template"
                id="template"
                value="modern">

            <input
                type="hidden"
                name="hobbies"
                id="hobbies"
                value="">

        </div>


        <!-- ================================================= -->
        <!-- STEP 10 -->
        <!-- ================================================= -->

        <div class="step">

            <div class="success-box">

                <div class="success-icon">
                    📄
                </div>

                <div class="step-title">
                    10. Generate Your CV
                </div>

                <div class="step-description">
                    Your information is ready.
                    Click the button below to generate your professional PDF CV.
                </div>

                <button
                    class="generate-button"
                    type="submit">

                    GENERATE PROFESSIONAL CV

                </button>

            </div>

        </div>


        <!-- NAVIGATION -->

        <div class="navigation">

            <button
                type="button"
                class="nav-button back-button"
                id="backButton"
                onclick="previousStep()">

                ← Back

            </button>

            <button
                type="button"
                class="nav-button next-button"
                id="nextButton"
                onclick="nextStep()">

                Next →

            </button>

        </div>

    </form>

</div>


<script>

    let currentStep = 0;

    const stepNames = [
        "Personal Information",
        "Professional Summary",
        "Experience",
        "Education",
        "Skills",
        "Certificates",
        "Languages",
        "References",
        "Choose Template",
        "Generate CV"
    ];

    const steps = document.querySelectorAll(".step");

    const progressBar =
        document.getElementById("progressBar");

    const stepLabel =
        document.getElementById("stepLabel");

    const stepName =
        document.getElementById("stepName");

    const backButton =
        document.getElementById("backButton");

    const nextButton =
        document.getElementById("nextButton");


    function showStep(index) {

        steps.forEach(function(step, i) {

            step.classList.toggle(
                "active",
                i === index
            );

        });

        currentStep = index;

        const number = index + 1;

        const percentage =
            (number / steps.length) * 100;

        progressBar.style.width =
            percentage + "%";

        stepLabel.textContent =
            "Step " + number + " of " + steps.length;

        stepName.textContent =
            stepNames[index];


        if (index === 0) {

            backButton.style.visibility =
                "hidden";

        } else {

            backButton.style.visibility =
                "visible";

        }


        if (index === steps.length - 1) {

            nextButton.style.display =
                "none";

        } else {

            nextButton.style.display =
                "block";

        }

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    }


    function validateCurrentStep() {

        const current =
            steps[currentStep];

        const fields =
            current.querySelectorAll(
                "input[required], textarea[required]"
            );

        for (let field of fields) {

            if (!field.checkValidity()) {

                field.reportValidity();

                return false;
            }
        }

        return true;
    }


    function nextStep() {

        if (!validateCurrentStep()) {
            return;
        }

        if (currentStep < steps.length - 1) {

            showStep(currentStep + 1);

        }
    }


    function previousStep() {

        if (currentStep > 0) {

            showStep(currentStep - 1);

        }
    }


    function selectTemplate(card, templateName) {

        document
            .querySelectorAll(".template-card")
            .forEach(function(item) {

                item.classList.remove("selected");

            });

        card.classList.add("selected");

        document.getElementById("template").value =
            templateName;

    }


    document
        .getElementById("cvForm")
        .addEventListener("submit", function(event) {

            if (!validateCurrentStep()) {

                event.preventDefault();

            }

        });


    showStep(0);

</script>

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
