import json
import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
from tqdm import tqdm

# Load environment variables
load_dotenv()

# Create Pinecone client using new SDK
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

def load_jsonl(path: Path) -> List[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def convert_to_documents(records: List[dict]) -> List[Document]:
    documents = []
    for record in records:
        metadata = record.copy()  # copy all top-level fields into metadata

        # Extract individual fields for enrichment
        module_id = record.get("module_id", "")
        major_section = record.get("major_section", "")
        sub_section = record.get("sub_section", "")
        title = record.get("title", "")
        page_start = record.get("pdf_page_start", "")
        page_end = record.get("pdf_page_end", "")
        base_text = record.get("text", "")

        enriched_text = (
            f"Title: {title}\n"
            f"Module ID: {module_id}\n"
            f"Major Section: {major_section}\n"
            f"Sub Section: {sub_section}\n"
            f"Source: pp. {page_start}–{page_end}\n\n"
            f"{base_text}"
        )

        metadata["id"] = record.get("id")

        documents.append(Document(page_content=enriched_text, metadata=metadata))
    return documents

def embed_documents(docs: List[Document]) -> List[dict]:
    embeddings = OpenAIEmbeddings()
    vectors = []
    for doc in tqdm(docs, desc="Embedding documents"):
        vector = embeddings.embed_query(doc.page_content)
        vectors.append({
            "id": doc.metadata["id"],
            "values": vector,
            "metadata": doc.metadata
        })
    return vectors

def upload_to_pinecone(vectors: List[dict], namespace: str, index_name: str):
    index = pc.Index(index_name)
    print(f"Uploading to Pinecone namespace: {namespace}")
    for i in range(0, len(vectors), 100):
        batch = vectors[i:i+100]
        index.upsert(vectors=batch, namespace=namespace)
    print(f"Uploaded {len(vectors)} vectors to namespace '{namespace}'")

def process_and_upload(jsonl_path: str, namespace: str, index_name: str):
    print(f"\nLoading JSONL: {jsonl_path}")
    records = load_jsonl(Path(jsonl_path))
    print(f"Loaded {len(records)} records")

    docs = convert_to_documents(records)
    print(f"Prepared {len(docs)} documents for embedding")

    vectors = embed_documents(docs)
    print(f"Embedded {len(vectors)} documents")

    upload_to_pinecone(vectors, namespace, index_name)