import os
import tempfile
import base64
import uuid
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

# Register Montserrat
if os.path.exists(MONTSERRAT_EXTRA_BOLD):
    try:
        pdfmetrics.registerFont(TTFont("Montserrat-ExtraBold", MONTSERRAT_EXTRA_BOLD))
    except Exception as e:
        print(f"Warning: Could not register Montserrat font: {e}")
else:
    print("Notice: Montserrat-ExtraBold.ttf not found in fonts/. Using standard Helvetica fallback.")

# Register Dancing Script
if os.path.exists(DANCING_SCRIPT):
    try:
        pdfmetrics.registerFont(TTFont("DancingScript", DANCING_SCRIPT))
    except Exception as e:
        print(f"Warning: Could not register DancingScript font: {e}")
else:
    print("Notice: DancingScript-Regular.ttf not found in fonts/. Using standard Helvetica fallback.")

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

.char-counter {
    text-align: right;
    margin-top: 5px;
    font-size: 12px;
    color: #777;
}

.char-counter.warning {
    color: #b07a00;
}

.char-counter.limit {
    color: #b00020;
    font-weight: bold;
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
<input name="title" maxlength="70" placeholder="e.g. Software Developer">

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
<textarea
    id="summary"
    name="summary"
    maxlength="500"
    placeholder="Write a short professional summary about yourself..."
></textarea>


<div class="buttons">
<button type="button" class="back" onclick="prevStep()">← Back</button>
<button type="button" class="next" onclick="nextStep()">Next →</button>
</div>
</div>


<div class="step">
<h2>3. Work Experience</h2>

<label>Experience</label>
<textarea name="experience"
maxlength="1200"
placeholder="Job Title - Company - Dates

Describe your responsibilities and achievements.

Add another position below if needed."></textarea>
<div class="char-counter">
    <span>0</span> / 1200 characters
</div>


<div class="buttons">
<button type="button" class="back" onclick="prevStep()">← Back</button>
<button type="button" class="next" onclick="nextStep()">Next →</button>
</div>
</div>


<div class="step">
<h2>4. Education</h2>

<label>Education</label>
<textarea name="education"
maxlength="600"
placeholder="Degree - Institution - Year

Add your education history here."></textarea>
<div class="char-counter">
    <span>0</span> / 600 characters
</div>

<div class="buttons">
<button type="button" class="back" onclick="prevStep()">← Back</button>
<button type="button" class="next" onclick="nextStep()">Next →</button>
</div>
</div>


<div class="step">
<h2>5. Skills</h2>

<label>Skills</label>
<textarea name="skills"
maxlength="400"
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
maxlength="500"
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
maxlength="250"
placeholder="English - Fluent
Spanish - Native"></textarea>

<div class="buttons">
<button type="button" class="back" onclick="prevStep()">← Back</button>
<button type="button" class="next" onclick="nextStep()">Next →</button>
</div>
</div>


<div class="step">
<h2>8. Interests</h2>

<label>Interests & Hobbies</label>
<textarea name="hobbies"
maxlength="250"
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
maxlength="500"
placeholder="Name - Position - Company
Email / Phone"></textarea>

<label>Signature (optional)</label>
<input type="file" name="signature" accept="image/png,image/jpeg,image/jpg">

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
    data-color="#D6AA4C"
    style="background:#D6AA4C"
    onclick="selectColor(this)"
    aria-label="Gold"
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

<div class="color-section">

    <h3>Choose Sidebar Color</h3>

    <p class="small">
        Choose the color of the left sidebar column.
    </p>

    <input
        type="hidden"
        name="sidebar_color"
        id="sidebarColorInput"
        value="#173F49"
    >

    <div class="color-grid">

        <button
            type="button"
            class="color-option selected"
            data-sidebar-color="#173F49"
            style="background:#173F49"
            onclick="selectSidebarColor(this)"
            aria-label="Dark Teal"
        ></button>

        <button
            type="button"
            class="color-option"
            data-sidebar-color="#0D4B56"
            style="background:#0D4B56"
            onclick="selectSidebarColor(this)"
            aria-label="Teal"
        ></button>

        <button
            type="button"
            class="color-option"
            data-sidebar-color="#1F2937"
            style="background:#1F2937"
            onclick="selectSidebarColor(this)"
            aria-label="Charcoal"
        ></button>

        <button
            type="button"
            class="color-option"
            data-sidebar-color="#123B2A"
            style="background:#123B2A"
            onclick="selectSidebarColor(this)"
            aria-label="Dark Green"
        ></button>

        <button
            type="button"
            class="color-option"
            data-sidebar-color="#3B2F4A"
            style="background:#3B2F4A"
            onclick="selectSidebarColor(this)"
            aria-label="Dark Purple"
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
        document.querySelectorAll(".color-option[data-color]");

    options.forEach(option => {
        option.classList.remove("selected");
    });

    button.classList.add("selected");

    document.getElementById("accentColorInput")
        .value = button.dataset.color;
}


