import json
from pathlib import Path

WEB_DIR = Path(__file__).resolve().parent
files = list(WEB_DIR.glob("*_web.json"))

for file in files:
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Skip if the JSON is not a list
    if not isinstance(data, list):
        print(f"[!] Skipping {file.name} — not a list")
        continue

    # Determine study program abbreviation (if available)
    first_meta = data[0].get("metadata", {}) if data else {}
    abbrev = first_meta.get("studyProgramAbbrev", "FBM").upper()

    for idx, record in enumerate(data, start=1):
        record["id"] = f"WEB_{abbrev}_{idx:03d}"  # e.g., WEB_BMI_001, WEB_BMI_002

    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f" Updated {file.name} → {len(data)} records with IDs")
