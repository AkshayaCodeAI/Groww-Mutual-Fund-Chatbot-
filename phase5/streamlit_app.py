"""
Phase 5: Frontend — Groww MF FAQ Chatbot (Streamlit).
Run from project root: streamlit run phase5/streamlit_app.py
Uses Phase 4 API at CHAT_API_URL or Phase 3 RAG in-process if API is unavailable.
"""

import os
import sys
from pathlib import Path

# Project root on path for phase3/phase4 imports
ROOT = Path(__file__).resolve().parents[1]  # project root (folder containing phase1..phase6, data)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))  # so "from phase3.pipeline" works

import html
import streamlit as st

CHAT_API_URL = os.environ.get("CHAT_API_URL", "").strip()
# When no API URL or localhost, use in-process RAG so the bot answers without waiting for API timeout
USE_API = bool(CHAT_API_URL and "localhost" not in CHAT_API_URL.lower() and "127.0.0.1" not in CHAT_API_URL)
CHUNKS_PATH = ROOT / "data" / "chunks" / "all_chunks.jsonl"


def _ensure_chunks_exist() -> None:
    """If data/chunks/all_chunks.jsonl is missing (e.g. fresh deploy), build from phase1 + parsed."""
    if CHUNKS_PATH.exists():
        return
    try:
        from phase2.chunk import run_build_chunks
        (ROOT / "data" / "chunks").mkdir(parents=True, exist_ok=True)
        run_build_chunks()
    except Exception:
        pass


