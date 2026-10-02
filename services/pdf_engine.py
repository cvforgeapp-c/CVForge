import fitz  # PyMuPDF

def generate_ats_pdf(data: dict, output_path: str, watermarked: bool = True):
    """Renders clean single-column ATS compliant PDF using PyMuPDF."""
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)  # Letter size
    margin = 36
    y = margin

    # Colors
    PRIMARY_COLOR = (15/255, 41/255, 66/255)
    SECONDARY_COLOR = (59/255, 122/255, 158/255)
    TEXT_COLOR = (45/255, 55/255, 72/255)

    # 1. Header Section
    name = data.get("candidate_name", "CANDIDATE NAME").upper()
    page.insert_text(fitz.Point(margin, y + 16), name, fontsize=18, fontname="helv-bold", color=PRIMARY_COLOR)
    y += 24

    title = data.get("target_title", "Professional Title")
    page.insert_text(fitz.Point(margin, y + 10), title, fontsize=11, fontname="helv-bold", color=SECONDARY_COLOR)
    y += 18

    contact = f"{data.get('phone', '')} | {data.get('email', '')} | {data.get('location', '')}"
    page.insert_text(fitz.Point(margin, y + 8), contact, fontsize=8.5, fontname="helv", color=TEXT_COLOR)
    y += 20

    # Separator Line
    page.draw_line(fitz.Point(margin, y), fitz.Point(612 - margin, y), color=SECONDARY_COLOR, width=0.8)
    y += 15

    # 2. Professional Summary
    page.insert_text(fitz.Point(margin, y + 10), "PROFESSIONAL SUMMARY", fontsize=10, fontname="helv-bold", color=PRIMARY_COLOR)
    y += 16
    summary = data.get("summary", "")
    rc = page.insert_textbox(fitz.Rect(margin, y, 612 - margin, y + 60), summary, fontsize=9, fontname="helv", color=TEXT_COLOR)
    y += rc + 15

    # 3. Work Experience
    page.insert_text(fitz.Point(margin, y + 10), "PROFESSIONAL EXPERIENCE", fontsize=10, fontname="helv-bold", color=PRIMARY_COLOR)
    y += 18

    for exp in data.get("experiences", []):
        header_line = f"{exp.get('role')} — {exp.get('company')} ({exp.get('dates')})"
        page.insert_text(fitz.Point(margin, y + 8), header_line, fontsize=9.5, fontname="helv-bold", color=TEXT_COLOR)
        y += 14

        for bullet in exp.get("bullets", []):
            bullet_text = f"•  {bullet}"
            rc = page.insert_textbox(fitz.Rect(margin + 10, y, 612 - margin, y + 40), bullet_text, fontsize=8.5, fontname="helv", color=TEXT_COLOR)
            y += rc + 4
        y += 8

    # 4. Optional Watermark Layer
    if watermarked:
        for p in doc:
            p.insert_text(
                fitz.Point(150, 400),
                "CVforge.co",
                fontsize=55,
                fontname="helv-bold",
                color=(0.8, 0.8, 0.8),
                morph=(fitz.Point(150, 400), fitz.Matrix(45))  # Diagonal matrix
            )

    doc.save(output_path)
    doc.close()
