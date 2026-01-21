import re
import spacy
from typing import List
from config import Config
from models.paper import Paper, Claim

class ClaimExtractor:
    def __init__(self):
       
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("Warning: spaCy model not found. Using basic extraction.")
            self.nlp = None
    
    def extract_claims(self, paper: Paper) -> List[Claim]:
        """Extract claim sentences from abstract and conclusion."""
        claims = []
        
    
        claim_patterns = [
            r'\bwe (show|demonstrate|present|propose|introduce|achieve|improve)\b',
            r'\bour (method|approach|model|system|framework) (achieves|outperforms|improves)\b',
            r'\bresults (show|demonstrate|indicate|suggest)\b',
            r'\b(significantly|substantially) (better|higher|lower|faster) than\b',
            r'\bstate-of-the-art\b',
            r'\bF1 score|accuracy|precision|recall|BLEU|ROUGE\b',
        ]
        
     
        claims.extend(self._extract_from_text(
            paper.abstract, paper, "abstract", claim_patterns
        ))
        
       
        claims.extend(self._extract_from_text(
            paper.conclusion, paper, "conclusion", claim_patterns
        ))
        
        return claims
    
    def _extract_from_text(self, text: str, paper: Paper, 
                          section: str, patterns: List[str]) -> List[Claim]:
        """Extract claims from a text section."""
        if not text:
            return []
        
        claims = []
        sentences = self._split_sentences(text)
        
        for i, sentence in enumerate(sentences):
            if self._is_claim(sentence, patterns):
                claim = Claim(
                    claim_id=f"{paper.paper_id}_{section}_{i}",
                    text=sentence.strip(),
                    paper_id=paper.paper_id,
                    paper_title=paper.title,
                    year=paper.year,
                    venue=paper.venue,
                    section=section
                )
                claims.append(claim)
        
        return claims
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        if self.nlp:
            doc = self.nlp(text)
            return [sent.text for sent in doc.sents]
        else:
       
            return re.split(r'(?<=[.!?])\s+', text)
    
    def _is_claim(self, sentence: str, patterns: List[str]) -> bool:
        """Determine if a sentence is a claim."""
     
        if len(sentence) < Config.MIN_CLAIM_LENGTH or \
           len(sentence) > Config.MAX_CLAIM_LENGTH:
            return False
        
        sentence_lower = sentence.lower()
        for pattern in patterns:
            if re.search(pattern, sentence_lower):
                return True
        
      
        if any(keyword in sentence_lower for keyword in 
               ['we show', 'we demonstrate', 'outperforms', 'achieves']):
            return True
        
        return False
