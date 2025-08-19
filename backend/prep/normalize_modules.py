"""
Normalize study program JSON/JS files into JSONL records for embedding.
Each line = one module with metadata + DE/EN text fields.
"""

import json, json5, glob, re
from pathlib import Path
from datetime import date

# ---------- Path setup ----------
HERE = Path(__file__).resolve()
BACKEND_DIR = HERE.parents[1]
RAW_DIR = BACKEND_DIR / "data" / "MHB_Alle_Studiengaenge"
OUT_DIR = BACKEND_DIR / "data" / "normalized"
OUT_DIR.mkdir(parents=True, exist_ok=True)
# Ensure output directory exists
PROGRAM_PATTERNS = [
    str(RAW_DIR / "**" / "Studiengang_*.js"),
    str(RAW_DIR / "**" / "Studiengang_*.json"),
]

TODAY = str(date.today())

# ---------- Helpers ----------

def find_program_files() -> list[Path]:
    files = []
    for pat in PROGRAM_PATTERNS:
        files.extend(glob.glob(pat, recursive=True))
    return [Path(f) for f in files]

# Helper to read program JSON/JS files
def read_program_objs(path: Path):
    """Load .js/.json into one or more program dicts."""
    raw = path.read_text(encoding="utf-8").strip()
    # Strip common JS export wrappers
    raw = re.sub(r'^\s*export\s+default\s+', '', raw)
    raw = re.sub(r'^\s*module\.exports\s*=\s*', '', raw)
    data = json5.loads(raw)

    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        return [data]
    else:
        raise ValueError(f"Unsupported top-level type in {path}: {type(data)}")

# Helper to normalize season strings
def norm_season(s: str):
    if not s: return None
    s = s.lower()
    if "winter" in s: return "winter"
    if "summer" in s: return "summer"
    if "every" in s: return "every"
    if "to_be_announced" in s: return "tba"
    return s

# Helper to normalize language strings
def norm_language(s: str):
    if not s: return None
    s = s.lower()
    if s in {"de","en"}: return s
    if "en_on" in s: return "en_on_demand"
    if "de_on" in s: return "de_on_demand"
    if "mixed" in s: return "mixed"
    return s

# Helper to parse float values
def parse_float(v):
    try:
        return float(v)
    except Exception:
        return None

# Helper to join text parts
def join(parts):
    return "\n".join([p for p in parts if p and str(p).strip()])

# ---------- Build one record ----------

