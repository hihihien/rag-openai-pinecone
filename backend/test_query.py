import os, json
from dotenv import load_dotenv
from pinecone import Pinecone
import openai

load_dotenv()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX"))
openai.api_key = os.getenv("OPENAI_API_KEY")

EMBED_MODEL = "text-embedding-3-small"

def embed(q):
    return openai.embeddings.create(model=EMBED_MODEL, input=[q]).data[0].embedding

# Try a question for BMT
q = "Was lernt man in Ingenieurinformatik 1?"
vec = embed(q)
res = index.query(
    vector=vec,
    top_k=5,
    include_metadata=True,
    namespace="BMT",           # pick a program abbrev here
    filter=None                # can add {"season":{"$eq":"winter"}} etc.
)

for m in res.matches:
    md = m.metadata
    print(f"{m.id}  score={m.score:.3f}")
    print(f"  {md.get('moduleNumber')}  {md.get('moduleNameDe')}  {md.get('credits')} CP")
    print(f"  season={md.get('season')}  examType={md.get('examType')}  lang={md.get('heldInLanguage')}")
    print(f"  snippet: {md.get('snippet','')[:160]}...\n")