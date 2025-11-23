def format_module_text(module_offer):
    mod = module_offer.get("module", {})

    # Defensive check for nested revisers
    revisers = mod.get("revisers", [])
    reviser = revisers[0].get("user", {}) if revisers and isinstance(revisers[0], dict) else {}

    # Extract fields safely
    title = mod.get("nameEnglish") or mod.get("nameGerman") or "N/A"
    module_number = module_offer.get("moduleNumber", "N/A")
    credits = module_offer.get("creditPoints", "N/A")
    semester = module_offer.get("suggestedSemesterOfAttendance", "N/A")
    season = module_offer.get("offeredInSeason", "N/A")
    language = mod.get("heldInLanguage", "N/A")
    exam_type = mod.get("examType", "N/A")
    lecturer = f"{reviser.get('title', '')} {reviser.get('firstName', '')} {reviser.get('lastName', '')}".strip()

    # English and German content blocks
    goals_en = (mod.get("goalsOfLectureEnglish") or "").strip()
    content_en = (mod.get("contentsOfLectureEnglish") or "").strip()
    literature_en = (mod.get("literatureEnglish") or "").strip()

    goals_de = (mod.get("goalsOfLectureGerman") or "").strip()
    content_de = (mod.get("contentsOfLectureGerman") or "").strip()
    literature_de = (mod.get("literatureGerman") or "").strip()

    # Build formatted string
    text = f"""
    Title: {title}
    Module Number: {module_number}
    Credits: {credits} CP
    Semester: {semester}
    Offered In: {season}
    Language: {language}
    Exam Type: {exam_type}
    Instructor: {lecturer}

    --- Goals (EN) ---
    {goals_en.strip()}

    --- Goals (DE) ---
    {goals_de.strip()}

    --- Contents (EN) ---
    {content_en.strip()}

    --- Contents (DE) ---
    {content_de.strip()}

    --- Literature (EN) ---
    {literature_en.strip()}

    --- Literature (DE) ---
    {literature_de.strip()}
    """

    return text.strip()
