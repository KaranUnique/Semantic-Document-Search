import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="RAG Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

from components.styles import inject_styles

inject_styles()

if "active_page" not in st.session_state:
    st.session_state.active_page = "Home"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ── helpers ──────────────────────────────────────────────────────────────────
def _nav_btn(label, page_key, icon):
    is_active = st.session_state.active_page == page_key
    cls = "nav-active" if is_active else ""
    st.markdown(f"<div class='{cls}'>", unsafe_allow_html=True)
    if st.button(f"{icon}  {label}", key=f"nav_{page_key}", use_container_width=True):
        st.session_state.active_page = page_key
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div class='sb-profile'>
            <div class='sb-avatar'>MT</div>
            <div>
                <span class='sb-name'>Mike Taylor</span>
                <span class='sb-caret'>⌄</span>
            </div>
        </div>
        <div class='sb-divider'></div>
        <span class='sb-label'>WORKSPACE</span>
        """,
        unsafe_allow_html=True,
    )

    _nav_btn("Home", "Home", "⊞")
    _nav_btn("Team", "Team", "◎")

    st.markdown("<span class='sb-label'>PROJECTS</span>", unsafe_allow_html=True)

    # "Upload Documents" navigates to Home but needs a distinct key
    is_active = st.session_state.active_page in ("Home", "Upload Documents")
    cls = "nav-active" if is_active else ""
    st.markdown(f"<div class='{cls}'>", unsafe_allow_html=True)
    if st.button("▤  Upload Documents", key="nav_upload_docs", use_container_width=True):
        st.session_state.active_page = "Home"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # sub-items (indented style)
    for page_key, label in [
        ("Chat Assistant",  "Chat Assistant"),
        ("Semantic Search", "Semantic Search"),
        ("Summaries",       "Summaries"),
    ]:
        is_active = st.session_state.active_page == page_key
        cls = "nav-active" if is_active else ""
        st.markdown(f"<div class='{cls}' style='padding-left:12px;'>", unsafe_allow_html=True)
        if st.button(label, key=f"nav_{page_key}", use_container_width=True):
            st.session_state.active_page = page_key
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <span class='sb-label'>TAGS</span>
        <div class='sb-tag'><span class='sb-dot sb-dot-red'></span> Urgent</div>
        <div class='sb-tag'><span class='sb-dot sb-dot-green'></span> Reviewed</div>
        <div style='margin-top:auto; padding-top:24px;'>
            <div class='sb-settings'>⚙  Settings</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── PAGE ROUTING ──────────────────────────────────────────────────────────────
page = st.session_state.active_page

try:
    if page in ("Home", "Upload Documents"):
        from pages.upload_page import render_upload
        render_upload()
    elif page == "Chat Assistant":
        from pages.chat_page import render_chat
        render_chat()
    elif page == "Semantic Search":
        from pages.search_page import render_search
        render_search()
    elif page == "Summaries":
        from pages.summary_page import render_summary
        render_summary()
    elif page == "Team":
        st.markdown(
            "<div style='padding:32px;color:#9EA3AF;font-size:14px;'>Team management coming soon.</div>",
            unsafe_allow_html=True,
        )
    else:
        from pages.upload_page import render_upload
        render_upload()
except Exception as e:
    st.error(f"Failed to render page '{page}': {str(e)}")
