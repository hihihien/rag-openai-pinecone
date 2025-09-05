import fitz
import re
import json
from pathlib import Path

# === Paths ===
PDF_PATH = Path("backend/data/MHB_Alle_Studiengaenge/MHB_BDAISY_PO21/Modulhandbuch_DAISY_V6-3_final.pdf")
OUT_PATH = PDF_PATH.with_name("DAISY_MHB_chunks.jsonl")

# === Patterns ===
module_line_re = re.compile(r"^(D\d+(?:\.\d+)*|PF\s?\d+(?:\.\d+)*):?\s+(.+)")
section_heading_re = re.compile(r"^(Pflichtfächer \d\. Semester|Vertiefung .+|PF\d .+|Abschlusssemester.*)", re.IGNORECASE)
major_heading_re = re.compile(r"^(Basissemester.*|Vertiefungsbereich|Professionelle Fokusbereiche|Abschlusssemester.*)", re.IGNORECASE)

# === Section map (loaded as state during scan)
current_major = None
current_sub = None

# === Extraction state
doc = fitz.open(str(PDF_PATH))
chunks = []
buffer = []
current_module = None
pdf_page_start = None
page_num = 0

def flush_module():
    global current_module, buffer, pdf_page_start, page_num
    if current_module and buffer:
        chunks.append({
            "id": f"DAISY_MHB_{current_module['module_id'].replace('.', '_').replace(' ', '_')}",
            "module_id": current_module["module_id"],
            "major_section": current_module["major_section"],
            "sub_section": current_module["sub_section"],            
            "title": current_module["title"],
            "text": "\n".join(buffer).strip(),
            "pdf_page_start": pdf_page_start,
            "pdf_page_end": page_num
        })
    current_module = None
    buffer.clear()

# === Main loop ===
for page in doc:
    page_num += 1
    lines = page.get_text().splitlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Match major sections
        if major_heading_re.match(line):
            current_major = line
            current_sub = None
            continue

        # Match sub-sections
        if section_heading_re.match(line):
            current_sub = line
            continue

        # Match module line
        module_match = module_line_re.match(line)
        if module_match:
            flush_module()
            pdf_page_start = page_num
            current_module = {
                "module_id": module_match.group(1).strip(),
                "title": module_match.group(2).strip(),
                "major_section": current_major or "Unbekannt",
                "sub_section": current_sub or "Unbekannt"
            }
            buffer = [line]
        elif current_module:
            buffer.append(line)

# Final flush
flush_module()

# Save
with OUT_PATH.open("w", encoding="utf-8") as f:
    for chunk in chunks:
        f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

print(f"Extracted {len(chunks)} modules to {OUT_PATH}")