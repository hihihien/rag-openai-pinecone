def format_module_text(module_offer):
    mod = module_offer.get("module", {})

    # Get ALL revisers
    revisers = mod.get("revisers", [])

    # Combine all reviser names safely
    reviser_names = []
    for r in revisers:
        if isinstance(r, dict):
            user = r.get("user", {})
            name = f"{user.get('title', '')} {user.get('firstName', '')} {user.get('lastName', '')}".strip()
            if name:
                reviser_names.append(name)

    # Final instructor string (joined with "; ")
    lecturer = "; ".join(reviser_names) if reviser_names else "N/A"

    # Extract fields safely
    title = mod.get("nameEnglish") or mod.get("nameGerman") or "N/A"
    module_number = module_offer.get("moduleNumber", "N/A")
    credits = module_offer.get("creditPoints", "N/A")
    semester = module_offer.get("suggestedSemesterOfAttendance", "N/A")
    season = module_offer.get("offeredInSeason", "N/A")
    language = mod.get("heldInLanguage", "N/A")
    exam_type = mod.get("examType", "N/A")

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
    {goals_en}

    --- Goals (DE) ---
    {goals_de}

    --- Contents (EN) ---
    {content_en}

    --- Contents (DE) ---
    {content_de}

    --- Literature (EN) ---
    {literature_en}

    --- Literature (DE) ---
    {literature_de}
    """

    return text.strip()
