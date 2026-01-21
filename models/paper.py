from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Paper(BaseModel):
    paper_id: str
    title: str
    authors: List[str]
    year: int
    venue: str
    abstract: str = ""
    introduction: str = ""
    results: str = ""
    discussion: str = ""
    conclusion: str = ""
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    
class Claim(BaseModel):
    claim_id: str
    text: str
    paper_id: str
    paper_title: str
    year: int
    venue: str
    section: str 
    embedding: Optional[List[float]] = None
    
class Evidence(BaseModel):
    evidence_id: str
    text: str
    paper_id: str
    paper_title: str
    year: int
    venue: str
    section: str 
    embedding: Optional[List[float]] = None
