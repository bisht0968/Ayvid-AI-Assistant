import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}

def scrape_page(url: str, max_chars: int = 1500) -> str:
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove noise
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        # Collapse whitespace
        text = " ".join(text.split())
        return text[:max_chars]
    except Exception as e:
        return f"[Could not scrape: {e}]"


def get_web_context(search_results: list) -> list:
    context = []
    for result in search_results:
        scraped = scrape_page(result["url"])
        context.append({
            "title": result["title"],
            "url": result["url"],
            "content": scraped
        })
    return context