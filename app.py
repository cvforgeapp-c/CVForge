from flask import Flask, request, render_template_string, send_file
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
* { box-sizing: border-box; }

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
}

.subtitle {
    text-align: center;
    color: #777;
    margin-bottom: 25px;
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

.step { display: none; }
.step.active { display: block; }

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

input, textarea, select {
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
}
.template-grid {
    display: grid;
    gap: 15px;
    margin-top: 18px;
}

.template-option {
    width: 100%;
    text-align: left;
    background: #ffffff;
    border: 2px solid #d9e0e0;
    border-radius: 16px;
    padding: 20px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.template-option:hover {
    border-color: #0d4f4f;
    transform: translateY(-2px);
}

.template-option.selected {
    border-color: #c9a227;
    background: #f8f5e9;
    box-shadow: 0 4px 15px rgba(201,162,39,.18);
}

.template-name {
    font-size: 20px;
    font-weight: bold;
    color: #173f3f;
    margin-bottom: 8px;
}

.template-description {
    color: #777;
    font-size: 15px;
    line-height: 1.5;
}

.template-badge {
    display: inline-block;
    margin-top: 12px;
    padding: 7px 12px;
    border-radius: 20px;
    background: #e7eeee;
    color: #173f3f;
    font-size: 13px;
    font-weight: bold;
}

.template-option.selected .template-badge {
    background: #c9a227;
    color: white;
}

.checkmark {
    float: right;
    display: none;
    color: #c9a227;
    font-size: 24px;
    font-weight: bold;
}

.template-option.selected .checkmark {
    display: block;
}

@media(max-width:600px) {
    .container { padding: 10px; }
    .card { padding: 18px; }
    .buttons { flex-direction: column; }
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
<textarea name="summary"
placeholder="Write a short professional summary about yourself..."></textarea>

<div class="buttons">
<button type="button" class="back" onclick="prevStep()">← Back</button>
<button type="button" class="next" onclick="nextStep()">Next →</button>
</div>
</div>


<div class="step">
<h2>3. Work Experience</h2>

<label>Experience</label>
<textarea name="experience"
placeholder="Job Title - Company - Dates

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
<textarea name="education"
placeholder="Degree - Institution - Year

Add your education history here."></textarea>

<div class="buttons">
<button type="button" class="back" onclick="prevStep()">← Back</button>
<button type="button" class="next" onclick="nextStep()">Next →</button>
</div>
</div>


<div class="step">
<h2>5. Skills</h2>

<label>Skills</label>
<textarea name="skills"
placeholder="Python
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
<textarea name="certificates"
placeholder="Certificate Name - Organization - Year"></textarea>

<div class="buttons">
<button type="button" class="back" onclick="prevStep()">← Back</button>
<button type="button" class="next" onclick="nextStep()">Next →</button>
</div>
</div>


<div class="step">
<h2>7. Languages</h2>

<label>Languages</label>
<textarea name="languages"
placeholder="English - Fluent
Amharic - Native"></textarea>

<div class="buttons">
<button type="button" class="back" onclick="prevStep()">← Back</button>
<button type="button" class="next" onclick="nextStep()">Next →</button>
</div>
</div>


<div class="step">
<h2>8. Interests</h2>

<label>Interests & Hobbies</label>
<textarea name="hobbies"
placeholder="Technology
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
<textarea name="references"
placeholder="Name - Position - Company
Email / Phone"></textarea>

<div class="buttons">
<button type="button" class="back" onclick="prevStep()">← Back</button>
<button type="button" class="next" onclick="nextStep()">Next →</button>
</div>
</div>


<div class="step">
<h2>10. Choose Template</h2>

<p class="small">
Choose the design that best matches your job application.
</p>

<input type="hidden" name="template" id="templateInput" value="modern">

<div class="template-grid">

<button
    type="button"
    class="template-option selected"
    data-template="modern"
    onclick="selectTemplate(this)"
>
    <span class="checkmark">✓</span>

    <div class="template-name">
        Modern Professional
    </div>

    <div class="template-description">
        Premium visual design with a profile photo,
        clean sections and a modern professional layout.
    </div>

    <span class="template-badge">
        ✓ Selected
    </span>
</button>


<button
    type="button"
    class="template-option"
    data-template="classic"
    onclick="selectTemplate(this)"
>
    <span class="checkmark">✓</span>

    <div class="template-name">
        Classic Professional
    </div>

    <div class="template-description">
        Elegant and traditional design with a full-width
        header. No photo. Ideal for corporate applications.
    </div>

    <span class="template-badge">
        Select
    </span>
</button>


<button
    type="button"
    class="template-option"
    data-template="ats"
    onclick="selectTemplate(this)"
>
    <span class="checkmark">✓</span>

    <div class="template-name">
        ATS Friendly
    </div>

    <div class="template-description">
        Simple single-column, text-focused design with
        no photo, icons or graphics.
    </div>

    <span class="template-badge">
        Select
    </span>
</button>

</div>

<div class="buttons">

<button
    type="button"
    class="back"
    onclick="prevStep()"
>
    ← Back
</button>

<button
    type="button"
    class="next"
    onclick="nextStep()"
>
    Next →
</button>

</div>

</div>


<div class="step">
<h2>11. Generate Your CV</h2>

<p>Your information is ready.</p>

<div class="buttons">
<button type="button" class="back" onclick="prevStep()">← Back</button>
<button type="submit" class="generate">
GENERATE & PREVIEW CV
</button>
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
function selectTemplate(button) {

    const options = document.querySelectorAll(".template-option");

    options.forEach(option => {

        option.classList.remove("selected");

        const badge = option.querySelector(".template-badge");

        if (badge) {
            badge.textContent = "Select";
        }

    });

    button.classList.add("selected");

    const badge = button.querySelector(".template-badge");

    if (badge) {
        badge.textContent = "✓ Selected";
    }

    document.getElementById("templateInput").value =
        button.dataset.template;
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

<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>

<style>

* {
    box-sizing: border-box;
}

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
    margin-bottom: 8px;
}

.subtitle {
    text-align: center;
    color: #777;
    margin-bottom: 20px;
}

.preview-box {
    width: 100%;
    background: #dfe7e7;
    padding: 10px;
    border-radius: 12px;
}

.pdf-page {
    width: 100%;
    height: auto;
    display: block;
    background: white;
    margin-bottom: 15px;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0,0,0,.12);
}

.loading {
    text-align: center;
    padding: 30px;
    color: #777;
    font-weight: bold;
}

.error {
    text-align: center;
    padding: 30px;
    color: #b00020;
    font-weight: bold;
}

.buttons {
    display: flex;
    gap: 12px;
    margin-top: 20px;
}

a {
    flex: 1;
    text-align: center;
    text-decoration: none;
    padding: 15px;
    border-radius: 10px;
    font-weight: bold;
    font-size: 16px;
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

    .container {
        padding: 8px;
    }

    .card {
        padding: 12px;
    }

    .preview-box {
        padding: 5px;
    }

    .buttons {
        flex-direction: column;
    }

    .pdf-page {
        margin-bottom: 10px;
    }
}

</style>

</head>

<body>

<div class="container">

<div class="card">

<h1>Your CV Preview</h1>

<div class="subtitle">
Your professional CV is ready
</div>

<div class="preview-box" id="previewBox">

<div class="loading" id="loading">
Preparing your CV preview...
</div>

</div>

<div class="buttons">

<a
    class="edit"
    href="/"
>
← Edit CV
</a>

<a
    class="download"
    href="/download/{{ token }}"
>
⬇ DOWNLOAD CV
</a>

</div>

</div>

</div>


<script>

pdfjsLib.GlobalWorkerOptions.workerSrc =
    "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";


const pdfBase64 = "{{ pdf_data }}";

const previewBox = document.getElementById("previewBox");

const loading = document.getElementById("loading");


async function renderPDF() {

    try {

        const binaryString = atob(pdfBase64);

        const len = binaryString.length;

        const bytes = new Uint8Array(len);

        for (let i = 0; i < len; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }

        const pdf = await pdfjsLib.getDocument({
            data: bytes
        }).promise;


        loading.remove();


        for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber++) {

            const page = await pdf.getPage(pageNumber);


            const containerWidth =
                previewBox.clientWidth - 20;


            const originalViewport =
                page.getViewport({ scale: 1 });


            const scale =
                containerWidth / originalViewport.width;


            const viewport =
                page.getViewport({ scale: scale });


            const canvas =
                document.createElement("canvas");


            canvas.className = "pdf-page";


            const context =
                canvas.getContext("2d");


            canvas.width = viewport.width;

            canvas.height = viewport.height;


            previewBox.appendChild(canvas);


            await page.render({
                canvasContext: context,
                viewport: viewport
            }).promise;

        }

    } catch (error) {

        loading.remove();

        const errorMessage =
            document.createElement("div");

        errorMessage.className = "error";

        errorMessage.textContent =
            "Unable to display the CV preview. Please try again.";

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


def draw_wrapped(
    c,
    text,
    x,
    y,
    width,
    font="Helvetica",
    size=9,
    leading=12,
    color=colors.black
):
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
def draw_profile_photo(c, photo_path, x, y, size):
    if not photo_path:
        return

    if not os.path.exists(photo_path):
        return

    try:
        c.saveState()

        # Center of the photo
        cx = x + size / 2
        cy = y - size / 2
        radius = size / 2

        # White border
        c.setFillColor(colors.white)
        c.circle(
            cx,
            cy,
            radius + 2 * mm,
            fill=1,
            stroke=0
        )

        # Circular clipping area
        path = c.beginPath()
        path.circle(cx, cy, radius)
        c.clipPath(path, stroke=0, fill=0)

        # Draw photo
        image = ImageReader(photo_path)

        c.drawImage(
            image,
            x,
            y - size,
            width=size,
            height=size,
            preserveAspectRatio=True,
            anchor='c',
            mask='auto'
        )

        c.restoreState()

    except Exception:
        pass


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

    photo_size = 24 * mm

    draw_profile_photo(
        c,
        data.get("photo"),
        page_width - photo_size - 15 * mm,
        page_height - 12 * mm,
        photo_size
    )

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 21)
    c.drawString(
        x,
        page_height - 23 * mm,
        name
    )

    if title:
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.HexColor("#E6EEEE"))
        c.drawString(
            x,
            page_height - 32 * mm,
            title
        )

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

    y = draw_sidebar_title(c, "Contact", x, y)

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
        y = draw_sidebar_title(c, "Skills", x, y)
        y = draw_sidebar_list(
            c,
            data.get("skills"),
            x,
            y,
            width
        )
        y -= 8

    if clean(data.get("languages")):
        y = draw_sidebar_title(c, "Languages", x, y)
        y = draw_sidebar_list(
            c,
            data.get("languages"),
            x,
            y,
            width
        )
        y -= 8

    if clean(data.get("hobbies")):
        y = draw_sidebar_title(c, "Interests", x, y)
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

    return draw_wrapped(
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

    # =========================================================
    # MODERN PROFESSIONAL - CVForge
    # =========================================================

    BLUE = colors.HexColor("#0868D7")
    DARK_BLUE = colors.HexColor("#063B82")
    LIGHT_BLUE = colors.HexColor("#EAF5FF")
    VERY_LIGHT_BLUE = colors.HexColor("#F7FBFF")
    TEXT = colors.HexColor("#173F6F")
    GRAY = colors.HexColor("#5E6B78")
    WHITE = colors.white

    # ---------------------------------------------------------
    # HEADER
    # ---------------------------------------------------------

    header_height = 67 * mm

    # Main blue header
    c.setFillColor(BLUE)
    c.rect(
        0,
        page_height - header_height,
        page_width,
        header_height,
        fill=1,
        stroke=0
    )

    # Dark blue lower header accent
    c.setFillColor(DARK_BLUE)
    c.rect(
        0,
        page_height - header_height,
        page_width,
        5 * mm,
        fill=1,
        stroke=0
    )

    # ---------------------------------------------------------
    # PHOTO - LEFT
    # ---------------------------------------------------------

    photo_size = 42 * mm
    photo_x = 10 * mm
    photo_y = page_height - 8 * mm

    if data.get("photo"):
        draw_profile_photo(
            c,
            data.get("photo"),
            photo_x,
            photo_y,
            photo_size
        )

        # Blue/white border around photo
        c.saveState()

        c.setStrokeColor(WHITE)
        c.setLineWidth(2 * mm)

        c.circle(
            photo_x + photo_size / 2,
            photo_y - photo_size / 2,
            photo_size / 2,
            fill=0,
            stroke=1
        )

        c.restoreState()

    # ---------------------------------------------------------
    # NAME + TITLE
    # ---------------------------------------------------------

    name = clean(data.get("name")) or "Your Name"
    title = clean(data.get("title"))

    name_x = 57 * mm
    name_y = page_height - 25 * mm

    # Name
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 22)

    c.drawString(
        name_x,
        name_y,
        name
    )

    # Professional title
    if title:
        c.setFillColor(WHITE)
        c.setFont("Helvetica", 12)

        c.drawString(
            name_x,
            page_height - 34 * mm,
            title
        )

    # Small decorative line
    c.setStrokeColor(WHITE)
    c.setLineWidth(0.8)

    c.line(
        name_x,
        page_height - 39 * mm,
        name_x + 72 * mm,
        page_height - 39 * mm
    )

    # ---------------------------------------------------------
    # SHORT SUMMARY IN HEADER
    # ---------------------------------------------------------

    summary = clean(data.get("summary"))

    if summary:

        summary_width = 78 * mm

        draw_wrapped(
            c,
            summary,
            name_x,
            page_height - 44 * mm,
            summary_width,
            "Helvetica-Oblique",
            8,
            10,
            colors.HexColor("#EAF4FF")
        )

    # ---------------------------------------------------------
    # HEADER CONTACT AREA - RIGHT
    # ---------------------------------------------------------

    contact_x = 145 * mm
    contact_y = page_height - 21 * mm
    contact_width = page_width - contact_x - 8 * mm

    header_contacts = [
        data.get("phone"),
        data.get("email"),
        data.get("location"),
        data.get("linkedin"),
        data.get("website")
    ]

    for item in header_contacts:

        item = clean(item)

        if not item:
            continue

        # Small white separator
        c.setFillColor(WHITE)
        c.circle(
            contact_x,
            contact_y + 1,
            1.2 * mm,
            fill=1,
            stroke=0
        )

        contact_y = draw_wrapped(
            c,
            item,
            contact_x + 5 * mm,
            contact_y,
            contact_width - 5 * mm,
            "Helvetica",
            7.5,
            9,
            WHITE
        )

        contact_y -= 2 * mm

    # Vertical separator
    c.setStrokeColor(WHITE)
    c.setLineWidth(0.6)

    c.line(
        139 * mm,
        page_height - 17 * mm,
        139 * mm,
        page_height - 53 * mm
    )

    # ---------------------------------------------------------
    # BODY
    # ---------------------------------------------------------

    body_top = page_height - header_height

    sidebar_width = 62 * mm

    # Light blue sidebar
    c.setFillColor(LIGHT_BLUE)

    c.rect(
        0,
        0,
        sidebar_width,
        body_top,
        fill=1,
        stroke=0
    )

    # Main white area
    c.setFillColor(VERY_LIGHT_BLUE)

    c.rect(
        sidebar_width,
        0,
        page_width - sidebar_width,
        body_top,
        fill=1,
        stroke=0
    )

    # ---------------------------------------------------------
    # HELPER: MODERN SECTION
    # ---------------------------------------------------------

    def modern_section_title(title, x, y, width):

        # Circle
        c.setFillColor(BLUE)

        c.circle(
            x + 5 * mm,
            y - 1 * mm,
            5 * mm,
            fill=1,
            stroke=0
        )

        # Simple white marker
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 8)

        c.drawCentredString(
            x + 5 * mm,
            y - 3.5 * mm,
            "•"
        )

        # Section title
        c.setFillColor(TEXT)
        c.setFont("Helvetica-Bold", 11)

        c.drawString(
            x + 13 * mm,
            y + 1 * mm,
            title.upper()
        )

        # Blue line
        c.setStrokeColor(BLUE)
        c.setLineWidth(0.7)

        c.line(
            x + 13 * mm,
            y - 3 * mm,
            x + width,
            y - 3 * mm
        )

        return y - 11 * mm

    # =========================================================
    # LEFT SIDEBAR
    # =========================================================

    sidebar_x = 9 * mm
    sidebar_width_inner = sidebar_width - 18 * mm
    sy = body_top - 10 * mm

    # ---------------------------------------------------------
    # CONTACT
    # ---------------------------------------------------------

    sy = modern_section_title(
        "Contact",
        sidebar_x,
        sy,
        sidebar_width_inner
    )

    contact_items = [
        data.get("phone"),
        data.get("email"),
        data.get("location"),
        data.get("linkedin"),
        data.get("website")
    ]

    for item in contact_items:

        item = clean(item)

        if not item:
            continue

        sy = draw_wrapped(
            c,
            item,
            sidebar_x,
            sy,
            sidebar_width_inner,
            "Helvetica",
            8,
            10,
            TEXT
        )

        sy -= 2 * mm

    # ---------------------------------------------------------
    # PROFESSIONAL SUMMARY
    # ---------------------------------------------------------

    if summary:

        sy -= 4 * mm

        sy = modern_section_title(
            "Professional Summary",
            sidebar_x,
            sy,
            sidebar_width_inner
        )

        sy = draw_wrapped(
            c,
            summary,
            sidebar_x,
            sy,
            sidebar_width_inner,
            "Helvetica",
            8,
            10,
            TEXT
        )

    # ---------------------------------------------------------
    # SKILLS
    # ---------------------------------------------------------

    skills = clean(data.get("skills"))

    if skills:

        sy -= 5 * mm

        sy = modern_section_title(
            "Skills",
            sidebar_x,
            sy,
            sidebar_width_inner
        )

        skill_items = [
            item.strip()
            for item in skills.replace(",", "\n").splitlines()
            if item.strip()
        ]

        for item in skill_items:

            sy = draw_wrapped(
                c,
                "• " + item,
                sidebar_x,
                sy,
                sidebar_width_inner,
                "Helvetica",
                8,
                10,
                TEXT
            )

            sy -= 1 * mm

    # ---------------------------------------------------------
    # LANGUAGES
    # ---------------------------------------------------------

    languages = clean(data.get("languages"))

    if languages:

        sy -= 4 * mm

        sy = modern_section_title(
            "Languages",
            sidebar_x,
            sy,
            sidebar_width_inner
        )

        language_items = [
            item.strip()
            for item in languages.replace(",", "\n").splitlines()
            if item.strip()
        ]

        for item in language_items:

            sy = draw_wrapped(
                c,
                "• " + item,
                sidebar_x,
                sy,
                sidebar_width_inner,
                "Helvetica",
                8,
                10,
                TEXT
            )

            sy -= 1 * mm

    # ---------------------------------------------------------
    # INTERESTS
    # ---------------------------------------------------------

    hobbies = clean(data.get("hobbies"))

    if hobbies:

        sy -= 4 * mm

        sy = modern_section_title(
            "Interests",
            sidebar_x,
            sy,
            sidebar_width_inner
        )

        hobby_items = [
            item.strip()
            for item in hobbies.replace(",", "\n").splitlines()
            if item.strip()
        ]

        for item in hobby_items:

            sy = draw_wrapped(
                c,
                "• " + item,
                sidebar_x,
                sy,
                sidebar_width_inner,
                "Helvetica",
                8,
                10,
                TEXT
            )

            sy -= 1 * mm

    # =========================================================
    # RIGHT MAIN CONTENT
    # =========================================================

    main_x = sidebar_width + 11 * mm
    main_width = page_width - main_x - 10 * mm
    my = body_top - 12 * mm

    # ---------------------------------------------------------
    # EXPERIENCE
    # ---------------------------------------------------------

    experience = clean(data.get("experience"))

    if experience:

        my = modern_section_title(
            "Professional Experience",
            main_x,
            my,
            main_width
        )

        blocks = [
            block.strip()
            for block in experience.split("\n\n")
            if block.strip()
        ]

        for block in blocks:

            lines = block.splitlines()

            if not lines:
                continue

            heading = clean(lines[0])

            # Job title
            c.setFillColor(DARK_BLUE)
            c.setFont("Helvetica-Bold", 10.5)

            c.drawString(
                main_x,
                my,
                heading
            )

            my -= 5 * mm

            body_lines = [
                clean(line)
                for line in lines[1:]
                if clean(line)
            ]

            if body_lines:

                body_text = " ".join(body_lines)

                # Convert sentences into bullet-style lines
                sentences = [
                    s.strip()
                    for s in body_text.replace("•", "\n").splitlines()
                    if s.strip()
                ]

                if len(sentences) == 1:

                    my = draw_wrapped(
                        c,
                        "• " + sentences[0],
                        main_x,
                        my,
                        main_width,
                        "Helvetica",
                        8,
                        10,
                        TEXT
                    )

                else:

                    for sentence in sentences:

                        my = draw_wrapped(
                            c,
                            "• " + sentence,
                            main_x,
                            my,
                            main_width,
                            "Helvetica",
                            8,
                            10,
                            TEXT
                        )

                        my -= 1 * mm

            my -= 4 * mm

    # ---------------------------------------------------------
    # EDUCATION
    # ---------------------------------------------------------

    education = clean(data.get("education"))

    if education:

        my -= 2 * mm

        my = modern_section_title(
            "Education",
            main_x,
            my,
            main_width
        )

        blocks = [
            block.strip()
            for block in education.split("\n\n")
            if block.strip()
        ]

        for block in blocks:

            lines = block.splitlines()

            if not lines:
                continue

            c.setFillColor(DARK_BLUE)
            c.setFont("Helvetica-Bold", 10)

            c.drawString(
                main_x,
                my,
                clean(lines[0])
            )

            my -= 5 * mm

            body = " ".join(
                clean(line)
                for line in lines[1:]
                if clean(line)
            )

            if body:

                my = draw_wrapped(
                    c,
                    body,
                    main_x,
                    my,
                    main_width,
                    "Helvetica",
                    8,
                    10,
                    TEXT
                )

            my -= 4 * mm

    # ---------------------------------------------------------
    # CERTIFICATES
    # ---------------------------------------------------------

    certificates = clean(data.get("certificates"))

    if certificates:

        my -= 2 * mm

        my = modern_section_title(
            "Certificates & Training",
            main_x,
            my,
            main_width
        )

        certificate_items = [
            item.strip()
            for item in certificates.splitlines()
            if item.strip()
        ]

        for item in certificate_items:

            my = draw_wrapped(
                c,
                "• " + item,
                main_x,
                my,
                main_width,
                "Helvetica",
                8,
                10,
                TEXT
            )

            my -= 1 * mm

    # ---------------------------------------------------------
    # REFERENCES
    # ---------------------------------------------------------

    references = clean(data.get("references"))

    if references:

        my -= 4 * mm

        my = modern_section_title(
            "References",
            main_x,
            my,
            main_width
        )

        my = draw_wrapped(
            c,
            references,
            main_x,
            my,
            main_width,
            "Helvetica",
            8,
            10,
            TEXT
        )

    # =========================================================
    # DECORATIVE FOOTER
    # =========================================================

    footer_y = 11 * mm

    # Light blue curve
    c.setFillColor(colors.HexColor("#CDE9FF"))

    path = c.beginPath()

    path.moveTo(0, footer_y + 17 * mm)

    path.curveTo(
        25 * mm,
        footer_y + 7 * mm,
        43 * mm,
        footer_y + 3 * mm,
        70 * mm,
        footer_y + 7 * mm
    )

    path.curveTo(
        88 * mm,
        footer_y + 10 * mm,
        100 * mm,
        footer_y + 4 * mm,
        115 * mm,
        footer_y
    )

    path.lineTo(0, footer_y)
    path.close()

    c.drawPath(
        path,
        fill=1,
        stroke=0
    )

    # Dark blue curve
    c.setFillColor(DARK_BLUE)

    path2 = c.beginPath()

    path2.moveTo(0, footer_y + 7 * mm)

    path2.curveTo(
        25 * mm,
        footer_y - 1 * mm,
        45 * mm,
        footer_y - 2 * mm,
        70 * mm,
        footer_y + 2 * mm
    )

    path2.curveTo(
        88 * mm,
        footer_y + 5 * mm,
        100 * mm,
        footer_y + 1 * mm,
        115 * mm,
        footer_y - 2 * mm
    )

    path2.lineTo(0, footer_y - 2 * mm)
    path2.close()

    c.drawPath(
        path2,
        fill=1,
        stroke=0
    )

    # Footer message
    c.setFillColor(BLUE)
    c.setFont("Helvetica-BoldOblique", 8)

    c.drawString(
        75 * mm,
        13 * mm,
        "BUILD YOUR FUTURE"
    )

    c.setFont("Helvetica", 6.5)

    c.drawString(
        75 * mm,
        8 * mm,
        "Professional • Modern • Career Ready"
    )


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

    if clean(data.get("summary")):
        y = draw_section_title(
            c,
            "Professional Summary",
            margin,
            y,
            content_width
        )

        y = draw_wrapped(
            c,
            data.get("summary"),
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

    if clean(data.get("summary")):
        y = draw_section_title(
            c,
            "Professional Summary",
            margin,
            y,
            content_width
        )

        y = draw_wrapped(
            c,
            data.get("summary"),
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

    generate_pdf(data, filename)

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
