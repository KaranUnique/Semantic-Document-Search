import streamlit as st
from services.api_client import APIClient

def render_upload():
    """Renders the document ingestion (Batch Upload) screen."""
    st.markdown(
        """
        <div class='brand-header-card'>
            <h1>📤 Upload Documents</h1>
            <p>Upload files to process and index them for semantic search and Q&A.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2 = st.columns([1.8, 1.2])
    
    with col1:
        st.markdown("<h3 style='color:#1E3A8A;'>Select Files to Upload</h3>", unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Upload files",
            type=["pdf", "docx", "pptx", "txt"],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )
        
        # Ingestion Button
        if uploaded_files:
            st.write(f"📂 {len(uploaded_files)} files selected.")
            
            # Form check for individual file size limits
            valid_files = []
            max_size_mb = 15.0
            
            for file in uploaded_files:
                size_mb = len(file.getvalue()) / (1024.0 * 1024.0)
                if size_mb > max_size_mb:
                    st.warning(f"⚠️ '{file.name}' exceeds the {max_size_mb}MB limit ({size_mb:.1f}MB) and will be skipped.")
                else:
                    valid_files.append(file)
            
            if valid_files:
                if st.button("🚀 Process & Upload", use_container_width=True):
                    with st.spinner("Processing files..."):
                        try:
                            # Batch Ingest
                            results = APIClient.upload_documents(valid_files)
                            
                            st.success(f"🎉 Success! Successfully processed {len(results)} documents.")
                            
                            # Log individual metrics
                            for doc in results:
                                st.toast(f"Processed '{doc['name']}' ({doc['chunk_count']} chunks)", icon="✅")
                                
                        except Exception as e:
                            st.error(f"Upload failed: {str(e)}")
            else:
                st.error("No valid files available for upload. Please check file sizes.")
        else:
            st.info("Drag and drop your documents here (PDF, DOCX, PPTX, or TXT). Limit 15MB per file.")

    with col2:
        st.markdown(
            """
            <div style='background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 20px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);'>
                <h4 style='color:#1E3A8A; margin-top:0;'>🧠 How It Works</h4>
                <hr style='border:0; border-top:1px solid #E2E8F0; margin:10px 0;'>
                
                <h5 style='color:#0D9488; margin-top:10px; margin-bottom:5px;'>📖 Text Extraction</h5>
                <p style='font-size:12.5px; color:#4B5563; margin-bottom:12px;'>
                    Files are parsed page-by-page. For PDFs, native text is extracted. Word, PowerPoint, and Text files are processed to preserve content structure.
                </p>

                <h5 style='color:#0D9488; margin-top:10px; margin-bottom:5px;'>✂️ Text Chunking</h5>
                <p style='font-size:12.5px; color:#4B5563; margin-bottom:12px;'>
                    Extracted text is partitioned using a <strong>Recursive Character Splitter</strong> with a target size of 1,000 characters and a 200-character overlap for better context.
                </p>
                
                <h5 style='color:#0D9488; margin-top:10px; margin-bottom:5px;'>🔢 Embeddings</h5>
                <p style='font-size:12.5px; color:#4B5563; margin-bottom:0;'>
                    Each chunk is converted to a vector embedding using <strong>sentence-transformers</strong> (all-MiniLM-L6-v2) and stored in ChromaDB for semantic search.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
