

import argparse
from models.paper import Paper
from pipeline.ingestion_pipeline import IngestionPipeline
from retrieval.retriever import ClaimEvidenceRetriever
from pipeline.auto_ingestion_pipeline import AutoIngestionPipeline 
from config import Config
import json

def create_sample_papers():
    """Create sample papers for demonstration."""
    papers = [
        Paper(
            paper_id="paper_001",
            title="Attention Is All You Need",
            authors=["Vaswani et al."],
            year=2017,
            venue="NeurIPS",
            abstract="We propose the Transformer, a model architecture based solely on attention mechanisms. "
                    "Our model achieves state-of-the-art results on machine translation tasks.",
            results="On WMT 2014 English-to-German translation, our model achieved a BLEU score of 28.4. "
                   "Training time was reduced by 10x compared to recurrent models.",
            conclusion="The Transformer shows that attention mechanisms alone are sufficient for "
                      "sequence transduction tasks, achieving better performance than recurrent models."
        ),
        Paper(
            paper_id="paper_002",
            title="BERT: Pre-training of Deep Bidirectional Transformers",
            authors=["Devlin et al."],
            year=2019,
            venue="NAACL",
            abstract="We introduce BERT, a bidirectional transformer model for language understanding. "
                    "BERT achieves state-of-the-art results on eleven NLP tasks.",
            results="BERT achieved 93.2% accuracy on GLUE benchmark, surpassing previous best by 7%. "
                   "Performance gains observed across all evaluated tasks.",
            conclusion="Bidirectional pre-training significantly improves performance on NLP tasks."
        ),
    ]
    return papers

def main():
    parser = argparse.ArgumentParser(description="Scientific Claim-Evidence Mapper")
    parser.add_argument('--ingest', action='store_true', help='Ingest sample papers')
    parser.add_argument('--query', type=str, help='Query the system')
    
    parser.add_argument('--auto-query', type=str, 
                       help='Query with automatic arXiv paper fetching')
    parser.add_argument('--num-papers', type=int, default=5,
                       help='Number of papers to fetch from arXiv (default: 5)')
    parser.add_argument('--topic', type=str,
                       help='Fetch papers on a specific topic from arXiv')
    parser.add_argument('--category', type=str,
                       help='Fetch papers from arXiv category (e.g., cs.CL, cs.AI)')
    
    args = parser.parse_args()
    
    Config.ensure_directories()
    
    if args.auto_query:
        print(f"\n{'='*70}")
        print(f"AUTO-QUERY MODE: {args.auto_query}")
        print(f"{'='*70}")
        
        auto_pipeline = AutoIngestionPipeline()
       
        result = auto_pipeline.process_query_with_auto_fetch(
            args.auto_query, 
            args.num_papers
        )
    
        print(f"\n{'='*70}")
        print(f"RETRIEVING EVIDENCE")
        print(f"{'='*70}")
        
        retriever = ClaimEvidenceRetriever()
        results = retriever.retrieve(args.auto_query)
        
        print("\n" + "="*70)
        print("RELATED CLAIMS")
        print("="*70)
        for i, claim in enumerate(results['related_claims'][:5], 1):
            print(f"\n{i}. {claim['text']}")
            print(f"   📄 {claim['paper_title']} ({claim['year']})")
            print(f"   📍 {claim['venue']} | 📊 Similarity: {claim['similarity_score']:.1%}")
        
        print("\n" + "="*70)
        print("SUPPORTING EVIDENCE")
        print("="*70)
        for ev in results['evidence']['supporting'][:5]:
            print(f"\n✅ {ev['text']}")
            print(f"   📄 {ev['paper_title']} ({ev['year']})")
        
        print("\n" + "="*70)
        print("CONTRADICTING EVIDENCE")
        print("="*70)
        for ev in results['evidence']['contradicting'][:5]:
            print(f"\n❌ {ev['text']}")
            print(f"   📄 {ev['paper_title']} ({ev['year']})")
        
        print("\n" + "="*70)
   
    elif args.topic:
        print(f"\nFetching papers on topic: '{args.topic}'")
        auto_pipeline = AutoIngestionPipeline()
        result = auto_pipeline.fetch_and_ingest_by_topic(args.topic, args.num_papers)
        print(f"\n✓ Fetched {result.get('papers_count', 0)} papers")
        print(f"✓ Extracted {result.get('claims_count', 0)} claims")
        print(f"✓ Extracted {result.get('evidence_count', 0)} evidence")
 
    elif args.category:
        print(f"\nFetching papers from category: '{args.category}'")
        auto_pipeline = AutoIngestionPipeline()
        result = auto_pipeline.fetch_by_arxiv_category(args.category, args.num_papers)
        print(f"\n✓ Fetched {result.get('papers_count', 0)} papers")
        print(f"✓ Extracted {result.get('claims_count', 0)} claims")
        print(f"✓ Extracted {result.get('evidence_count', 0)} evidence")

    elif args.ingest:
        print("Ingesting sample papers...")
        pipeline = IngestionPipeline()
        papers = create_sample_papers()
        results = pipeline.process_papers(papers)
        print(f"\n✓ Ingested {results['claims_count']} claims and {results['evidence_count']} evidence")
 
    elif args.query:
        print(f"\nQuerying: {args.query}\n")
        retriever = ClaimEvidenceRetriever()
        results = retriever.retrieve(args.query)
        
        print("\n=== RELATED CLAIMS ===")
        for claim in results['related_claims'][:5]:
            print(f"\n• {claim['text']}")
            print(f"  [{claim['paper_title']}, {claim['year']}]")
            print(f"  Similarity: {claim['similarity_score']:.3f}")
        
        print("\n=== SUPPORTING EVIDENCE ===")
        for ev in results['evidence']['supporting']:
            print(f"\n• {ev['text']}")
            print(f"  [{ev['paper_title']}, {ev['year']}]")
        
        print("\n=== CONTRADICTING EVIDENCE ===")
        for ev in results['evidence']['contradicting']:
            print(f"\n• {ev['text']}")
            print(f"  [{ev['paper_title']}, {ev['year']}]")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()