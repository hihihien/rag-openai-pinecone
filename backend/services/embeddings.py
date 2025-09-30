import openai
from typing import List
import logging

EMBED_MODEL = "text-embedding-3-large"

def embed(text: str) -> List[float]:
    """Embed a single text using OpenAI Embedding API."""
    try:
        res = openai.embeddings.create(model=EMBED_MODEL, input=[text])
        return res.data[0].embedding
    except Exception as e:
        logging.error(f"[embedding] Error while embedding single text: {e}")
        return []

def embed_batch(texts: List[str]) -> List[List[float]]:
    """Embed a batch of texts."""
    try:
        res = openai.embeddings.create(model=EMBED_MODEL, input=texts)
        return [d.embedding for d in res.data]
    except Exception as e:
        logging.error(f"[embedding] Error while embedding batch: {e}")
        return [[] for _ in texts]

def detect_lang(text: str) -> str:
    """Heuristically detect whether text is German or English."""
    t = text.lower()
    german_markers = ["wie", "modul", "studierende", "prüfung", "ects", "vorlesung", "cp", "sws"]
    return "de" if any(word in t for word in german_markers) else "en"

