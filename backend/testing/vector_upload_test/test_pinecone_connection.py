from pinecone import Pinecone
from dotenv import load_dotenv  
import os

load_dotenv()

api_key = os.getenv("PINECONE_API_KEY")
index_name = os.getenv("PINECONE_INDEX")

print("using API Key:", api_key)
pc = Pinecone(api_key=api_key)

print("available indexes:", pc.list_indexes().names())

index = pc.Index(index_name)
print(f"successfully connected to index: {index_name}")
