from typing import List, Tuple
from services.loader import ID_TO_TEXT, ID_TO_META
from pydantic import BaseModel

# lowered threshold to include weaker matches
SCORE_THRESHOLD = 0.2
PER_MODULE_CAP = 2
MAX_CONTEXT_CHUNKS = 6
MAX_CONTEXT_CHARS = 9000

class SourceItem(BaseModel):
    id: str
    moduleNumber: str
    moduleNameDe: str = ""
    moduleNameEn: str = ""
    studyProgramAbbrev: str = ""
    season: str = ""
    credits: str = ""
    examType: str = ""
    score: float = 0.0

def build_context(matches) -> Tuple[str, List[SourceItem]]:
    used, parts, sources = {}, [], []
    for m in matches:
        if m.score < SCORE_THRESHOLD:
            continue
        rid = m.id
        meta = ID_TO_META.get(rid, {})
        mod = meta.get("moduleNumber", "UNK")
        used[mod] = used.get(mod, 0) + 1
        if used[mod] > PER_MODULE_CAP:
            continue

        full = ID_TO_TEXT.get(rid) or m.metadata.get("snippet")
        if not full:
            continue

        header = f"[{meta.get('studyProgramAbbrev')}] {mod} • {meta.get('moduleNameDe') or meta.get('moduleNameEn')}"
        parts.append(f"{header}\n{'-'*len(header)}\n{full}")

        sources.append(SourceItem(
            id=rid,
            moduleNumber=mod,
            moduleNameDe=meta.get("moduleNameDe", ""),
            moduleNameEn=meta.get("moduleNameEn", ""),
            studyProgramAbbrev=meta.get("studyProgramAbbrev", ""),
            season=meta.get("season", ""),
            credits=meta.get("credits", ""),
            examType=meta.get("examType", ""),
            score=m.score
        ))

        if len(parts) >= MAX_CONTEXT_CHUNKS:
            break

    context = "\n\n".join(parts)
    return context[:MAX_CONTEXT_CHARS], sources
