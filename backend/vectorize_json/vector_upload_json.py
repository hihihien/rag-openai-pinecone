#this was used for the merged jsonl files which were created from JS + PDF data
import os
import json
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from pinecone import Pinecone
import openai

# === CONFIG ===
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX"))

EMBED_MODEL = "text-embedding-3-large"
BATCH_SIZE = 100
MERGED_DIR = Path("backend/data/merged")

# === Embedding helper ===
def embed_batch(texts: List[str]) -> List[List[float]]:
    response = openai.embeddings.create(model=EMBED_MODEL, input=texts)
    return [r.embedding for r in response.data]

def sanitize_metadata(metadata: dict) -> dict:
    """Ensure all Pinecone metadata values are valid types."""
    clean = {}
    for k, v in metadata.items():
        if v is None:
            clean[k] = "no data"
        elif isinstance(v, (str, int, float, bool)):
            clean[k] = v
        elif isinstance(v, list) and all(isinstance(i, str) for i in v):
            clean[k] = v
        else:
            clean[k] = str(v)  # fallback: convert to string
    return clean

# === Upload logic ===
def upload_file(path: Path):
    print(f"[upload] Processing file: {path.name}")
    namespace = path.stem.split("_")[0]  # e.g., "BMI" from "BMI_merged.jsonl"

    batch_ids, batch_texts, batch_meta = [], [], []
    total_uploaded = 0

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            text = rec.get("text", "").strip()
            if not text or len(text) < 20:
                continue

            rid = rec.get("id") or f"auto-{hash(text)}"
            raw_metadata = rec.get("metadata", {}) or {}
            metadata = sanitize_metadata(raw_metadata)

            batch_ids.append(rid)
            batch_texts.append(text)
            batch_meta.append(metadata)

            if len(batch_ids) >= BATCH_SIZE:
                vectors = [
                    {"id": batch_ids[i], "values": vec, "metadata": batch_meta[i]}
                    for i, vec in enumerate(embed_batch(batch_texts))
                ]
                index.upsert(vectors=vectors, namespace=namespace)
                print(f"  • Upserted {len(vectors)} vectors to namespace '{namespace}'")
                total_uploaded += len(vectors)
                batch_ids, batch_texts, batch_meta = [], [], []

        # Final flush
        if batch_ids:
            vectors = [
                {"id": batch_ids[i], "values": vec, "metadata": batch_meta[i]}
                for i, vec in enumerate(embed_batch(batch_texts))
            ]
            index.upsert(vectors=vectors, namespace=namespace)
            print(f"  • Upserted {len(vectors)} vectors to namespace '{namespace}'")
            total_uploaded += len(vectors)

    print(f"[✓] {path.name}: Uploaded {total_uploaded} vectors.\n")

# === Main script ===
if __name__ == "__main__":
    merged_files = sorted(MERGED_DIR.glob("*.jsonl"))
    if not merged_files:
        print("No merged files found in 'data/merged/'.")
        exit(1)

    print(f"[•] Found {len(merged_files)} merged files:")
    for file in merged_files:
        print(f"  - {file.name}")

    for file in merged_files:
        upload_file(file)

    print("[✓] All merged modules uploaded to Pinecone.")
