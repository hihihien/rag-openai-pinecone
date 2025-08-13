from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import openai
from pinecone import Pinecone
import os

# Load env variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_env = os.getenv("PINECONE_ENV")
pinecone_index_name = os.getenv("PINECONE_INDEX")

# Init FastAPI app
app = FastAPI()

# Allow frontend access
origins=[
        "http://localhost:3000",
        "https://rag-openai-pinecone.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to Pinecone index
pc = Pinecone(api_key=pinecone_api_key)
index = pc.Index(pinecone_index_name)

# Request body
class QuestionRequest(BaseModel):
    question: str

# Helper: embed a question
def embed_question(text):
    res = openai.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    return res.data[0].embedding

# Helper: call OpenAI chat with context
def ask_openai(context, question):
    prompt = f"""
Du bist ein akademischer Assistent und hilfst Studierenden, ihre Module im Masterstudiengang Medieninformatik zu verstehen.

Hier sind relevante Auszüge aus dem Modulhandbuch:

{context}

Bitte beantworte die folgende Frage ausführlich und auf Deutsch:

{question}
"""
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content

# Main endpoint
@app.post("/ask")
async def ask_question(req: QuestionRequest):
    question = req.question
    question_vector = embed_question(question)

    # Query Pinecone
    result = index.query(
        vector=question_vector,
        top_k=5,
        include_metadata=True
    )

    # Extract matched content
    context_chunks = []
    for match in result.matches:
        if "text" in match.metadata:
            context_chunks.append(match.metadata["text"])
        elif "content" in match.metadata:
            context_chunks.append(match.metadata["content"])
        else:
            # Build from title/module ID
            fallback = f"[{match.metadata.get('module_id', '')}] {match.metadata.get('title', '')}"
            context_chunks.append(fallback)

    context = "\n\n".join(context_chunks)

    # Ask OpenAI
    answer = ask_openai(context, question)

    return {"answer": answer}

# Optional: test root route
@app.get("/")
def read_root():
    return {"message": "RAG Chatbot API is running"}
