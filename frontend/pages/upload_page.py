import json
import streamlit as st
from services.api_client import APIClient


def render_upload():
    left_col, right_col = st.columns([1, 1], gap="medium")

    # ── LEFT: Upload + Knowledge Base ────────────────────────────────────────
    with left_col:
        # Panel wrapper
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-header'>Upload Knowledge</div>", unsafe_allow_html=True)
        st.markdown("<div style='padding:16px 20px;'>", unsafe_allow_html=True)

        # Drop zone
        st.markdown(
            """
            <div style='border:1.5px dashed #EBEBED; border-radius:10px;
                        background:#F7F7F8; padding:28px 16px; text-align:center; margin-bottom:4px;'>
                <div style='font-size:22px; margin-bottom:8px;'>⬆</div>
                <div style='font-size:13.5px; font-weight:500; color:#5C5F6A; margin-bottom:4px;'>
                    Click to upload or drag and drop
                </div>
                <div style='font-size:12px; color:#9EA3AF;'>PDF, TXT, MD or DOCX (max. 10MB)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        uploaded_files = st.file_uploader(
            "upload",
            type=["pdf", "docx", "pptx", "txt", "md"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )

        if uploaded_files:
            valid_files = [f for f in uploaded_files if len(f.getvalue()) / 1048576 <= 10.0]
            skipped = len(uploaded_files) - len(valid_files)
            if skipped:
                st.warning(f"{skipped} file(s) exceed 10 MB and were skipped.")

            st.markdown(
                f"<p style='font-size:13px;color:#5C5F6A;margin:8px 0 4px;'>"
                f"<b>{len(valid_files)}</b> file(s) ready</p>",
                unsafe_allow_html=True,
            )
            if valid_files:
                if st.button("Process & Upload", use_container_width=True, type="primary"):
                    with st.spinner("Processing…"):
                        try:
                            results = APIClient.upload_documents(valid_files)
                            st.success(f"Processed {len(results)} document(s).")
                            for doc in results:
                                st.toast(f"✓ {doc['name']} — {doc['chunk_count']} chunks")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Upload failed: {str(e)}")

        st.markdown("</div>", unsafe_allow_html=True)

        # Breadcrumb + Add New row
        st.markdown(
            """
            <div style='padding:4px 20px 10px; display:flex; align-items:center;
                        justify-content:space-between;'>
                <div style='font-size:13px; color:#9EA3AF; display:flex; align-items:center; gap:5px;'>
                    <span>Home</span>
                    <span style='font-size:11px;'>›</span>
                    <span style='color:#111318; font-weight:600;'>Knowledge Base</span>
                </div>
                <button style='display:inline-flex; align-items:center; gap:5px;
                    padding:5px 13px; background:#E8483A; color:white;
                    border:none; border-radius:6px; font-size:12.5px; font-weight:600;
                    font-family:Inter,sans-serif; cursor:pointer;'>
                    ＋ Add New
                </button>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # File table
        try:
            documents = APIClient.get_documents()
        except Exception:
            documents = []

        if documents:
            rows_html = ""
            for doc in documents:
                ext = doc.get("file_type", "").lower()
                if ".pdf" in ext:
                    icon_cls, icon = "ficon-pdf", "📄"
                elif ".docx" in ext:
                    icon_cls, icon = "ficon-docx", "📝"
                elif ".pptx" in ext:
                    icon_cls, icon = "ficon-pptx", "📊"
                elif ".md" in ext:
                    icon_cls, icon = "ficon-md", "📋"
                else:
                    icon_cls, icon = "ficon-txt", "📃"

                size_bytes = doc.get("size_bytes", 0)
                size_str = (
                    f"{size_bytes / 1048576:.1f} MB" if size_bytes >= 1048576
                    else f"{size_bytes / 1024:.0f} KB" if size_bytes >= 1024
                    else f"{size_bytes} B"
                )
                uploaded_at = doc.get("uploaded_at", "")
                added_str = uploaded_at[:10] if uploaded_at else "—"

                rows_html += f"""
                <tr>
                    <td>
                        <div class='fname-cell'>
                            <div class='ficon {icon_cls}'>{icon}</div>
                            <span>{doc['name']}</span>
                        </div>
                    </td>
                    <td><span class='badge badge-indexed'>Indexed</span></td>
                    <td style='color:#5C5F6A;font-size:13px;'>{added_str}</td>
                    <td style='color:#5C5F6A;font-size:13px;'>{size_str}</td>
                </tr>"""
        else:
            rows_html = (
                "<tr><td colspan='4' style='text-align:center;color:#9EA3AF;"
                "padding:32px;font-size:13.5px;'>No documents yet.</td></tr>"
            )

        st.markdown(
            f"""
            <div style='padding:0 20px 20px;'>
            <table class='ftable'>
                <thead><tr>
                    <th>FILE NAME</th><th>STATUS</th><th>ADDED</th><th>SIZE</th>
                </tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── RIGHT: Chat Panel ─────────────────────────────────────────────────────
    with right_col:
        st.markdown(
            """
            <div class='panel' style='display:flex; flex-direction:column;'>
                <div style='display:flex; align-items:center; justify-content:space-between;
                            padding:14px 20px; border-bottom:1px solid #F3F3F5;'>
                    <div style='display:flex; align-items:center; gap:10px;'>
                        <div class='chat-av-ai' style='background:#EBEBED; font-size:16px;'>🎙</div>
                        <div>
                            <div style='font-size:14px; font-weight:600; color:#111318;'>AI Assistant</div>
                            <div style='font-size:11px; color:#12B76A; font-weight:500;'>● RAG Active</div>
                        </div>
                    </div>
                    <div style='font-size:20px; color:#9EA3AF; cursor:pointer; line-height:1;'>+</div>
                </div>
            """,
            unsafe_allow_html=True,
        )

        # Greeting if no history
        if not st.session_state.chat_history:
            st.markdown(
                """
                <div style='padding:20px 20px 8px;'>
                    <div style='display:flex; gap:10px; align-items:flex-start; margin-bottom:12px;'>
                        <div class='chat-av-ai'>🎙</div>
                        <div>
                            <div class='chat-ai-bubble'>
                                Hello! I'm ready to answer questions about your knowledge base.
                                Upload documents on the left to get started.
                            </div>
                            <div class='chat-ts'>Just now</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown("<div style='padding:16px 20px 4px;'>", unsafe_allow_html=True)
            for msg in st.session_state.chat_history:
                if msg["role"] == "assistant":
                    st.markdown(
                        f"""
                        <div style='display:flex; gap:10px; align-items:flex-start; margin-bottom:14px;'>
                            <div class='chat-av-ai'>🎙</div>
                            <div>
                                <div class='chat-ai-bubble'>{msg['content']}</div>
                                <div class='chat-ts'>Just now</div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if msg.get("citations"):
                        chips = "".join(
                            f"<span class='c-chip'><span class='c-idx'>{c['index']}</span>"
                            f"{c['source']} p.{c['page']}"
                            f"<span class='c-score'>{c['relevance_score']}%</span></span>"
                            for c in msg["citations"]
                        )
                        st.markdown(
                            f"<div style='margin:-8px 0 14px 42px;'>{chips}</div>",
                            unsafe_allow_html=True,
                        )
                else:
                    st.markdown(
                        f"""
                        <div style='display:flex; gap:10px; flex-direction:row-reverse;
                                    align-items:flex-start; margin-bottom:14px;'>
                            <div class='chat-av-user'>MT</div>
                            <div>
                                <div class='chat-user-bubble'>{msg['content']}</div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            st.markdown("</div>", unsafe_allow_html=True)

        # Input area
        st.markdown(
            """
            <div style='padding:10px 20px 4px; border-top:1px solid #F3F3F5; margin-top:4px;'>
            """,
            unsafe_allow_html=True,
        )

        query = st.chat_input("Ask a question about your documents…")

        st.markdown(
            """
            <p style='font-size:10.5px; color:#9EA3AF; text-align:center; margin:2px 0 12px;'>
                AI can make mistakes. Verify important information.
            </p>
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if query:
            st.session_state.chat_history.append({"role": "user", "content": query})
            citations, full_answer = [], ""
            try:
                stream = APIClient.send_chat_message_stream(query)
                first = next(stream, "")
                text_start = ""
                if "[SOURCES_METADATA]:" in first:
                    parts = first.split("\n", 1)
                    json_str = parts[0].replace("[SOURCES_METADATA]:", "").strip()
                    citations = json.loads(json_str)
                    text_start = parts[1] if len(parts) > 1 else ""
                else:
                    text_start = first

                full_answer = text_start + "".join(stream)
            except Exception as e:
                full_answer = f"Error: {str(e)}"

            st.session_state.chat_history.append(
                {"role": "assistant", "content": full_answer, "citations": citations}
            )
            st.rerun()

        if st.session_state.chat_history:
            if st.button("Clear chat", key="clear_home"):
                st.session_state.chat_history = []
                st.rerun()
