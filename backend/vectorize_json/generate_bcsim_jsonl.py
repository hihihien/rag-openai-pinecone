import json
from pathlib import Path
from format_module_text import format_module_text

# ---------- Step 1: Load BCSIM Modules ----------
JSON_PATH = Path("backend/data/MHB_Alle_Studiengaenge/json/Studiengang_BCSIM_2027.json")

with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# Extract all module records from nested structure
modules = []
for entry in data:
    if isinstance(entry, dict) and "modules" in entry:
        modules.extend(entry["modules"])

print(f"Loaded {len(modules)} module records")

# ---------- Step 2: Format Each Module ----------
formatted_records = []

for m in modules:
    mod_num = m.get("moduleNumber", "unknown")
    print(f"→ Processing {mod_num}")

    try:
        text = format_module_text(m)
        if not text.strip():
            print(f"  Skipped (empty text)")
            continue
    except Exception as e:
        print(f"Failed to format text: {e}")
        continue

    try:
        mod = m.get("module", {})
        revisers = mod.get("revisers")
        if isinstance(revisers, list) and revisers and isinstance(revisers[0], dict):
            reviser = revisers[0].get("user", {}) or {}
        else:
            reviser = {}

        metadata = {
            "moduleNumber": mod_num,
            "moduleName": mod.get("nameEnglish") or mod.get("nameGerman"),
            "creditPoints": m.get("creditPoints"),
            "suggestedSemester": m.get("suggestedSemesterOfAttendance"),
            "offeredInSeason": m.get("offeredInSeason"),
            "examType": mod.get("examType"),
            "heldInLanguage": mod.get("heldInLanguage"),
            "reviserName": f"{reviser.get('title', '')} {reviser.get('firstName', '')} {reviser.get('lastName', '')}".strip(),
            "reviserEmail": reviser.get("email"),
            "studyProgramId": m.get("studyProgramId"),
            "source_type": "json"
        }

        formatted_records.append({
            "id": f"BCSIM__{mod_num.replace(' ', '_')}",
            "text": text,
            "metadata": metadata
        })

    except Exception as e:
        print(f"Failed to build metadata: {e}")

print(f"Prepared {len(formatted_records)} records for export")

# ---------- Step 3: Save to .jsonl ----------
output_path = Path("backend/data/processed_json/BCSIM.jsonl")
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, "w", encoding="utf-8") as f:
    for record in formatted_records:
        json.dump(record, f, ensure_ascii=False)
        f.write("\n")

print(f"Exported {len(formatted_records)} records to {output_path}")