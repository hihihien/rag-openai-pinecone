from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

from services.loader import load_text_store, AVAILABLE_NAMESPACES
from services.embeddings import embed, detect_lang
from services.pinecone_search import build_filter, search_all_namespaces
from services.context_builder import build_context, SourceItem
from services.prompt_utils import ask_openai
from services.logger import save_log

# === Simple program inference (substring style) ===
def infer_programs_simple(text: str) -> List[str]:
    t = (text or "").lower()
    hits: List[str] = []

    # Abbreviations first (cheap and helpful)
    if "btb" in t: hits.append("BTB")
    if "bmt" in t: hits.append("BMT")
    if "bmi" in t: hits.append("BMI")
    if "mmi" in t: hits.append("MMI")
    if "bcsim" in t or "csim" in t: hits.append("BCSIM")
    if "bdaisy" in t or "daisy" in t: hits.append("BDAISY")
    if "mar" in t: hits.append("MAR")

    # German/English names → abbrev (your exact style)
    if "ton und bild" in t:
        hits.append("BTB")
    if "medientechnik" in t:
        hits.append("BMT")

    # Medieninformatik → BMI vs MMI (master cues)
    if "medieninformatik" in t:
        if ("master" in t) or ("msc" in t) or ("m.sc" in t):
            hits.append("MMI")
        else:
            hits.append("BMI")

    if "creative, synthetic and interactive media" in t:
        hits.append("BCSIM")

    if ("data science, ai und intelligente systeme" in t) or ("daisy" in t):
        hits.append("BDAISY")

    if "applied research in digital media technologies" in t:
        hits.append("MAR")

    # de-dup while preserving order
    seen = set()
    return [p for p in hits if not (p in seen or seen.add(p))]


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
    # decide target programs for each request only
    if req.program:
        prog = (req.program or "").upper()
        target_programs = [prog]
    else:
        target_programs = infer_programs_simple(req.question)  

    # Select namespaces to search
    namespaces = ["FBM_WEB"]
    if target_programs:
        # include only namespaces that actually exist
        added_any = False
        for p in target_programs:
            for ns in (p, f"{p}_WEB"):
                if ns in AVAILABLE_NAMESPACES:
                    namespaces.append(ns)
                    added_any = True
        # fallback to global search if none of the inferred namespaces exist
        if not added_any:
            namespaces.extend(AVAILABLE_NAMESPACES)
    else:
        # when no program is provided or inferred, then search everything
        namespaces.extend(AVAILABLE_NAMESPACES)

    flt = build_filter(
        season=req.season,
        exam_type=req.examType,
        min_credits=req.minCredits,
        max_credits=req.maxCredits
    )

    # Embed with augment with inferred codes if any
    query_for_embed = (
        req.question if not target_programs
        else f"{req.question} ({', '.join(target_programs)})"
    )
    qvec = embed(query_for_embed)

    # use first program as primary for small score bias
    primary = (req.program.upper() if req.program else (target_programs[0] if target_programs else None))

    # perform vector search across namespaces
    matches = search_all_namespaces(
        vector=qvec,
        top_k=req.top_k or 8,
        filter=flt,
        program=primary,
        namespaces=namespaces
    )

    context, sources = build_context(matches)

    if not context:
        lang = detect_lang(req.question)
        msg = (
            "Ich konnte dazu nichts in den Daten dieses Chatbots finden."
            if lang == "de"
            else "I couldn't find anything relevant in the chatbot's data."
        )
        save_log(req.question, msg, [])
        return AnswerResponse(answer=msg, sources=[], program=(req.program or "").upper())

    answer = ask_openai(context, req.question, req.history or [])

    # Build footer
    footer_lines = ["**Quellen und weiterführende Seiten:**"]
    seen_links = set()

    for src in sources[:5]:
        # PDF references
        if src.pdfUrl and src.pdfUrl not in seen_links:
            label = f"PDF Modulhandbuch {src.studyProgramAbbrev or ''}".strip()
            footer_lines.append(f"- [{label} (Seite {src.pdfPageStart}–{src.pdfPageEnd})]({src.pdfUrl})")
            seen_links.add(src.pdfUrl)

        # Study program URL
        if src.studyProgramUrl and src.studyProgramUrl not in seen_links:
            label = (
                f"{src.studyProgramAbbrev} Studiengangsseite"
                if src.studyProgramAbbrev else
                "Fachbereich Medien Seite"
            )
            footer_lines.append(f"- [{label}]({src.studyProgramUrl})")
            seen_links.add(src.studyProgramUrl)

        # Web links
        if src.links:
            for link in src.links:
                link_label = link.get("text", "").strip()
                link_url = link.get("url", src.source)

                # Skip if no label or URL
                if not link_label or not link_url:
                    continue

                if link_url not in seen_links:
                    footer_lines.append(f"- [{link_label}]({link_url})")
                    seen_links.add(link_url)

        elif src.source and src.source not in seen_links:
            label = (
                f"{src.studyProgramAbbrev} Studiengangsseite"
                if src.studyProgramAbbrev else
                "Fachbereich Medien Seite"
            )
            footer_lines.append(f"- [{label}]({src.source})")
            seen_links.add(src.source)

    footer = "\n".join(footer_lines) if len(footer_lines) > 1 else ""
    final_answer = f"{answer.strip()}\n\n{footer}" if footer else answer.strip()

    save_log(req.question, final_answer, sources, program=(req.program or "").upper())
    return AnswerResponse(answer=final_answer, sources=sources)


@app.post("/ask-simple", response_model=AnswerResponse)
def ask_simple(question: str = Body(..., media_type="text/plain")):
    return ask(QuestionRequest(question=question))
