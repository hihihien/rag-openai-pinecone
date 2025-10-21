import os
import json
import uuid
from bs4 import BeautifulSoup

# === Configuration ===
HTML_PATH = os.path.join("data", "raw_html", "fbm_home.html")
SAVE_DIR = os.path.join("data", "processed_web")
OUTPUT_FILE = "fbm_home.jsonl"
SOURCE_URL = "https://medien.hs-duesseldorf.de/"

os.makedirs(SAVE_DIR, exist_ok=True)

def extract_links(element):
    """Extract all <a> links from a section."""
    links = []
    for a in element.find_all("a", href=True):
        href = a["href"].strip()
        if href and not href.startswith("#"):
            links.append({"text": a.get_text(strip=True), "url": href})
    return links

def parse_html_to_records(html_path):
    """Parse HTML into structured records based on headings and paragraphs."""
    html = open(html_path, "r", encoding="utf-8").read()
    soup = BeautifulSoup(html, "html.parser")
    records = []

    for header in soup.find_all(["h1", "h2", "h3"]):
        section_title = header.get_text(" ", strip=True)
        paragraphs, links = [], []

        # Collect following siblings until next heading
        for sib in header.find_next_siblings():
            if sib.name in ["h1", "h2", "h3"]:
                break
            if sib.name in ["p", "li"]:
                text = sib.get_text(" ", strip=True)
                if text:
                    paragraphs.append(text)
                links.extend(extract_links(sib))

        if not paragraphs:
            continue

        record = {
            "id": f"fbm_{uuid.uuid4().hex[:8]}",
            "text": " ".join(paragraphs),
            "metadata": {
                "category": "fbm_general",
                "section": section_title,
                "links": links,
                "source": SOURCE_URL
            },
        }
        records.append(record)

    # Fallback if no headings found
    if not records:
        main = soup.find("main") or soup.find("body")
        if main:
            text = " ".join([p.get_text(" ", strip=True) for p in main.find_all("p")])
            if text.strip():
                records.append({
                    "id": f"fbm_{uuid.uuid4().hex[:8]}",
                    "text": text,
                    "metadata": {"category": "fbm_general", "section": "Hauptinhalt", "source": SOURCE_URL}
                })

    return records

def save_jsonl(records, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Saved {len(records)} records to {output_path}")

def main():
    records = parse_html_to_records(HTML_PATH)
    output_path = os.path.join(SAVE_DIR, OUTPUT_FILE)
    save_jsonl(records, output_path)

if __name__ == "__main__":
    main()