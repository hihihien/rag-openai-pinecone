# Extract structured MHB chunks from all MHB PDFs by module section

import fitz
import re
import json
from pathlib import Path

RAW_DIR = Path("backend/data/MHB_Alle_Studiengaenge")
OUT_PATH = Path(__file__).parent.parent / "data/pdf_chunks/mhb_pdf_chunks.jsonl"
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

modul_pattern = re.compile(r"^(\w{3})\s?(\d{2}(?:\.\d{2})?)\s-\s(.+)")

section_headers = {
    "responsible": "Verantwortlich",
    "contents": "Inhalte",
    "objectives": "Lernziele",
    "assessment": "Prüfungsform",
    "teaching_method": "Lehrform",
    "language": "Sprache"
}

def extract_sections(text: str) -> dict:
    result = {}
    pattern = re.compile(r"(?P<header>(%s)):\s*(.*?)\s*(?=(?:%s):|\Z)" % (
        "|".join(section_headers.values()), "|".join(section_headers.values())), re.DOTALL)
    for match in pattern.finditer(text):
        header = match.group("header")
        key = next(k for k, v in section_headers.items() if v == header)
        result[key] = match.group(0).strip()
    return result

chunks = []

print("[chunker] Scanning for MHB PDFs...")
mhb_files = list(RAW_DIR.glob("**/*MHB*PO*.pdf"))

for path in mhb_files:
    folder = path.parent.name
    match = re.match(r"MHB_(\w+)_PO(\d{2})", folder)
    if not match:
        print(f"[WARN] Skipping folder: {folder}")
        continue

    abbrev, po = match.groups()
    namespace = f"{abbrev}_pdf"
    print(f"[parse] {path.name} → {abbrev}, PO{po}, ns={namespace}")

    doc = fitz.open(str(path))
    current = None
    buffer = []
    page_num = 0

    for page in doc:
        page_num += 1
        lines = page.get_text().splitlines()

        for line in lines:
            m = modul_pattern.match(line.strip())
            if m:
                if current:
                    full = "\n".join(buffer)
                    sections = extract_sections(full)
                    for sec, val in sections.items():
                        if len(val.strip()) < 30:
                            continue
                        chunks.append({
                            "id": f"{current['id']}__{sec}",
                            "namespace": namespace,
                            "text": val.strip(),
                            "metadata": {
                                "studyProgramAbbrev": abbrev,
                                "module_id": current['id'],
                                "module_name": current['title'],
                                "section": sec,
                                "pdf_page_start": current['page'],
                                "pdf_page_end": page_num,
                                "source_type": "mhb_pdf",
                                "source_file": path.name
                            }
                        })
                    buffer = []

                current = {
                    "id": f"{m.group(1)}-{m.group(2)}",
                    "title": m.group(3).strip(),
                    "page": page_num
                }
            if current:
                buffer.append(line.strip())

    if current and buffer:
        full = "\n".join(buffer)
        sections = extract_sections(full)
        for sec, val in sections.items():
            if len(val.strip()) < 30:
                continue
            chunks.append({
                "id": f"{current['id']}__{sec}",
                "namespace": namespace,
                "text": val.strip(),
                "metadata": {
                    "studyProgramAbbrev": abbrev,
                    "module_id": current['id'],
                    "module_name": current['title'],
                    "section": sec,
                    "pdf_page_start": current['page'],
                    "pdf_page_end": page_num,
                    "source_type": "mhb_pdf",
                    "source_file": path.name
                }
            })
print(f"[chunker] Extracted {len(chunks)} chunks from {len(mhb_files)} MHB PDFs")

# Save .jsonl (for embedding)
with open(OUT_PATH, "w", encoding="utf-8") as f:
    for c in chunks:
        f.write(json.dumps(c, ensure_ascii=False) + "\n")

# Save .json (for readability/debug)
with open(OUT_PATH.with_suffix(".json"), "w", encoding="utf-8") as f:
    json.dump(chunks, f, indent=2, ensure_ascii=False)

print(f"[chunker] Saved chunks to {OUT_PATH} and {OUT_PATH.with_suffix('.json')}")