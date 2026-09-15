from flask import Flask, request, render_template_string, send_file
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
import os
import tempfile
import base64
import uuid
from PIL import Image
from io import BytesIO

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
.color-section {
    margin-top: 25px;
    padding: 18px;
    background: #f7f9f9;
    border-radius: 14px;
}

.color-section h3 {
    margin: 0 0 6px;
    color: #173f3f;
}

.color-grid {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    margin-top: 15px;
}

.color-option {
    width: 42px;
    height: 42px;
    border-radius: 50%;
    border: 4px solid white;
    box-shadow: 0 0 0 1px #ccd8d8;
    cursor: pointer;
    padding: 0;
    flex: none;
}

.color-option.selected {
    box-shadow:
        0 0 0 2px #222,
        0 3px 10px rgba(0,0,0,.18);
    transform: scale(1.08);
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
spanish - Native"></textarea>

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
<div class="color-section">

<h3>Choose CV Color</h3>

<p class="small">
Choose the accent color for your CV. This color will be used for the header, section lines and highlights.
</p>

<input
    type="hidden"
    name="accent_color"
    id="accentColorInput"
    value="#1599A8"
>

<div class="color-grid">

<button
    type="button"
    class="color-option selected"
    data-color="#1599A8"
    style="background:#1599A8"
    onclick="selectColor(this)"
    aria-label="Teal"
></button>

<button
    type="button"
    class="color-option"
    data-color="#1769AA"
    style="background:#1769AA"
    onclick="selectColor(this)"
    aria-label="Blue"
></button>

<button
    type="button"
    class="color-option"
    data-color="#173F63"
    style="background:#173F63"
    onclick="selectColor(this)"
    aria-label="Navy"
></button>

<button
    type="button"
    class="color-option"
    data-color="#8B2F3B"
    style="background:#8B2F3B"
    onclick="selectColor(this)"
    aria-label="Burgundy"
></button>

<button
    type="button"
    class="color-option"
    data-color="#704C8C"
    style="background:#704C8C"
    onclick="selectColor(this)"
    aria-label="Purple"
></button>

<button
    type="button"
    class="color-option"
    data-color="#357A5B"
    style="background:#357A5B"
    onclick="selectColor(this)"
    aria-label="Green"
></button>

</div>

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
function selectColor(button) {

    const options =
        document.querySelectorAll(".color-option");

    options.forEach(option => {
        option.classList.remove("selected");
    });

    button.classList.add("selected");

    document.getElementById("accentColorInput").value =
        button.dataset.color;
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

    c.setFillColor(colors.HexColor("#333333"))
    c.setFont("Helvetica", 8.5)

    for item in items:
        lines = wrap_text(
            c,
            "✓ " + item,
            "Helvetica",
            8.5,
            width
        )

        for line in lines:
            c.drawString(x, y, line)
            y -= 12

        y -= 3

    return y


_modern_canvas = None


def wrap(text, font, size, width):
    return wrap_text(
        _modern_canvas,
        text,
        font,
        size,
        width
    )


def blocks(text):
    result = []

    for block in clean(text).split("\n\n"):
        lines = [
            line.strip()
            for line in block.splitlines()
            if line.strip()
        ]

        if lines:
            result.append(lines)

    return result
    
def remove_photo_background(input_path):
    output_path = os.path.join(
        tempfile.gettempdir(),
        "CVForge_white_" + uuid.uuid4().hex + ".png"
    )

    image = Image.open(input_path).convert("RGB")

    width, height = image.size
    pixels = image.load()

    # Background color from the top-left corner
    bg_r, bg_g, bg_b = pixels[0, 0]

    # Replace similar background pixels with white
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]

            distance = (
                abs(r - bg_r)
                + abs(g - bg_g)
                + abs(b - bg_b)
            )

            # Higher value removes more of the colored background
            if distance < 100:
                pixels[x, y] = (255, 255, 255)

    image.save(output_path, "PNG")

    return output_path
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


# ============================================================
# MODERN PROFESSIONAL — CVFORGE 2026
# ============================================================

def modern_icon(c, kind, cx, cy, r=5.2*mm):
    """Draw clean white vector icons inside blue circles."""
    c.saveState()

    blue = colors.HexColor("#0875D1")
    white = colors.white

    c.setFillColor(blue)
    c.circle(cx, cy, r, fill=1, stroke=0)

    c.setStrokeColor(white)
    c.setFillColor(white)
    c.setLineWidth(1.2)

    # person
    if kind == "person":
        c.circle(cx, cy + 2.1*mm, 1.5*mm, fill=1, stroke=0)
        c.roundRect(
            cx - 3.0*mm, cy - 3.2*mm,
            6.0*mm, 3.5*mm,
            1.5*mm, fill=1, stroke=0
        )

    # target / summary
    elif kind == "summary":
        c.circle(cx, cy, 3.2*mm, fill=0, stroke=1)
        c.circle(cx, cy, 1.3*mm, fill=0, stroke=1)
        c.line(cx-4.0*mm, cy, cx+4.0*mm, cy)
        c.line(cx, cy-4.0*mm, cx, cy+4.0*mm)

    # gear / skills
    elif kind == "skills":
        c.circle(cx, cy, 2.5*mm, fill=0, stroke=1)
        for a in range(0, 360, 45):
            import math
            rad = math.radians(a)
            x1 = cx + math.cos(rad)*3.0*mm
            y1 = cy + math.sin(rad)*3.0*mm
            x2 = cx + math.cos(rad)*4.1*mm
            y2 = cy + math.sin(rad)*4.1*mm
            c.line(x1, y1, x2, y2)

    # globe / languages
    elif kind == "globe":
        c.circle(cx, cy, 3.5*mm, fill=0, stroke=1)
        c.ellipse(
            cx-1.8*mm, cy-3.5*mm,
            cx+1.8*mm, cy+3.5*mm,
            fill=0, stroke=1
        )
        c.line(cx-3.5*mm, cy, cx+3.5*mm, cy)

    # briefcase / experience
    elif kind == "briefcase":
        c.roundRect(
            cx-3.8*mm, cy-2.7*mm,
            7.6*mm, 5.2*mm,
            1*mm, fill=0, stroke=1
        )
        c.line(cx-1.8*mm, cy+2.5*mm, cx+1.8*mm, cy+2.5*mm)
        c.line(cx-1.8*mm, cy+2.5*mm, cx-1.8*mm, cy+3.5*mm)
        c.line(cx+1.8*mm, cy+2.5*mm, cx+1.8*mm, cy+3.5*mm)

    # education
    elif kind == "education":
        p = c.beginPath()
        p.moveTo(cx-4.5*mm, cy+1.8*mm)
        p.lineTo(cx, cy+4.0*mm)
        p.lineTo(cx+4.5*mm, cy+1.8*mm)
        p.lineTo(cx, cy-0.5*mm)
        p.close()
        c.drawPath(p, fill=1, stroke=0)
        c.line(cx-3.2*mm, cy+1.0*mm, cx-3.2*mm, cy-2.8*mm)
        c.arc(
            cx-3.8*mm, cy-4.0*mm,
            cx+3.8*mm, cy+0.5*mm,
            200, 140
        )

    # certificate
    elif kind == "certificate":
        c.roundRect(
            cx-3.0*mm, cy-3.8*mm,
            6.0*mm, 7.6*mm,
            0.7*mm, fill=0, stroke=1
        )
        c.line(cx-1.8*mm, cy+1.5*mm, cx+1.8*mm, cy+1.5*mm)
        c.line(cx-1.8*mm, cy, cx+1.8*mm, cy)
        c.circle(cx, cy-2.0*mm, 1.0*mm, fill=0, stroke=1)

    # references
    elif kind == "references":
        c.circle(cx-1.8*mm, cy+1.5*mm, 1.3*mm, fill=1, stroke=0)
        c.circle(cx+2.0*mm, cy+1.0*mm, 1.1*mm, fill=1, stroke=0)
        c.arc(
            cx-4.0*mm, cy-4.0*mm,
            cx+0.8*mm, cy+1.5*mm,
            0, 180
        )
        c.arc(
            cx+0.0*mm, cy-4.0*mm,
            cx+4.0*mm, cy+1.0*mm,
            0, 180
        )

    c.restoreState()


def modern_section(c, title, icon, x, y, width):
    """Modern blue section heading."""
    modern_icon(c, icon, x + 5*mm, y - 1.5*mm)

    tx = x + 14*mm

    c.setFillColor(colors.HexColor("#0B5DB7"))
    c.setFont("Helvetica-Bold", 12.2)
    c.drawString(tx, y + 1*mm, title.upper())

    c.setStrokeColor(colors.HexColor("#1684DC"))
    c.setLineWidth(0.7)
    c.line(tx, y - 3.2*mm, x + width, y - 3.2*mm)

    return y - 11*mm


def modern_bullets(c, items, x, y, width, size=9.2, leading=4.7*mm):
    for item in items:
        item = item.strip()
        if not item:
            continue

        lines = wrap(
            item,
            "Helvetica",
            size,
            width - 7*mm
        )

        for n, line in enumerate(lines):
            if y < 23*mm:
                return y

            c.setFillColor(colors.HexColor("#0A62B7"))

            if n == 0:
                c.circle(
                    x + 1.5*mm,
                    y + 1.1*mm,
                    0.8*mm,
                    fill=1,
                    stroke=0
                )

            c.setFillColor(colors.HexColor("#183B63"))
            c.setFont("Helvetica", size)
            c.drawString(x + 6*mm, y, line)
            y -= leading

        y -= 1.2*mm

    return y


def modern_text(c, value, x, y, width, size=9.2, leading=4.8*mm):
    if not value:
        return y

    for paragraph in value.splitlines():
        paragraph = paragraph.strip()

        if not paragraph:
            y -= 2.5*mm
            continue

        lines = wrap(
            paragraph,
            "Helvetica",
            size,
            width
        )

        for line in lines:
            if y < 23*mm:
                return y

            c.setFillColor(colors.HexColor("#183B63"))
            c.setFont("Helvetica", size)
            c.drawString(x, y, line)
            y -= leading

    return y


def modern_wave_footer(c, W):
    """Layered blue curved footer matching the reference design."""

    # light blue wave
    p1 = c.beginPath()
    p1.moveTo(0, 24*mm)
    p1.curveTo(
        35*mm, 13*mm,
        75*mm, 12*mm,
        115*mm, 20*mm
    )
    p1.curveTo(
        155*mm, 28*mm,
        190*mm, 17*mm,
        W, 24*mm
    )
    p1.lineTo(W, 0)
    p1.lineTo(0, 0)
    p1.close()

    c.setFillColor(colors.HexColor("#B8E3FA"))
    c.drawPath(p1, fill=1, stroke=0)

    # medium blue wave
    p2 = c.beginPath()
    p2.moveTo(0, 15*mm)
    p2.curveTo(
        40*mm, 5*mm,
        70*mm, 8*mm,
        115*mm, 14*mm
    )
    p2.curveTo(
        155*mm, 20*mm,
        195*mm, 8*mm,
        W, 16*mm
    )
    p2.lineTo(W, 0)
    p2.lineTo(0, 0)
    p2.close()

    c.setFillColor(colors.HexColor("#0875D1"))
    c.drawPath(p2, fill=1, stroke=0)

    # dark blue wave
    p3 = c.beginPath()
    p3.moveTo(0, 7*mm)
    p3.curveTo(
        35*mm, 0,
        70*mm, 3*mm,
        112*mm, 7*mm
    )
    p3.curveTo(
        155*mm, 12*mm,
        200*mm, 2*mm,
        W, 8*mm
    )
    p3.lineTo(W, 0)
    p3.lineTo(0, 0)
    p3.close()

    c.setFillColor(colors.HexColor("#07509B"))
    c.drawPath(p3, fill=1, stroke=0)


def generate_modern(c, data):
    global _modern_canvas
    _modern_canvas = c

    W, H = A4

    c.setTitle(
        "CV - " + clean(data.get("name"))
    )

    # ==============================
    # COLORS
    # ==============================

    try:
        accent = colors.HexColor(
            clean(data.get("accent_color")) or "#1599A8"
        )
    except Exception:
        accent = colors.HexColor("#1599A8")

    dark = colors.HexColor("#123F55")
    text = colors.HexColor("#164F63")
    muted = colors.HexColor("#4F6F79")
    sidebar_bg = colors.HexColor("#E7F7FA")
    white = colors.white
    soft_line = colors.HexColor("#8CCED6")

    # ==============================
    # LAYOUT
    # ==============================

    sidebar_w = 76 * mm
    margin_right = 10 * mm

    main_x = sidebar_w + 10 * mm
    main_w = W - main_x - margin_right

    header_h = 48 * mm
    band_h = 14 * mm

    header_bottom = H - header_h
    band_y = header_bottom - band_h

    # =========================================================
    # WHITE HEADER
    # =========================================================

    c.setFillColor(white)

    c.rect(
        0,
        header_bottom,
        W,
        header_h,
        fill=1,
        stroke=0
    )
    



    # =========================================================
    # NAME
    # =========================================================

    name = clean(data.get("name")) or "Your Name"

    name_x = 82 * mm
    name_y = H - 19 * mm

    name_size = 25

    while (
        c.stringWidth(
            name,
            "Helvetica-Bold",
            name_size
        )
        > W - name_x - margin_right
        and name_size > 17
    ):
        name_size -= 1

    c.setFillColor(dark)

    c.setFont(
        "Helvetica-Bold",
        name_size
    )

    c.drawString(
        name_x,
        name_y,
        name
    )

    # =========================================================
    # PROFESSIONAL TITLE UNDER NAME
    # =========================================================

    professional_title = (
        clean(data.get("title"))
        or "PROFESSIONAL"
    )

    title_text = professional_title.upper()

    title_size = 11

    while (
        c.stringWidth(
            title_text,
            "Helvetica",
            title_size
        )
        > W - name_x - margin_right
        and title_size > 8
    ):
        title_size -= 0.5

    c.setFillColor(dark)

    c.setFont(
        "Helvetica",
        title_size
    )

    c.drawString(
        name_x,
        name_y - 11 * mm,
        title_text
    )

    # =========================================================
    # FULL WIDTH TEAL BAND
    # =========================================================

    c.setFillColor(accent)

    c.rect(
        0,
        band_y,
        W,
        band_h,
        fill=1,
        stroke=0
    )

    c.setFillColor(white)

    c.setFont(
        "Helvetica-Bold",
        11
    )

    c.drawCentredString(
        W / 2,
        band_y + 4.3 * mm,
        title_text
    )

    # =========================================================
    # SIDEBAR
    # =========================================================

    bottom = 10 * mm

    c.setFillColor(sidebar_bg)

    c.rect(
        0,
        bottom,
        sidebar_w,
        band_y - bottom,
        fill=1,
        stroke=0
    )

    sidebar_y = band_y - 12 * mm

    # =========================================================
    # SIDEBAR HEADING
    # =========================================================

    def sidebar_heading(title_text):

        nonlocal sidebar_y

        c.setFillColor(dark)

        c.setFont(
            "Helvetica-Bold",
            10.5
        )

        c.drawString(
            9 * mm,
            sidebar_y,
            title_text.upper()
        )

        sidebar_y -= 2.8 * mm

        c.setStrokeColor(accent)
        c.setLineWidth(0.9)

        c.line(
            9 * mm,
            sidebar_y,
            sidebar_w - 9 * mm,
            sidebar_y
        )

        sidebar_y -= 5 * mm

    # =========================================================
    # SIMPLE CONTACT ICON
    # =========================================================

    def contact_icon(kind, x, y):

        c.saveState()

        c.setStrokeColor(accent)
        c.setFillColor(accent)
        c.setLineWidth(1)

        if kind == "email":

            c.rect(
                x,
                y - 3.5 * mm,
                6 * mm,
                4.5 * mm,
                fill=0,
                stroke=1
            )

            c.line(
                x,
                y + 1 * mm,
                x + 3 * mm,
                y - 1.5 * mm
            )

            c.line(
                x + 6 * mm,
                y + 1 * mm,
                x + 3 * mm,
                y - 1.5 * mm
            )

       
        elif kind == "phone":

            c.setLineWidth(1.7)

            p = c.beginPath()

            p.moveTo(
                x + 1 * mm,
                y + 1.5 * mm
            )

            p.curveTo(
                x + 2 * mm,
                y + 3 * mm,
                x + 4 * mm,
                y - 1 * mm,
                x + 5.5 * mm,
                y + 0.5 * mm
            )

            c.drawPath(
                p,
                stroke=1,
                fill=0
            )

       
        elif kind == "location":

            c.circle(
                x + 3 * mm,
                y,
                2 * mm,
                fill=0,
                stroke=1
            )

            p = c.beginPath()

            p.moveTo(
                x + 1 * mm,
                y - 1 * mm
            )

            p.lineTo(
                x + 3 * mm,
                y - 4.5 * mm
            )

            p.lineTo(
                x + 5 * mm,
                y - 1 * mm
            )

            c.drawPath(
                p,
                stroke=1,
                fill=0
            )

       
        elif kind == "linkedin":

            c.setFont(
                "Helvetica-Bold",
                6.5
            )

            c.drawString(
                x,
                y - 2 * mm,
                "in"
            )

            c.rect(
                x - 0.7 * mm,
                y - 3 * mm,
                6 * mm,
                4.8 * mm,
                fill=0,
                stroke=1
            )

       
        elif kind == "website":

            c.circle(
                x + 3 * mm,
                y,
                2.7 * mm,
                fill=0,
                stroke=1
            )

            c.line(
                x + 0.4 * mm,
                y,
                x + 5.6 * mm,
                y
            )

            c.line(
                x + 3 * mm,
                y - 2.5 * mm,
                x + 3 * mm,
                y + 2.5 * mm
            )

        c.restoreState()

    # =========================================================
    # CONTACT
    # =========================================================

    sidebar_heading("Contact")

    contact_items = [
        ("email", clean(data.get("email"))),
        ("phone", clean(data.get("phone"))),
        ("location", clean(data.get("location"))),
        ("linkedin", clean(data.get("linkedin"))),
        ("website", clean(data.get("website")))
    ]

    for kind, value in contact_items:

        if not value:
            continue

        contact_icon(
            kind,
            9 * mm,
            sidebar_y + 1 * mm
        )

        wrapped = wrap_text(
            c,
            value,
            "Helvetica",
            8.2,
            sidebar_w - 25 * mm
        )

        for line in wrapped:

            c.setFillColor(text)

            c.setFont(
                "Helvetica",
                8.2
            )

            c.drawString(
                18 * mm,
                sidebar_y,
                line
            )

            sidebar_y -= 4.3 * mm

        sidebar_y -= 1.2 * mm
        

    # =========================================================
    # PROFILE SUMMARY
    # =========================================================

    if clean(data.get("summary")):

        sidebar_heading(
            "Profile Summary"
        )

        summary_lines = wrap_text(
            c,
            clean(data.get("summary")),
            "Helvetica",
            8.5,
            sidebar_w - 18 * mm
        )

        for line in summary_lines:

            c.setFillColor(text)

            c.setFont(
                "Helvetica",
                8.5
            )

            c.drawString(
                9 * mm,
                sidebar_y,
                line
            )

            sidebar_y -= 4.35 * mm

        sidebar_y -= 3 * mm
        

    # =========================================================
    # SKILLS
    # =========================================================

    if clean(data.get("skills")):

        sidebar_heading("Skills")

        for raw in clean(
            data.get("skills")
        ).splitlines():

            skill = raw.strip()

            if not skill:
                continue

            if skill.startswith("•"):
                skill = skill[1:].strip()

            if skill.startswith("-"):
                skill = skill[1:].strip()

            wrapped = wrap_text(
                c,
                skill,
                "Helvetica",
                8.3,
                sidebar_w - 20 * mm
            )

            for i, line in enumerate(wrapped):

                c.setFillColor(text)

                c.setFont(
                    "Helvetica",
                    8.3
                )

                if i == 0:

                    c.drawString(
                        9 * mm,
                        sidebar_y,
                        "✓"
                    )

                c.drawString(
                    16 * mm,
                    sidebar_y,
                    line
                )

                sidebar_y -= 4.1 * mm

        sidebar_y -= 3 * mm
        

    # =========================================================
    # LANGUAGES
    # =========================================================

    if clean(data.get("languages")):

        sidebar_heading(
            "Languages"
        )

        for raw in clean(
            data.get("languages")
        ).splitlines():

            language = raw.strip()

            if not language:
                continue

            if language.startswith("•"):
                language = language[1:].strip()

            if language.startswith("-"):
                language = language[1:].strip()

            wrapped = wrap_text(
                c,
                language,
                "Helvetica",
                8.3,
                sidebar_w - 20 * mm
            )

            for i, line in enumerate(wrapped):

                c.setFillColor(text)

                c.setFont(
                    "Helvetica",
                    8.3
                )

                if i == 0:

                    c.drawString(
                        9 * mm,
                        sidebar_y,
                        "✓"
                    )

                c.drawString(
                    16 * mm,
                    sidebar_y,
                    line
                )

                sidebar_y -= 4.1 * mm

        sidebar_y -= 3 * mm
        

    # =========================================================
    # OPTIONAL INTERESTS
    # =========================================================

    if clean(data.get("hobbies")):

        sidebar_heading(
            "Interests"
        )

        for raw in clean(
            data.get("hobbies")
        ).splitlines():

            interest = raw.strip()

            if not interest:
                continue

            if interest.startswith("•"):
                interest = interest[1:].strip()

            if interest.startswith("-"):
                interest = interest[1:].strip()

            wrapped = wrap_text(
                c,
                interest,
                "Helvetica",
                8.3,
                sidebar_w - 20 * mm
            )

            for i, line in enumerate(wrapped):

                c.setFillColor(text)

                c.setFont(
                    "Helvetica",
                    8.3
                )

                if i == 0:

                    c.drawString(
                        9 * mm,
                        sidebar_y,
                        "•"
                    )

                c.drawString(
                    16 * mm,
                    sidebar_y,
                    line
                )

                sidebar_y -= 4.1 * mm

        sidebar_y -= 2 * mm

    # =========================================================
    # MAIN COLUMN
    # =========================================================

    main_y = band_y - 12 * mm

    def main_heading(title_text):

        nonlocal main_y

        c.setFillColor(dark)

        c.setFont(
            "Helvetica-Bold",
            10.5
        )

        c.drawString(
            main_x,
            main_y,
            title_text.upper()
        )

        main_y -= 2.8 * mm

        c.setStrokeColor(accent)
        c.setLineWidth(0.9)

        c.line(
            main_x,
            main_y,
            W - margin_right,
            main_y
        )

        main_y -= 5 * mm

    # =========================================================
    # EXPERIENCE PARSER
    # =========================================================

    def get_experience_jobs(raw_text):

        lines = []

        for raw in clean(raw_text).splitlines():

            line = raw.strip()

            if not line:
                continue

            lower = line.lower()

            # Remove accidental instructional text
            if lower.startswith("important:"):
                continue

            if "if your current code separates" in lower:
                continue

            if lower == "use this format:":
                continue

            lines.append(line)

        jobs = []
        current = None

        for line in lines:

            parts = [
                p.strip()
                for p in line.split("|")
            ]

            # A line containing at least
            # Job | Company | Location | Dates
            # starts a new job.
            is_job_header = (
                len(parts) >= 4
            )

            if is_job_header:

                if current:
                    jobs.append(current)

                current = {
                    "title": parts[0],
                    "company": parts[1],
                    "location": parts[2],
                    "dates": parts[3],
                    "bullets": []
                }

            else:

                if current is None:
                    continue

                # Ignore accidental format instructions
                if line.lower() in [
                    "use this format",
                    "use this format:"
                ]:
                    continue

                current["bullets"].append(line)

        if current:
            jobs.append(current)

        return jobs

    # =========================================================
    # PROFESSIONAL EXPERIENCE
    # =========================================================

    if clean(data.get("experience")):

        main_heading(
            "Professional Experience"
        )

        jobs = get_experience_jobs(
            data.get("experience")
        )

        for job in jobs:

            # Job title
            c.setFillColor(dark)

            c.setFont(
                "Helvetica-Bold",
                9.5
            )

            c.drawString(
                main_x,
                main_y,
                job["title"]
            )

            # Dates
            if job["dates"]:

                c.setFillColor(accent)

                c.setFont(
                    "Helvetica",
                    8.2
                )

                date_width = c.stringWidth(
                    job["dates"],
                    "Helvetica",
                    8.2
                )

                c.drawString(
                    W - margin_right - date_width,
                    main_y,
                    job["dates"]
                )

            main_y -= 4.8 * mm

            # Company + location
            company_line = job["company"]

            if job["location"]:

                if company_line:
                    company_line += (
                        "  •  "
                        + job["location"]
                    )
                else:
                    company_line = job["location"]

            if company_line:

                c.setFillColor(text)

                c.setFont(
                    "Helvetica",
                    8.6
                )

                c.drawString(
                    main_x,
                    main_y,
                    company_line
                )

                main_y -= 4.5 * mm

            # Bullets
            for bullet in job["bullets"]:

                if not bullet:
                    continue

                if bullet.startswith("•"):
                    bullet = bullet[1:].strip()

                if bullet.startswith("-"):
                    bullet = bullet[1:].strip()

                wrapped = wrap_text(
                    c,
                    bullet,
                    "Helvetica",
                    8.5,
                    main_w - 8 * mm
                )

                for i, line in enumerate(wrapped):

                    c.setFillColor(text)

                    c.setFont(
                        "Helvetica",
                        8.5
                    )

                    if i == 0:

                        c.drawString(
                            main_x,
                            main_y,
                            "•"
                        )

                    c.drawString(
                        main_x + 6 * mm,
                        main_y,
                        line
                    )

                    main_y -= 4.2 * mm

            # Clear separation between jobs
            main_y -= 4 * mm

    # =========================================================
    # EDUCATION
    # =========================================================

    if clean(data.get("education")):

        main_heading("Education")

        education_blocks = [
            block.strip()
            for block in clean(
                data.get("education")
            ).split("\n\n")
            if block.strip()
        ]

        for block in education_blocks:

            lines = [
                line.strip()
                for line in block.splitlines()
                if line.strip()
            ]

            if not lines:
                continue

            parts = [
                p.strip()
                for p in lines[0].split("|")
            ]

            degree = parts[0]

            institution = (
                parts[1]
                if len(parts) > 1
                else ""
            )

            location = (
                parts[2]
                if len(parts) > 2
                else ""
            )

            dates = (
                parts[3]
                if len(parts) > 3
                else ""
            )

            c.setFillColor(dark)

            c.setFont(
                "Helvetica-Bold",
                9.2
            )

            c.drawString(
                main_x,
                main_y,
                degree
            )

            if dates:

                c.setFillColor(accent)

                c.setFont(
                    "Helvetica",
                    8.2
                )

                date_width = c.stringWidth(
                    dates,
                    "Helvetica",
                    8.2
                )

                c.drawString(
                    W - margin_right - date_width,
                    main_y,
                    dates
                )

            main_y -= 4.8 * mm

            institution_line = institution

            if location:

                if institution_line:
                    institution_line += (
                        "  •  "
                        + location
                    )
                else:
                    institution_line = location

            if institution_line:

                c.setFillColor(text)

                c.setFont(
                    "Helvetica",
                    8.5
                )

                c.drawString(
                    main_x,
                    main_y,
                    institution_line
                )

                main_y -= 4.5 * mm

            main_y -= 3 * mm

    # =========================================================
    # CERTIFICATES
    # =========================================================

    if clean(data.get("certificates")):

        main_heading(
            "Certificates & Training"
        )

        for raw in clean(
            data.get("certificates")
        ).splitlines():

            certificate = raw.strip()

            if not certificate:
                continue

            if certificate.startswith("•"):
                certificate = certificate[1:].strip()

            if certificate.startswith("-"):
                certificate = certificate[1:].strip()

            wrapped = wrap_text(
                c,
                certificate,
                "Helvetica",
                8.4,
                main_w - 8 * mm
            )

            for i, line in enumerate(wrapped):

                c.setFillColor(text)

                c.setFont(
                    "Helvetica",
                    8.4
                )

                if i == 0:

                    c.drawString(
                        main_x,
                        main_y,
                        "•"
                    )

                c.drawString(
                    main_x + 6 * mm,
                    main_y,
                    line
                )

                main_y -= 4.2 * mm

        main_y -= 3 * mm

    # =========================================================
    # REFERENCES
    # =========================================================

    if clean(data.get("references")):

        main_heading("References")

        wrapped = wrap_text(
            c,
            clean(data.get("references")),
            "Helvetica",
            8.4,
            main_w - 8 * mm
        )

        for i, line in enumerate(wrapped):

            c.setFillColor(text)

            c.setFont(
                "Helvetica",
                8.4
            )

            if i == 0:

                c.drawString(
                    main_x,
                    main_y,
                    "•"
                )

            c.drawString(
                main_x + 6 * mm,
                main_y,
                line
            )

            main_y -= 4.2 * mm
            

                # =========================================================
    # PHOTO — REFERENCE POSITION
    # Circular photo overlaps WHITE HEADER + TEAL BAND
    # =========================================================

    photo_path = clean(data.get("photo"))

    if photo_path and os.path.exists(photo_path):

        # Larger photo to match the reference
        photo_size = 48 * mm

        
        photo_cx = 39 * mm
        photo_cy = header_bottom + 15 * mm

        radius = photo_size / 2

        try:
            c.saveState()

            # -------------------------------------------------
            # WHITE OUTER CIRCLE
            # -------------------------------------------------

            c.setFillColor(colors.white)

            c.circle(
                photo_cx,
                photo_cy,
                radius + 2.5 * mm,
                fill=1,
                stroke=0
            )

            # -------------------------------------------------
            # TEAL CIRCULAR FRAME
            # -------------------------------------------------

            c.setStrokeColor(accent)
            c.setLineWidth(3.5)

            c.circle(
                photo_cx,
                photo_cy,
                radius + 1.0 * mm,
                fill=0,
                stroke=1
            )

            # -------------------------------------------------
            # CLIP PHOTO TO PERFECT CIRCLE
            # -------------------------------------------------

            path = c.beginPath()

            path.circle(
                photo_cx,
                photo_cy,
                radius
            )

            c.clipPath(
                path,
                stroke=0,
                fill=0
            )

            # -------------------------------------------------
            # PHOTO — SLIGHT ZOOM
            # -------------------------------------------------

            image = ImageReader(photo_path)

            zoom = 1.08

            draw_size = photo_size * zoom

            draw_x = (
                photo_cx
                - draw_size / 2
            )

            draw_y = (
                photo_cy
                - draw_size / 2
            )

            c.drawImage(
                image,
                draw_x,
                draw_y,
                width=draw_size,
                height=draw_size,
                preserveAspectRatio=True,
                anchor="c",
                mask="auto"
            )

            c.restoreState()

        except Exception:
            pass

    # =========================================================
    # FOOTER
    # =========================================================

    c.setStrokeColor(soft_line)
    c.setLineWidth(0.4)

    c.line(
        10 * mm,
        7 * mm,
        W - 10 * mm,
        7 * mm
    )

    c.setFillColor(
        colors.HexColor("#8A9AA0")
    )

    c.setFont(
        "Helvetica",
        6
    )

    c.drawCentredString(
        W / 2,
        4 * mm,
        "Created with CVForge"
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
        "template": request.form.get("template", "modern"),
"accent_color": request.form.get(
    "accent_color",
    "#1599A8"
)
    }
    photo = request.files.get("photo")

if photo and photo.filename:
    photo_path = os.path.join(
        tempfile.gettempdir(),
        "CVForge_" + photo.filename
    )

    photo.save(photo_path)

    try:
        photo_path = remove_photo_background(photo_path)
    except Exception:
        pass

    data["photo"] = photo_path

else:
    data["photo"] = ""

    filename = os.path.join(
        tempfile.gettempdir(),
        "CVForge_" + uuid.uuid4().hex + ".pdf"
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
