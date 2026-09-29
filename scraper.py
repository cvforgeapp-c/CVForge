import re
import urllib.request
from bs4 import BeautifulSoup

def scrape_job_url(job_url: str, timeout: int = 6) -> str:
    if not job_url or not job_url.startswith(("http://", "https://")):
        return ""

    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        ),
        'Accept-Language': 'en-US,en;q=0.9',
    }

    try:
        req = urllib.request.Request(job_url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            html = response.read().decode('utf-8', errors='ignore')

        try:
            soup = BeautifulSoup(html, 'html.parser')
            for element in soup(["script", "style", "nav", "footer", "header", "form"]):
                element.decompose()
            text = soup.get_text(separator=' ')
        except Exception:
            text = re.sub(r'<[^>]+>', ' ', html)

        cleaned_text = ' '.join(text.split())
        return cleaned_text[:5000]

    except Exception as e:
        print(f"[Scraper Error] Failed to fetch {job_url}: {str(e)}")
        return ""
