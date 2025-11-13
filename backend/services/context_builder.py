from typing import List, Tuple, Optional
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
    # Avoid mutable default list
    links: Optional[List[dict]] = None


def build_context(matches) -> Tuple[str, List[SourceItem]]:
    """
    Builds a context string with WEB data first, then module content.
    Applies SCORE_THRESHOLD, PER_MODULE_CAP, MAX_CONTEXT_CHUNKS (per section),
    and trims to MAX_CONTEXT_CHARS.
    """
    used_per_module = {}
    parts: List[str] = []
    sources: List[SourceItem] = []

    # Split matches into WEB vs MODULE using metadata
    web_matches: List = []
    module_matches: List = []

    for m in matches:
        if (m.score or 0) < SCORE_THRESHOLD:
            continue

        meta = ID_TO_META.get(m.id, {}) or {}
        study_abbr = meta.get("studyProgramAbbrev", "") or ""
        category = meta.get("category", "") or ""
        section = meta.get("section", "") or ""
        source = meta.get("source", "") or ""

        is_web = ("WEB" in study_abbr) or bool(category) or bool(section) or bool(source)
        if is_web:
            web_matches.append(m)
        else:
            module_matches.append(m)

    def build_section(match_list: List, section_label: str) -> List[str]:
        """Return a list of formatted blocks for this section, capped by MAX_CONTEXT_CHUNKS."""
        section_parts: List[str] = []

        for m in match_list:
            rid = m.id
            meta = ID_TO_META.get(rid, {}) or {}

            mod = meta.get("moduleNumber", "UNK")
            used_per_module[mod] = used_per_module.get(mod, 0) + 1
            if used_per_module[mod] > PER_MODULE_CAP:
                continue

            # Prefer full text from in-memory store; fall back to Pinecone snippet
            full_text = ID_TO_TEXT.get(rid)
            if not full_text:
                # m.metadata may be a dict-like; guard safely
                snippet = getattr(m, "metadata", {}) or {}
                full_text = snippet.get("snippet", "")
            if not full_text:
                continue

            study_abbr = meta.get("studyProgramAbbrev", "") or ""
            module_name = (
                meta.get("moduleNameDe")
                or meta.get("moduleNameEn")
                or meta.get("moduleName", "")
                or ""
            )
            category = meta.get("category", "") or ""
            section = meta.get("section", "") or ""
            source = meta.get("source", "") or ""
            links = meta.get("links", []) or []

            # Header line
            if section_label == "WEB":
                header = f"[{study_abbr or 'FBM_WEB'}] {category or section or 'Website Information'}"
            else:
                header = f"[{study_abbr}] {mod} • {module_name}"

            section_parts.append(f"{header}\n{'-' * len(header)}\n{full_text}")

            # Record source item
            sources.append(
                SourceItem(
                    id=rid,
                    moduleNumber=mod,
                    moduleNameDe=meta.get("moduleNameDe", "") or "",
                    moduleNameEn=meta.get("moduleNameEn") or meta.get("moduleName", "") or "",
                    studyProgramAbbrev=study_abbr,
                    season=meta.get("season", "") or "",
                    credits=meta.get("credits", "") or "",
                    examType=meta.get("examType", "") or "",
                    score=float(m.score or 0),
                    sourceFile=meta.get("source_file", "") or "",
                    pdfPageStart=int(meta.get("pdf_page_start", 0) or 0),
                    pdfPageEnd=int(meta.get("pdf_page_end", 0) or 0),
                    studyProgramUrl=meta.get("studyProgram_Url", "") or "",
                    pdfUrl=meta.get("pdf_url", "") or "",
                    category=category,
                    section=section,
                    source=source,
                    links=links,
                )
            )

            if len(section_parts) >= MAX_CONTEXT_CHUNKS:
                break

        if not section_parts:
            return []
        label = "Website Information" if section_label == "WEB" else "Modulhandbuch-Inhalte"
        return [f"\n### {label}\n"] + section_parts

    # Assemble: WEB first, then MODULE
    ordered_parts = build_section(web_matches, "WEB") + build_section(module_matches, "MODULE")

    context = "\n\n".join(ordered_parts)
    return context[:MAX_CONTEXT_CHARS], sources
