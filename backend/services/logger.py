import json
from datetime import datetime
from pathlib import Path
from typing import List
from backend.services.context_builder import SourceItem

# where logs are stored
LOG_FILE = Path(__file__).resolve().parent.parent / "logs" / "chat_log.jsonl"
LOG_FILE.parent.mkdir(exist_ok=True)

def save_log(question: str, answer: str, sources: List[SourceItem]):
    """Append a single Q&A log entry into logs/chat_log.jsonl"""
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "question": question,
        "answer": answer,
        "sources": [s.dict() for s in sources]
    }
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")