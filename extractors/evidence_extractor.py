import re
import spacy
from typing import List
from config import Config
from models.paper import Paper, Evidence

class EvidenceExtractor:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            self.nlp = None
    
    def extract_evidence(self, paper: Paper) -> List[Evidence]:
        """Extract evidence statements from results and discussion."""
        evidence_list = []
        
    
        evidence_patterns = [
            r'\b(achieved|obtained|reached|measured|observed|found)\b',
            r'\b\d+(\.\d+)?%\b',
            r'\b(improved|increased|decreased|reduced) by\b',
            r'\b(BLEU|ROUGE|F1|accuracy|precision|recall) (score )?(of |is )\d+',
            r'\b(training|inference) time\b',
            r'\bexperiment(s)? (show|showed|demonstrate)\b',
            r'\b(table|figure) \d+ shows\b',
        ]
       
        evidence_list.extend(self._extract_from_text(
            paper.results, paper, "results", evidence_patterns
        ))
        
      
        evidence_list.extend(self._extract_from_text(
            paper.discussion, paper, "discussion", evidence_patterns
        ))
        
        return evidence_list
    
    def _extract_from_text(self, text: str, paper: Paper,
                          section: str, patterns: List[str]) -> List[Evidence]:
        """Extract evidence from a text section."""
        if not text:
            return []
        
        evidence_list = []
        sentences = self._split_sentences(text)
        
        for i, sentence in enumerate(sentences):
            if self._is_evidence(sentence, patterns):
                evidence = Evidence(
                    evidence_id=f"{paper.paper_id}_{section}_{i}",
                    text=sentence.strip(),
                    paper_id=paper.paper_id,
                    paper_title=paper.title,
                    year=paper.year,
                    venue=paper.venue,
                    section=section
                )
                evidence_list.append(evidence)
        
        return evidence_list
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        if self.nlp:
            doc = self.nlp(text)
            return [sent.text for sent in doc.sents]
        else:
            return re.split(r'(?<=[.!?])\s+', text)
    
    def _is_evidence(self, sentence: str, patterns: List[str]) -> bool:
        """Determine if a sentence contains evidence."""
        if len(sentence) < Config.MIN_EVIDENCE_LENGTH:
            return False
        
        sentence_lower = sentence.lower()
        for pattern in patterns:
            if re.search(pattern, sentence_lower):
                return True
        
        
        if re.search(r'\d+(\.\d+)?', sentence):
            if any(keyword in sentence_lower for keyword in 
                   ['score', 'accuracy', 'performance', 'result']):
                return True
        
        return False
