# Embed and upload all normalized + PDF chunk files into Pinecone

import os
import json
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv
from pinecone import Pinecone
import openai

# Setup
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX"))

EMBED_MODEL = "text-embedding-3-large"
BATCH = 100

ROOTS = [
    Path("backend/data/normalized"),                     # JSON-based
    Path("backend/data/MHB_Alle_Studiengaenge")          # scattered PDFs and PO jsonl chunks
]

# Helpers
def find_jsonl_files(roots: List[Path]) -> List[Path]:
    files = []
    for root in roots:
        for p in root.rglob("*.jsonl"):
            if any(part.startswith(".") for part in p.parts):
                continue
            if p.name.startswith(".") or p.name.startswith("all_"):
                continue
            files.append(p)
    return files

def embed_batch(texts: List[str]) -> List[List[float]]:
    res = openai.embeddings.create(model=EMBED_MODEL, input=texts)
    return [d.embedding for d in res.data]

# Upload
def upload_file(path: Path):
    print(f"[upload] File: {path.name}")
    total = 0
    with path.open("r", encoding="utf-8") as f:
        batch_ids, batch_texts, batch_meta = [], [], []

        for line in f:
            rec = json.loads(line)
            text = rec.get("text")
            if not text or len(text.strip()) < 20:
                continue

            rid = rec.get("id") or f"auto-{hash(text)}"
            ns = rec.get("namespace") or "default"
            md = rec.get("metadata") or {}

            batch_ids.append(rid)
            batch_texts.append(text.strip())
            batch_meta.append(md)

            if len(batch_ids) >= BATCH:
                vectors = [
                    {"id": batch_ids[i], "values": embed, "metadata": batch_meta[i]}
                    for i, embed in enumerate(embed_batch(batch_texts))
                ]
                index.upsert(vectors=vectors, namespace=ns)
                print(f"upserted {len(vectors)}")
                total += len(vectors)
                batch_ids, batch_texts, batch_meta = [], [], []

        # Final flush
        if batch_ids:
            vectors = [
                {"id": batch_ids[i], "values": embed, "metadata": batch_meta[i]}
                for i, embed in enumerate(embed_batch(batch_texts))
            ]
            index.upsert(vectors=vectors, namespace=ns)
            print(f"upserted {len(vectors)}")
            total += len(vectors)

    print(f"{path.name}: {total} vectors uploaded\n")

# Main
if __name__ == "__main__":
    all_files = find_jsonl_files(ROOTS)
    print(f"[scan] Found {len(all_files)} .jsonl files")
    for file in all_files:
        upload_file(file)
    print("All files uploaded to Pinecone.")