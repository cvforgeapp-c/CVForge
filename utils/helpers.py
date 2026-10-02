import re
from flask import jsonify

def format_response(data=None, message="Success", status_code=200):
    """Generates standardized JSON success response."""
    payload = {"status": "success", "message": message}
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status_code

def format_error(error_message="An error occurred", status_code=400):
    """Generates standardized JSON error response."""
    return jsonify({"status": "error", "error": error_message}), status_code

def clean_text(text: str) -> str:
    """Removes unwanted non-printable characters and extra whitespace from extracted text."""
    if not text:
        return ""
    cleaned = re.sub(r'[\r\t]', ' ', text)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()