def build_record(program, offer):
    mod = offer.get("module", {})
    abbr = program.get("abbreviation","UNK")
    module_number = offer.get("moduleNumber") or mod.get("id")
    rid = f"{abbr}-{module_number}"

    # --- Program metadata ---
    prog_meta = {
        "studyProgramId": program.get("id"),
        "studyProgramName": program.get("name"),
        "studyProgramNameEn": program.get("nameEnglish"),
        "studyProgramAbbrev": abbr,
        "degree": program.get("degree"),
        "examinationRegulation": program.get("examinationRegulation"),
        "totalCP": program.get("totalCP"),
        "standardPeriod": program.get("standardPeriod"),
        "specialisationName": program.get("specialisationName"),
        "programImagePath": program.get("programImagePath"),
        "coordinators": program.get("coordinators", []),
    }

    # --- Offer metadata ---
    offer_meta = {
        "offerId": offer.get("id"),
        "moduleNumber": module_number,
        "suggestedSemesterOfAttendance": offer.get("suggestedSemesterOfAttendance"),
        "offeredInSeason": offer.get("offeredInSeason"),
        "offeredInSeasonNorm": norm_season(offer.get("offeredInSeason")),
        "creditPoints": offer.get("creditPoints"),
        "creditPointsNum": parse_float(offer.get("creditPoints")),
        "isGraded": offer.get("isGraded"),
        "partOfOverallGrade": offer.get("partOfOverallGrade"),
        "offerType": offer.get("type"),
        "formalPrereqDe": offer.get("formalRequirementsGerman"),
        "formalPrereqEn": offer.get("formalRequirementsEnglish"),
        "contentPrereqDe": offer.get("contentRequirementsGerman"),
        "contentPrereqEn": offer.get("contentRequirementsEnglish"),
    }

    # --- Module metadata ---
    sws = {
        "lecture": mod.get("swsLecture"),
        "practice": mod.get("swsPractice"),
        "seminar": mod.get("swsSeminar"),
        "tutorial": mod.get("swsTutorial"),
        "exercise": mod.get("swsExercise"),
        "project": mod.get("swsProject"),
        "seminarLesson": mod.get("swsSeminarLesson"),
        "researchProject": mod.get("swsResearchProject"),
        "accompaniedSelfStudy": mod.get("swsAccompaniedSelfStudy"),
    }
    workload = {
        "contactTime": mod.get("workloadContactTime"),
        "selfStudy": mod.get("workloadSelfStudy"),
        "total": mod.get("workloadTotal"),
    }

    # Module metadata
    module_meta = {
        "moduleId": mod.get("id"),
        "moodleCourseId": mod.get("moodleCourseId"),
        "moduleNameDe": mod.get("nameGerman"),
        "moduleNameEn": mod.get("nameEnglish"),
        "moduleAbbrevDe": mod.get("abbrevGerman"),
        "moduleAbbrevEn": mod.get("abbrevEnglish"),
        "contentsDe": mod.get("contentsOfLectureGerman"),
        "contentsEn": mod.get("contentsOfLectureEnglish"),
        "goalsDe": mod.get("goalsOfLectureGerman"),
        "goalsEn": mod.get("goalsOfLectureEnglish"),
        "literatureDe": mod.get("literatureGerman"),
        "literatureEn": mod.get("literatureEnglish"),
        "examAttendanceDe": mod.get("examAttendanceGerman"),
        "examAttendanceEn": mod.get("examAttendanceEnglish"),
        "sws": sws,
        "heldInLanguage": mod.get("heldInLanguage"),
        "heldInLanguageNorm": norm_language(mod.get("heldInLanguage")),
        "durationSemesters": mod.get("durationSemesters"),
        "workload": workload,
        "expectedGroupSize": mod.get("expectedGroupSize"),
        "examType": mod.get("examType"),
        "examTypeMayDeviate": mod.get("examTypeMayDeviate"),
        "additionalAttributes": mod.get("additionalAttributes", []),
        "revisers": mod.get("revisers", []),
        "offeredInCatalogues": mod.get("offeredInCatalogues", []),
        "leftSideRelations": mod.get("leftSideRelations", []),
        "rightSideRelations": mod.get("rightSideRelations", []),
    }

    # --- Other fields ---
    cross_apps = offer.get("studyProgramSpecificValues", [])

    lang_tags = []
    if module_meta["contentsDe"] or module_meta["goalsDe"]:
        lang_tags.append("de")
    if module_meta["contentsEn"] or module_meta["goalsEn"]:
        lang_tags.append("en")

    # --- Build retrieval texts ---
    text_de = join([
        f"{module_meta['moduleNameDe']} ({module_meta['moduleAbbrevDe']})",
        module_meta["contentsDe"],
        module_meta["goalsDe"],
        offer_meta["formalPrereqDe"],
        offer_meta["contentPrereqDe"],
        module_meta["examAttendanceDe"],
        f"Prüfungsform: {module_meta['examType']}",
    ])
    text_en = join([
        f"{module_meta['moduleNameEn']} ({module_meta['moduleAbbrevEn']})",
        module_meta["contentsEn"],
        module_meta["goalsEn"],
        offer_meta["formalPrereqEn"],
        offer_meta["contentPrereqEn"],
        module_meta["examAttendanceEn"],
        f"Exam type: {module_meta['examType']}",
    ])

    # --- Final record ---
    return {
        "id": rid,
        "namespace": abbr,
        "program": prog_meta,
        "offer": offer_meta,
        "module": module_meta,
        "crossProgramAppearances": cross_apps,
        "langTags": lang_tags,
        "seasonTags": [offer_meta["offeredInSeasonNorm"]] if offer_meta["offeredInSeasonNorm"] else [],
        "textDe": text_de,
        "textEn": text_en,
        "source_type": "study_program_json",
        "source_program_file": program.get("fileName",""),
        "version": program.get("examinationRegulation"),
        "lastUpdated": TODAY,
    }

# ---------- Main ----------

def main():
    files = find_program_files()
    print(f"[normalize] RAW_DIR: {RAW_DIR}")
    print(f"[normalize] OUT_DIR: {OUT_DIR}")
    print(f"[normalize] Found {len(files)} program file(s).")
    # Ensure we have files to process
    if not files:
        print("No program files found. Double-check paths.")
        return
    # Process each program file
    for f in files:
        programs = read_program_objs(f)
        print(f"[normalize] {f.name}: {len(programs)} program object(s)")
        # Normalize each program object
        for program in programs:
            program["fileName"] = f.name
            abbr = program.get("abbreviation", f.stem)
            out_path = OUT_DIR / f"{abbr}.jsonl"

            written = 0
            with out_path.open("w", encoding="utf-8") as out:
                for offer in program.get("modules", []):
                    try:
                        rec = build_record(program, offer)
                        out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                        written += 1
                    except Exception as e:
                        print(f"[WARN] {f.name}:{abbr} skipping one module: {e}")

            print(f"✓ {abbr}: wrote {written} records → {out_path}")

if __name__ == "__main__":
    main()

