# chunk_btb_mhb.py
# Extract full per-module chunks from BTB_MHB_PO2025_V1.0.pdf

import fitz  # PyMuPDF
import re
import json
from pathlib import Path

# File paths
PDF_PATH = Path("backend/data/MHB_Alle_Studiengaenge/MHB_BTB_PO25/BTB_MHB_PO2025_V1.0.pdf")
OUT_BASE = PDF_PATH.with_name("BTB_MHB_PO2025_chunks")

# Patterns for HSD and RSH
HSD_PATTERN = re.compile(r"^(BTB[\s\dF_\.W]+)\s?[–-]\s?(.+)$")  # e.g. BTB 10 - Mathematik 1
RSH_PATTERN = re.compile(
    r"^Studiengang Ton und Bild (?:– )?(Modul [\d\.\w]+|Wahlmodul|Schwerpunkt):?\s+(.+)$"
)  # e.g. Studiengang Ton und Bild – Schwerpunkt: Visual Music 1

print(f"[chunker] Reading: {PDF_PATH.name}")
doc = fitz.open(str(PDF_PATH))

# Initialization
chunks = []
current = None
buffer = []
page_num = 0
rsh_id_counter = {}  # for deduplicating RSH module IDs

# Main loop
for page in doc:
    page_num += 1
    lines = page.get_text().splitlines()

    for line in lines:
        line = line.strip()
        hsd_match = HSD_PATTERN.match(line)
        rsh_match = RSH_PATTERN.match(line)

        if hsd_match or rsh_match:
            # Save previous chunk
            if current:
                chunks.append({
                    "id": current["module_id"],
                    "namespace": "BTB_pdf",
                    "text": "\n".join(buffer).strip(),
                    "metadata": {
                        "module_id": current["module_id"],
                        "module_name": current["module_name"],
                        "studyProgramAbbrev": "BTB",
                        "source_file": PDF_PATH.name,
                        "pdf_page_start": current["start_page"],
                        "pdf_page_end": page_num - 1
                    }
                })
                buffer = []

            # Start new chunk
            if hsd_match:
                current = {
                    "module_id": hsd_match.group(1).replace(" ", ""),
                    "module_name": hsd_match.group(2).strip(),
                    "start_page": page_num
                }

            elif rsh_match:
                raw_id = rsh_match.group(1).replace(" ", "_").replace(".", "_")
                name_part = rsh_match.group(2).strip()
                base_id = f"RSH_{raw_id}"

                # Ensure uniqueness
                count = rsh_id_counter.get(base_id, 0) + 1
                rsh_id_counter[base_id] = count
                unique_id = f"{base_id}_{count}"

                current = {
                    "module_id": unique_id,
                    "module_name": name_part,
                    "start_page": page_num
                }

        # Accumulate lines
        if current:
            buffer.append(line)

# Save last chunk
if current and buffer:
    chunks.append({
        "id": current["module_id"],
        "namespace": "BTB_pdf",
        "text": "\n".join(buffer).strip(),
        "metadata": {
            "module_id": current["module_id"],
            "module_name": current["module_name"],
            "studyProgramAbbrev": "BTB",
            "source_file": PDF_PATH.name,
            "pdf_page_start": current["start_page"],
            "pdf_page_end": page_num
        }
    })

# Write output files
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