from typing import Dict, List
from storage.qdrant_manager import QdrantManager
from embeddings.embedding_service import EmbeddingService
from retrieval.categorizer import EvidenceCategorizer
from config import Config

class ClaimEvidenceRetriever:
    def __init__(self):
        self.qdrant = QdrantManager()
        self.embedder = EmbeddingService()
        self.categorizer = EvidenceCategorizer()
    
    def retrieve(self, query: str) -> Dict:
        """Retrieve related claims and categorized evidence."""
    
        query_embedding = self.embedder.encode(query)[0].tolist()
        
       
        claim_results = self.qdrant.search_claims(
            query_embedding,
            top_k=Config.TOP_K_CLAIMS
        )
        
    
        evidence_results = self.qdrant.search_evidence(
            query_embedding,
            top_k=Config.TOP_K_EVIDENCE
        )
        
      
        categorized_evidence = {
            'supporting': [],
            'contradicting': [],
            'neutral': []
        }
        
        for result in evidence_results:
            if result.score < Config.SIMILARITY_THRESHOLD:
                continue
            
            category = self.categorizer.categorize(
                query,
                result.payload['text']
            )
            
            evidence_item = {
                **result.payload,
                'similarity_score': result.score
            }
            categorized_evidence[category].append(evidence_item)
        
       
        related_claims = [
            {**result.payload, 'similarity_score': result.score}
            for result in claim_results
            if result.score >= Config.SIMILARITY_THRESHOLD
        ]
        
        return {
            'query': query,
            'related_claims': related_claims,
            'evidence': categorized_evidence
        }
