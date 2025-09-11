from shared_uploader import process_and_upload
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Set parameters for MMI
jsonl_path = "backend/data/processed_pdf/MMI_MHB_PO2025_chunks.jsonl"
namespace = "MMI_pdf"
index_name = os.getenv("PINECONE_INDEX")

if not index_name:
    raise RuntimeError("PINECONE_INDEX is not set in the .env file.")

# Run upload
process_and_upload(
    jsonl_path=jsonl_path,
    namespace=namespace,
    index_name=index_name
)