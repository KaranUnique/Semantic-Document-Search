import json
import streamlit as st
from services.api_client import APIClient


def render_chat():
    st.markdown(
        """
        <div style='margin-bottom:16px;'>
            <div style='font-size:20px; font-weight:700; color:#111318; margin-bottom:3px;'>
                Chat Assistant
            </div>
            <div style='font-size:13px; color:#9EA3AF;'>
                Ask questions about your uploaded documents.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class='panel'>
            <div style='display:flex; align-items:center; justify-content:space-between;
                        padding:14px 20px; border-bottom:1px solid #F3F3F5;'>
                <div style='display:flex; align-items:center; gap:10px;'>
                    <div class='chat-av-ai'>🎙</div>
                    <div>
                        <div style='font-size:14px; font-weight:600; color:#111318;'>AI Assistant</div>
                        <div style='font-size:11px; color:#12B76A; font-weight:500;'>● RAG Active</div>
                    </div>
                </div>
                <div style='font-size:20px; color:#9EA3AF;'>+</div>
            </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='padding:16px 20px 4px;'>", unsafe_allow_html=True)

    if not st.session_state.chat_history:
        st.markdown(
            """
            <div style='display:flex; gap:10px; align-items:flex-start; margin-bottom:14px;'>
                <div class='chat-av-ai'>🎙</div>
                <div>
                    <div class='chat-ai-bubble'>
                        Hello! I'm ready to answer questions about your knowledge base.
                        Upload documents first, then ask me anything.
                    </div>
                    <div class='chat-ts'>Just now</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
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

    # Input
    st.markdown(
        "<div style='padding:10px 20px 4px; border-top:1px solid #F3F3F5;'>",
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
        if st.button("Clear chat", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()
