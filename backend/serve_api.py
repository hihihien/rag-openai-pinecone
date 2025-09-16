from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional, List

from services.loader import load_text_store, AVAILABLE_NAMESPACES
from services.embeddings import embed
from services.pinecone_search import build_filter, search_all_namespaces
from services.context_builder import build_context, SourceItem
from services.prompt_utils import ask_openai

# Load in-memory data
load_text_store()

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
    return {"message": "RAG Chatbot API is running", "namespaces": AVAILABLE_NAMESPACES}

class QuestionRequest(BaseModel):
    question: str
    history: Optional[List[Dict[str,str]]] = None
    program: Optional[str] = None
    season: Optional[str] = None
    examType: Optional[str] = None
    minCredits: Optional[float] = None
    maxCredits: Optional[float] = None
    top_k: Optional[int] = None

class AnswerResponse(BaseModel):
    answer: str
    sources: List[SourceItem]

@app.post("/ask", response_model=AnswerResponse)
def ask(req: QuestionRequest):
    qvec = embed(req.question)
    flt = build_filter(
        season=req.season,
        exam_type=req.examType,
        min_credits=req.minCredits,
        max_credits=req.maxCredits
    )
    matches = search_all_namespaces(qvec, req.top_k or 8, filter=flt, program=req.program)
    context, sources = build_context(matches)

    if not context:
        msg = "Ich konnte dazu nichts im Modulhandbuch finden." if req.question.lower().startswith("wie") else "I couldn't find anything relevant in the module handbook."
        return AnswerResponse(answer=msg, sources=[])

    answer = ask_openai(context, req.question, req.history or [])
    return AnswerResponse(answer=answer, sources=sources)

@app.post("/ask-simple", response_model=AnswerResponse)
def ask_simple(question: str = Body(..., media_type="text/plain")):
    return ask(QuestionRequest(question=question))
