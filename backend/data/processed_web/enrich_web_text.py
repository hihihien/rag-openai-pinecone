import json
from pathlib import Path

# Folder where your web JSON files are stored
WEB_DIR = Path("backend/data/processed_web")
OUT_DIR = WEB_DIR / "enriched"
OUT_DIR.mkdir(exist_ok=True)

for file in WEB_DIR.glob("*.json"):
    with file.open("r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[skip] {file.name}: JSON decode error → {e}")
            continue

    # Some of your files might have a list of records instead of one dict
    records = data if isinstance(data, list) else [data]
    enriched = []

    for rec in records:
        meta = rec.get("metadata", {})
        text = rec.get("text", "").strip()

        # Collect additional info
        section = meta.get("section", "")
        source = meta.get("source", "")
        links = meta.get("links", [])

        # Add section info (if available)
        if section:
            text += f"\n\nAbschnitt: {section}"

        # Add link info in readable form
        if links:
            text += "\n\nLinks:"
            for link in links:
                link_text = link.get("text", "").strip()
                link_url = link.get("url", "").strip()
                if link_text and link_url:
                    text += f'\n- {link_text}: {link_url}'

        # Add the general source URL
        if source:
            text += f"\n\nWeitere Informationen: {source}"

        rec["text"] = text.strip()
        enriched.append(rec)

    out_path = OUT_DIR / file.name
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)

    print(f" Enriched {len(enriched)} records → {out_path.name}")
