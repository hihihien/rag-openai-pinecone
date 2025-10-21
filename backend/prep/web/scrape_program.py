# backend/prep/web/scrape_program.py

import os
from prep.web.scrape_utils import fetch_html, clean_html, save_html
from prep.web.urls import URLS

SAVE_BASE = os.path.join("data", "raw_html")

def scrape_program(program: str):
    """Scrape all pages for a given study program (defined in urls.py)."""
    if program not in URLS:
        raise ValueError(f"Program '{program}' not found in urls.py")

    program_urls = URLS[program]
    if isinstance(program_urls, str):
        program_urls = {"main": program_urls}

    save_dir = os.path.join(SAVE_BASE, program.lower())
    os.makedirs(save_dir, exist_ok=True)

    for page_name, url in program_urls.items():
        print(f"Scraping {program.upper()} → {page_name}")
        try:
            soup = fetch_html(url)
            soup = clean_html(soup)
            save_html(soup, os.path.join(save_dir, f"{program.lower()}_{page_name}.html"))
        except Exception as e:
            print(f" Failed to scrape {url}: {e}")

if __name__ == "__main__":
    scrape_program("btb")