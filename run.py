from app.services.ingestion import load_file, chunk_documents
from pathlib import Path

docs = load_file(Path("data/sample_kb/company_handbook.md"))

print(docs)