def inject_custom_css():
    """Responsive, mobile-friendly CSS; bot left, user right; improved icons."""
    st.markdown("""
    <style>
    /* Container: comfortable width on desktop, full width on mobile */
    .block-container {
        max-width: 42rem;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        padding-left: 1.25rem;
        padding-right: 1.25rem;
    }
    @media (min-width: 640px) {
        .block-container { padding-left: 2rem; padding-right: 2rem; }
    }
    /* Chat row: bot on left, user on right */
    [data-testid="stChatMessage"] {
        padding: 0.5rem 0;
        display: flex;
        align-items: flex-start;
        width: 100%;
    }
    /* Bot (assistant) on the left: avatar left, message right of avatar */
    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        flex-direction: row;
        justify-content: flex-start;
        align-self: flex-start;
        background: #fafafa !important;
        border-radius: 1rem;
        border: 1px solid #e0e0e0;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0 0.5rem 0;
        max-width: 85%;
    }
    /* User on the right: whole block pushed right, avatar left of bubble */
    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        flex-direction: row;
        justify-content: flex-end;
        align-self: flex-end;
        margin-left: auto;
        max-width: 85%;
    }
    /* User question bubble: soft blue, stays right-aligned */
    .user-question-bubble {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border: 1px solid #90caf9;
        border-radius: 0.75rem;
        padding: 0.75rem 1rem;
        margin: 0.25rem 0;
        color: #1565c0;
        font-size: 1rem;
        line-height: 1.5;
    }
    /* Avatars: circular, Groww-style */
    [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-user"],
    [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-assistant"] {
        border-radius: 50% !important;
        overflow: hidden;
        box-shadow: 0 2px 6px rgba(106, 125, 223, 0.25);
        flex-shrink: 0;
        min-width: 2.25rem !important;
        min-height: 2.25rem !important;
    }
    /* User icon: Groww blue */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="chatAvatarIcon-user"] {
        background: #6A7DDF !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="chatAvatarIcon-user"] svg,
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="chatAvatarIcon-user"] img {
        filter: brightness(0) invert(1);
    }
    /* Bot icon: Groww gradient (blue top, mint green bottom) */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="chatAvatarIcon-assistant"] {
        background: linear-gradient(180deg, #6A7DDF 0%, #6AEBAF 100%) !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="chatAvatarIcon-assistant"] svg,
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="chatAvatarIcon-assistant"] img {
        filter: brightness(0) invert(1);
    }
    /* Example question buttons: theme-aware (light / dark / custom) */
    .stButton > button {
        width: 100%;
        min-height: 2.75rem;
        padding: 0.6rem 1rem;
        font-size: 0.95rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
        text-align: left;
        border: 1px solid #6A7DDF;
        background: #e8ecfc;
        color: #2d3a7b;
    }
    .stButton > button:hover {
        background: #d4dcf7;
        border-color: #6A7DDF;
        color: #1a2260;
    }
    @media (min-width: 640px) {
        .stButton > button { width: 100%; max-width: 100%; }
    }
    /* Chat input: soft gray border (no red/alert look); blue on focus */
    div[data-testid="stChatInput"] {
        border: 1px solid #b0bec5 !important;
        box-shadow: none !important;
    }
    div[data-testid="stChatInput"]:focus-within {
        border-color: #90caf9 !important;
        box-shadow: 0 0 0 1px rgba(144, 202, 249, 0.3) !important;
    }
    [data-testid="stChatInput"] textarea {
        min-height: 2.75rem;
        font-size: 1rem;
        border: none !important;
        box-shadow: none !important;
    }
    [data-testid="stChatInput"] textarea:focus {
        border: none !important;
        box-shadow: none !important;
    }
    /* Info box (disclaimer): subtle */
    .stAlert {
        border-radius: 0.5rem;
    }
    /* Spacing for answer block */
    .answer-block {
        padding: 0.75rem 0;
    }
    /* Disclaimer below chat input (fixed at bottom, after "Ask a question" bar) */
    .disclaimer-below-chat {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        text-align: center;
        padding: 8px 16px;
        font-size: 0.8rem;
        color: #666;
        background: #fafafa;
        border-top: 1px solid #e8e8e8;
        z-index: 999;
    }
    [data-theme="dark"] .disclaimer-below-chat,
    [data-theme="Dark"] .disclaimer-below-chat {
        background: #1e3a5f;
        border-top-color: #1565c0;
        color: #b0b0b0;
    }

    /* ========== Dark mode: dark blue bubbles for questions and answers ========== */
    [data-theme="dark"] .user-question-bubble {
        background: #0d47a1 !important;
        border-color: #0a3d91 !important;
        color: #ffffff !important;
    }
    /* Bot/assistant message bubble: dark blue-gray (no white boxes) */
    [data-theme="dark"] div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background: #1e3a5f !important;
        border-color: #1565c0 !important;
    }
    [data-theme="dark"] .stButton > button {
        color: #e3f2fd !important;
        background: #2d3a7b !important;
        border-color: #6A7DDF !important;
    }
    [data-theme="dark"] .stButton > button:hover {
        background: #3d4d9a !important;
        border-color: #6AEBAF !important;
        color: #ffffff !important;
    }
    [data-theme="dark"] [data-testid="stChatInput"],
    [data-theme="dark"] [data-testid="stChatInput"] textarea {
        color: #ffffff !important;
        background-color: #1e3a5f !important;
        border-color: #1565c0 !important;
    }
    [data-theme="dark"] [data-testid="stChatInput"] textarea::placeholder {
        color: #b0b0b0 !important;
    }
    /* Chat message text in dark mode: light on dark blue */
    [data-theme="dark"] [data-testid="stChatMessage"] [data-testid="stMarkdown"],
    [data-theme="dark"] [data-testid="stChatMessage"] [data-testid="stMarkdown"] p {
        color: #e3f2fd !important;
    }
    /* Fallback: Streamlit may use "Dark" or "Light" (capital D/L) */
    [data-theme="Dark"] .user-question-bubble {
        background: #0d47a1 !important;
        border-color: #0a3d91 !important;
        color: #ffffff !important;
    }
    [data-theme="Dark"] div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background: #1e3a5f !important;
        border-color: #1565c0 !important;
    }
    [data-theme="Dark"] .stButton > button {
        color: #e3f2fd !important;
        background: #2d3a7b !important;
        border-color: #6A7DDF !important;
    }
    [data-theme="Dark"] .stButton > button:hover {
        background: #3d4d9a !important;
        border-color: #6AEBAF !important;
        color: #ffffff !important;
    }
    /* Light theme (explicit for custom theme when set to light) */
    [data-theme="light"] .stButton > button,
    [data-theme="Light"] .stButton > button {
        border: 1px solid #6A7DDF !important;
        background: #e8ecfc !important;
        color: #2d3a7b !important;
    }
    [data-theme="light"] .stButton > button:hover,
    [data-theme="Light"] .stButton > button:hover {
        background: #d4dcf7 !important;
        border-color: #6A7DDF !important;
        color: #1a2260 !important;
    }
    </style>
    """, unsafe_allow_html=True)


def _scheme_id_from_url(url: str) -> str | None:
    """Extract scheme_id from a Groww scheme page URL, or None."""
    if not url or "/mutual-funds/" not in url:
        return None
    parts = url.rstrip("/").split("/")
    if len(parts) < 2:
        return None
    slug = parts[-1]
    if slug in ("mutual-funds", "help", "blog") or not slug:
        return None
    return slug


def _query_uses_pronoun_for_scheme(query: str) -> bool:
    """True if the query uses a pronoun referring to a previously mentioned scheme."""
    q = query.lower().strip()
    phrases = (
        "this fund", "this scheme", "the fund", "the scheme",
        "above fund", "above scheme", "that fund", "that scheme",
        "same fund", "same scheme", "this fund's", "the above fund",
    )
    return any(p in q for p in phrases)


