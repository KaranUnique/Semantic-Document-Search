import streamlit as st
from services.api_client import APIClient


def render_search():
    st.markdown(
        """
        <div style='margin-bottom:16px;'>
            <div style='font-size:20px; font-weight:700; color:#111318; margin-bottom:3px;'>
                Semantic Search
            </div>
            <div style='font-size:13px; color:#9EA3AF;'>
                Find relevant passages across your documents using vector similarity.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Search bar panel
    st.markdown("<div class='panel' style='padding:16px 20px; margin-bottom:16px;'>", unsafe_allow_html=True)

    col1, col2 = st.columns([8, 2])
    with col1:
        query = st.text_input(
            "query",
            placeholder="e.g. quarterly revenue projections or vacation policy",
            label_visibility="collapsed",
        )
    with col2:
        top_k = st.selectbox("k", options=[3, 5, 10, 15], index=1, label_visibility="collapsed")

    search_clicked = st.button("Search", use_container_width=True, type="primary")
    st.markdown("</div>", unsafe_allow_html=True)

    if not search_clicked:
        return

    if not query.strip():
        st.warning("Enter a search term first.")
        return

    with st.spinner("Searching…"):
        try:
            results = APIClient.semantic_search(query, top_k)
        except Exception as e:
            st.error(f"Search failed: {str(e)}")
            return

    if not results:
        st.markdown(
            "<div class='panel' style='padding:40px; text-align:center; color:#9EA3AF; font-size:13.5px;'>"
            "No matching passages found.</div>",
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        f"<p style='font-size:13px; color:#9EA3AF; margin-bottom:12px;'>"
        f"<span style='color:#111318; font-weight:600;'>{len(results)}</span> passages found</p>",
        unsafe_allow_html=True,
    )

    for idx, r in enumerate(results):
        ext = r.get("file_type", "").lower()
        if ".pdf" in ext:
            type_bg, type_color, type_label = "#FEE2E2", "#991B1B", "PDF"
        elif ".docx" in ext:
            type_bg, type_color, type_label = "#DBEAFE", "#1E40AF", "DOCX"
        elif ".pptx" in ext:
            type_bg, type_color, type_label = "#FFEDD5", "#9A3412", "PPTX"
        else:
            type_bg, type_color, type_label = "#F1F5F9", "#475569", ext.upper().replace(".", "") or "TXT"

        st.markdown(
            f"""
            <div class='panel' style='padding:14px 18px; margin-bottom:10px;'>
                <div style='display:flex; align-items:center; justify-content:space-between;
                            margin-bottom:10px; flex-wrap:wrap; gap:6px;'>
                    <div style='display:flex; align-items:center; gap:8px;'>
                        <span style='background:#3B82F6; color:#fff; border-radius:50%;
                                     width:20px; height:20px; display:inline-flex;
                                     align-items:center; justify-content:center;
                                     font-size:10px; font-weight:700;'>{idx+1}</span>
                        <span style='font-size:14px; font-weight:600; color:#111318;'>{r["source"]}</span>
                        <span style='background:{type_bg}; color:{type_color};
                                     font-size:10px; font-weight:600;
                                     padding:1px 7px; border-radius:4px;'>{type_label}</span>
                        <span style='font-size:12px; color:#9EA3AF;'>p. {r["page"]}</span>
                    </div>
                    <span style='background:#ECFDF5; color:#065F46; border:1px solid #D1FAE5;
                                 font-size:12px; font-weight:600;
                                 padding:3px 10px; border-radius:20px;'>
                        {r["relevance_score"]}% match
                    </span>
                </div>
                <div style='font-size:13px; color:#334155; line-height:1.55;
                             background:#F7F7F8; padding:10px 12px;
                             border-radius:6px; border:1px solid #EBEBED;
                             font-family:monospace;'>
                    {r["text"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
