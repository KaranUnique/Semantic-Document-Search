import streamlit as st
from services.api_client import APIClient


def render_summary():
    st.markdown(
        """
        <div style='margin-bottom:16px;'>
            <div style='font-size:20px; font-weight:700; color:#111318; margin-bottom:3px;'>
                Document Summaries
            </div>
            <div style='font-size:13px; color:#9EA3AF;'>
                Generate a structured AI summary with key insights for any uploaded document.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        documents = APIClient.get_documents()
    except Exception as e:
        st.error(f"Failed to load documents: {str(e)}")
        return

    if not documents:
        st.markdown(
            "<div class='panel' style='padding:48px; text-align:center; color:#9EA3AF; font-size:13.5px;'>"
            "No documents found. Upload files on the Home page first.</div>",
            unsafe_allow_html=True,
        )
        return

    doc_names = [d["name"] for d in documents]

    st.markdown("<div class='panel' style='padding:16px 20px; margin-bottom:16px;'>", unsafe_allow_html=True)

    col1, col2 = st.columns([7, 3])
    with col1:
        selected = st.selectbox("Document", options=doc_names, label_visibility="collapsed")
    with col2:
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        submit = st.button("Generate Summary", use_container_width=True, type="primary")

    st.markdown("</div>", unsafe_allow_html=True)

    if not submit:
        return

    st.markdown(
        f"<p style='font-size:13px; color:#9EA3AF; margin-bottom:12px;'>"
        f"Summarising <span style='color:#111318; font-weight:600;'>{selected}</span>…</p>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='panel' style='padding:20px 24px;'>", unsafe_allow_html=True)
    placeholder = st.empty()
    full_summary = ""

    try:
        for token in APIClient.summarize_document_stream(selected):
            full_summary += token
            placeholder.markdown(full_summary)
    except Exception as e:
        st.error(f"Summary failed: {str(e)}")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    st.markdown("</div>", unsafe_allow_html=True)

    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.success("Summary generated.")
    with col_b:
        st.download_button(
            label="Download (.md)",
            data=full_summary,
            file_name=f"{selected.rsplit('.', 1)[0]}_summary.md",
            mime="text/markdown",
            use_container_width=True,
        )