def call_api(query: str, scheme_id: str | None = None) -> dict | None:
    """Call Phase 4 API. Returns None on failure. scheme_id used for pronoun resolution."""
    if not CHAT_API_URL:
        return None
    try:
        import urllib.request
        import json
        body = {"query": query}
        if scheme_id:
            body["scheme_id"] = scheme_id
        req = urllib.request.Request(
            f"{CHAT_API_URL.rstrip('/')}/chat",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.load(resp)
    except Exception:
        return None


def run_rag_in_process(query: str, scheme_id: str | None = None) -> dict:
    """Run Phase 3 RAG pipeline in-process. Pass explicit chunks path so chunks are found regardless of cwd."""
    try:
        from phase3.pipeline import run_pipeline
        return run_pipeline(query, scheme_id=scheme_id, chunks_path=str(CHUNKS_PATH))
    except ImportError:
        return {
            "answer": "RAG pipeline not available (Phase 3). Start the API or run phase2 chunk + phase3 in this repo.",
            "citation_url": "",
            "last_updated": "",
            "refused": False,
        }
    except Exception as e:
        return {
            "answer": f"Pipeline error: {e}. Ensure phase2 chunk has been run (data/chunks exist).",
            "citation_url": "",
            "last_updated": "",
            "refused": False,
        }


def main():
    st.set_page_config(
        page_title="Groww MF",
        page_icon="💬",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    _ensure_chunks_exist()  # build chunks on first run if missing (deploy-ready)
    inject_custom_css()

    st.title("Groww MF")
    st.caption("Your Groww mutual fund facts assistant.")

    welcome = (
        "Hi! I'm **Groww MF**. Ask me anything about these mutual fund schemes—"
        "expense ratios, minimum SIP, riskometer, and more."
    )
    st.info(welcome)

    # Persistent chat history and last scheme (for "this fund" / pronoun resolution)
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "last_scheme_id" not in st.session_state:
        st.session_state.last_scheme_id = None

    example_queries = [
        "Expense ratio of HDFC Silver ETF FoF?",
        "Minimum SIP for SBI Gold Fund?",
        "What is Riskometer?",
    ]
    for q in example_queries:
        if st.button(q, key=q):
            st.session_state["last_query"] = q

    query = st.chat_input("Ask a question...")
    if query is not None:
        st.session_state["last_query"] = query

    # Process new query (from input or example button) and add to history
    if "last_query" in st.session_state:
        q = st.session_state["last_query"]
        # Resolve pronouns: "this fund" / "the fund" -> use last-discussed scheme
        use_scheme_id = None
        if _query_uses_pronoun_for_scheme(q) and st.session_state.get("last_scheme_id"):
            use_scheme_id = st.session_state.last_scheme_id
        # Append user message to chat history
        st.session_state.messages.append({"role": "user", "content": q})
        result = None
        try:
            with st.spinner("Getting answer..."):
                if USE_API:
                    result = call_api(q, scheme_id=use_scheme_id)
                if result is None:
                    result = run_rag_in_process(q, scheme_id=use_scheme_id)
        except Exception as e:
            result = {
                "answer": f"Something went wrong while getting an answer. Please try again. ({e!s})",
                "citation_url": "",
                "last_updated": "",
                "refused": False,
            }
        if result is None:
            result = {
                "answer": "Could not reach the answer service. Please try again.",
                "citation_url": "",
                "last_updated": "",
                "refused": False,
            }
        answer = (result.get("answer") or "").strip()
        if not answer and result.get("citation_url"):
            answer = "See the source link below for details from our data."
        if not answer:
            answer = "No answer could be generated. Please try rephrasing your question or ask something like: 'What is Riskometer?' or 'Expense ratio of HDFC Silver ETF FoF?'"
        st.session_state.messages.append({
            "role": "assistant",
            "answer": answer,
            "citation_url": result.get("citation_url", ""),
            "last_updated": result.get("last_updated", ""),
            "refused": result.get("refused", False),
        })
        # Remember last scheme from citation so next "this fund" refers to it
        url = result.get("citation_url", "")
        if url:
            sid = _scheme_id_from_url(url)
            if sid:
                st.session_state.last_scheme_id = sid
        del st.session_state["last_query"]

    # Render full chat history in the chat area
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(
                    f'<div class="user-question-bubble">{html.escape(msg["content"])}</div>',
                    unsafe_allow_html=True,
                )
        else:
            with st.chat_message("assistant"):
                answer_text = (msg.get("answer") or "").strip()
                if not answer_text and msg.get("citation_url"):
                    answer_text = "See the source link below for details from our data."
                if not answer_text:
                    answer_text = "No answer could be generated. Please try rephrasing your question."
                st.markdown(answer_text)
                url = msg.get("citation_url", "")
                # One clear citation link in every answer
                if url:
                    if msg.get("refused"):
                        st.markdown(f"**Learn more:** [Groww Mutual Funds blog]({url})")
                    else:
                        st.markdown(f"**Source:** [View source]({url})")
                lu = msg.get("last_updated", "")
                if lu and not msg.get("refused"):
                    st.caption(f"Last updated from sources: {lu}")
                if msg.get("refused"):
                    st.caption("Facts only; no investment advice.")

    # Disclaimer fixed below the "Ask a question" chat input
    st.markdown(
        '<div class="disclaimer-below-chat">Facts only, no investment advice.</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
