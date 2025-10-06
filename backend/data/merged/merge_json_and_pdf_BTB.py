import json
from pathlib import Path

# === CONFIG ===
BASE_DIR = Path(__file__).resolve().parent.parent  # backend/data
JSON_PATH = BASE_DIR / "processed_json" / "BTB.jsonl"
PDF_PATH = BASE_DIR / "processed_pdf" / "BTB_MHB_PO2025_chunks.jsonl"
OUT_PATH = Path(__file__).resolve().parent / "BTB_merged.jsonl"

STUDIENGANG_URL = "https://medien.hs-duesseldorf.de/btub"
PDF_URL = "https://medien.hs-duesseldorf.de/studium/studiengaenge/Documents/Modulhandb%C3%BCcher/BTB_MHB_PO2025_V1.0.pdf"

# === LOAD JSON MODULE DATA ===
with JSON_PATH.open("r", encoding="utf-8") as f:
    json_records = [json.loads(line) for line in f if line.strip()]
json_lookup = {rec["id"]: rec for rec in json_records}

# === LOAD PDF CHUNKS ===
with PDF_PATH.open("r", encoding="utf-8") as f:
    pdf_records = [json.loads(line) for line in f if line.strip()]
pdf_lookup = {rec["id"]: rec for rec in pdf_records}

# === Final merged output
merged_records = []

# === Step 1: Merge JSON records (base)
for json_id, json_rec in json_lookup.items():
    merged = json_rec.copy()
    pdf_rec = pdf_lookup.get(json_id)

    if pdf_rec:
        merged["text"] = json_rec["text"].strip() + "\n\n" + pdf_rec["text"].strip()
        pdf_meta = pdf_rec.get("metadata", {})
    else:
        merged["text"] = json_rec["text"].strip()
        pdf_meta = {}

    meta = merged.get("metadata", {}).copy()

    # === Fallback for module names
    module_name_en = meta.get("moduleName", None)
    module_name_de = pdf_meta.get("module_name", None)

    if module_name_en and not module_name_de:
        module_name_de = module_name_en
    elif module_name_de and not module_name_en:
        module_name_en = module_name_de
    elif not module_name_en and not module_name_de:
        module_name_en = module_name_de = "no data"

    # === Metadata enrichment
    meta.update({
        "moduleName": module_name_en,
        "moduleNameDe": module_name_de,
        "source_file": pdf_meta.get("source_file", "no data"),
        "pdf_page_start": pdf_meta.get("pdf_page_start", 0),
        "pdf_page_end": pdf_meta.get("pdf_page_end", 0),
        "studyProgramAbbrev": pdf_meta.get("studyProgramAbbrev", meta.get("studyProgramAbbrev", "BTB")),
        "studyProgram_Url": STUDIENGANG_URL,
        "pdf_url": PDF_URL
    })

    merged["metadata"] = meta
    merged_records.append(merged)

# === Step 2: Include unmatched PDF-only records
for pdf_id, pdf_rec in pdf_lookup.items():
    if pdf_id in json_lookup:
        continue

    pdf_meta = pdf_rec.get("metadata", {})
    module_name_de = pdf_meta.get("module_name", None)
    module_name_en = module_name_de if module_name_de else "no data"

    merged = {
        "id": pdf_id,
        "text": pdf_rec["text"].strip(),
        "metadata": {
            "moduleNumber": pdf_id,
            "moduleName": module_name_en,
            "moduleNameDe": module_name_de if module_name_de else module_name_en,
            "creditPoints": "no data",
            "suggestedSemester": "no data",
            "offeredInSeason": "no data",
            "examType": "no data",
            "heldInLanguage": "no data",
            "reviserName": "no data",
            "reviserEmail": "no data",
            "studyProgramAbbrev": pdf_meta.get("studyProgramAbbrev", "BTB"),
            "source_file": pdf_meta.get("source_file", "no data"),
            "pdf_page_start": pdf_meta.get("pdf_page_start", 0),
            "pdf_page_end": pdf_meta.get("pdf_page_end", 0),
            "studyProgram_Url": STUDIENGANG_URL,
            "pdf_url": PDF_URL
        }
    }
    merged_records.append(merged)

# === SAVE TO OUTPUT FILE ===
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with OUT_PATH.open("w", encoding="utf-8") as f:
    for rec in merged_records:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

print(f"[✓] Merged {len(merged_records)} BTB records → {OUT_PATH}")