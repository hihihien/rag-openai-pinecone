import fitz
import re
import json
from pathlib import Path

# === File paths ===
PDF_PATH = Path("backend/data/MHB_Alle_Studiengaenge/MHB_BDAISY_PO21/PO21_796.pdf")
OUTPUT_PATH = Path("backend/data/processed")
OUT_BASE = OUTPUT_PATH.with_name("PO21_796_paragraph_chunks")

# === Patterns ===
SECTION_PATTERN = re.compile(r"^(I{1,3})\.\s+.+")
PARAGRAPH_HEADER_PATTERN = re.compile(r"^§\s?(\d+[a-zA-Z]?)\s+[–-]\s+(.+)")
SPLIT_PARAGRAPH_PATTERN = re.compile(r"^§\s?(\d+[a-zA-Z]?)$")
SUBPARA_PATTERN = re.compile(r"^\((\d+)\)\s+(.*)")

# === State ===
doc = fitz.open(str(PDF_PATH))
chunks = []
current_section = None
current_paragraph_number = None
current_paragraph_title = None
current_subpara_num = None
current_subpara_lines = []
unstructured_lines = []
paragraph_start_page = None
page_num = 0

def flush_subpara():
    global current_subpara_num, current_subpara_lines
    if current_paragraph_number and current_subpara_num and current_subpara_lines:
        chunks.append({
            "id": f"DAISY_PO21_paragraph_{current_paragraph_number}_{current_subpara_num}",
            "section": current_section,
            "paragraph": f"§ {current_paragraph_number} – {current_paragraph_title}",
            "subsection_number": current_subpara_num,
            "text": "\n".join(current_subpara_lines).strip(),
            "pdf_page_start": paragraph_start_page,
            "pdf_page_end": page_num
        })
        current_subpara_num = None
        current_subpara_lines = []

for page in doc:
    page_num += 1
    lines = page.get_text().splitlines()
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # Section header
        section_match = SECTION_PATTERN.match(line)
        if section_match:
            current_section = line
            i += 1
            continue

        # Full § header in one line
        para_match = PARAGRAPH_HEADER_PATTERN.match(line)
        if para_match:
            flush_subpara()

            # Flush previous unstructured block
            if current_paragraph_number and unstructured_lines:
                chunks.append({
                    "id": f"DAISY_PO21_paragraph_{current_paragraph_number}_0",
                    "section": current_section,
                    "paragraph": f"§ {current_paragraph_number} – {current_paragraph_title}",
                    "subsection_number": "0",
                    "text": "\n".join(unstructured_lines).strip(),
                    "pdf_page_start": paragraph_start_page,
                    "pdf_page_end": page_num
                })
                unstructured_lines = []

            current_paragraph_number = para_match.group(1)
            current_paragraph_title = para_match.group(2)
            paragraph_start_page = page_num
            unstructured_lines = []
            i += 1
            continue

        # Split § header across two lines
        split_para_match = SPLIT_PARAGRAPH_PATTERN.match(line)
        if split_para_match and i + 1 < len(lines):
            flush_subpara()

            if current_paragraph_number and unstructured_lines:
                chunks.append({
                    "id": f"DAISY_PO21_paragraph_{current_paragraph_number}_0",
                    "section": current_section,
                    "paragraph": f"§ {current_paragraph_number} – {current_paragraph_title}",
                    "subsection_number": "0",
                    "text": "\n".join(unstructured_lines).strip(),
                    "pdf_page_start": paragraph_start_page,
                    "pdf_page_end": page_num
                })
                unstructured_lines = []

            current_paragraph_number = split_para_match.group(1)
            i += 1
            current_paragraph_title = lines[i].strip()
            paragraph_start_page = page_num
            unstructured_lines = []
            i += 1
            continue

        # Subparagraph (1), (2), ...
        subpara_match = SUBPARA_PATTERN.match(line)
        if subpara_match:
            if current_paragraph_number:
                flush_subpara()
                current_subpara_num = subpara_match.group(1)
                current_subpara_lines = [line]
            i += 1
            continue

        # Append line to current subpara or to unstructured block
        if current_paragraph_number:
            if current_subpara_lines:
                current_subpara_lines.append(line)
            else:
                unstructured_lines.append(line)

        i += 1

# Final flushes
flush_subpara()

if current_paragraph_number and unstructured_lines:
    chunks.append({
        "id": f"DAISY_PO21_paragraph_{current_paragraph_number}_0",
        "section": current_section,
        "paragraph": f"§ {current_paragraph_number} – {current_paragraph_title}",
        "subsection_number": "0",
        "text": "\n".join(unstructured_lines).strip(),
        "pdf_page_start": paragraph_start_page,
        "pdf_page_end": page_num
    })

# === Save ===
out_json = OUT_BASE.with_suffix(".json")
out_jsonl = OUT_BASE.with_suffix(".jsonl")

with out_json.open("w", encoding="utf-8") as f:
    json.dump(chunks, f, indent=2, ensure_ascii=False)

with out_jsonl.open("w", encoding="utf-8") as f:
    for chunk in chunks:
        f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

print(f"[chunker] Extracted {len(chunks)} paragraph chunks")
print(f"  JSON : {out_json.name}")
print(f"  JSONL: {out_jsonl.name}")