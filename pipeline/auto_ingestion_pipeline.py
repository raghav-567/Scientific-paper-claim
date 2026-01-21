
from typing import List
from models.paper import Paper
from arxiv_fetcher.arxiv_client import SmartArxivFetcher
from pipeline.ingestion_pipeline import IngestionPipeline
from storage.qdrant_manager import QdrantManager

class AutoIngestionPipeline:
    """
    Pipeline that automatically fetches and ingests papers based on queries.
    """
    
    def __init__(self):
        self.arxiv_fetcher = SmartArxivFetcher()
        self.ingestion_pipeline = IngestionPipeline()
        self.qdrant = QdrantManager()
    
    def process_query_with_auto_fetch(self, query: str, num_papers: int = 5,
                                     force_refetch: bool = False) -> dict:
        """
        Process a query by:
        1. Checking if we have enough relevant papers
        2. Fetching new papers if needed
        3. Ingesting them
        4. Returning retrieval results
        """
        print(f"\n{'='*60}")
        print(f"AUTO-FETCH MODE: Processing query")
        print(f"{'='*60}")
     
        if force_refetch or self._should_fetch_papers(query):
            print("\n📥 Fetching papers from arXiv...")
            papers = self.arxiv_fetcher.fetch_relevant_papers(query, num_papers)
            
            if papers:
                print(f"\n⚙️  Processing {len(papers)} papers...")
                result = self.ingestion_pipeline.process_papers(papers)
                print(f"\n✓ Added {result['claims_count']} claims and "
                      f"{result['evidence_count']} evidence to database")
            else:
                print("\n⚠️  No papers found on arXiv for this query")
        else:
            print("\n✓ Using existing papers in database")
        
        return {
            'status': 'success',
            'message': 'Papers fetched and processed'
        }
    
    def _should_fetch_papers(self, query: str) -> bool:
        """
        Determine if we should fetch new papers.
        For now, we'll fetch on first query or periodically.
        """

        try:
            collections = self.qdrant.client.get_collections().collections
            for col in collections:
                info = self.qdrant.client.get_collection(col.name)
                if info.points_count > 0:
                    return False
            return True
        except:
            return True
    
    def fetch_and_ingest_by_topic(self, topic: str, num_papers: int = 10):
        """Fetch papers on a specific topic and ingest them."""
        papers = self.arxiv_fetcher.fetch_relevant_papers(topic, num_papers)
        if papers:
            return self.ingestion_pipeline.process_papers(papers)
        return None