import streamlit as st
from services.api_client import APIClient

def render_summary():
    """Renders the document summarization page."""
    st.markdown(
        """
        <div class='brand-header-card'>
            <h1>📝 Document Summarization</h1>
            <p>Select any uploaded document and generate a structured AI summary with key insights and takeaways.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Load documents
    try:
        documents = APIClient.get_documents()
    except Exception as e:
        st.error(f"Failed to load document library: {str(e)}")
        documents = []
        
    if not documents:
        st.info("Your library is empty. Please visit the **Upload Documents** page to add files.")
        return
        
    doc_names = [d["name"] for d in documents]
    
    # Form select
    col1, col2 = st.columns([7, 3])
    with col1:
        selected_doc_name = st.selectbox("Choose a Document to Summarize", options=doc_names)
    with col2:
        st.write("")
        st.write("")
        submit = st.button("📝 Generate Summary", use_container_width=True)
        
    if submit:
        # Initialize Summary container
        st.markdown(f"<h3>Generating summary for: <i>{selected_doc_name}</i></h3>", unsafe_allow_html=True)
        summary_placeholder = st.empty()
        
        # Stream summary from backend
        try:
            token_stream = APIClient.summarize_document_stream(selected_doc_name)
            
            full_summary = ""
            # Stream tokens
            for token in token_stream:
                full_summary += token
                summary_placeholder.markdown(full_summary)
                
            # Offer download as Markdown on successful completion
            st.success("Summary generated successfully!")
            st.download_button(
                label="📥 Download Summary (.md)",
                data=full_summary,
                file_name=f"{selected_doc_name.split('.')[0]}_summary.md",
                mime="text/markdown",
                use_container_width=True
            )
        except Exception as summary_err:
            st.error(f"Summary generation failed: {str(summary_err)}")
