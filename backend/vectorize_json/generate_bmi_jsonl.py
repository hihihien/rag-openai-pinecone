import json
from pathlib import Path
from format_module_text import format_module_text

# ---------- Step 1: Load BMI Modules ----------
JSON_PATH = Path("backend/data/MHB_Alle_Studiengaenge/json/Studiengang_BMI_2025.json")

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
        mod_id = f"BMI__{mod_num.replace(' ', '_')}"

        mod = m.get("module", {})
        revisers = mod.get("revisers", [])

        # --- Combine reviser names ---
        reviser_names = []
        reviser_emails = []

        for r in revisers:
            if isinstance(r, dict):
                user = r.get("user", {})
                name = f"{user.get('title', '')} {user.get('firstName', '')} {user.get('lastName', '')}".strip()
                email = user.get("email")

                if name:
                    reviser_names.append(name)
                if email:
                    reviser_emails.append(email)

        # Final metadata strings
        reviser_name_str = "; ".join(reviser_names) if reviser_names else "N/A"
        reviser_email_str = "; ".join(reviser_emails) if reviser_emails else "N/A"

        metadata = {
            "moduleNumber": mod_num,
            "moduleName": mod.get("nameEnglish") or mod.get("nameGerman"),
            "creditPoints": m.get("creditPoints"),
            "suggestedSemester": m.get("suggestedSemesterOfAttendance"),
            "offeredInSeason": m.get("offeredInSeason"),
            "examType": mod.get("examType"),
            "heldInLanguage": mod.get("heldInLanguage"),
            "reviserName": reviser_name_str,
            "reviserEmail": reviser_email_str,
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
output_path = Path("backend/data/processed_json/BMI.jsonl")
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, "w", encoding="utf-8") as f:
    for record in formatted_records:
        json.dump(record, f, ensure_ascii=False)
        f.write("\n")

print(f"Exported {len(formatted_records)} records to {output_path}")