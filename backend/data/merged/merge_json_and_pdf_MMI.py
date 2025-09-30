import json
from pathlib import Path

# === CONFIG (relative to current script location) ===
BASE_DIR = Path(__file__).resolve().parent.parent  # this goes to backend/data/
JSON_PATH = BASE_DIR / "processed_json" / "MMI.jsonl"
PDF_PATH = BASE_DIR / "processed_pdf" / "MMI_MHB_PO2025_chunks.jsonl"
OUT_PATH = Path(__file__).resolve().parent / "MMI_merged.jsonl"  # save to current folder

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

    # Fallback logic for module names
    module_name_en = meta.get("moduleName", None)
    module_name_de = pdf_meta.get("module_name", None)

    if module_name_en and not module_name_de:
        module_name_de = module_name_en
    elif module_name_de and not module_name_en:
        module_name_en = module_name_de
    elif not module_name_en and not module_name_de:
        module_name_en = module_name_de = "no data"

    meta["moduleName"] = module_name_en
    meta["moduleNameDe"] = module_name_de
    meta["source_file"] = pdf_meta.get("source_file", "no data")
    meta["pdf_page_start"] = pdf_meta.get("pdf_page_start", "no data")
    meta["pdf_page_end"] = pdf_meta.get("pdf_page_end", "no data")
    meta["studyProgramAbbrev"] = pdf_meta.get("studyProgramAbbrev", meta.get("studyProgramAbbrev", "no data"))

    merged["metadata"] = meta
    merged_records.append(merged)

# === Step 2: Include unmatched PDF-only records
for pdf_id, pdf_rec in pdf_lookup.items():
    if pdf_id in json_lookup:
        continue  # already merged

    pdf_meta = pdf_rec.get("metadata", {})
    module_name_de = pdf_meta.get("module_name", None)
    module_name_en = module_name_de if module_name_de else "no data"

    merged = {
        "id": pdf_id,  # ✅ keep original ID
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
            "studyProgramAbbrev": pdf_meta.get("studyProgramAbbrev", "no data"),
            "source_file": pdf_meta.get("source_file", "no data"),
            "pdf_page_start": pdf_meta.get("pdf_page_start", "no data"),
            "pdf_page_end": pdf_meta.get("pdf_page_end", "no data")
        }
    }
    merged_records.append(merged)

# === SAVE TO OUTPUT FILE ===
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with OUT_PATH.open("w", encoding="utf-8") as f:
    for rec in merged_records:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

print(f"[✓] Merged {len(merged_records)} records → {OUT_PATH}")
