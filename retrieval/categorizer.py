import re
from typing import Literal

class EvidenceCategorizer:
    def __init__(self):
        self.supporting_keywords = [
            'achieved', 'improved', 'outperform', 'better', 'higher',
            'superior', 'surpass', 'exceed', 'success', 'effective',
            'gain', 'increase', 'enhance', 'boost', 'advance'
        ]
        
        self.contradicting_keywords = [
            'failed', 'worse', 'lower', 'inferior', 'poor',
            'limitation', 'drawback', 'weakness', 'decrease',
            'decline', 'reduce', 'degrade', 'unable', 'cannot',
            'ineffective', 'unsuccessful'
        ]
    
    def categorize(self, query: str, evidence_text: str) -> Literal['supporting', 'contradicting', 'neutral']:
        """Categorize evidence as supporting, contradicting, or neutral."""
        query_lower = query.lower()
        evidence_lower = evidence_text.lower()
      
        if self._has_negation_context(evidence_lower):
            if self._text_similarity(query_lower, evidence_lower):
                return 'contradicting'
     
        supporting_score = sum(1 for kw in self.supporting_keywords 
                              if kw in evidence_lower)
        contradicting_score = sum(1 for kw in self.contradicting_keywords 
                                 if kw in evidence_lower)
  
        query_claims_improvement = any(word in query_lower for word in 
                                      ['better', 'improve', 'outperform', 'higher'])
        evidence_shows_decline = any(word in evidence_lower for word in 
                                    ['worse', 'lower', 'decline', 'decrease'])
        
        if query_claims_improvement and evidence_shows_decline:
            return 'contradicting'
        
     
        if contradicting_score > supporting_score and contradicting_score >= 2:
            return 'contradicting'
        elif supporting_score > contradicting_score and supporting_score >= 2:
            return 'supporting'
        else:
            return 'neutral'
    
    def _has_negation_context(self, text: str) -> bool:
        """Check if text contains negation."""
        negation_patterns = [
            r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bfailed\b',
            r'\bunable\b', r'\bcannot\b', r'\bdidn\'t\b'
        ]
        return any(re.search(pattern, text) for pattern in negation_patterns)
    
    def _text_similarity(self, text1: str, text2: str) -> bool:
        """Simple word overlap similarity."""
        words1 = set(re.findall(r'\w+', text1))
        words2 = set(re.findall(r'\w+', text2))
        overlap = len(words1 & words2)
        return overlap > 3