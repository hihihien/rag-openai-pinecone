import json
from pathlib import Path
from typing import Dict, Any

# Global in-memory stores
ID_TO_TEXT: Dict[str, str] = {}
ID_TO_META: Dict[str, Dict[str, Any]] = {}
AVAILABLE_NAMESPACES = []

# === Paths ===
MERGED_PATH = Path(__file__).resolve().parent.parent / "data" / "merged"
WEB_PATH = Path(__file__).resolve().parent.parent / "data" / "processed_web"

def load_text_store():
    """Load merged JSONL files + web JSON files into memory."""
    global AVAILABLE_NAMESPACES
    seen_namespaces = set()

    # 1. Load merged module JSONL data
    for jf in MERGED_PATH.rglob("*.jsonl"):
        namespace = jf.stem.split("_")[0]  # e.g. BMI_merged as BMI
        seen_namespaces.add(namespace)

        with jf.open("r", encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                rid = rec.get("id")
                if not rid:
                    continue

                text = (rec.get("text") or "").strip()
                if not text:
                    continue
                ID_TO_TEXT[rid] = text

                meta = rec.get("metadata") or {}
                ID_TO_META[rid] = {
                    "studyProgramAbbrev": meta.get("studyProgramAbbrev", namespace),
                    "moduleNumber": meta.get("moduleNumber", ""),
                    "moduleNameDe": meta.get("moduleNameDe") or meta.get("moduleName", ""),
                    "moduleNameEn": meta.get("moduleNameEn") or meta.get("moduleName", ""),
                    "season": meta.get("offeredInSeason", ""),
                    "credits": meta.get("creditPoints", ""),
                    "examType": meta.get("examType", ""),
                    "source_file": meta.get("source_file", ""),
                    "pdf_page_start": meta.get("pdf_page_start", 0),
                    "pdf_page_end": meta.get("pdf_page_end", 0),
                    "studyProgram_Url": meta.get("studyProgram_Url", ""),
                    "pdf_url": meta.get("pdf_url", "")
                }

    # Load processed_web JSON data (for _WEB namespaces)
    if WEB_PATH.exists():
        for wf in WEB_PATH.glob("*_web.json"):
            try:
                data = json.loads(wf.read_text(encoding="utf-8"))

                # Determine program and namespace
                if isinstance(data, list):
                    if not data:
                        continue
                    first_meta = data[0].get("metadata", {})
                    prog = first_meta.get("studyProgramAbbrev")
                    namespace = f"{prog}_WEB" if prog else "FBM_WEB"
                    seen_namespaces.add(namespace)

                    for rec in data:
                        rid = rec.get("id")
                        if not rid:
                            continue
                        txt = (rec.get("text") or "").strip()
                        if not txt:
                            continue
                        ID_TO_TEXT[rid] = txt
                        meta = rec.get("metadata") or {}
                        ID_TO_META[rid] = {
                            "studyProgramAbbrev": prog or "FBM",
                            "category": meta.get("category", ""),
                            "section": meta.get("section", ""),
                            "links": meta.get("links", []),
                            "source": meta.get("source", ""),
                        }

                elif isinstance(data, dict):
                    meta = data.get("metadata") or {}
                    prog = meta.get("studyProgramAbbrev")
                    namespace = f"{prog}_WEB" if prog else "FBM_WEB"
                    seen_namespaces.add(namespace)
                    rid = data.get("id")
                    if rid and data.get("text"):
                        ID_TO_TEXT[rid] = data["text"]
                        ID_TO_META[rid] = {
                            "studyProgramAbbrev": prog or "FBM",
                            "category": meta.get("category", ""),
                            "section": meta.get("section", ""),
                            "links": meta.get("links", []),
                            "source": meta.get("source", ""),
                        }

            except Exception as e:
                print(f"Error loading {wf.name}: {e}")

    AVAILABLE_NAMESPACES.clear()
    AVAILABLE_NAMESPACES.extend(sorted(seen_namespaces))

    print(f"Loaded {len(ID_TO_TEXT)} records across {len(AVAILABLE_NAMESPACES)} namespaces.")
