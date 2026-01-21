
import streamlit as st
from retrieval.retriever import ClaimEvidenceRetriever
from pipeline.auto_ingestion_pipeline import AutoIngestionPipeline
from arxiv_fetcher.arxiv_client import SmartArxivFetcher

st.set_page_config(
    page_title="Scientific Claim-Evidence Mapper",
    page_icon="🔬",
    layout="wide"
)

st.markdown("""
<style>
    .stAlert > div {
        padding: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.title("🔬 Scientific Claim-Evidence Mapper")
st.markdown("*Powered by arXiv • Automated paper fetching and analysis*")


@st.cache_resource
def get_components():
    retriever = ClaimEvidenceRetriever()
    auto_pipeline = AutoIngestionPipeline()
    return retriever, auto_pipeline

try:
    retriever, auto_pipeline = get_components()
except Exception as e:
    st.error(f"Error initializing system: {e}")
    st.info("Make sure Qdrant is running: `docker run -p 6333:6333 qdrant/qdrant`")
    st.stop()

with st.sidebar:
    st.header("🤖 Auto-Fetch Settings")
    
    auto_fetch = st.checkbox(
        "Enable Auto-Fetch from arXiv",
        value=True,
        help="Automatically fetch relevant papers from arXiv when searching"
    )
    
    if auto_fetch:
        num_papers = st.slider(
            "Papers to fetch per query",
            min_value=3,
            max_value=20,
            value=5,
            help="More papers = better coverage but slower processing"
        )
    else:
        num_papers = 5
    
    st.divider()
    
    st.header("📚 About")
    st.info(
        "This system **automatically fetches papers from arXiv** based on your query, "
        "extracts claims and evidence, and helps you explore the literature."
    )
    
    st.header("🔍 How it works")
    st.markdown("""
    1. **Auto-Fetch**: Queries arXiv for relevant papers
    2. **Extract**: Claims from abstracts, evidence from results
    3. **Embed**: Semantic vectors for retrieval
    4. **Categorize**: Supporting/contradicting/neutral evidence
    """)
    
    st.divider()
    
    st.header("💡 Sample Queries")
    sample_queries = [
        "Transformers outperform RNNs",
        "BERT improves language understanding",
        "Attention mechanisms have quadratic complexity",
        "GPT-3 demonstrates few-shot learning",
        "Vision transformers for image classification",
    ]
    
    for query in sample_queries:
        if st.button(query, key=query, use_container_width=True):
            st.session_state.query = query
            st.session_state.trigger_search = True

    st.divider()
    
 
    st.header("📥 Bulk Import")
    topic = st.text_input("Topic to import papers", placeholder="e.g., 'transformers NLP'")
    bulk_num = st.number_input("Number of papers", min_value=5, max_value=50, value=10)
    
    if st.button("Import Papers", use_container_width=True):
        if topic:
            with st.spinner(f"Fetching {bulk_num} papers on '{topic}'..."):
                result = auto_pipeline.fetch_and_ingest_by_topic(topic, bulk_num)
                if result:
                    st.success(f"✓ Imported {result['claims_count']} claims and "
                             f"{result['evidence_count']} evidence!")


st.divider()

query = st.text_area(
    "🔎 Enter a scientific claim to explore:",
    value=st.session_state.get('query', ''),
    height=100,
    placeholder="e.g., 'Vision transformers achieve better performance on ImageNet'",
    help="The system will automatically fetch relevant papers from arXiv!"
)

col1, col2, col3 = st.columns([2, 1, 3])
with col1:
    search_button = st.button("🔍 Search & Auto-Fetch", type="primary", use_container_width=True)
with col2:
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.clear()
        st.rerun()


if (search_button or st.session_state.get('trigger_search', False)) and query:
    st.session_state.trigger_search = False
    
    if auto_fetch:
        with st.spinner("📥 Fetching relevant papers from arXiv..."):
            try:
                auto_pipeline.process_query_with_auto_fetch(query, num_papers)
                st.success("✓ Papers fetched and processed!")
            except Exception as e:
                st.warning(f"Could not fetch papers: {e}")
    
   
    with st.spinner("🔄 Analyzing claims and evidence..."):
        try:
            results = retriever.retrieve(query)
            st.session_state.results = results
            
       
            total_evidence = (len(results['evidence']['supporting']) + 
                            len(results['evidence']['contradicting']) + 
                            len(results['evidence']['neutral']))
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Related Claims Found", len(results['related_claims']))
            with col2:
                st.metric("Evidence Statements", total_evidence)
                
        except Exception as e:
            st.error(f"Error during search: {e}")


if 'results' in st.session_state:
    results = st.session_state.results
    
    st.divider()
    
 
    st.header("📋 Related Claims from Literature")
    
    if results['related_claims']:
        for i, claim in enumerate(results['related_claims'][:5], 1):
            with st.expander(
                f"**{i}. {claim['paper_title']}** ({claim['year']}) • "
                f"Similarity: {claim['similarity_score']:.1%}",
                expanded=i <= 2
            ):
                st.markdown(f"> *{claim['text']}*")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.caption(f"📅 {claim['year']}")
                with col2:
                    st.caption(f"📍 {claim['venue']}")
                with col3:
                    st.caption(f"📄 {claim['section']}")
                with col4:
                    if 'arxiv_id' in claim:
                        st.caption(f"🔗 arXiv:{claim.get('arxiv_id', 'N/A')}")
    else:
        st.info("No related claims found. Try fetching more papers or adjusting your query.")
    
    st.divider()
    
 
    st.header("🔍 Evidence Analysis")
    
   
    col1, col2, col3 = st.columns(3)
    with col1:
        count = len(results['evidence']['supporting'])
        st.metric("✅ Supporting", count)
    with col2:
        count = len(results['evidence']['contradicting'])
        st.metric("❌ Contradicting", count)
    with col3:
        count = len(results['evidence']['neutral'])
        st.metric("⚪ Neutral", count)
    

    tab1, tab2, tab3 = st.tabs([
        f"✅ Supporting ({len(results['evidence']['supporting'])})",
        f"❌ Contradicting ({len(results['evidence']['contradicting'])})",
        f"⚪ Neutral ({len(results['evidence']['neutral'])})"
    ])
    
    def display_evidence(evidence_list, emoji):
        if evidence_list:
            for item in evidence_list:
                with st.container():
                    st.markdown(f"{emoji} **{item['paper_title']}** ({item['year']})")
                    st.markdown(f"*{item['text']}*")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.caption(f"📍 {item['venue']}")
                    with col2:
                        st.caption(f"📄 {item['section']}")
                    with col3:
                        st.caption(f"📊 {item['similarity_score']:.1%}")
                    st.divider()
        else:
            st.info(f"No {emoji} evidence found")
    
    with tab1:
        display_evidence(results['evidence']['supporting'], "✅")
    
    with tab2:
        display_evidence(results['evidence']['contradicting'], "❌")
    
    with tab3:
        display_evidence(results['evidence']['neutral'], "⚪")

# Footer
st.divider()
st.caption("💡 Powered by arXiv API • Papers are automatically fetched and analyzed in real-time")
st.caption("⚠️ This system surfaces evidence without judging correctness. Always verify claims independently.")