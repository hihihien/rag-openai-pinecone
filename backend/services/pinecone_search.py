import os
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from pinecone import Pinecone

from services.loader import AVAILABLE_NAMESPACES

load_dotenv()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX"))

def build_filter(
    season: Optional[str] = None,
    exam_type: Optional[str] = None,
    min_credits: Optional[float] = None,
    max_credits: Optional[float] = None
) -> Optional[Dict[str, Any]]:
    """Builds a Pinecone metadata filter dictionary."""
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
    program: Optional[str] = None,
    namespaces: Optional[List[str]] = None
):
    """Query across namespaces, slightly boosting local program matches."""
    all_matches = []

    target_namespaces = namespaces or AVAILABLE_NAMESPACES

    for ns in target_namespaces:
        res = index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True,
            namespace=ns,
            filter=filter
        )
        for match in res.matches:
            # Small bias boost for matches from the user's study program
            if program and ns.startswith(program):
                match.score *= 1.05
            all_matches.append(match)

    # Sort by score and return top_k
    return sorted(all_matches, key=lambda m: m.score or 0, reverse=True)[:top_k]