function selectSidebarColor(button) {

    const options =
        document.querySelectorAll(".color-option[data-sidebar-color]");

    options.forEach(option => {
        option.classList.remove("selected");
    });

    button.classList.add("selected");

    document.getElementById("sidebarColorInput")
        .value = button.dataset.sidebarColor;
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
// =========================================================
// INPUT LIMIT ENFORCEMENT + CHARACTER COUNTERS
// =========================================================

document.querySelectorAll("textarea[data-limit]").forEach(function(textarea) {

    const counter = textarea.parentElement.querySelector(".char-counter");
    const number = counter ? counter.querySelector("span") : null;

    const limit = parseInt(
        textarea.dataset.limit,
        10
    );

    function updateCounter() {

        if (textarea.value.length > limit) {
            textarea.value = textarea.value.substring(0, limit);
        }

        const length = textarea.value.length;

        if (number) {
            number.textContent = length;
        }

        if (counter) {
            counter.classList.remove(
                "warning",
                "limit"
            );

            if (length >= limit) {
                counter.classList.add("limit");
            }
            else if (length >= limit * 0.9) {
                counter.classList.add("warning");
            }
        }
    }

    textarea.addEventListener(
        "input",
        updateCounter
    );

    textarea.addEventListener(
        "paste",
        function() {
            setTimeout(updateCounter, 0);
        }
    );

    updateCounter();
});
</script>

<script>
/* =========================================================
   CVFORGE — CHARACTER LIMIT + LIVE COUNTER
   ========================================================= */

document.querySelectorAll("textarea[maxlength], input[maxlength]").forEach(function(field) {

    const limit = parseInt(field.getAttribute("maxlength"), 10);

    if (!limit) {
        return;
    }

    /* Find existing counter */
    let counter = field.nextElementSibling;

    /* If there is no proper counter, create one */
    if (!counter || !counter.classList.contains("char-counter")) {
        counter = document.createElement("div");
        counter.className = "char-counter";
        field.parentNode.insertBefore(counter, field.nextSibling);
    }

    function updateCounter() {

        /* HARD LIMIT */
        if (field.value.length > limit) {
            field.value = field.value.substring(0, limit);
        }

        const length = field.value.length;

        counter.textContent = length + " / " + limit + " characters";

        /* Counter color */
        counter.classList.remove("warning", "limit");

        if (length >= limit) {
            counter.classList.add("limit");
        }
        else if (length >= limit * 0.9) {
            counter.classList.add("warning");
        }
    }

    /* Typing */
    field.addEventListener("input", updateCounter);

    /* Paste */
    field.addEventListener("paste", function() {
        setTimeout(updateCounter, 0);
    });

    /* Initial value */
    updateCounter();
});
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
<script>
document.querySelectorAll('[data-char-counter]').forEach(function (field) {
    const counter = field.nextElementSibling;

    function updateCounter() {
        counter.textContent =
            field.value.length + " / " + field.maxLength + " characters";
    }

    field.addEventListener("input", updateCounter);
    updateCounter();
});
</script>

</body>
</html>
"""


def clean(text):
    if not text:
        return ""
    return str(text).strip()
    
    _modern_canvas = None


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
    if not text:
        return []

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

    # PHONE
    elif kind == "phone":
        c.setLineWidth(1.4)
        p = c.beginPath()
        p.moveTo(cx - 2.5*mm, cy + 2.5*mm)
        p.curveTo(
            cx - 3.5*mm, cy + 1.0*mm,
            cx - 1.5*mm, cy - 2.0*mm,
            cx + 1.5*mm, cy - 2.8*mm
        )
        p.curveTo(
            cx + 2.5*mm, cy - 3.0*mm,
            cx + 3.2*mm, cy - 2.0*mm,
            cx + 2.5*mm, cy - 1.0*mm
        )
        c.drawPath(p, fill=0, stroke=1)

    # EMAIL
    elif kind == "email":
        c.setLineWidth(1.1)
        c.roundRect(
            cx - 3.5*mm,
            cy - 2.5*mm,
            7.0*mm,
            5.0*mm,
            0.7*mm,
            fill=0,
            stroke=1
        )
        c.line(
            cx - 3.2*mm,
            cy + 2.0*mm,
            cx,
            cy - 0.2*mm
        )
        c.line(
            cx,
            cy - 0.2*mm,
            cx + 3.2*mm,
            cy + 2.0*mm
        )

    # LOCATION
    elif kind == "location":
        c.setLineWidth(1.2)
        c.circle(
            cx,
            cy + 1.0*mm,
            2.2*mm,
            fill=0,
            stroke=1
        )
        c.circle(
            cx,
            cy + 1.0*mm,
            0.7*mm,
            fill=1,
            stroke=0
        )
        p = c.beginPath()
        p.moveTo(cx - 2.2*mm, cy)
        p.curveTo(
            cx - 2.2*mm,
            cy - 2.5*mm,
            cx,
            cy - 4.0*mm,
            cx,
            cy - 4.0*mm
        )
        p.curveTo(
            cx,
            cy - 4.0*mm,
            cx + 2.2*mm,
            cy - 2.5*mm,
            cx + 2.2*mm,
            cy
        )
        c.drawPath(p, fill=0, stroke=1)

    # LINKEDIN
    elif kind == "linkedin":
        c.setFillColor(white)
        c.roundRect(
            cx - 3.5*mm,
            cy - 3.5*mm,
            7.0*mm,
            7.0*mm,
            0.8*mm,
            fill=1,
            stroke=0
        )
        c.setFillColor(blue)
        c.setFont("Helvetica-Bold", 6.5)
        c.drawCentredString(
            cx,
            cy - 2.2*mm,
            "in"
        )

    # WEBSITE
    elif kind == "website":
        c.setLineWidth(1.1)
        c.circle(
            cx,
            cy,
            3.3*mm,
            fill=0,
            stroke=1
        )
        c.ellipse(
            cx - 1.6*mm,
            cy - 3.3*mm,
            cx + 1.6*mm,
            cy + 3.3*mm,
            fill=0,
            stroke=1
        )
        c.line(
            cx - 3.3*mm,
            cy,
            cx + 3.3*mm,
            cy
        )

    c.restoreState()

def modern_contact_icon(c, kind, cx, cy):
    """White contact icons matching the Modern CV reference."""

    c.saveState()

    white = colors.white
    c.setStrokeColor(white)
    c.setFillColor(white)

    # PHONE
    if kind == "phone":
        c.setLineWidth(1.8)

        p = c.beginPath()

        p.moveTo(
            cx - 2.8 * mm,
            cy + 2.8 * mm
        )

        p.curveTo(
            cx - 4.0 * mm,
            cy + 1.5 * mm,
            cx - 1.5 * mm,
            cy - 2.5 * mm,
            cx + 1.5 * mm,
            cy - 3.0 * mm
        )

        p.curveTo(
            cx + 3.0 * mm,
            cy - 3.3 * mm,
            cx + 3.8 * mm,
            cy - 1.8 * mm,
            cx + 2.8 * mm,
            cy - 0.8 * mm
        )

        p.lineTo(
            cx + 1.2 * mm,
            cy + 0.8 * mm
        )

        p.curveTo(
            cx + 0.5 * mm,
            cy + 1.5 * mm,
            cx - 0.5 * mm,
            cy + 2.5 * mm,
            cx - 1.0 * mm,
            cy + 3.2 * mm
        )

        p.close()

        c.drawPath(
            p,
            fill=1,
            stroke=0
        )

    # EMAIL
    elif kind == "email":
        c.setLineWidth(1.3)

        c.roundRect(
            cx - 4.0 * mm,
            cy - 2.8 * mm,
            8.0 * mm,
            5.6 * mm,
            0.5 * mm,
            fill=0,
            stroke=1
        )

        c.line(
            cx - 3.7 * mm,
            cy + 2.3 * mm,
            cx,
            cy - 0.3 * mm
        )

        c.line(
            cx,
            cy - 0.3 * mm,
            cx + 3.7 * mm,
            cy + 2.3 * mm
        )

    # LOCATION
    elif kind == "location":
        p = c.beginPath()

        p.moveTo(
            cx,
            cy - 4.5 * mm
        )

        p.curveTo(
            cx - 1.0 * mm,
            cy - 2.8 * mm,
            cx - 3.5 * mm,
            cy + 0.2 * mm,
            cx - 3.5 * mm,
            cy + 2.0 * mm
        )

        p.curveTo(
            cx - 3.5 * mm,
            cy + 4.2 * mm,
            cx - 1.9 * mm,
            cy + 5.2 * mm,
            cx,
            cy + 5.2 * mm
        )

        p.curveTo(
            cx + 1.9 * mm,
            cy + 5.2 * mm,
            cx + 3.5 * mm,
            cy + 4.2 * mm,
            cx + 3.5 * mm,
            cy + 2.0 * mm
        )

        p.curveTo(
            cx + 3.5 * mm,
            cy + 0.2 * mm,
            cx + 1.0 * mm,
            cy - 2.8 * mm,
            cx,
            cy - 4.5 * mm
        )

        p.close()

        c.drawPath(
            p,
            fill=1,
            stroke=0
        )

        c.setFillColor(colors.HexColor("#173F49"))

        c.circle(
            cx,
            cy + 2.0 * mm,
            1.1 * mm,
            fill=1,
            stroke=0
        )

    # LINKEDIN
    elif kind == "linkedin":
        c.setFillColor(white)

        c.roundRect(
            cx - 3.8 * mm,
            cy - 3.8 * mm,
            7.6 * mm,
            7.6 * mm,
            0.7 * mm,
            fill=1,
            stroke=0
        )

        c.setFillColor(
            colors.HexColor("#173F49")
        )

        c.setFont(
            "Helvetica-Bold",
            6.8
        )

        c.drawCentredString(
            cx,
            cy - 2.3 * mm,
            "in"
        )

    # WEBSITE / GLOBE
    elif kind == "website":
        c.setLineWidth(1.3)

        c.circle(
            cx,
            cy,
            3.8 * mm,
            fill=0,
            stroke=1
        )

        c.ellipse(
            cx - 1.8 * mm,
            cy - 3.8 * mm,
            cx + 1.8 * mm,
            cy + 3.8 * mm,
            fill=0,
            stroke=1
        )

        c.line(
            cx - 3.8 * mm,
            cy,
            cx + 3.8 * mm,
            cy
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

def limit_text(text, max_chars):
    if not text:
        return ""

    text = str(text).strip()

    if len(text) <= max_chars:
        return text

    shortened = text[:max_chars].rsplit(" ", 1)[0].strip()

    return shortened + "..."


def modern(data,file):
    W, H = A4

    c = canvas.Canvas(file, pagesize=A4)
    global _modern_canvas
    _modern_canvas = c
    c.setTitle("CV - " + (data.get("name") or "My CV"))

    # =========================================================
    # COLORS
    # =========================================================
    teal = colors.HexColor("#053D47")
    sidebar_color = colors.HexColor(data.get("sidebar_color") or "#173F49")
    gold = colors.HexColor(data.get("accent_color") or "#F2B632")
    white = colors.white
    dark = colors.HexColor("#123F4A")
    muted = colors.HexColor("#5E6F73")

    # =========================================================
    # PAGE STRUCTURE
    # =========================================================
    sidebar_w = 78 * mm
    main_x = sidebar_w + 14 * mm
    main_w = W - main_x - 13 * mm

    # =========================================================
    # SIDEBAR
    # =========================================================
    background = colors.HexColor("#FAFCFB")
    c.setFillColor(background)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(sidebar_color)
    c.rect(0, 0, sidebar_w, H, stroke=0, fill=1)

    
    # =========================
    # PROFILE PHOTO
    # =========================
    photo = data.get("photo")

    if photo and os.path.exists(photo):
        try:
            from reportlab.lib.utils import ImageReader

            # Photo position — centered in sidebar
            photo_size = 48 * mm
            photo_x = (sidebar_w - photo_size) / 2
            photo_y = H - 63 * mm

            # Outer gold border
            c.setFillColor(gold)
            c.circle(
                photo_x + photo_size / 2,
                photo_y + photo_size / 2,
                photo_size / 2 + 2.2 * mm,
                stroke=0,
                fill=1
            )

            # Thin dark ring between white and gold
            c.setStrokeColor(colors.HexColor("#222222"))
            c.setLineWidth(1.2)
            c.circle(
                photo_x + photo_size / 2,
                photo_y + photo_size / 2,
                photo_size / 2 + 1.2 * mm,
                stroke=1,
                fill=0
            )

            # Inner white border
            c.setFillColor(colors.white)
            c.circle(
                photo_x + photo_size / 2,
                photo_y + photo_size / 2,
                photo_size / 2 + 0.8 * mm,
                stroke=0,
                fill=1
            )

            # Circular photo clipping
            c.saveState()

            path = c.beginPath()
            path.circle(
                photo_x + photo_size / 2,
                photo_y + photo_size / 2,
                photo_size / 2
            )
            c.clipPath(path, stroke=0, fill=0)

            # Draw uploaded photo
            c.drawImage(
                ImageReader(photo),
                photo_x,
                photo_y,
                width=photo_size,
                height=photo_size,
                preserveAspectRatio=True,
                anchor="c",
                mask="auto"
            )

            c.restoreState()

        except Exception:
            pass

    # =========================================================
    # HELPER: WRAPPED TEXT
    # =========================================================
    def draw_lines(
        value,
        x,
        y,
        width,
        font="Helvetica",
        size=8.8,
        leading=4.6 * mm,
        color=dark,
        bullet=False
    ):
    
        if not value:
            return y

        c.setFillColor(color)
        c.setFont(font, size)

        for paragraph in value.splitlines():

            paragraph = paragraph.strip()

            if not paragraph:
                y -= leading * 0.55
                continue

            lines = wrap(
                paragraph,
                font,
                size,
                width
            )

            for index, line in enumerate(lines):

                if bullet:
                    prefix = "• " if index == 0 else "  "
                else:
                    prefix = ""

                c.drawString(
                    x,
                    y,
                    prefix + line
                )

                y -= leading

        return y

    # =========================================================
    # HELPER: MAIN SECTION TITLE
    # =========================================================
    def main_section(title, x, y, width):
        c.setFillColor(teal)
        c.circle(
            x + 5 * mm,
            y + 1 * mm,
            5.2 * mm,
            stroke=0,
            fill=1
        )
        # Briefcase icon
        cx = x + 5 * mm
        cy = y + 1 * mm
        
        # Experience briefcase icon
        if "experience" in title.lower():
            c.setFillColor(gold)
            c.setStrokeColor(gold)

        # Main solid briefcase
            c.roundRect(
                cx - 4.2 * mm,
                cy - 3.0 * mm,
                8.4 * mm,
                6.0 * mm,
                0.8 * mm,
                stroke=0,
                fill=1
            )

        # Handle
        c.setLineWidth(1.2)

        c.line(
            cx - 1.7 * mm,
            cy + 2.6 * mm,
            cx - 1.7 * mm,
            cy + 4.0 * mm
        )

        c.line(
            cx + 1.7 * mm,
            cy + 2.6 * mm,
            cx + 1.7 * mm,
            cy + 4.0 * mm
        )

        c.line(
            cx - 1.7 * mm,
            cy + 4.0 * mm,
            cx + 1.7 * mm,
            cy + 4.0 * mm
        )

        # Small center clasp
        c.setFillColor(teal)

        c.rect(
            cx - 0.8 * mm,
            cy - 0.5 * mm,
            1.6 * mm,
            1.0 * mm,
            stroke=0,
            fill=1
        )
        
        if "education" in title.lower():
            c.setFillColor(gold)

            # Graduation cap
            c.setLineWidth(1.4)
            c.setStrokeColor(gold)

            # Cap diamond
            c.line(
                cx - 5.0 * mm,
                cy + 1.0 * mm,
                cx,
                cy + 4.0 * mm
            )

            c.line(
                cx,
                cy + 4.0 * mm,
                cx + 5.0 * mm,
                cy + 1.0 * mm
            )

            c.line(
                cx + 5.0 * mm,
                cy + 1.0 * mm,
                cx,
                cy - 2.0 * mm
            )

            c.line(
                cx,
                cy - 2.0 * mm,
                cx - 5.0 * mm,
                cy + 1.0 * mm
            )

            # Cap base
            c.roundRect(
                cx - 3.8 * mm,
                cy - 2.8 * mm,
                7.6 * mm,
                1.8 * mm,
                0.5 * mm,
                stroke=0,
                fill=1
            )

            # Tassel
            c.setLineWidth(0.9)

            c.line(
                cx + 4.5 * mm,
                cy + 1.0 * mm,
                cx + 4.5 * mm,
                cy - 2.5 * mm
            )

            c.circle(
                cx + 4.5 * mm,
                cy - 3.0 * mm,
                0.6 * mm,
                stroke=0,
                fill=1
            )
                    # =====================================================
        # CERTIFICATE ICON
        # =====================================================
        if "certificate" in title.lower():

            c.setStrokeColor(gold)
            c.setFillColor(gold)
            c.setLineWidth(1.0)

            # Certificate paper
            c.roundRect(
                cx - 3.0 * mm,
                cy - 3.5 * mm,
                6.0 * mm,
                7.0 * mm,
                0.5 * mm,
                stroke=1,
                fill=0
            )

            # Text lines
            c.line(
                cx - 1.8 * mm,
                cy + 1.5 * mm,
                cx + 1.8 * mm,
                cy + 1.5 * mm
            )

            c.line(
                cx - 1.8 * mm,
                cy,
                cx + 1.8 * mm,
                cy
            )

            c.line(
                cx - 1.8 * mm,
                cy - 1.5 * mm,
                cx + 0.8 * mm,
                cy - 1.5 * mm
            )

            # Certificate seal
            c.circle(
                cx,
                cy - 2.7 * mm,
                0.9 * mm,
                stroke=1,
                fill=0
            )

            # Small ribbon
            c.line(
                cx - 0.5 * mm,
                cy - 3.4 * mm,
                cx - 1.4 * mm,
                cy - 4.7 * mm
            )

            c.line(
                cx + 0.5 * mm,
                cy - 3.4 * mm,
                cx + 1.4 * mm,
                cy - 4.7 * mm
            )
                    
            
            
            
                                    # =====================================================
        # REFERENCES ICON — TWO PERSONS
        # Front = WHITE
        # Back = GOLD
        # =====================================================
        if "reference" in title.lower():

            # -------------------------------------------------
            # BACK PERSON — GOLD
            # -------------------------------------------------
            c.setFillColor(gold)

            # Head
            c.circle(
                cx + 2.0 * mm,
                cy + 2.0 * mm,
                1.15 * mm,
                stroke=0,
                fill=1
            )

            # Body
            p = c.beginPath()

            p.moveTo(
                cx - 0.2 * mm,
                cy - 2.8 * mm
            )

            p.curveTo(
                cx - 0.2 * mm,
                cy - 0.5 * mm,
                cx + 1.0 * mm,
                cy - 0.2 * mm,
                cx + 2.0 * mm,
                cy - 0.2 * mm
            )

            p.curveTo(
                cx + 3.0 * mm,
                cy - 0.2 * mm,
                cx + 4.0 * mm,
                cy - 1.0 * mm,
                cx + 4.0 * mm,
                cy - 2.8 * mm
            )

            p.close()

            c.drawPath(
                p,
                fill=1,
                stroke=0
            )

            # -------------------------------------------------
            # FRONT PERSON — WHITE
            # -------------------------------------------------
            c.setFillColor(colors.white)

            # Head
            c.circle(
                cx - 1.7 * mm,
                cy + 2.3 * mm,
                1.35 * mm,
                stroke=0,
                fill=1
            )

            # Body
            p = c.beginPath()

            p.moveTo(
                cx - 4.4 * mm,
                cy - 3.0 * mm
            )

            p.curveTo(
                cx - 4.4 * mm,
                cy - 0.5 * mm,
                cx - 3.0 * mm,
                cy + 0.1 * mm,
                cx - 1.7 * mm,
                cy + 0.1 * mm
            )

            p.curveTo(
                cx - 0.4 * mm,
                cy + 0.1 * mm,
                cx + 1.0 * mm,
                cy - 0.5 * mm,
                cx + 1.0 * mm,
                cy - 3.0 * mm
            )

            p.close()

            c.drawPath(
                p,
                fill=1,
                stroke=0
            )
    
        c.setFillColor(dark)
        c.setFont(
            "Helvetica-Bold",
            11.5
        )
        c.drawString(
            x + 14 * mm,
            y,
            title.upper()
        )
        
        c.setStrokeColor(gold)
        c.setLineWidth(1.1)
        
        c.line(
            x + 12 * mm,
            y - 4.5 * mm,
            x + width,
            y - 4.5 * mm
        )
        
        # Fixed distance between section line and first content line
        SECTION_CONTENT_GAP = 7 * mm
        
        return y - 4.5 * mm - SECTION_CONTENT_GAP

        # =========================================================
    # HELPER: SIDEBAR SECTION TITLE
    # =========================================================
    def sidebar_section(title, x, y, width):

        # Sidebar icon
        icon_kind = {
            "contact": "person",
            "skills": "skills",
            "languages": "globe",
            "interests": "heart"
        }.get(title.lower())

        # Draw small gold icon
        if icon_kind:
            c.saveState()

            c.setStrokeColor(gold)
            c.setFillColor(gold)
            c.setLineWidth(1.1)
            
            cx = x + 3.5 * mm
            cy = y + 0.5 * mm

        # PERSON
        if icon_kind == "person":
            c.circle(
                cx,
                cy + 1.8 * mm,
                1.4 * mm,
                stroke=1,
                fill=0
            )
            c.arc(
                cx - 3.0 * mm,
                cy - 3.0 * mm,
                cx + 3.0 * mm,
                cy + 2.0 * mm,
                0,
                180
            )
           
        # phone
        elif icon_kind == "phone":
            c.setLineWidth(1.5)

            p = c.beginPath()
            p.moveTo(cx - 2.8*mm, cy + 2.8*mm)
            p.curveTo(
                cx - 3.5*mm, cy + 1.0*mm,
                cx - 1.5*mm, cy - 2.0*mm,
                cx + 1.8*mm, cy - 3.0*mm
            )
            p.curveTo(
                cx + 2.8*mm, cy - 3.3*mm,
                cx + 3.5*mm, cy - 2.2*mm,
                cx + 3.0*mm, cy - 1.2*mm
            
            )
            c.drawPath(p, fill=0, stroke=1)


        # email
        elif icon_kind == "email":
            c.setLineWidth(1.2)

            c.roundRect(
                cx - 3.8*mm,
                cy - 2.7*mm,
                7.6*mm,
                5.4*mm,
                0.8*mm,
                fill=0,
                stroke=1
            )

            c.line(
                cx - 3.5*mm,
                cy + 2.3*mm,
                cx,
                cy - 0.2*mm
            )

            c.line(
                cx,
                cy - 0.2*mm,
                cx + 3.5*mm,
                cy + 2.3*mm
            )


        # location
        elif icon_kind == "location":
            c.setLineWidth(1.2)

            c.circle(
                cx,
                cy + 1.2*mm,
                2.0*mm,
                fill=0,
                stroke=1
            )

            p = c.beginPath()
            p.moveTo(cx - 3.2*mm, cy + 1.0*mm)
            p.curveTo(
                cx - 3.2*mm, cy - 1.8*mm,
                cx,
                cy - 4.0*mm,
                cx,
                cy - 4.0*mm
            )
            p.curveTo(
                cx,
                cy - 4.0*mm,
                cx + 3.2*mm,
                cy - 1.8*mm,
                cx + 3.2*mm,
                cy + 1.0*mm
            )
            c.drawPath(p, fill=0, stroke=1)


        # LinkedIn
        elif icon_kind == "linkedin":
            c.setFont("Helvetica-Bold", 6.5)
            c.drawCentredString(
                cx,
                cy - 2.2*mm,
                "in"
            )


        # website
        elif icon_kind == "website":
            c.circle(
                cx,
                cy,
                3.5*mm,
                fill=0,
                stroke=1
            )

            c.ellipse(
                cx - 1.7*mm,
                cy - 3.5*mm,
                cx + 1.7*mm,
                cy + 3.5*mm,
                fill=0,
                stroke=1
            )

            c.line(
                cx - 3.5*mm,
                cy,
                cx + 3.5*mm,
                cy
            )

        # SKILLS / GEAR
        elif icon_kind == "skills":
            c.circle(
                cx,
                cy,
                2.0 * mm,
                stroke=1,
                fill=0
            )
            
            import math
            
            for angle in range(0, 360, 45):
                rad = math.radians(angle)

                x1 = cx + math.cos(rad) * 2.5 * mm
                y1 = cy + math.sin(rad) * 2.5 * mm

                x2 = cx + math.cos(rad) * 3.5 * mm
                y2 = cy + math.sin(rad) * 3.5 * mm

                c.line(x1, y1, x2, y2)
                
        
        # LANGUAGES / GLOBE
        elif icon_kind == "globe":
            c.circle(
                cx,
                cy,
                3.0 * mm,
                stroke=1,
                fill=0
            )

            c.ellipse(
                cx - 1.5 * mm,
                cy - 3.0 * mm,
                cx + 1.5 * mm,
                cy + 3.0 * mm,
                stroke=1,
                fill=0
            )

            c.line(
                cx - 3.0 * mm,
                cy,
                cx + 3.0 * mm,
                cy
            )

        # INTERESTS / HEART
        elif icon_kind == "heart":
            p = c.beginPath()

            p.moveTo(
                cx,
                cy - 3.0 * mm
            )

            p.curveTo(
                cx - 5.0 * mm,
                cy + 0.5 * mm,
                cx - 2.8 * mm,
                cy + 3.0 * mm,
                cx,
                cy + 1.2 * mm
            )

            p.curveTo(
                cx + 2.8 * mm,
                cy + 3.0 * mm,
                cx + 5.0 * mm,
                cy + 0.5 * mm,
                cx,
                cy - 3.0 * mm
            )

            p.close()

            c.drawPath(
                p,
                fill=1,
                stroke=0
            )
            
        c.restoreState()

        # Section title
        c.setFillColor(gold)
        c.setFont(
            "Helvetica-Bold",
            10.5
        )

        title_x = x + 8 * mm

        c.drawString(
            title_x,
            y,
            title.upper()
        )

        # Section line
        c.setStrokeColor(gold)
        c.setLineWidth(1)

        c.line(
            title_x,
            y - 2.2 * mm,
            x + width,
            y - 2.2 * mm
        )

        return y - 9 * mm


    # =========================================================
    # SIDEBAR CONTENT
    # =========================================================
    sx = 10 * mm
    sw = sidebar_w - 20 * mm
    sy = H - 78 * mm

    # CONTACT
    sy = sidebar_section(
        "Contact",
        sx,
        sy,
        sw
    )

    contact_items = [
    ("phone", data.get("phone")),
    ("email", data.get("email")),
    ("location", data.get("location")),
    ("linkedin", data.get("linkedin")),
    ("website", data.get("website"))
]

    for icon_kind, value in contact_items:

        if value:

            # Contact text
            sy = draw_lines(
                value,
                sx + 2 * mm,
                sy,
                sw - 2 * mm,
                size=8.2,
                leading=4.8 * mm,
                color=white
            )
            
    sy -= 2.0 * mm


    # =========================================================
    # SKILLS
    # =========================================================
    if data.get("skills"):

        sy -= 8 * mm

        sy = sidebar_section(
            "Skills",
            sx,
            sy,
            sw
        )

        skills = [
            item.strip()
            for item in data.get("skills", "").split(",")
            if item.strip()
        ]

        for skill in skills:

            sy = draw_lines(
                skill,
                sx,
                sy,
                sw,
                size=9,
                leading=5 * mm,
                color=white,
                bullet=True
            )

            sy -= 0.5 * mm


    # =========================================================
    # LANGUAGES
    # =========================================================
    if data.get("languages"):

        sy -= 8 * mm

        sy = sidebar_section(
            "Languages",
            sx,
            sy,
            sw
        )

        for row in data.get("languages", "").splitlines():

            row = row.strip()

            if row:

                sy = draw_lines(
                    row,
                    sx,
                    sy,
                    sw,
                    size=9,
                    leading=5 * mm,
                    color=white,
                    bullet=True
                )


    # =========================================================
    # INTERESTS
    # =========================================================
    if data.get("hobbies"):

        sy -= 8 * mm

        sy = sidebar_section(
            "Interests",
            sx,
            sy,
            sw
        )

        interests = [
            item.strip()
            for item in data.get("hobbies", "").split(",")
            if item.strip()
        ]

        for item in interests:

            sy = draw_lines(
                item,
                sx,
                sy,
                sw,
                size=9,
                leading=5 * mm,
                color=white,
                bullet=True
            )


    # =========================================================
    # NAME
    # =========================================================
    name = (data.get("name") or "My CV").upper()

    name_size = 32

    while (
        name_size > 17
        and stringWidth(
            name[:45],
            "Helvetica-Bold",
            name_size
        ) > main_w
    ):
        name_size -= 1

    c.setFillColor(dark)
    c.setFont(
        "Helvetica-Bold",
        name_size
    )

    c.drawString(
        main_x,
        H - 23 * mm,
        name[:45]
    )


    # =========================================================
    # PROFESSIONAL TITLE
    # =========================================================
    title = data.get("title") or ""

    if title:

        c.setFillColor(gold)
        c.setFont(
            "Helvetica-Bold",
            16
        )

        c.drawString(
            main_x,
            H - 33 * mm,
            title[:70].upper()
        )


    # =========================================================
    # MAIN CONTENT
    # =========================================================
    y = H - 43 * mm


    # =========================================================
    # SUMMARY
    # =========================================================
    if data.get("summary"):

        y = draw_lines(
            data["summary"],
            main_x,
            y,
            main_w,
            size=9.5,
            leading=4.8 * mm,
            color=muted
        )

        y -= 7 * mm
        # =========================================================
        # LIMITATIONS
        # =========================================================
        if data.get("limitations"):
            y = main_section(
                "Limitations",
                main_x,
                y,
                main_w
            )

            y = draw_lines(
                data["limitations"],
                main_x,
                y,
                main_w,
                size=8.8,
                leading=5.0 * mm,
                color=muted
            )
            
            y -= 5 * mm


        # =========================================================
    # EXPERIENCE
    # =========================================================
    if data.get("experience"):

        y = main_section(
            "Experience",
            main_x,
            y,
            main_w
        )

        experience_text = data.get(
            "experience",
            ""
        ).strip()

        # Split the experience into lines
        experience_lines = [
            line.strip()
            for line in experience_text.splitlines()
            if line.strip()
        ]

        current_job = False

        for line in experience_lines:

            # -------------------------------------------------
            # A line containing "|" is treated as a job header
            # Example:
            # Digital Marketing Specialist |
            # BrightWave Media | New York, NY | 2022 - Present
            # -------------------------------------------------
            if line.count("|") >= 2:

                parts = [
                    item.strip()
                    for item in line.split("|")
                    if item.strip()
                ]

                job = (
                    parts[0]
                    if parts
                    else ""
                )

                meta = " • ".join(
                    parts[1:]
                )

                # Add separation before a new job
                if current_job:
                    y -= 4 * mm

                # Job title
                if job:

                    c.setFillColor(dark)
                    c.setFont(
                        "Helvetica-Bold",
                        10.2
                    )

                    c.drawString(
                        main_x,
                        y,
                        job[:85]
                    )

                    y -= 4.5 * mm

                # Company / location / dates
                if meta:

                    c.setFillColor(gold)
                    c.setFont(
                        "Helvetica-Oblique",
                        8.5
                    )

                    c.drawString(
                        main_x,
                        y,
                        meta[:115]
                    )

                    y -= 5 * mm

                current_job = True

            # -------------------------------------------------
            # Bullet / responsibility
            # -------------------------------------------------
            else:

                description = line

                # Remove an existing bullet so CVForge
                # creates a consistent bullet itself
                if description.startswith("•"):
                    description = description[1:].strip()

                y = draw_lines(
                    description,
                    main_x + 3 * mm,
                    y,
                    main_w - 3 * mm,
                    size=8.8,
                    leading=5.2 * mm,
                    color=muted,
                    bullet=True
                )

                y -= 1 * mm

        # Space after the complete Experience section
        y -= 5 * mm


    # =========================================================
    # EDUCATION
    # =========================================================
    if data.get("education"):

        y = main_section(
            "Education",
            main_x,
            y,
            main_w
        )

        for row in data["education"].splitlines():

            row = row.strip()

            if not row:
                continue

            parts = [
                item.strip()
                for item in row.split("|")
            ]

            degree = (
                parts[0]
                if parts
                else row
            )

            c.setFillColor(dark)
            c.setFont(
                "Helvetica-Bold",
                9.6
            )

            c.drawString(
                main_x,
                y,
                degree[:90]
            )

            y -= 4.3 * mm

            if len(parts) > 1:

                c.setFillColor(muted)
                c.setFont(
                    "Helvetica",
                    8.5
                )

                c.drawString(
                    main_x,
                    y,
                    " • ".join(parts[1:])[:115]
                )

                y -= 5.2 * mm

        # SPACE BETWEEN SECTIONS
    y -= 4 * mm


    # =========================================================
    # CERTIFICATES
    # =========================================================
    if data.get("certificates"):

        y = main_section(
            "Certificates",
            main_x,
            y,
            main_w
        )

        for row in data["certificates"].splitlines():

            row = row.strip()

            if row:

                y = draw_lines(
                    row,
                    main_x,
                    y,
                    main_w,
                    size=8.8,
                    leading=4.5 * mm,
                    color=muted,
                    bullet=True
                )

        # SPACE BETWEEN SECTIONS
    y -= 3 * mm


    # =========================================================
    # REFERENCES
    # =========================================================
    if data.get("references"):

        y = main_section(
            "References",
            main_x,
            y,
            main_w
        )

        for row in data["references"].splitlines():

            row = row.strip()

            if row:

                y = draw_lines(
                    row,
                    main_x,
                    y,
                    main_w,
                    size=8.4,
                    leading=4.4 * mm,
                    color=muted
                )

        y -= 3 * mm


    # Safe Signature Handling (Windows Friendly & Clean File Lock Management)
    signature = data.get("signature")

    if signature and getattr(signature, "filename", None):
        signature_temp_path = None
        try:
            signature.seek(0)
            signature_image = Image.open(signature)
            
            if signature_image.mode not in ("RGB", "RGBA"):
                signature_image = signature_image.convert("RGBA")

    # Create temporary file safely
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        signature_temp_path = temp_file.name
        temp_file.close()  # Close handle immediately so PIL & ReportLab can access it without file lock errors

        signature_image.save(signature_temp_path, format="PNG")

        signature_width = 45 * mm
        signature_height = 18 * mm
        img_width, img_height = signature_image.size

        if img_width > 0 and img_height > 0:
            ratio = min(signature_width / img_width, signature_height / img_height)
            draw_width = img_width * ratio
            draw_height = img_height * ratio

            c.drawImage(
                signature_temp_path,
                main_x,
                y - draw_height - 3 * mm,
                width=draw_width,
                height=draw_height,
                preserveAspectRatio=True,
                mask="auto"
            )
    except Exception as e:
        print(f"Signature rendering error: {e}")
    finally:
    # Guarantee cleanup of temporary signature file
        if signature_temp_path and os.path.exists(signature_temp_path):
            try:
                os.unlink(signature_temp_path)
            except OSError:
                pass



    # SAVE MODERN PDF
    c.save()   


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

    template = clean(
        data.get("template")
    ).lower()

    # Modern creates and saves its own canvas
    if template == "modern":
        modern(data, filename)
        return

    # Classic and ATS use this canvas
    c = canvas.Canvas(
        filename,
        pagesize=A4
    )

    if template == "classic":

        generate_classic(
            c,
            data
        )

    elif template == "ats":

        generate_ats(
            c,
            data
        )

    else:

        # Default to Modern
        modern(data, filename)
        return

    c.save()

@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/generate", methods=["POST"])
def generate():
    photo = request.files.get("photo")
    signature = request.files.get("signature")
    # =========================================================
    # SERVER-SIDE INPUT LIMITS
    # Browser limits can be bypassed, so enforce them here too.
    # =========================================================

    def form_limit(name, maximum):
        value = request.form.get(name, "")
        return value[:maximum]
    limitations = request.form.get("limitations", "").strip()
   
    data = {
    "name": form_limit("name", 100),
    "title": form_limit("title", 70),
    "phone": form_limit("phone", 50),
    "email": form_limit("email", 100),
    "location": form_limit("location", 100),
    "linkedin": form_limit("linkedin", 200),
    "website": form_limit("website", 200),
    "summary": form_limit("summary", 500),
    "limitations": form_limit("limitations", 300),
    "experience": form_limit("experience", 1200),
    "education": form_limit("education", 600),
    "skills": form_limit("skills", 400),
    "certificates": form_limit("certificates", 500),
    "languages": form_limit("languages", 250),
    "hobbies": form_limit("hobbies", 250),
    "references": form_limit("references", 500),
    "signature": signature,
    "template": request.form.get("template", "modern"),
    "accent_color": request.form.get("accent_color"),
    "sidebar_color": request.form.get(
        "sidebar_color",
        "#173F49"
    ),
}

    

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
        "CVForge_" + uuid.uuid4().hex + ".pdf"
    )

    generate_pdf(data, filename)
    print("PDF PATH:", filename)
    print("PDF EXISTS:", os.path.exists(filename))
    
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
