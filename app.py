from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from src.wiki_engine import get_engine, get_generator, load_wiki_data


st.set_page_config(
    page_title="WikiQuest AI",
    page_icon="🎮",
    layout="centered",
    initial_sidebar_state="collapsed",
)


@st.cache_data
def cached_data() -> pd.DataFrame:
    return load_wiki_data()


@st.cache_resource
def cached_engine():
    return get_engine()


@st.cache_resource
def cached_generator():
    return get_generator()


def run_query(question: str, answer_style: str) -> dict:
    results = engine.search(question.strip(), category="All", top_k=5)
    answer = generator.answer(question.strip(), results, style=answer_style)
    return {"question": question.strip(), "answer": answer, "results": results}


data = cached_data()
engine = cached_engine()
generator = cached_generator()

if "messages" not in st.session_state:
    st.session_state.messages = []
else:
    st.session_state.messages = [
        message
        for message in st.session_state.messages
        if "<div class=" not in str(message.get("content", ""))
        and "&lt;div class=" not in str(message.get("content", ""))
        and "qa-assistant" not in str(message.get("content", ""))
        and "source-row" not in str(message.get("content", ""))
    ]
if "question_input_key" not in st.session_state:
    st.session_state.question_input_key = 0

st.markdown(
    """
    <style>
    :root {
        --ink: #f4f4f4;
        --muted: #a9a9a9;
        --paper: #000000;
        --line: #4a4a4a;
        --button: #0b0b0b;
        --source: #c4c4c4;
    }
    .stApp {
        background: var(--paper);
        color: var(--ink);
    }
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background: #000000 !important;
    }
    header, [data-testid="stToolbar"], [data-testid="stSidebar"], [data-testid="stDecoration"] {
        display: none;
    }
    .block-container {
        max-width: 1280px;
        padding-top: 42vh;
        padding-bottom: 7rem;
    }
    h1, h2, h3, p, label {
        letter-spacing: 0;
    }
    .main .block-container {
        text-align: center;
    }
    .app-title {
        color: #8d8d8d;
        font-size: 0.88rem;
        font-weight: 650;
        line-height: 1.2;
        margin-bottom: 0.25rem;
        text-align: center;
    }
    .app-subtitle {
        color: #6f6f6f;
        font-size: 0.72rem;
        line-height: 1.35;
        margin: 0 auto;
        max-width: 520px;
        text-align: center;
    }
    .app-footer {
        position: fixed;
        left: 0;
        right: 0;
        bottom: 2rem;
        z-index: 1;
        pointer-events: none;
    }
    div[data-testid="stHorizontalBlock"] {
        max-width: 1080px;
        margin-left: auto;
        margin-right: auto;
        gap: 0 !important;
        animation: barIn 420ms ease-out both;
        border: 1px solid var(--line);
        background: #030303;
    }
    div[data-testid="column"] {
        padding-left: 0 !important;
        padding-right: 0 !important;
    }
    [data-testid="stChatMessage"] {
        background: transparent;
        border: 0;
        padding: 0.2rem 0;
        color: #e8e8e8;
    }
    [data-testid="stChatMessage"] p {
        font-size: 1rem;
        line-height: 1.6;
        color: #e8e8e8;
    }
    [data-testid="stForm"] {
        border-radius: 0 !important;
        border: 1px solid var(--line);
        background: transparent;
        max-width: 760px;
        margin: 0 auto 1.2rem;
    }
    [data-testid="stForm"] label {
        color: var(--muted);
        font-size: 0.78rem;
        font-weight: 650;
        text-transform: uppercase;
    }
    [data-testid="stSelectbox"] {
        text-align: left;
    }
    [data-testid="stSelectbox"] div {
        border-radius: 0 !important;
    }
    [data-testid="stTextInput"] input {
        background: #030303;
        border: 0;
        border-radius: 0 !important;
        color: var(--ink);
        height: 4.1rem !important;
        min-height: 4.1rem !important;
        line-height: 4.1rem !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        font-size: 1.05rem;
        box-shadow: none !important;
    }
    [data-testid="stTextInput"] div,
    [data-testid="stTextInput"] div[data-baseweb="input"],
    [data-baseweb="input"],
    [data-baseweb="select"],
    [data-baseweb="select"] > div {
        border-radius: 0 !important;
        box-shadow: none !important;
    }
    [data-baseweb="input"] {
        border: 0 !important;
        border-left: 1px solid var(--line) !important;
        border-right: 1px solid var(--line) !important;
        background: #030303 !important;
        height: 4.1rem !important;
        align-items: center !important;
    }
    [data-baseweb="select"] > div {
        background: #030303 !important;
        border: 0 !important;
        color: #d8d8d8 !important;
        height: 4.1rem !important;
        align-items: center !important;
    }
    [data-baseweb="select"] span {
        color: #d8d8d8 !important;
    }
    [data-testid="stTextInput"] input::placeholder {
        color: #8c8c8c;
        opacity: 1;
    }
    .stButton > button {
        border-radius: 0 !important;
        border: 0;
        background: var(--button);
        color: #d8d8d8;
        height: 4.1rem;
        width: 100%;
        font-weight: 700;
        font-size: 1.02rem;
    }
    button {
        border-radius: 0 !important;
    }
    .stButton > button:hover {
        border-color: transparent;
        background: #151515;
        color: #ffffff;
    }
    .sources {
        border-top: 1px solid var(--line);
        margin-top: 1.4rem;
        padding-top: 0.9rem;
        color: var(--source);
        font-size: 0.92rem;
        text-align: left;
    }
    .source-row {
        margin: 0.35rem 0;
        line-height: 1.45;
        color: #d8d8d8;
    }
    .source-row a {
        color: var(--ink);
        text-decoration: none;
        border-bottom: 1px solid #777777;
    }
    .qa-history {
        max-width: 860px;
        margin: 0 auto 2rem;
        text-align: left;
        animation: historyIn 420ms ease-out both;
    }
    .qa-row {
        display: grid;
        grid-template-columns: 1.9rem 1fr;
        gap: 0.8rem;
        margin-bottom: 1.1rem;
        color: #e8e8e8;
        line-height: 1.65;
        font-size: 0.98rem;
    }
    .qa-avatar {
        width: 1.9rem;
        height: 1.9rem;
        display: grid;
        place-items: center;
        background: #1d1d1d;
        color: #e8e8e8;
        font-size: 0.72rem;
        font-weight: 700;
    }
    .qa-user .qa-avatar {
        background: #f4f4f4;
        color: #000000;
    }
    .qa-content {
        padding-top: 0.1rem;
    }
    @keyframes barIn {
        from {
            opacity: 0;
            transform: translateY(18px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    @keyframes historyIn {
        from {
            opacity: 0;
            transform: translateY(-12px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <style>
    .block-container {{
        padding-top: {"8vh" if st.session_state.messages else "42vh"} !important;
        padding-bottom: {"3rem" if st.session_state.messages else "7rem"} !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

def render_history() -> None:
    chunks = ['<div class="qa-history" style="max-width:860px;margin:0 auto 2rem;text-align:left;">']

    for message in st.session_state.messages:
        role_class = "qa-user" if message["role"] == "user" else "qa-assistant"
        label = "Q" if message["role"] == "user" else "A"
        content = html.escape(message["content"]).replace("\n", "<br>")
        chunks.append(
            f"""
            <div class="qa-row {role_class}">
                <div class="qa-avatar">{label}</div>
                <div class="qa-content">{content}</div>
            </div>
            """
        )

    latest_sources = []
    for message in reversed(st.session_state.messages):
        if message.get("results"):
            latest_sources = message["results"]
            break

    if latest_sources:
        source_items = []
        for result in latest_sources[:5]:
            title = html.escape(result.title)
            category = html.escape(result.category)
            url = html.escape(result.source_url)
            source_items.append(
                f'<div class="source-row"><a href="{url}" target="_blank">{title}</a> · {category} · score {result.score:.3f}</div>'
            )
        chunks.append('<div class="sources"><strong>Sources</strong>' + "".join(source_items) + "</div>")

    chunks.append("</div>")
    st.markdown("".join(chunks), unsafe_allow_html=True)


def render_input_bar() -> tuple[bool, str, str]:
    style_col, input_col, button_col = st.columns([1.55, 7.9, 1.1])
    with style_col:
        selected_style = st.selectbox(
            "Style",
            ["Balanced", "Quick tip", "Step-by-step"],
            label_visibility="collapsed",
        )
    with input_col:
        entered_question = st.text_input(
            "Question",
            placeholder="Ask a Stardew Valley wiki question",
            label_visibility="collapsed",
            key=f"question_input_{st.session_state.question_input_key}",
        )
    with button_col:
        was_submitted = st.button("Ask", width="stretch")
    return was_submitted, entered_question, selected_style


if st.session_state.messages:
    render_history()

submitted, question_text, answer_style = render_input_bar()

if submitted and question_text.strip():
    st.session_state.messages.append({"role": "user", "content": question_text.strip(), "results": []})
    response = run_query(question_text.strip(), answer_style)
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response["answer"],
            "results": response["results"],
        }
    )
    st.session_state.question_input_key += 1
    st.rerun()

if not st.session_state.messages:
    st.markdown(
        """
        <div class="app-footer">
            <div class="app-title">WikiQuest AI</div>
            <div class="app-subtitle">Ask a Stardew Valley question. Answers are grounded in the local wiki dataset.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
