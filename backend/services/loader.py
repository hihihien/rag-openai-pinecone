import json
from pathlib import Path
from typing import Dict, Any

ID_TO_TEXT: Dict[str, str] = {}
ID_TO_META: Dict[str, Dict[str, Any]] = {}
AVAILABLE_NAMESPACES = []

DATA_PATHS = [
    Path(__file__).resolve().parent.parent / "data" / "processed_json",
    Path(__file__).resolve().parent.parent / "data" / "processed_pdf"
]

def load_text_store():
    global AVAILABLE_NAMESPACES
    seen_namespaces = set()

    for data_dir in DATA_PATHS:
        for jf in data_dir.rglob("*.jsonl"):
            namespace = jf.stem
            seen_namespaces.add(namespace)

            with jf.open("r", encoding="utf-8") as f:
                for line in f:
                    rec = json.loads(line)
                    rid = rec.get("id")
                    if not rid:
                        continue

                    text = rec.get("text") or ""
                    if not text.strip():
                        continue
                    ID_TO_TEXT[rid] = text

                    meta = rec.get("metadata") or {}
                    if not meta:
                        meta = {
                            "studyProgramAbbrev": rec.get("studyProgramAbbrev"),
                            "moduleNumber": rec.get("moduleNumber"),
                            "moduleNameDe": rec.get("moduleNameDe"),
                            "moduleNameEn": rec.get("moduleNameEn"),
                            "examType": rec.get("examType"),
                            "offeredInSeason": rec.get("offeredInSeason"),
                            "creditPoints": rec.get("creditPoints"),
                        }

                    ID_TO_META[rid] = {
                        "studyProgramAbbrev": meta.get("studyProgramAbbrev"),
                        "moduleNumber": meta.get("moduleNumber"),
                        "moduleNameDe": meta.get("moduleNameDe"),
                        "moduleNameEn": meta.get("moduleNameEn"),
                        "season": meta.get("offeredInSeasonNorm") or meta.get("offeredInSeason"),
                        "credits": meta.get("creditPoints"),
                        "examType": meta.get("examType"),
                    }

    AVAILABLE_NAMESPACES.clear()
    AVAILABLE_NAMESPACES.extend(sorted(seen_namespaces))