"""
Use FastAPI
Prereqs:
- Normalized JSONL files in backend/data/normalized/*.jsonl  (from normalize_modules.py)
- Vectors uploaded to Pinecone (vector_upload.py)
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from unittest import result

from dotenv import load_dotenv
from fastapi import FastAPI,Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import openai
from pinecone import Pinecone


# =========================
# Config & Initialization
# =========================

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data" / "normalized"

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX"))

EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"
TOP_K = 8
SCORE_THRESHOLD = 0.58
PER_MODULE_CAP = 2
MAX_CONTEXT_CHUNKS = 6
MAX_CONTEXT_CHARS = 9000
AVAILABLE_NAMESPACES = sorted([p.stem for p in DATA_DIR.glob("*.jsonl")])

# ========== Text Store ==========
ID_TO_TEXT: Dict[str, str] = {}
ID_TO_META: Dict[str, Dict[str, Any]] = {}

def _build_full_text(rec):
    de = (rec.get("textDe") or "").strip()
    en = (rec.get("textEn") or "").strip()
    return f"{de}\n\n{en}" if de and en else de or en

def load_text_store():
    for jf in DATA_DIR.glob("*.jsonl"):
        with jf.open("r", encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                rid = rec.get("id")
                if not rid:
                    continue
                ID_TO_TEXT[rid] = _build_full_text(rec)
                meta = {
                    **rec.get("offer", {}),
                    **rec.get("module", {}),
                    **rec.get("program", {})
                }
                ID_TO_META[rid] = {
                    "studyProgramAbbrev": meta.get("studyProgramAbbrev"),
                    "moduleNumber": meta.get("moduleNumber"),
                    "moduleNameDe": meta.get("moduleNameDe"),
                    "moduleNameEn": meta.get("moduleNameEn"),
                    "season": meta.get("offeredInSeasonNorm"),
                    "credits": meta.get("creditPoints"),
                    "examType": meta.get("examType"),
                }

load_text_store()

# ========== FastAPI ==========
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def root():
    return {"message": "RAG Chatbot API is running"}

# ========== Schemas ==========
class QuestionRequest(BaseModel):
    question: str
    program: Optional[str] = None
    season: Optional[str] = None
    examType: Optional[str] = None
    minCredits: Optional[float] = None
    maxCredits: Optional[float] = None
    top_k: Optional[int] = None

class SourceItem(BaseModel):
    id: str
    moduleNumber: Optional[str] = None
    moduleNameDe: Optional[str] = None
    moduleNameEn: Optional[str] = None
    studyProgramAbbrev: Optional[str] = None
    season: Optional[str] = None
    credits: Optional[str] = None
    examType: Optional[str] = None
    score: Optional[float] = None

class AnswerResponse(BaseModel):
    answer: str
    sources: List[SourceItem]

# ========== Helpers ==========
def embed(text: str) -> List[float]:
    res = openai.embeddings.create(model=EMBED_MODEL, input=[text])
    return res.data[0].embedding

def detect_lang(text: str) -> str:
    t = text.lower()
    if any(word in t for word in ["wie", "modul", "studierende", "prüfung", "ects"]):
        return "de"
    return "en"

def build_prompt(context: str, question: str, lang: str) -> List[Dict[str, str]]:
    sys = {
        "de": "Du bist ein akademischer Assistent. Antworte nur mit dem gegebenen Kontext. Wenn du nichts findest, sage es deutlich.",
        "en": "You are an academic assistant. Only use the context. If you can't find anything, say so."
    }
    return [
        {"role": "system", "content": sys[lang]},
        {"role": "user", "content": f"Kontext:\n{context}\n\nFrage: {question}" if lang == "de" else f"Context:\n{context}\n\nQuestion: {question}"}
    ]

def build_filter(req: QuestionRequest) -> Optional[Dict[str, Any]]:
    f = {}
    if req.season: f["season"] = {"$eq": req.season}
    if req.examType: f["examType"] = {"$eq": req.examType}
    r = {}
    if req.minCredits: r["$gte"] = req.minCredits
    if req.maxCredits: r["$lte"] = req.maxCredits
    if r: f["creditPointsNum"] = r
    return f or None

def search_all_ns(qvec, top_k, flt, program):
    if program:
        return index.query(vector=qvec, top_k=top_k, include_metadata=True, namespace=program, filter=flt).matches
    all_matches = []
    for ns in AVAILABLE_NAMESPACES:
        res = index.query(vector=qvec, top_k=max(2, top_k // len(AVAILABLE_NAMESPACES)), include_metadata=True, namespace=ns, filter=flt)
        all_matches.extend(res.matches)
    return sorted(all_matches, key=lambda m: m.score or 0, reverse=True)[:top_k]

def build_context(matches) -> (str, List[SourceItem]):
    used, parts, sources = {}, [], []
    for m in matches:
        if m.score < SCORE_THRESHOLD: continue
        rid = m.id
        meta = ID_TO_META.get(rid, {})
        mod = meta.get("moduleNumber", "UNK")
        used[mod] = used.get(mod, 0) + 1
        if used[mod] > PER_MODULE_CAP: continue
        full = ID_TO_TEXT.get(rid) or m.metadata.get("snippet")
        if not full: continue
        header = f"[{meta.get('studyProgramAbbrev')}] {mod} • {meta.get('moduleNameDe') or meta.get('moduleNameEn')}"
        parts.append(f"{header}\n{'-'*len(header)}\n{full}")
        sources.append(SourceItem(
            id=rid,
            moduleNumber=mod,
            moduleNameDe=meta.get("moduleNameDe"),
            moduleNameEn=meta.get("moduleNameEn"),
            studyProgramAbbrev=meta.get("studyProgramAbbrev"),
            season=meta.get("season"),
            credits=meta.get("credits"),
            examType=meta.get("examType"),
            score=m.score
        ))
        if len(parts) >= MAX_CONTEXT_CHUNKS: break
    context = "\n\n".join(parts)
    return context[:MAX_CONTEXT_CHARS], sources

def ask_openai(context, question):
    lang = detect_lang(question)
    msgs = build_prompt(context, question, lang)
    res = openai.chat.completions.create(model=CHAT_MODEL, messages=msgs, temperature=0.2)
    return res.choices[0].message.content

# ========== Endpoints ==========

@app.post("/ask", response_model=AnswerResponse)
def ask(req: QuestionRequest):
    qvec = embed(req.question)
    flt = build_filter(req)
    matches = search_all_ns(qvec, req.top_k or TOP_K, flt, req.program)
    context, sources = build_context(matches)
    if not context:
        msg = "Ich konnte dazu nichts im Modulhandbuch finden." if detect_lang(req.question) == "de" else "I couldn't find anything relevant in the module handbook."
        return AnswerResponse(answer=msg, sources=[])
    answer = ask_openai(context, req.question)
    return AnswerResponse(answer=answer, sources=sources)

@app.post("/ask-simple", response_model=AnswerResponse)
def ask_simple(question: str = Body(..., media_type="text/plain")):
    return ask(QuestionRequest(question=question))