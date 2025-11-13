from typing import List, Tuple
from services.loader import ID_TO_TEXT, ID_TO_META
from pydantic import BaseModel

SCORE_THRESHOLD = 0.3
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
    links: list = []


def build_context(matches) -> Tuple[str, List[SourceItem]]:
    """Builds a combined context string and a list of source metadata for answer generation."""

    used = {}
    parts = []
    sources = []

    for m in matches:
        if m.score < SCORE_THRESHOLD:
            continue

        rid = m.id
        meta = ID_TO_META.get(rid, {})
        mod = meta.get("moduleNumber", "UNK")
        used[mod] = used.get(mod, 0) + 1
        if used[mod] > PER_MODULE_CAP:
            continue

        full_text = ID_TO_TEXT.get(rid) or m.metadata.get("snippet")
        if not full_text:
            continue

        study_abbr = meta.get("studyProgramAbbrev", "")
        module_name = meta.get("moduleNameDe") or meta.get("moduleNameEn") or meta.get("moduleName", "")
        category = meta.get("category", "")
        section = meta.get("section", "")
        source = meta.get("source", "")

        # Determine the data type
        if "WEB" in study_abbr or category or section or source:
            header_type = "WEB"
        else:
            header_type = "MODULE"

        # Create a clear header showing source origin
        if header_type == "WEB":
            header = f"[{study_abbr or 'FBM_WEB'}] {category or section or 'Website Information'}"
        else:
            header = f"[{study_abbr}] {mod} • {module_name}"

        parts.append(f"{header}\n{'-' * len(header)}\n{full_text}")

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

        if len(parts) >= MAX_CONTEXT_CHUNKS:
            break

    # Join context and trim to max character length
    context = "\n\n".join(parts)
    return context[:MAX_CONTEXT_CHARS], sources
