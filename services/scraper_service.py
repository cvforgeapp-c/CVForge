import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup
import re

def parse_resume_stream(file_stream, filename: str) -> dict:
    """Extracts raw text and metadata from uploaded resume stream (PDF/DOCX)."""
    text = ""
    if filename.endswith('.pdf'):
        doc = fitz.open(stream=file_stream.read(), filetype="pdf")
        for page in doc:
            text += page.get_text("text") + "\n"
    else:
        # Fallback text decoding for docx / txt
        text = file_stream.read().decode('utf-8', errors='ignore')

    return {"raw_text": text.strip()}

def scrape_job_posting(job_url: str) -> dict:
    """Safely scrapes target job posting description and details."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        response = requests.get(job_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()

        cleaned_text = ' '.join(soup.stripped_strings)
        title_match = soup.find('title')
        title = title_match.string.strip() if title_match else "Target Role"

        return {
            "title": title[:100],
            "description": cleaned_text[:5000],  # Constrain LLM context budget
            "url": job_url
        }
    except Exception as e:
        # Fallback parser logic
        return {
            "title": "Target Role",
            "description": f"Failed to auto-fetch page structure. Extracting plain terms from URL: {job_url}",
            "url": job_url
        }
