import os
import json
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv
from pinecone import Pinecone
import openai

# ========== Config ==========
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX"))

EMBED_MODEL = "text-embedding-3-large"
BATCH = 100

# Folder for exported .jsonl files (from generate_*.py scripts)
PROCESSED_DIR = Path("backend/data/processed_json")

# ========== Embedding Helper ==========
def embed_batch(texts: List[str]) -> List[List[float]]:
    res = openai.embeddings.create(model=EMBED_MODEL, input=texts)
    return [d.embedding for d in res.data]

# ========== Upload Logic ==========
def upload_file(path: Path):
    print(f"[upload] File: {path.name}")
    total = 0

    with path.open("r", encoding="utf-8") as f:
        batch_ids, batch_texts, batch_meta = [], [], []

        for line in f:
            rec = json.loads(line)
            text = rec.get("text", "").strip()
            if not text or len(text) < 20:
                continue

            rid = rec.get("id") or f"auto-{hash(text)}"
            namespace = rid.split("__")[0] if "__" in rid else "default"
            meta_raw = rec.get("metadata") or {}
            meta = {k: v for k, v in meta_raw.items() if v is not None}

            batch_ids.append(rid)
            batch_texts.append(text)
            batch_meta.append(meta)

            if len(batch_ids) >= BATCH:
                vectors = [
                    {"id": batch_ids[i], "values": embed, "metadata": batch_meta[i]}
                    for i, embed in enumerate(embed_batch(batch_texts))
                ]
                index.upsert(vectors=vectors, namespace=namespace)
                print(f"  upserted {len(vectors)}")
                total += len(vectors)
                batch_ids, batch_texts, batch_meta = [], [], []

        # Final flush
        if batch_ids:
            vectors = [
                {"id": batch_ids[i], "values": embed, "metadata": batch_meta[i]}
                for i, embed in enumerate(embed_batch(batch_texts))
            ]
            index.upsert(vectors=vectors, namespace=namespace)
            print(f"  upserted {len(vectors)}")
            total += len(vectors)

    print(f"{path.name}: {total} vectors uploaded\n")

# ========== Main ==========
if __name__ == "__main__":
    jsonl_files = sorted(PROCESSED_DIR.glob("*.jsonl"))
    if not jsonl_files:
        print("No files found in 'processed_json' folder.")
        exit(1)

    print(f"[scan] Found {len(jsonl_files)} processed .jsonl files")
    for file in jsonl_files:
        upload_file(file)
    print(" All JSON module files uploaded to Pinecone.")
