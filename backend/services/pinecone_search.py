import os
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from pinecone import Pinecone

from backend.services.loader import AVAILABLE_NAMESPACES

load_dotenv()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX"))

def build_filter(
    season: Optional[str] = None,
    exam_type: Optional[str] = None,
    min_credits: Optional[float] = None,
    max_credits: Optional[float] = None
) -> Optional[Dict[str, Any]]:
    f = {}
    if season:
        f["season"] = {"$eq": season}
    if exam_type:
        f["examType"] = {"$eq": exam_type}
    if min_credits or max_credits:
        r = {}
        if min_credits:
            r["$gte"] = min_credits
        if max_credits:
            r["$lte"] = max_credits
        f["creditPointsNum"] = r
    return f or None

def search_all_namespaces(
    vector: List[float],
    top_k: int,
    filter: Optional[Dict[str, Any]] = None,
    program: Optional[str] = None
):
    if program:
        return index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True,
            namespace=program,
            filter=filter
        ).matches

    all_matches = []
    for ns in AVAILABLE_NAMESPACES:
        res = index.query(
            vector=vector,
            top_k=top_k,  # query fully in each namespace
            include_metadata=True,
            namespace=ns,
            filter=filter
        )
        all_matches.extend(res.matches)

    return sorted(all_matches, key=lambda m: m.score or 0, reverse=True)[:top_k]
