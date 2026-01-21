# Scientific Claim–Evidence Mapper

End-to-end system for extracting scientific claims from papers, indexing evidence statements, and retrieving supporting / contradicting / neutral evidence using semantic search over Qdrant.

---

## 1. Overview

This project builds a **claim-centric retrieval system** for scientific literature.

Pipeline:

1. Ingest papers  
2. Extract claims (abstract + conclusion)  
3. Extract evidence (results + discussion)  
4. Generate embeddings (Sentence-Transformers)  
5. Store vectors in Qdrant  
6. Query a claim → retrieve related claims + categorized evidence  

No judgment of correctness. Only retrieval and weak categorization.

---

## 2. Architecture

Paper
↓
ClaimExtractor / EvidenceExtractor
↓
EmbeddingService
↓
Qdrant (Claims + Evidence)
↓
Retriever
↓
Categorizer
↓
CLI / Streamlit UI


---

## Directory Structure



├── requirements.txt
├── config.py
├── models/
│ └── paper.py
├── extractors/
│ ├── claim_extractor.py
│ └── evidence_extractor.py
├── embeddings/
│ └── embedding_service.py
├── storage/
│ └── qdrant_manager.py
├── retrieval/
│ ├── retriever.py
│ └── categorizer.py
├── pipeline/
│ └── ingestion_pipeline.py
├── app.py
└── main.py


---

## Installation

### Create environment

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows

Install dependencies
pip install -r requirements.txt

Install spaCy model
python -m spacy download en_core_web_sm

Run Qdrant
Docker
docker run -p 6333:6333 qdrant/qdrant


Dashboard:

http://localhost:6333/dashboard

Configuration

Edit config.py:

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

TOP_K_CLAIMS = 10
TOP_K_EVIDENCE = 20
SIMILARITY_THRESHOLD = 0.25

Ingest Papers
Sample ingestion
python main.py --ingest


Actions:

Load sample papers

Extract claims and evidence

Generate embeddings

Store in Qdrant

Output:

✓ Ingested X claims and Y evidence

Query (CLI)
python main.py --query "Transformer models outperform RNNs"


Outputs:

Related claims

Supporting evidence

Contradicting evidence

Run Web UI
streamlit run app.py


Interface:

Claim input

Related claims list

Evidence tabs:

Supporting

Contradicting

Neutral

Paper Input Format
Paper(
    paper_id="paper_001",
    title="...",
    authors=[...],
    year=2019,
    venue="NAACL",
    abstract="...",
    results="...",
    discussion="...",
    conclusion="..."
)


Used sections:

Claims → abstract, conclusion

Evidence → results, discussion

Retrieval Logic
Claim Search

Semantic search in scientific_claims.

Evidence Search

Semantic search in scientific_evidence.

Categorization

Rule-based:

Supporting → improvement / performance keywords

Contradicting → negation + degradation keywords

Neutral → fallback

No LLM inference.

Limitations

Regex-based extraction

Rule-based categorization

No citation grounding

No numerical verification

No cross-paper normalization

System retrieves evidence only.
System does not assess truth.

Recommended Extensions

Transformer-based claim classifier

NLI-based contradiction detection

Citation-aware linking

Year-aware retrieval

Paper-level aggregation

Numerical consistency checking

Use Cases

Literature review automation

Claim auditing

Survey preparation

Reproducibility analysis

Research monitoring

System Requirements

Python ≥ 3.9

RAM ≥ 8 GB (16 GB recommended)

Disk ≥ 5 GB

GPU optional

License

Research and educational use.

Design Principle

Retrieval-first scientific auditing system.
No hallucination.
No answer generation.
Only indexed evidence.