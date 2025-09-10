import json
import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
from tqdm import tqdm

# Load env vars
load_dotenv()

# Init Pinecone client
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Paths and constants
jsonl_path = "backend/data/MHB_Alle_Studiengaenge/MHB_BDAISY_PO21/PO21_796_paragraph_chunks.jsonl"
namespace = "DAISY_PO21_pdf"
index_name = os.getenv("PINECONE_INDEX")

if not index_name:
    raise RuntimeError("PINECONE_INDEX is not set in the .env file.")

# --- Functions ---

def load_jsonl(path: Path) -> List[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def convert_to_documents(records: List[dict]) -> List[Document]:
    documents = []
    for record in records:
        metadata = record.copy()  # full record into metadata

        section = record.get("section", "")
        paragraph = record.get("paragraph", "")
        subsection = record.get("subsection_number", "")
        page_start = record.get("pdf_page_start", "")
        page_end = record.get("pdf_page_end", "")
        text = record.get("text", "")

        enriched_text = (
            f"Section: {section}\n"
            f"Paragraph: {paragraph}\n"
            f"Subsection: {subsection}\n"
            f"Source: pp. {page_start}–{page_end}\n\n"
            f"{text}"
        )

        documents.append(Document(
            page_content=enriched_text,
            metadata=metadata
        ))
    return documents

def embed_documents(docs: List[Document]) -> List[dict]:
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vectors = []
    for doc in tqdm(docs, desc="Embedding paragraphs"):
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

# --- Main ---
print(f"\nLoading JSONL: {jsonl_path}")
records = load_jsonl(Path(jsonl_path))
print(f"Loaded {len(records)} records")

docs = convert_to_documents(records)
print(f"Prepared {len(docs)} documents for embedding")

vectors = embed_documents(docs)
print(f"Embedded {len(vectors)} documents")

upload_to_pinecone(vectors, namespace, index_name)