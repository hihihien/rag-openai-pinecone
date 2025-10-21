import os
import requests
from bs4 import BeautifulSoup

def fetch_html(url: str, user_agent: str = "Mozilla/5.0 (compatible; HSD-FBM-Scraper/1.0)") -> BeautifulSoup:
    """Fetch HTML from a URL and return a BeautifulSoup object."""
    print(f"Fetching: {url}")
    headers = {"User-Agent": user_agent}
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")

def clean_html(soup: BeautifulSoup) -> BeautifulSoup:
    """Remove navigation, footer, and script/style tags to focus on content."""
    for tag in soup.select("header, footer, nav, script, style"):
        tag.decompose()
    return soup

def save_html(soup: BeautifulSoup, save_path: str):
    """Save prettified HTML to the given path."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(soup.prettify())
    print(f"Saved: {save_path}")