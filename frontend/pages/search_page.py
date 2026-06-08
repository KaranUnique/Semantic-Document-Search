import streamlit as st
from services.api_client import APIClient

def render_search():
    """Renders the Semantic Search page."""
    st.markdown(
        """
        <div class='brand-header-card'>
            <h1>🔍 Semantic Search</h1>
            <p>Search your documents using vector embeddings to find semantically similar content. Results include relevance scores and source citations.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2 = st.columns([8, 2])
    
    with col1:
        query = st.text_input("Enter Search Term or Concept", placeholder="e.g. quarterly profit projections or vacation policy")
    with col2:
        top_k = st.selectbox("Top Results (K)", options=[3, 5, 10, 15], index=1)
        
    if st.button("🔍 Search", use_container_width=True):
        if not query.strip():
            st.warning("Please enter a valid search term.")
            return
            
        with st.spinner("Searching documents..."):
            try:
                results = APIClient.semantic_search(query, top_k)
                
                if not results:
                    st.info("No matching text chunks found in your document library.")
                    return
                    
                st.markdown(f"<h4>Found {len(results)} relevant passages:</h4>", unsafe_allow_html=True)
                
                # Render matching chunk cards
                for idx, r in enumerate(results):
                    ref_num = idx + 1
                    
                    # File type color badge
                    ext = r["file_type"].lower()
                    badge_color = "#E2E8F0"
                    text_color = "#475569"
                    if ext == ".pdf":
                        badge_color = "#FEE2E2"
                        text_color = "#991B1B"
                    elif ext in [".docx", ".doc"]:
                        badge_color = "#DBEAFE"
                        text_color = "#1E40AF"
                    elif ext in [".pptx", ".ppt"]:
                        badge_color = "#FFEDD5"
                        text_color = "#9A3412"
                        
                    st.markdown(
                        f"""
                        <div style='background-color: white; border: 1px solid #E2E8F0; padding: 20px; border-radius: 12px; margin-bottom: 15px; box-shadow:0 2px 4px rgba(0,0,0,0.01);'>
                            <div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; border-bottom:1px solid #F1F5F9; padding-bottom:8px; margin-bottom:12px;'>
                                <div style='display:flex; gap:10px; align-items:center;'>
                                    <span style='background-color:#2563EB; color:white; border-radius:50%; width:20px; height:20px; display:inline-flex; align-items:center; justify-content:center; font-size:12px; font-weight:700;'>{ref_num}</span>
                                    <strong style='font-size:14.5px; color:#1E293B;'>📄 {r["source"]}</strong>
                                    <span style='background-color:{badge_color}; color:{text_color}; font-size:10px; font-weight:600; padding:1px 6px; border-radius:4px;'>{r["file_type"].upper()}</span>
                                    <span style='color:#64748B; font-size:12.5px;'>Page: {r["page"]}</span>
                                </div>
                                <span style='background-color:#F0FDFA; color:#0D9488; border:1px solid #CCFBF1; font-size:12px; font-weight:600; padding:3px 8px; border-radius:6px;'>
                                    Relevance: {r["relevance_score"]}%
                                </span>
                            </div>
                            <p style='font-size:14px; color:#334155; line-height:1.5; margin:0; font-family: monospace; background-color:#F8FAFC; padding:12px; border-radius:6px; border:1px solid #F1F5F9;'>
                                {r["text"]}
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            except Exception as e:
                st.error(f"Search failed: {str(e)}")
