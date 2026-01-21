# arxiv_fetcher/arxiv_client.py
import arxiv
import re
from typing import List, Optional
from models.paper import Paper
from datetime import datetime

class ArxivClient:
    def __init__(self):
        self.client = arxiv.Client()
    
    def search_papers(self, query: str, max_results: int = 10, 
                     sort_by: arxiv.SortCriterion = arxiv.SortCriterion.Relevance) -> List[Paper]:
        """
        Search arXiv for papers matching the query.
        
        Args:
            query: Search query (e.g., "transformer language models")
            max_results: Maximum number of papers to fetch
            sort_by: Sort criterion (Relevance, LastUpdatedDate, SubmittedDate)
        """
        print(f"\n🔍 Searching arXiv for: '{query}'")
        print(f"   Fetching up to {max_results} papers...")
        
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=sort_by
        )
        
        papers = []
        for result in self.client.results(search):
            paper = self._convert_to_paper(result)
            if paper:
                papers.append(paper)
                print(f"   ✓ {paper.title[:60]}... ({paper.year})")
        
        print(f"\n✓ Fetched {len(papers)} papers from arXiv")
        return papers
    
    def search_by_category(self, category: str, max_results: int = 10) -> List[Paper]:
        """
        Search by arXiv category (e.g., 'cs.CL', 'cs.AI', 'cs.LG')
        """
        query = f"cat:{category}"
        return self.search_papers(query, max_results, arxiv.SortCriterion.LastUpdatedDate)
    
    def _convert_to_paper(self, result: arxiv.Result) -> Optional[Paper]:
        """Convert arXiv result to Paper object."""
        try:
            
            summary = result.summary.replace('\n', ' ').strip()
            
           
            abstract, results, conclusion = self._parse_summary(summary)
            
            paper = Paper(
                paper_id=result.entry_id.split('/')[-1].replace('v', '_v'),
                title=result.title,
                authors=[author.name for author in result.authors],
                year=result.published.year,
                venue="arXiv",
                abstract=abstract,
                introduction="", 
                results=results,
                discussion="", 
                conclusion=conclusion,
                arxiv_id=result.entry_id.split('/')[-1]
            )
            return paper
        except Exception as e:
            print(f"   ⚠️  Error processing paper: {e}")
            return None
    
    def _parse_summary(self, summary: str):
        """
        Attempt to parse abstract, results, and conclusion from summary.
        Since arXiv API only provides abstracts, we'll use heuristics.
        """
     
        sections = re.split(r'\b(Results?:|Conclusion:|We show|We demonstrate|Our experiments)\b', 
                          summary, flags=re.IGNORECASE)
        
        abstract = summary
        results = ""
        conclusion = ""
       
        if len(sections) > 1:
            abstract = sections[0]
            
          
            results_match = re.search(
                r'(we (achieve|obtain|show|demonstrate|find|observe)[^.]+\d+[^.]*\.)',
                summary, re.IGNORECASE
            )
            if results_match:
                results = results_match.group(0)
            
           
            conclusion_match = re.search(
                r'(we (conclude|demonstrate|show) that[^.]+\.)',
                summary, re.IGNORECASE
            )
            if conclusion_match:
                conclusion = conclusion_match.group(0)
        
        return abstract, results, conclusion


class SmartArxivFetcher:
    """
    Intelligent fetcher that automatically finds relevant papers
    based on the user's query and keeps the database updated.
    """
    
    def __init__(self):
        self.client = ArxivClient()
    
    def fetch_relevant_papers(self, user_query: str, num_papers: int = 5) -> List[Paper]:
        """
        Fetch papers relevant to the user's query.
        
        Strategy:
        1. Extract key terms from query
        2. Search arXiv
        3. Return most relevant papers
        """
   
        search_query = self._prepare_search_query(user_query)
        
        papers = self.client.search_papers(
            query=search_query,
            max_results=num_papers,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        return papers
    
    def _prepare_search_query(self, user_query: str) -> str:
        """
        Convert user query to arXiv search query.
        Extract key technical terms and remove common words.
        """

        query = re.sub(
            r'\b(achieves?|outperforms?|improves?|better than|state-of-the-art)\b',
            '',
            user_query,
            flags=re.IGNORECASE
        )
        
        query = query.strip()
      
        ml_keywords = ['transformer', 'bert', 'gpt', 'neural', 'deep learning', 
                      'machine learning', 'nlp', 'computer vision']
        
        has_ml_keyword = any(kw in query.lower() for kw in ml_keywords)
        
        if not has_ml_keyword:
          
            if any(word in query.lower() for word in ['language', 'text', 'translation']):
                query += " natural language processing"
            elif any(word in query.lower() for word in ['image', 'vision', 'detection']):
                query += " computer vision"
        
        return query