import json
from pathlib import Path

# === CONFIG ===
PROGRAM = "BCSIM"

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/data
JSON_PATH = BASE_DIR / "processed_json" / f"{PROGRAM}.jsonl"
OUT_PATH = Path(__file__).resolve().parent / f"{PROGRAM}_merged.jsonl"

# Program link for BCSIM
STUDIENGANG_URL = "https://medien.hs-duesseldorf.de/bcsim"

# === LOAD JSON DATA ===
with JSON_PATH.open("r", encoding="utf-8") as f:
    json_records = [json.loads(line) for line in f if line.strip()]

merged_records = []

# === Enrich and normalize metadata ===
for rec in json_records:
    meta = rec.get("metadata", {}).copy()

    meta.update({
        "moduleNameDe": meta.get("moduleName", "no data"),
        "studyProgramAbbrev": PROGRAM,
        "studyProgram_Url": STUDIENGANG_URL
    })

    rec["metadata"] = meta
    merged_records.append(rec)

# === SAVE TO OUTPUT FILE ===
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with OUT_PATH.open("w", encoding="utf-8") as f:
    for rec in merged_records:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

print(f"[✓] Processed {len(merged_records)} BCSIM records → {OUT_PATH}")
