# utils.py - Helper utilities for text cleaning, file validation, and API formatting
import re

def sanitize_text(text: str) -> str:
    """Removes non-printable characters and extra whitespace from extracted PDF or scraped text."""
    if not text:
        return ""
    # Strip unnecessary blank lines and multi-spaces
    cleaned = re.sub(r'\r\n|\r|\n', '\n', text)
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    cleaned = re.sub(r'\n+', '\n', cleaned)
    return cleaned.strip()

def allowed_file(filename: str, allowed_extensions: set = {"pdf"}) -> bool:
    """Validates uploaded file extensions safely."""
    return bool(filename and '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions)

def format_api_response(status: str, data: dict = None, message: str = "", code: int = 200):
    """Standardizes JSON response shapes across Flask routes."""
    payload = {"status": status}
    if data is not None:
        payload["data"] = data
    if message:
        payload["message"] = message
    return payload, code
