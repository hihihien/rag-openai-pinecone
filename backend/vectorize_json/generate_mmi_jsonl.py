import json
from pathlib import Path
from format_module_text import format_module_text

# ---------- Step 1: Load MMI Modules ----------
JSON_PATH = Path("backend/data/MHB_Alle_Studiengaenge/json/Studiengang_MMI_2025.json")

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
    try:
        text = format_module_text(m)
        if not text.strip():
            continue

        mod_num = m.get("moduleNumber", "unknown")
        mod_id = f"MMI__{mod_num.replace(' ', '_')}"

        mod = m.get("module", {})
        reviser = mod.get("revisers", [{}])[0].get("user", {})

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
            "id": mod_id,
            "text": text,
            "metadata": metadata
        })

    except Exception as e:
        print(f"Failed to process module: {m.get('moduleNumber', '???')}")
        print(e)

print(f"Prepared {len(formatted_records)} records for export")

# ---------- Step 3: Save to .jsonl ----------
output_path = Path("backend/data/processed/MMI_modules_for_upload.jsonl")
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, "w", encoding="utf-8") as f:
    for record in formatted_records:
        json.dump(record, f, ensure_ascii=False)
        f.write("\n")

print(f"Exported {len(formatted_records)} records to {output_path}")