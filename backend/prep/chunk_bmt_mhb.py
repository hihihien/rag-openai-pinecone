# Extract full per-module chunks from BMT_MHB_PO2025_V1.0.pdf

import fitz  # PyMuPDF
import re
import json
from pathlib import Path

PDF_PATH = Path("backend/data/MHB_Alle_Studiengaenge/MHB_BMT_PO25/BMT_MHB_PO2025_V1.0.pdf")
OUT_BASE = PDF_PATH.with_name("BMT_MHB_PO2025_chunks")

MODULE_PATTERN = re.compile(r"^(BMT[\s\dF_\.]+)\s?[–-]\s?(.+)")  # Allow broader matches for submodules by catching header section syntaxs

print(f"[chunker] Reading: {PDF_PATH.name}")
doc = fitz.open(str(PDF_PATH))

chunks = []
current = None
buffer = []
page_num = 0

for page in doc:
    page_num += 1
    lines = page.get_text().splitlines()

    for line in lines:
        line = line.strip()
        match = MODULE_PATTERN.match(line)
        if match:
            if current:
                chunks.append({
                    "id": current["module_id"],
                    "namespace": "BMT_pdf",
                    "text": "\n".join(buffer).strip(),
                    "metadata": {
                        "module_id": current["module_id"],
                        "module_name": current["module_name"],
                        "studyProgramAbbrev": "BMT",
                        "source_file": PDF_PATH.name,
                        "pdf_page_start": current["start_page"],
                        "pdf_page_end": page_num - 1
                    }
                })
                buffer = []

            current = {
                "module_id": match.group(1).replace(" ", ""),
                "module_name": match.group(2).strip(),
                "start_page": page_num
            }

        if current:
            buffer.append(line)

# Add final module
if current and buffer:
    chunks.append({
        "id": current["module_id"],
        "namespace": "BMT_pdf",
        "text": "\n".join(buffer).strip(),
        "metadata": {
            "module_id": current["module_id"],
            "module_name": current["module_name"],
            "studyProgramAbbrev": "BMT",
            "source_file": PDF_PATH.name,
            "pdf_page_start": current["start_page"],
            "pdf_page_end": page_num
        }
    })

# Write outputs
out_jsonl = OUT_BASE.with_suffix(".jsonl")
out_json = OUT_BASE.with_suffix(".json")

with out_jsonl.open("w", encoding="utf-8") as f:
    for chunk in chunks:
        f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

with out_json.open("w", encoding="utf-8") as f:
    json.dump(chunks, f, indent=2, ensure_ascii=False)

print(f"[chunker] Extracted {len(chunks)} chunks →")
print(f"          {out_jsonl.name} (for Pinecone)")
print(f"          {out_json.name} (for inspection)")