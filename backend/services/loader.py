import json
from pathlib import Path
from typing import Dict, Any

ID_TO_TEXT: Dict[str, str] = {}
ID_TO_META: Dict[str, Dict[str, Any]] = {}
AVAILABLE_NAMESPACES = []

# Use merged data folder
DATA_PATHS = [
    Path(__file__).resolve().parent.parent / "data" / "merged"
]

def load_text_store():
    """Load merged JSONL files into in-memory dicts for fast lookup."""
    global AVAILABLE_NAMESPACES
    seen_namespaces = set()

    for data_dir in DATA_PATHS:
        for jf in data_dir.rglob("*.jsonl"):
            namespace = jf.stem.split("_")[0]  # e.g. "BMI" from "BMI_merged.jsonl"
            seen_namespaces.add(namespace)

            with jf.open("r", encoding="utf-8") as f:
                for line in f:
                    rec = json.loads(line)
                    rid = rec.get("id")
                    if not rid:
                        continue

                    text = rec.get("text", "").strip()
                    if not text:
                        continue
                    ID_TO_TEXT[rid] = text

                    meta = rec.get("metadata") or {}

                    ID_TO_META[rid] = {
                        "studyProgramAbbrev": meta.get("studyProgramAbbrev", namespace),
                        "moduleNumber": meta.get("moduleNumber"),
                        "moduleNameDe": meta.get("moduleNameDe") or meta.get("moduleName", ""),
                        "moduleNameEn": meta.get("moduleNameEn") or meta.get("moduleName", ""),
                        "season": meta.get("offeredInSeason", ""),
                        "credits": meta.get("creditPoints", ""),
                        "examType": meta.get("examType", ""),
                        "source_file": meta.get("source_file", ""),
                        "pdf_page_start": meta.get("pdf_page_start", 0),
                        "pdf_page_end": meta.get("pdf_page_end", 0),
                    }

    AVAILABLE_NAMESPACES.clear()
    AVAILABLE_NAMESPACES.extend(sorted(seen_namespaces))