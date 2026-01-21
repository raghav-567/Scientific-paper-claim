from typing import List
from models.paper import Paper
from extractors.claim_extractor import ClaimExtractor
from extractors.evidence_extractor import EvidenceExtractor
from embeddings.embedding_service import EmbeddingService
from storage.qdrant_manager import QdrantManager
from tqdm import tqdm

class IngestionPipeline:
    def __init__(self):
        self.claim_extractor = ClaimExtractor()
        self.evidence_extractor = EvidenceExtractor()
        self.embedder = EmbeddingService()
        self.qdrant = QdrantManager()
    
    def process_papers(self, papers: List[Paper]):
        """Process a batch of papers end-to-end."""
        print(f"\nProcessing {len(papers)} papers...")
        
        all_claims = []
        all_evidence = []
        
        for paper in tqdm(papers, desc="Extracting claims and evidence"):
     
            claims = self.claim_extractor.extract_claims(paper)
            all_claims.extend(claims)
            
      
            evidence = self.evidence_extractor.extract_evidence(paper)
            all_evidence.extend(evidence)
        
        print(f"\nExtracted {len(all_claims)} claims and {len(all_evidence)} evidence statements")
        
  
        print("\nGenerating embeddings...")
        all_claims = self.embedder.encode_claims(all_claims)
        all_evidence = self.embedder.encode_evidence(all_evidence)
        
    
        print("\nStoring in Qdrant...")
        if all_claims:
            self.qdrant.store_claims(all_claims)
        if all_evidence:
            self.qdrant.store_evidence(all_evidence)
        
        print("\n✓ Pipeline complete!")
        return {
            'claims_count': len(all_claims),
            'evidence_count': len(all_evidence)
        }