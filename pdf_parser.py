import pymupdf as fitz
from utils import sanitize_text

def extract_text_from_pdf_stream(file_stream: bytes) -> str:
    extracted_text = []
    try:
        doc = fitz.open(stream=file_stream, filetype="pdf")
        for page in doc:
            text = page.get_text("text")
            if text:
                extracted_text.append(text)
        doc.close()
        return "\n".join(extracted_text)
    except Exception as e:
        print(f"[PDF Parser Error]: {str(e)}")
        return ""
