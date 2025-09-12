import os
from dotenv import load_dotenv
from services.embeddings import embed
from services.pinecone_search import search_all_namespaces
from services.loader import ID_TO_TEXT, ID_TO_META, load_text_store

# Load env + in-memory text store
load_dotenv()
load_text_store()

# === Example question (change this) ===
QUESTION = "Welche Module gibt es im Studiengang BMT?"

# 1. Embed the question
qvec = embed(QUESTION)

# 2. Query Pinecone (top 5 matches, across all namespaces)
matches = search_all_namespaces(qvec, top_k=5)

# 3. Print results
print(f"\nQuery: {QUESTION}\n")
for m in matches:
    rid = m.id
    score = m.score
    meta = ID_TO_META.get(rid, {})
    text = ID_TO_TEXT.get(rid, "")[:300]  # show first 300 chars

    print("="*80)
    print(f"ID: {rid}")
    print(f"Score: {score:.4f}")
    print(f"Metadata: {meta}")
    print(f"Text snippet: {text}")