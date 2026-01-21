import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
   
    QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)
    
    CLAIMS_COLLECTION = "scientific_claims"
    EVIDENCE_COLLECTION = "scientific_evidence"

    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIM = 384
  
    MIN_CLAIM_LENGTH = 20
    MAX_CLAIM_LENGTH = 300
    MIN_EVIDENCE_LENGTH = 15
    
    TOP_K_CLAIMS = 10
    TOP_K_EVIDENCE = 20
    SIMILARITY_THRESHOLD = 0.5
    
    
    DATA_DIR = Path("data")
    PAPERS_DIR = DATA_DIR / "papers"
    
    @classmethod
    def ensure_directories(cls):
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.PAPERS_DIR.mkdir(exist_ok=True)