import os
import json
from pathlib import Path
from dotenv import load_dotenv
from pinecone import Pinecone
import openai
from typing import List, Dict, Any

# === CONFIG ===
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX"))

DATA_DIR = Path("backend/data/processed_web")
EMBED_MODEL = "text-embedding-3-large"


# === Helpers ===
def embed_text(text: str) -> List[float]:
    """Create embedding for one text."""
    res = openai.embeddings.create(model=EMBED_MODEL, input=[text])
    return res.data[0].embedding


def sanitize_metadata(meta: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure all Pinecone metadata values are valid types."""
    clean = {}
    for k, v in meta.items():
        if v is None:
            clean[k] = "no data"
        elif isinstance(v, (str, int, float, bool)):
            clean[k] = v
        elif isinstance(v, list):
            # Convert list of dicts (like links) into a readable string
            if all(isinstance(i, dict) for i in v):
                link_texts = []
                for link in v:
                    label = link.get("text", "")
                    url = link.get("url", "")
                    if label and url:
                        link_texts.append(f"{label} ({url})")
                    elif label:
                        link_texts.append(label)
                clean[k] = ", ".join(link_texts)
            elif all(isinstance(i, str) for i in v):
                clean[k] = v
            else:
                clean[k] = str(v)
        else:
            clean[k] = str(v)
    return clean


def build_embedding_text(data: dict) -> str:
    """Combine main text with metadata details like category, section, and link texts."""
    text = data.get("text", "").strip()
    meta = data.get("metadata", {}) or {}
    parts = [text]

    # Include metadata fields to enrich embeddings
    if meta.get("category"):
        parts.append(f"Kategorie: {meta['category']}")
    if meta.get("section"):
        parts.append(f"Abschnitt: {meta['section']}")

    # Append links (both text and URLs) for semantic and factual grounding
    if meta.get("links"):
        link_texts = []
        for link in meta["links"]:
            if isinstance(link, dict):
                label = link.get("text", "")
                url = link.get("url", "")
                if label and url:
                    link_texts.append(f"{label} ({url})")
                elif label:
                    link_texts.append(label)
        if link_texts:
            parts.append("Studiengänge / Programme: " + ", ".join(link_texts))

    return "\n".join(parts)


def upload_file(path: Path):
    """Upload one .json file from processed_web."""
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # Handle both list of records and single record
    records = data if isinstance(data, list) else [data]

    namespace = path.stem.replace("_web", "").upper() + "_WEB"

    print(f"Processing {path.name} → namespace '{namespace}'")

    for i, rec in enumerate(records, start=1):
        # Create ID if missing
        rid = rec.get("id") or f"WEB_{namespace}_{i:03d}"
        emb_text = build_embedding_text(rec)
        if not emb_text or len(emb_text) < 10:
            continue

        vec = embed_text(emb_text)
        meta = sanitize_metadata(rec.get("metadata", {}))
        meta_with_snippet = {**meta, "snippet": emb_text[:300]}

        index.upsert(
            vectors=[{"id": rid, "values": vec, "metadata": meta_with_snippet}],
            namespace=namespace
        )

    print(f"Finished uploading {len(records)} records to {namespace}\n")


# === MAIN ===
if __name__ == "__main__":
    json_files = sorted(DATA_DIR.glob("*.json"))
    if not json_files:
        print("No JSON files found in processed_web/")
        exit(1)

    for f in json_files:
        upload_file(f)

    print("All web data uploaded to Pinecone.")
