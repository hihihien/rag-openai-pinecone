import os
import json
from dotenv import load_dotenv
import openai
from pinecone import Pinecone

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_env = os.getenv("PINECONE_ENV")
index_name = os.getenv("PINECONE_INDEX")

# Initialize Pinecone
pc = Pinecone(api_key=pinecone_api_key)
index = pc.Index(index_name)

# Load parsed module data
with open("data/modules.json", "r", encoding="utf-8") as f:
    raw_modules = json.load(f)

texts = [mod["content"] for mod in raw_modules if len(mod["content"]) >= 200]
metadatas = [{"module_id": mod["module_id"], "title": mod["title"]} for mod in raw_modules if len(mod["content"]) >= 200]
ids = [f"mod-{i}" for i in range(len(texts))]

# Embed with OpenAI
def embed_texts(texts):
    res = openai.embeddings.create(
        input=texts,
        model="text-embedding-3-small"
    )
    return [r.embedding for r in res.data]

# Upload in batches
BATCH_SIZE = 50
for i in range(0, len(texts), BATCH_SIZE):
    batch_texts = texts[i:i + BATCH_SIZE]
    batch_ids = ids[i:i + BATCH_SIZE]
    batch_metadatas = metadatas[i:i + BATCH_SIZE]
    batch_embeddings = embed_texts(batch_texts)

    vectors = [{
        "id": batch_ids[j],
        "values": batch_embeddings[j],
        "metadata": batch_metadatas[j]
    } for j in range(len(batch_ids))]

    index.upsert(vectors=vectors)
    print(f"Uploaded batch {i // BATCH_SIZE + 1} of {len(texts) // BATCH_SIZE + 1}")

print("All documents successfully embedded and uploaded to Pinecone.")