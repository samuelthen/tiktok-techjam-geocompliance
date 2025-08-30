import streamlit as st
from datetime import datetime
from ragflow_client import RAGFlowClient
from reranking_utils import EvidenceReranker
import base64

# TikTok page config
st.set_page_config(
    page_title="TikTok Geo-Compliance Co-pilot",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Function to load TikTok logo
@st.cache_data
def get_tiktok_logo():
    try:
        with open('/Users/samuelthen/Documents/AI Development Suites/techjam/TikTok_logo.svg.png', 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

# CSS with improved styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    :root {
        --tiktok-red: #FF0050;
        --tiktok-black: #161823;
        --tiktok-white: #ffffff;
        --tiktok-light-gray: #f8f8f8;
        --tiktok-border-gray: #e1e1e1;
        --tiktok-text-gray: #656565;
        --tiktok-dark-text: #2c2c2c;
    }
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background: var(--tiktok-white);
    }
    
    /* Hide Streamlit elements */
    .stApp > header {visibility: hidden;}
    .stDeployButton {display: none;}
    .stDecoration {display: none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp > div:first-child {padding-top: 1rem;}
    
    /* Container - made wider */
    .main-container {
        max-width: 900px;
        margin: 0 auto;
        padding: 0 2rem;
    }
    
    /* Header with larger logo */
    .header {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem 0;
        border-bottom: 1px solid var(--tiktok-border-gray);
        margin-bottom: 3rem;
    }
    
    .logo-container {
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }
    
    .logo-image {
        width: 80px !important;
        height: 80px !important;
        object-fit: contain;
    }
    
    .logo-fallback {
        width: 80px;
        height: 80px;
        background: var(--tiktok-black);
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 40px;
        font-weight: 800;
        transform: rotate(-8deg);
    }
    
    .header-text {
        text-align: left;
    }
    
    .header-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: var(--tiktok-black);
        margin: 0;
        letter-spacing: -1px;
    }
    
    .header-subtitle {
        font-size: 1rem;
        color: var(--tiktok-text-gray);
        margin: 0.5rem 0 0 0;
        font-weight: 400;
    }
    
    /* Search container styling */
    .search-container {
        margin: 2rem 0;
        display: flex;
        gap: 12px;
        align-items: stretch;
    }
    
    /* Override Streamlit text input styling for light theme */
    .stTextInput > div > div > input {
        background-color: var(--tiktok-white) !important;
        border: 2px solid var(--tiktok-border-gray) !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.25rem !important;
        font-size: 1rem !important;
        color: var(--tiktok-dark-text) !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
        transition: all 0.3s ease !important;
        height: 3.5rem !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--tiktok-red) !important;
        box-shadow: 0 0 0 3px rgba(255, 0, 80, 0.1) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: var(--tiktok-text-gray) !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: var(--tiktok-red) !important;
        border: none !important;
        border-radius: 12px !important;
        color: white !important;
        padding: 0.75rem 2rem !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        height: 3.5rem !important;
        transition: all 0.2s ease !important;
        white-space: nowrap !important;
        letter-spacing: 0.25px !important;
    }
    
    .stButton > button:hover {
        background: #E6004A !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(255, 0, 80, 0.3) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Results styling - reduced font sizes */
    .results-container {
        background: var(--tiktok-white);
        border: 1px solid var(--tiktok-border-gray);
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    }
    
    .status-indicator {
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        letter-spacing: 0.3px;
        text-transform: uppercase;
    }
    
    .status-ragflow {
        background: var(--tiktok-red);
        color: white;
    }
    
    
    .classification-badge {
        display: inline-block;
        padding: 0.8rem 1.5rem;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 1.5rem;
    }
    
    .classification-yes {
        background: var(--tiktok-red);
        color: white;
    }
    
    .classification-no {
        background: #00D9FF;
        color: white;
    }
    
    .classification-uncertain {
        background: #FF6B35;
        color: white;
    }
    
    .confidence-container {
        display: flex;
        align-items: center;
        gap: 1rem;
        background: var(--tiktok-light-gray);
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
    }
    
    .confidence-bar {
        flex: 1;
        height: 8px;
        background: var(--tiktok-border-gray);
        border-radius: 4px;
        overflow: hidden;
    }
    
    .confidence-fill {
        height: 100%;
        background: var(--tiktok-red);
        border-radius: 4px;
        transition: width 0.5s ease;
    }
    
    .confidence-text {
        font-weight: 600;
        color: var(--tiktok-black);
        font-size: 0.9rem;
    }
    
    .content-section {
        margin-bottom: 1.5rem;
        padding-bottom: 1.5rem;
        border-bottom: 1px solid var(--tiktok-border-gray);
    }
    
    .content-section:last-child {
        border-bottom: none;
    }
    
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--tiktok-black);
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .section-content {
        color: var(--tiktok-dark-text);
        line-height: 1.6;
        font-size: 0.95rem;
    }
    
    /* Loading */
    .loading-container {
        text-align: center;
        padding: 3rem 0;
    }
    
    .loading-spinner {
        width: 40px;
        height: 40px;
        border: 3px solid var(--tiktok-border-gray);
        border-top: 3px solid var(--tiktok-red);
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto 1rem;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .loading-text {
        font-size: 1rem;
        font-weight: 500;
        color: var(--tiktok-dark-text);
    }
    
    /* Evidence section styling - reduced sizes */
    .evidence-header {
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--tiktok-black);
    }
    
    .evidence-subtitle {
        color: var(--tiktok-text-gray);
        font-size: 0.85rem;
        font-style: italic;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-size: 0.9rem !important;
        color: var(--tiktok-black) !important;
    }
    
    .streamlit-expanderHeader p {
        color: var(--tiktok-black) !important;
    }
    
    div[data-testid="stExpander"] summary {
        color: var(--tiktok-black) !important;
    }
    
    div[data-testid="stExpander"] summary p {
        color: var(--tiktok-black) !important;
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .main-container {
            padding: 0 1rem;
        }
        
        .logo-container {
            flex-direction: column;
            gap: 1rem;
            text-align: center;
        }
        
        .header-title {
            font-size: 1.8rem;
        }
        
        .search-container {
            flex-direction: column;
            gap: 0.8rem;
        }
        
        .stButton > button {
            width: 100% !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'ragflow_client' not in st.session_state:
    st.session_state.ragflow_client = RAGFlowClient()
if 'reranker' not in st.session_state:
    st.session_state.reranker = EvidenceReranker()

def main():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Header with large logo
    logo_base64 = get_tiktok_logo()
    
    if logo_base64:
        st.markdown(f"""
        <div class="header">
            <div class="logo-container">
                <img src="data:image/png;base64,{logo_base64}" class="logo-image" alt="TikTok Logo">
                <div class="header-text">
                    <h1 class="header-title">Geo-Compliance Co-pilot</h1>
                    <p class="header-subtitle">AI-powered geo-specific regulatory compliance analysis</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="header">
            <div class="logo-container">
                <div class="logo-fallback">♪</div>
                <div class="header-text">
                    <h1 class="header-title">TikTok Geo-Compliance Co-pilot</h1>
                    <p class="header-subtitle">AI-powered geo-specific regulatory compliance analysis</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Search input and button - improved alignment
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    col1, col2 = st.columns([5, 1], gap="small")
    
    with col1:
        search_query_input = st.text_input(
            "",
            placeholder="Describe a TikTok feature for geo-compliance analysis...",
            key="search_input",
            label_visibility="collapsed"
        )
    
    with col2:
        search_button = st.button("🌍 Analyze", type="primary", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Use JavaScript communication or check for URL parameters
    query_params = st.experimental_get_query_params()
    if 'q' in query_params:
        search_query = query_params['q'][0]
        st.session_state.search_query = search_query
    
    # Detect search input from button or text input
    if search_button and search_query_input.strip():
        search_query = search_query_input.strip()
        if search_query:
            st.session_state.search_query = search_query
            print(f"🔍 User submitted query: {search_query}")
        
        
        # Loading animation
        st.markdown("""
        <div class="loading-container">
            <div class="loading-spinner"></div>
            <div class="loading-text">Analyzing geo-compliance ...</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Perform analysis
        with st.spinner(""):
            try:
                print(f"🚀 Starting analysis for: {search_query}")
                result = st.session_state.ragflow_client.analyze_feature(search_query)
                print(f"✅ Got result: {len(result.get('answer', ''))} char answer")
                
                processed_result = st.session_state.ragflow_client.process_compliance_response(
                    result['answer'], result['evidence']
                )
                print(f"✅ Processed result: {processed_result['classification']}")
                
                # Rerank evidence
                reranked_evidence = st.session_state.reranker.rerank_evidence(
                    search_query, result['evidence'], max_chunks=5
                )
                print(f"✅ Reranked evidence: {len(reranked_evidence)} chunks")
                
                st.session_state.search_results = {
                    'query': search_query,
                    'classification': processed_result['classification'],
                    'confidence': processed_result['confidence_score'],
                    'reasoning': processed_result['reasoning'],
                    'regulations': processed_result['applicable_regulations'],
                    'evidence': reranked_evidence,
                    'mode': result.get('mode', 'ragflow'),
                    'timestamp': datetime.now()
                }
                print(f"✅ Saved results to session state")
                
            except Exception as e:
                print(f"❌ Error in analysis: {e}")
                import traceback
                traceback.print_exc()
        
        st.rerun()
    
    # Display results
    if st.session_state.search_results:
        results = st.session_state.search_results
        
        # Status indicator - only show if RAGFlow active
        if results['mode'] == 'ragflow':
            st.markdown('<div class="status-indicator status-ragflow" style="margin-bottom: 1.5rem;">🔗 RAGFlow Active</div>', unsafe_allow_html=True)
        elif results['mode'] == 'error':
            st.error("⚠️ RAGFlow connection error. Please check the service status.")
            return
        
        # Two-column layout: Evidence on left, Analysis on right
        left_col, right_col = st.columns([1, 1], gap="large")
        
        with right_col:
            
            # Classification
            classification_class = f"classification-{results['classification'].lower()}"
            if results['classification'].upper() == "YES":
                badge_text = "🚨 GEO-COMPLIANCE REQUIRED"
            elif results['classification'].upper() == "NO":
                badge_text = "✅ NO GEO-COMPLIANCE NEEDED"
            else:
                badge_text = "⚠️ GEO-COMPLIANCE REVIEW"
            
            st.markdown(f'<div class="classification-badge {classification_class}">{badge_text}</div>', unsafe_allow_html=True)
            
            # Confidence
            try:
                confidence_score = int(results['confidence'])
                confidence_percent = (confidence_score / 10) * 100
            except:
                confidence_score = 0
                confidence_percent = 0
            
            st.markdown(f"""
            <div class="confidence-container">
                <span style="font-weight: 600; font-size: 0.9rem; color: var(--tiktok-black);">Confidence:</span>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: {confidence_percent}%"></div>
                </div>
                <span class="confidence-text" style="color: var(--tiktok-black);">{confidence_score}/10</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Analysis sections
            st.markdown(f"""
            <div class="content-section">
                <div class="section-title">🧠 Geo-Compliance Analysis</div>
                <div class="section-content">{results['reasoning']}</div>
            </div>
            
            <div class="content-section">
                <div class="section-title">⚖️ Regional Regulatory Requirements</div>
                <div class="section-content">{results['regulations']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with left_col:
            
            if results['evidence']:
                st.markdown("""
                <div class="content-section">
                    <div class="section-title">📋 Compliance Evidence</div>
                    <div class="section-content" style="color: var(--tiktok-text-gray); font-size: 0.9rem;">
                        Click each evidence item below to expand details
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                for evidence in results['evidence']:
                    # Each evidence in expandable container matching confidence style
                    with st.expander(
                        f"🌍 {evidence['source'][:35]}{'...' if len(evidence['source']) > 35 else ''} (Score: {evidence.get('similarity_score', 0):.2f})",
                        expanded=False
                    ):
                        st.markdown(f"""
                        <div class="confidence-container" style="margin: 0; padding: 1rem;">
                            <div style="width: 100%;">
                                <div style="color: var(--tiktok-black); line-height: 1.6; margin-bottom: 0.8rem;">
                                    {evidence['content']}
                                </div>
                                <div style="display: flex; gap: 1rem; font-size: 0.8rem; color: var(--tiktok-text-gray);">
                                    <span><strong>📊 Similarity:</strong> {evidence.get('similarity_score', 0):.2f}</span>
                                    {f'<span><strong>🤖 AI Rank:</strong> {evidence.get("ai_relevance_score", "N/A")}/5</span>' if evidence.get('ai_relevance_score') else ''}
                                    {f'<span><strong>🔗 Ref:</strong> {evidence.get("chunk_id", "")[:8]}...</span>' if evidence.get('chunk_id') else ''}
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="content-section">
                    <div class="section-title">📋 No Evidence Available</div>
                    <div class="section-content">No supporting evidence was found for this analysis.</div>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown('</div>', unsafe_allow_html=True)
        
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()