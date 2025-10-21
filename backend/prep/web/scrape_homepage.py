import os
from prep.web.scrape_utils import fetch_html, clean_html, save_html
from prep.web.urls import URLS

SAVE_DIR = os.path.join("data", "raw_html")
FILENAME = "fbm_home.html"

def scrape_homepage():
    """Scrape the FBM homepage and save the cleaned HTML."""
    url = URLS["fbm_home"]
    soup = fetch_html(url)
    soup = clean_html(soup)
    save_html(soup, os.path.join(SAVE_DIR, FILENAME))

if __name__ == "__main__":
    try:
        scrape_homepage()
    except Exception as e:
        print(f"Error scraping homepage: {e}")