import json
import requests
from datetime import datetime
from pathlib import Path
from typing import List
from services.context_builder import SourceItem
import os

LOG_FILE = Path(__file__).resolve().parent.parent / "logs" / "chat_log.jsonl"
LOG_FILE.parent.mkdir(exist_ok=True)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def save_log(question: str, answer: str, sources: List[SourceItem], session_id: str = "", program: str = ""):
    """Append Q&A log entry locally and to Supabase."""
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "session_id": session_id,
        "program": program,
        "question": question,
        "answer": answer,
        "sources": [s.dict() for s in sources],
    }

    # Local backup
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # Upload to Supabase 
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            r = requests.post(
                f"{SUPABASE_URL}/rest/v1/chat_logs",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal"
                },
                json=entry
            )
            if r.status_code >= 300:
                print(f"[supabase] Failed: {r.status_code} {r.text}")
            else:
                print("[supabase] Log saved.")
        except Exception as e:
            print(f"[supabase] Error: {e}")
