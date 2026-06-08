import json
import streamlit as st
from services.api_client import APIClient

def render_chat():
    """Renders the simple RAG Chat Assistant console."""
    st.markdown(
        """
        <div class='brand-header-card'>
            <h1>💬 Chat Assistant</h1>
            <p>Ask questions about your uploaded documents. Answers include source citations with page numbers and relevance scores.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Initialize chat history in session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Render citations for assistant messages
            if message["role"] == "assistant" and message.get("citations"):
                st.markdown("<p style='font-size:12px; color:#64748B; font-weight:600; margin-top:10px; margin-bottom:5px;'>Sources & References:</p>", unsafe_allow_html=True)
                chips_html = ""
                for c in message["citations"]:
                    chips_html += f"""
                    <div class='citation-chip'>
                        <span class='citation-idx'>{c['index']}</span>
                        <span>{c['source']} (Page {c['page']})</span>
                        <span class='citation-score'>Relevance: {c['relevance_score']}%</span>
                    </div>
                    """
                st.markdown(chips_html, unsafe_allow_html=True)
    
    # Chat input
    query = st.chat_input("Ask a question about your documents...")
    
    if query:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": query})
        
        # Render user query
        with st.chat_message("user"):
            st.markdown(query)
        
        # Render assistant response
        with st.chat_message("assistant"):
            citations = []
            
            try:
                # Initialize stream
                token_stream = APIClient.send_chat_message_stream(query)
                
                # Intercept first token chunk containing source citations
                first_chunk = next(token_stream, "")
                text_start = ""
                
                if "[SOURCES_METADATA]:" in first_chunk:
                    parts = first_chunk.split("\n", 1)
                    meta_line = parts[0]
                    text_start = parts[1] if len(parts) > 1 else ""
                    
                    json_str = meta_line.replace("[SOURCES_METADATA]:", "").strip()
                    citations = json.loads(json_str)
                else:
                    text_start = first_chunk
                
                # Stream writer generator
                def output_generator():
                    if text_start:
                        yield text_start
                    for token in token_stream:
                        yield token
                
                # Typewriter effect
                full_answer = st.write_stream(output_generator())
                
                # Render citations
                if citations:
                    st.markdown("<p style='font-size:12px; color:#64748B; font-weight:600; margin-top:10px; margin-bottom:5px;'>Sources & References:</p>", unsafe_allow_html=True)
                    chips_html = ""
                    for c in citations:
                        chips_html += f"""
                        <div class='citation-chip'>
                            <span class='citation-idx'>{c['index']}</span>
                            <span>{c['source']} (Page {c['page']})</span>
                            <span class='citation-score'>Relevance: {c['relevance_score']}%</span>
                        </div>
                        """
                    st.markdown(chips_html, unsafe_allow_html=True)
                
                # Add assistant message to chat history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": full_answer,
                    "citations": citations
                })
                
            except StopIteration:
                st.warning("No response received.")
            except Exception as stream_err:
                st.error(f"Failed to stream response: {str(stream_err)}")
