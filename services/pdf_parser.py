import fitz  # PyMuPDF
import re

def parse_resume_stream(file_stream, filename: str) -> dict:
    """
    Extracts raw text and metadata from uploaded resume stream (PDF or text/docx).
    """
    extracted_text = ""

    if filename.lower().endswith('.pdf'):
        # Read stream using PyMuPDF
        doc = fitz.open(stream=file_stream.read(), filetype="pdf")
        for page in doc:
            extracted_text += page.get_text("text") + "\n"
        doc.close()
    else:
        # Fallback UTF-8 reading for text files
        extracted_text = file_stream.read().decode('utf-8', errors='ignore')

    cleaned_text = extracted_text.strip()

    # Extract basic email & phone if present
    email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', cleaned_text)
    phone_match = re.search(r'\(?\+?[0-9]{1,3}\)?[-. ]?\(?[0-9]{1,4}\)?[-. ]?[0-9]{3,4}[-. ]?[0-9]{3,4}', cleaned_text)

    return {
        "raw_text": cleaned_text,
        "extracted_email": email_match.group(0) if email_match else "",
        "extracted_phone": phone_match.group(0) if phone_match else "",
        "char_count": len(cleaned_text)
    }
