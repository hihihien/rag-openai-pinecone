import openai
from typing import List

EMBED_MODEL = "text-embedding-3-large"


def embed(text: str) -> List[float]:
    """Embed a single text using OpenAI Embedding API."""
    res = openai.embeddings.create(model=EMBED_MODEL, input=[text])
    return res.data[0].embedding


def detect_lang(text: str) -> str:
    """Heuristically detect whether text is German or English."""
    t = text.lower()
    if any(word in t for word in ["wie", "modul", "studierende", "prüfung", "ects"]):
        return "de"
    return "en"
