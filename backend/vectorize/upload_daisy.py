from shared_uploader import process_and_upload
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Set parameters for DAISY
jsonl_path = "backend/data/MHB_Alle_Studiengaenge/MHB_BDAISY_PO21/DAISY_MHB_chunks.jsonl"
namespace = "DAISY_pdf"
index_name = os.getenv("PINECONE_INDEX")

if not index_name:
    raise RuntimeError("PINECONE_INDEX is not set in the .env file.")

# Run upload
process_and_upload(
    jsonl_path=jsonl_path,
    namespace=namespace,
    index_name=index_name
)