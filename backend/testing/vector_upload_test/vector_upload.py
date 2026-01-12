"""
Embed and upload normalized JSONL module records into Pinecone.

- Reads all JSONL files under backend/data/normalized/*.jsonl
- Builds embeddings from textDe + textEn 
- Upserts to Pinecone with:
    id         = record["id"]
    namespace  = record["namespace"]  (program abbreviation, e.g., "MMI")
    metadata   = compact, filter-friendly fields (+ optional snippet)
- Keeps full text only in JSONL (for rehydration at query time)
"""

import os
import json
from pathlib import Path
from typing import Iterable, Dict, Any, List, Optional

from dotenv import load_dotenv
from pinecone import Pinecone
import openai

# Config
HERE = Path(__file__).resolve()
BACKEND_DIR = HERE.parent
NORM_DIR = BACKEND_DIR / "data" / "normalized"

# include a short snippet (first N chars) in Pinecone metadata
INCLUDE_SNIPPET = True
SNIPPET_CHARS = 800  # safe size for preview without bloating metadata

BATCH = 100
EMBED_MODEL = "text-embedding-3-small"  # good trade-off cost/quality

# Init
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = os.getenv("PINECONE_INDEX")
if not index_name:
    raise RuntimeError("PINECONE_INDEX is not set in environment.")
index = pc.Index(index_name)


# Helpers
def iter_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

def embedding_inputs(rec: Dict[str, Any]) -> Optional[str]:
    # Build multilingual input text
    de = (rec.get("textDe") or "").strip()
    en = (rec.get("textEn") or "").strip()
    if not de and not en:
        return None
    # Order DE then EN 
    if de and en:
        return f"{de}\n\n{en}"
    return de or en

def compact_metadata(rec: Dict[str, Any]) -> Dict[str, Any]:
    """Pick filter-friendly fields; avoid huge nested blobs or full text."""
    prog = rec.get("program", {}) or {}
    offer = rec.get("offer", {}) or {}
    module = rec.get("module", {}) or {}

    md = {
        # ID basics
        "studyProgramAbbrev": prog.get("studyProgramAbbrev"),
        "studyProgramId": prog.get("studyProgramId"),
        "studyProgramName": prog.get("studyProgramName"),
        "degree": prog.get("degree"),
        "examinationRegulation": prog.get("examinationRegulation"),

        # Offer filters
        "moduleNumber": offer.get("moduleNumber"),
        "creditPoints": offer.get("creditPoints"),
        "creditPointsNum": offer.get("creditPointsNum"),
        "season": offer.get("offeredInSeasonNorm") or offer.get("offeredInSeason"),
        "isGraded": offer.get("isGraded"),
        "offerType": offer.get("offerType"),
        "suggestedSemesterOfAttendance": offer.get("suggestedSemesterOfAttendance"),

        # Module filters
        "moduleId": module.get("moduleId"),
        "moduleNameDe": module.get("moduleNameDe"),
        "moduleNameEn": module.get("moduleNameEn"),
        "moduleAbbrevDe": module.get("moduleAbbrevDe"),
        "moduleAbbrevEn": module.get("moduleAbbrevEn"),
        "examType": module.get("examType"),
        "heldInLanguage": module.get("heldInLanguage"),
        "heldInLanguageNorm": module.get("heldInLanguageNorm"),
        "durationSemesters": module.get("durationSemesters"),

        # Tags + provenance
        "langTags": rec.get("langTags"),
        "seasonTags": rec.get("seasonTags"),
        "version": rec.get("version"),
        "source_type": rec.get("source_type"),
        "source_program_file": rec.get("source_program_file"),
        "lastUpdated": rec.get("lastUpdated"),
    }

    # short snippet for UX (preview only; not full text!)
    if INCLUDE_SNIPPET:
        # Prefer DE snippet if present, otherwise EN
        de = (rec.get("textDe") or "").strip()
        en = (rec.get("textEn") or "").strip()
        snippet_src = de if de else en
        if snippet_src:
            md["snippet"] = snippet_src[:SNIPPET_CHARS]

    # Remove None to keep metadata compact
    return {k: v for k, v in md.items() if v is not None}


def embed_batch(texts: List[str]) -> List[List[float]]:
    resp = openai.embeddings.create(model=EMBED_MODEL, input=texts)
    # openai lib returns embeddings in order
    return [d.embedding for d in resp.data]


# Main
def main():
    if not NORM_DIR.exists():
        raise RuntimeError(f"Normalized dir not found: {NORM_DIR}")

    jsonl_files = sorted(NORM_DIR.glob("*.jsonl"))
    if not jsonl_files:
        raise RuntimeError(f"No JSONL files found under {NORM_DIR}")

    total = 0
    for jf in jsonl_files:
        # Namespace = program abbrev == filename stem (e.g., "MMI")
        namespace = jf.stem
        print(f"\n[upload] File: {jf.name}  →  namespace: {namespace}")

        # Collect records for this file
        buf_records: List[Dict[str, Any]] = []
        buf_texts: List[str] = []
        buf_ids: List[str] = []
        buf_mds: List[Dict[str, Any]] = []

        def flush():
            nonlocal buf_records, buf_texts, buf_ids, buf_mds, total
            if not buf_texts:
                return
            embs = embed_batch(buf_texts)
            payload = [{
                "id": buf_ids[i],
                "values": embs[i],
                "metadata": buf_mds[i]
            } for i in range(len(embs))]
            index.upsert(vectors=payload, namespace=namespace)
            total += len(payload)
            print(f"  upserted: {total} / (running total)")
            # clear buffers
            buf_records, buf_texts, buf_ids, buf_mds = [], [], [], []

        for rec in iter_jsonl(jf):
            text = embedding_inputs(rec)
            if not text:
                continue
            md = compact_metadata(rec)
            rid = rec.get("id")
            if not rid:
                continue

            buf_records.append(rec)
            buf_texts.append(text)
            buf_ids.append(rid)
            buf_mds.append(md)

            if len(buf_texts) >= BATCH:
                flush()

        # tail
        flush()

    print(f"\nDone. Total vectors upserted: {total}")


if __name__ == "__main__":
    main()