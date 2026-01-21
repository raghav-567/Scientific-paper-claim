from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
from config import Config
from models.paper import Claim, Evidence

class EmbeddingService:
    def __init__(self, model_name: str = None):
        """Initialize the embedding model."""
        if model_name is None:
            model_name = Config.EMBEDDING_MODEL
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        print(f"Model loaded. Embedding dimension: {self.dimension}")
    
    def encode(self, texts: Union[str, List[str]], 
               batch_size: int = 32) -> np.ndarray:
        """Generate embeddings for text(s)."""
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=len(texts) > 10,
            convert_to_numpy=True
        )
        
        return embeddings
    
    def encode_claims(self, claims: List[Claim]) -> List[Claim]:
        """Add embeddings to claim objects."""
        texts = [claim.text for claim in claims]
        embeddings = self.encode(texts)
        
        for claim, embedding in zip(claims, embeddings):
            claim.embedding = embedding.tolist()
        
        return claims
    
    def encode_evidence(self, evidence_list: List[Evidence]) -> List[Evidence]:
        """Add embeddings to evidence objects."""
        texts = [evidence.text for evidence in evidence_list]
        embeddings = self.encode(texts)
        
        for evidence, embedding in zip(evidence_list, embeddings):
            evidence.embedding = embedding.tolist()
        
        return evidence_list