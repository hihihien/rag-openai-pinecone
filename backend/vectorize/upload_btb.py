from shared_uploader import process_and_upload
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Set parameters for BTB
jsonl_path = "backend/data/MHB_Alle_Studiengaenge/MHB_BTB_PO25/BTB_MHB_PO2025_chunks.jsonl"
namespace = "BTB_pdf"
index_name = os.getenv("PINECONE_INDEX")

if not index_name:
    raise RuntimeError("PINECONE_INDEX is not set in the .env file.")

# Run upload
process_and_upload(
    jsonl_path=jsonl_path,
    namespace=namespace,
    index_name=index_name
)