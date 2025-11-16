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
    """detect whether text is German or English."""
    t = (text or "").lower()

    # strong hint: German umlauts/ß
    if any(ch in t for ch in ("ä", "ö", "ü", "ß")):
        return "de"

    german_markers = [
        # Question / helpers (German forms)
        "wie", "was", "wer", "wo", "warum", "wieso", "weshalb", "wann", "wem", "wen", "wohin", "woher", "wozu",
        "werde", "werden", "bin", "bist", "sind", "seid", "sind",
        "welche", "welcher", "welches", "gibt es", "kann ich", "ist",
        "helfen", "hilfe", "informationen", "kontakt",
        "finden", "suche", "suchen", "erklären", "erkläre", "erklärt",
        "bedeuten", "bedeutet", "bedeutung",
        "unterscheiden", "unterschied", "unterschiede",

        # Uni / admin (German-only words)
        "hochschule", "fachbereich", "studium", "studierende", "studierenden",
        "studiengang", "studiengänge", "studienbüro", "erstsemester",
        "bewerbung", "zulassung", "einschreibung", "immatrikulation",
        "rückmeldung", "exmatrikulation",

        # Semester / timing
        "wintersemester", "sommersemester", "vorlesungszeit", "vorlesungsfreie zeit", "semesterferien",

        # Modules / exams (German forms)
        "modul", "modulhandbuch", "modulbeschreibung",
        "prüf", "prüfungsordnung", "klausur", "mündliche prüfung", "schriftliche prüfung",
        "hausarbeit", "leistungspunkte", "sws",

        # Teaching formats (German)
        "vorlesung", "übung", "veranstaltungsverzeichnis",

        # Study plan / requirements
        "studienordnung", "studienverlaufsplan", "wahlbereich", "wahlpflicht", "pflichtmodul", "schwerpunkt",

        # Theses / docs (German forms)
        "bachelorarbeit", "masterarbeit", "zeugnis",

        # Roles / misc
        "dozent", "dozentin", "praxissemester", "formular", "richtlinie",
    ]

    return "de" if any(m in t for m in german_markers) else "en"

