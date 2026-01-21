from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List
from models.paper import Claim, Evidence
from config import Config

class QdrantManager:
    def __init__(self):
        """Initialize Qdrant client and create collections."""
        self.client = QdrantClient(
            host=Config.QDRANT_HOST,
            port=Config.QDRANT_PORT,
            api_key=Config.QDRANT_API_KEY
        )
        self._ensure_collections()
    
    def _ensure_collections(self):
        """Create collections if they don't exist."""
        collections = [c.name for c in self.client.get_collections().collections]
        
        if Config.CLAIMS_COLLECTION not in collections:
            self.client.create_collection(
                collection_name=Config.CLAIMS_COLLECTION,
                vectors_config=VectorParams(
                    size=Config.EMBEDDING_DIM,
                    distance=Distance.COSINE
                )
            )
            print(f"Created collection: {Config.CLAIMS_COLLECTION}")
        
        if Config.EVIDENCE_COLLECTION not in collections:
            self.client.create_collection(
                collection_name=Config.EVIDENCE_COLLECTION,
                vectors_config=VectorParams(
                    size=Config.EMBEDDING_DIM,
                    distance=Distance.COSINE
                )
            )
            print(f"Created collection: {Config.EVIDENCE_COLLECTION}")
    
    def store_claims(self, claims: List[Claim]):
        """Store claims in Qdrant."""
        points = []
        for claim in claims:
            point = PointStruct(
                id=hash(claim.claim_id) % (2**63),  # Ensure positive int
                vector=claim.embedding,
                payload={
                    "claim_id": claim.claim_id,
                    "text": claim.text,
                    "paper_id": claim.paper_id,
                    "paper_title": claim.paper_title,
                    "year": claim.year,
                    "venue": claim.venue,
                    "section": claim.section
                }
            )
            points.append(point)
        
        self.client.upsert(
            collection_name=Config.CLAIMS_COLLECTION,
            points=points
        )
        print(f"Stored {len(points)} claims in Qdrant")
    
    def store_evidence(self, evidence_list: List[Evidence]):
        """Store evidence in Qdrant."""
        points = []
        for evidence in evidence_list:
            point = PointStruct(
                id=hash(evidence.evidence_id) % (2**63),
                vector=evidence.embedding,
                payload={
                    "evidence_id": evidence.evidence_id,
                    "text": evidence.text,
                    "paper_id": evidence.paper_id,
                    "paper_title": evidence.paper_title,
                    "year": evidence.year,
                    "venue": evidence.venue,
                    "section": evidence.section
                }
            )
            points.append(point)
        
        self.client.upsert(
            collection_name=Config.EVIDENCE_COLLECTION,
            points=points
        )
        print(f"Stored {len(points)} evidence statements in Qdrant")
    
    def search_claims(self, query_vector: List[float], top_k: int = 10):
        """Search for similar claims."""
        return self.client.search(
            collection_name=Config.CLAIMS_COLLECTION,
            query_vector=query_vector,
            limit=top_k
        )
    
    def search_evidence(self, query_vector: List[float], top_k: int = 20):
        """Search for similar evidence."""
        return self.client.search(
            collection_name=Config.EVIDENCE_COLLECTION,
            query_vector=query_vector,
            limit=top_k
        )
