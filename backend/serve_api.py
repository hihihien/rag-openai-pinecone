from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

from services.loader import load_text_store, AVAILABLE_NAMESPACES
from services.embeddings import embed
from services.pinecone_search import build_filter, search_all_namespaces
from services.context_builder import build_context, SourceItem
from services.prompt_utils import ask_openai
from services.logger import save_log

# Load vector metadata (ID_TO_TEXT, ID_TO_META)
load_text_store()

# FastAPI setup
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
    return {
        "message": "RAG Chatbot API is running",
        "namespaces": AVAILABLE_NAMESPACES
    }


class QuestionRequest(BaseModel):
    question: str
    history: Optional[List[dict]] = None
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

    # Select namespaces to search
    namespaces = ["FBM_WEB"]
    if req.program:
        namespaces.append(req.program)
        namespaces.append(f"{req.program}_WEB")
    else:
        namespaces.extend(AVAILABLE_NAMESPACES)

    flt = build_filter(
        season=req.season,
        exam_type=req.examType,
        min_credits=req.minCredits,
        max_credits=req.maxCredits
    )

    # Perform vector search across namespaces
    matches = search_all_namespaces(
        vector=qvec,
        top_k=req.top_k or 8,
        filter=flt,
        program=req.program,
        namespaces=namespaces
    )

    context, sources = build_context(matches)

    if not context:
        msg = (
            "Ich konnte dazu nichts im Modulhandbuch finden."
            if req.question.lower().startswith("wie")
            else "I couldn't find anything relevant in the module handbook."
        )
        save_log(req.question, msg, [])
        return AnswerResponse(answer=msg, sources=[])

    answer = ask_openai(context, req.question, req.history or [])

    # Build footer with references
    footer_lines = ["Referenzen:"]
    seen_links = set()
    for src in sources[:3]:
        if src.pdfUrl and src.pdfUrl not in seen_links:
            footer_lines.append(f" - PDF Seite: {src.pdfUrl} (Seite {src.pdfPageStart}–{src.pdfPageEnd})")
            seen_links.add(src.pdfUrl)
        if src.studyProgramUrl and src.studyProgramUrl not in seen_links:
            footer_lines.append(f" - Studiengangsseite: {src.studyProgramUrl}")
            seen_links.add(src.studyProgramUrl)
        if hasattr(src, "source") and src.source and src.source not in seen_links:
            footer_lines.append(f" - Quelle: {src.source}")
            seen_links.add(src.source)
    footer = "\n".join(footer_lines)

    final_answer = answer.strip() + "\n\n" + footer
    save_log(req.question, final_answer, sources)
    return AnswerResponse(answer=final_answer, sources=sources)


@app.post("/ask-simple", response_model=AnswerResponse)
def ask_simple(question: str = Body(..., media_type="text/plain")):
    return ask(QuestionRequest(question=question))
