import os
import streamlit as st
from dotenv import load_dotenv

# Load frontend env variables if present
load_dotenv()

# Set up page configurations at the very top (mandatory in Streamlit)
st.set_page_config(
    page_title="Simple RAG Assistant",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="expanded"
)

from components.styles import inject_premium_styles
from services.api_client import APIClient

# Inject corporate brand stylesheet
inject_premium_styles()

# Initialize Session State
if "active_page" not in st.session_state:
    st.session_state.active_page = "Upload Documents"

# Define dynamic page imports to keep architecture clean and prevent circular references
def render_upload_page():
    from pages.upload_page import render_upload
    render_upload()

def render_chat_page():
    from pages.chat_page import render_chat
    render_chat()

def render_search_page():
    from pages.search_page import render_search
    render_search()

def render_summary_page():
    from pages.summary_page import render_summary
    render_summary()

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================

st.sidebar.markdown(
    """
    <div style='text-align: center; margin-bottom: 20px;'>
        <h2 style='color: #6366F1; font-weight: 700; margin: 0;'>� RAG Assistant</h2>
        <p style='color: #94A3B8; font-size: 11px;'>Simple Document Q&A System</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Core RAG Features Navigation
st.sidebar.markdown("<p style='color: #64748B; font-size: 11px; font-weight:600; margin-bottom: 5px; letter-spacing:0.05em;'>KNOWLEDGE MANAGEMENT</p>", unsafe_allow_html=True)
doc_pages = {
    "Upload Documents": "📤 Upload Documents",
}

st.sidebar.markdown("<p style='color: #64748B; font-size: 11px; font-weight:600; margin-top:15px; margin-bottom: 5px; letter-spacing:0.05em;'>AI ASSISTANT</p>", unsafe_allow_html=True)
ai_pages = {
    "Chat Assistant": "💬 Chat Assistant",
    "Semantic Search": "🔍 Semantic Search",
    "Summaries": "📝 Summaries",
}

# Render unified selector list
all_pages = {}
all_pages.update(doc_pages)
all_pages.update(ai_pages)

# Get current page index to maintain state
page_keys = list(all_pages.keys())
default_idx = page_keys.index(st.session_state.active_page) if st.session_state.active_page in page_keys else 0

selected_page_label = st.sidebar.radio(
    "Navigation",
    options=list(all_pages.values()),
    index=default_idx,
    label_visibility="collapsed"
)

# Map label back to key
st.session_state.active_page = [k for k, v in all_pages.items() if v == selected_page_label][0]

# ==========================================
# PAGE ROUTING
# ==========================================

page = st.session_state.active_page

try:
    if page == "Upload Documents":
        render_upload_page()
    elif page == "Chat Assistant":
        render_chat_page()
    elif page == "Semantic Search":
        render_search_page()
    elif page == "Summaries":
        render_summary_page()
except Exception as e:
    st.error(f"Failed to render page '{page}': {str(e)}")
