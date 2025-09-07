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

# Initialize Pinecone with environment variables
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

def load_jsonl(path: Path) -> List[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def convert_to_documents(records: List[dict]) -> List[Document]:
    documents = []
    for record in records:
        metadata = record.get("metadata", {}).copy()
        metadata["id"] = record.get("id")  # ensure ID always exists

        # Inject selected metadata fields into the embedded text
        module_name = metadata.get("module_name", "")
        study_program = metadata.get("studyProgramAbbrev", "")
        source_file = metadata.get("source_file", "")
        page_start = metadata.get("pdf_page_start", "")
        page_end = metadata.get("pdf_page_end", "")
        base_text = record["text"]

        enriched_text = f"Program: {study_program}\nModule: {module_name}\nSource: {source_file} (pp. {page_start}–{page_end})\n\n{base_text}"

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