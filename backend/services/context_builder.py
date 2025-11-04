from typing import List, Tuple
from services.loader import ID_TO_TEXT, ID_TO_META
from pydantic import BaseModel

SCORE_THRESHOLD = 0.2
PER_MODULE_CAP = 2
MAX_CONTEXT_CHUNKS = 6
MAX_CONTEXT_CHARS = 9000


class SourceItem(BaseModel):
    id: str
    moduleNumber: str = ""
    moduleNameDe: str = ""
    moduleNameEn: str = ""
    studyProgramAbbrev: str = ""
    season: str = ""
    credits: str = ""
    examType: str = ""
    score: float = 0.0
    sourceFile: str = ""
    pdfPageStart: int = 0
    pdfPageEnd: int = 0
    studyProgramUrl: str = ""
    pdfUrl: str = ""
    category: str = ""
    section: str = ""
    source: str = ""
    links: list = []  # <- new field for link text + url pairs
    links: list = []


def build_context(matches) -> Tuple[str, List[SourceItem]]:
    """Builds a context string with WEB data first, then module content."""

    used = {}
    parts = []
    sources = []

    # Split matches into two groups
    web_matches = []
    module_matches = []

    for m in matches:
        if m.score < SCORE_THRESHOLD:
            continue

        meta = ID_TO_META.get(m.id, {})
        study_abbr = meta.get("studyProgramAbbrev", "")
        category = meta.get("category", "")
        section = meta.get("section", "")
        source = meta.get("source", "")

        # Classify
        if "WEB" in study_abbr or category or section or source.endswith(".de/"):
            web_matches.append(m)
        else:
            module_matches.append(m)

    # Helper to build context from a list of matches
    def build_section(match_list, section_label):
        section_parts = []
        for m in match_list:
            rid = m.id
            meta = ID_TO_META.get(rid, {})
            mod = meta.get("moduleNumber", "UNK")

            # prevent repeating same module too often
            used[mod] = used.get(mod, 0) + 1
            if used[mod] > PER_MODULE_CAP:
                continue

        sources.append(SourceItem(
            id=rid,
            moduleNumber=mod,
            moduleNameDe=meta.get("moduleNameDe", ""),
            moduleNameEn=meta.get("moduleNameEn") or meta.get("moduleName", ""),
            studyProgramAbbrev=study_abbr,
            season=meta.get("season", ""),
            credits=meta.get("credits", ""),
            examType=meta.get("examType", ""),
            score=m.score,
            sourceFile=meta.get("source_file", ""),
            pdfPageStart=meta.get("pdf_page_start", 0),
            pdfPageEnd=meta.get("pdf_page_end", 0),
            studyProgramUrl=meta.get("studyProgram_Url", ""),
            pdfUrl=meta.get("pdf_url", ""),
            category=category,
            section=section,
            source=source,
            links=meta.get("links", [])
        ))

            study_abbr = meta.get("studyProgramAbbrev", "")
            module_name = meta.get("moduleNameDe") or meta.get("moduleNameEn") or meta.get("moduleName", "")
            category = meta.get("category", "")
            section = meta.get("section", "")
            source = meta.get("source", "")
            links = meta.get("links", [])

            # Choose a clear header
            if section_label == "WEB":
                header = f"[{study_abbr or 'FBM_WEB'}] {category or section or 'Website Information'}"
            else:
                header = f"[{study_abbr}] {mod} • {module_name}"

            section_parts.append(f"{header}\n{'-' * len(header)}\n{full_text}")

            # Add source info
            sources.append(SourceItem(
                id=rid,
                moduleNumber=mod,
                moduleNameDe=meta.get("moduleNameDe", ""),
                moduleNameEn=meta.get("moduleNameEn") or meta.get("moduleName", ""),
                studyProgramAbbrev=study_abbr,
                season=meta.get("season", ""),
                credits=meta.get("credits", ""),
                examType=meta.get("examType", ""),
                score=m.score,
                sourceFile=meta.get("source_file", ""),
                pdfPageStart=meta.get("pdf_page_start", 0),
                pdfPageEnd=meta.get("pdf_page_end", 0),
                studyProgramUrl=meta.get("studyProgram_Url", ""),
                pdfUrl=meta.get("pdf_url", ""),
                category=category,
                section=section,
                source=source,
                links=links,
            ))

            if len(section_parts) >= MAX_CONTEXT_CHUNKS:
                break

        if section_parts:
            label = "Website Information" if section_label == "WEB" else "Modulhandbuch-Inhalte"
            return [f"\n### {label}\n"] + section_parts
        return []

    # Build sections: WEB first, modules second
    ordered_parts = build_section(web_matches, "WEB") + build_section(module_matches, "MODULE")

    # Merge everything
    context = "\n\n".join(ordered_parts)
    return context[:MAX_CONTEXT_CHARS], sources
