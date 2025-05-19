import streamlit as st
import os
from dotenv import load_dotenv
from utils.styles import set_custom_style
from core.search import load_tfidf_index, search_similar
from core.responder import get_flan_response
import re

# ====== MUST BE FIRST ======
st.set_page_config(page_title="Whispers of Will", layout="centered")

# ====== Load style + env ======
set_custom_style()
load_dotenv()

# ====== Utility: extract quoted phrase ======
def extract_quoted_phrase(text: str) -> str:
    matches = re.findall(r'"(.*?)"', text)
    return matches[0] if matches else text

# ====== Utility: quote filtering ======
def filter_relevant_quote(results, user_input):
    quote_match = re.search(r'["](.+?)["]', user_input)
    if quote_match:
        target_phrase = quote_match.group(1).lower()
        norm_phrase = re.sub(r"[^\w\s]", "", target_phrase)
        def score_fn(text):
            return norm_phrase in re.sub(r"[^\w\s]", "", text.lower())
    else:
        user_keywords = [w for w in re.findall(r"\w+", user_input.lower()) if len(w) > 2]
        def score_fn(text):
            return sum(kw in text.lower() for kw in user_keywords)

    scored = [(score_fn(r["text"]), r) for r in results]
    scored.sort(reverse=True, key=lambda x: x[0])
    return [scored[0][1]] if scored else []

# ====== Main Query Logic ======
def handle_bard_query(user_input):
    query = extract_quoted_phrase(user_input)
    lowered = query.lower()

    # 判断任务类型
    if any(k in lowered for k in ["summarise", "summarize", "summary", "what happened"]):
        level = "scene"
        task_instruction = "Please summarise the scene in modern English."
    else:
        level = "sentence"
        task_instruction = "Explain the quote in simple modern English. What does it mean emotionally or symbolically?"

    # 检索上下文
    vectorizer, tfidf_matrix, metadata = load_tfidf_index(level=level)
    raw_results = search_similar(query, vectorizer, tfidf_matrix, metadata, level=level, top_k=5)
    results = filter_relevant_quote(raw_results, query)

    if results:
        r = results[0]
        quote_line = query.strip('"“”')
        full_context = f'{r["text"]}  ({r["play"]}, {r["act"]}, {r["scene"]})'
        citation = f'This quote appears in <strong>{r["play"]}</strong>, <em>{r["act"]}</em>, <em>{r["scene"]}</em>.'

        prompt = f'Explain the meaning of the quote: "{quote_line}"'
    else:
        citation = ""
        prompt = f"""
You are a helpful Shakespeare assistant.

The user asked: "{user_input}"

Unfortunately, no relevant quotes were found. Please respond using your general knowledge of Shakespeare's works.
""".strip()

    print("DEBUG prompt passed to flan:\n", prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
    response = get_flan_response(prompt)
    return response, citation

# ====== UI Layout ======
st.title(" Whispers of Will")

st.markdown("<div class='bard-label'>Ask something:</div>", unsafe_allow_html=True)
user_input = st.text_area("Your question", height=130, label_visibility="collapsed")

col1, col2 = st.columns(2)
with col1:
    respond = st.button("Respond", use_container_width=True)
with col2:
    clear = st.button("Clear", use_container_width=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if clear:
    st.session_state.chat_history = []
    st.rerun()

if respond and user_input.strip():
    with st.spinner("Summoning response..."):
        response, citation = handle_bard_query(user_input)
    st.session_state.chat_history.append({"role": "user", "text": user_input})
    st.session_state.chat_history.append({"role": "bard", "text": response, "cite": citation})

elif respond:
    st.warning("Please enter a message.")

# ====== History View ======
for message in reversed(st.session_state.chat_history):
    if message["role"] == "user":
        st.markdown(f"""
        <div style='background-color: #ffffffdd; padding: 1rem; margin: 1rem 0; border-radius: 12px; text-align: right; color: #000; border: 1px solid #aaa; max-width: 80%; margin-left: auto;'>
            <strong>You:</strong><br>{message['text']}
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style='background-color: #f9f1e7; padding: 1rem; margin: 1rem 0; border-radius: 12px; color: #2b1d0e; border: 2px solid #c76b3e; max-width: 80%; margin-right: auto;'>
            <strong>The Bard:</strong><br>
            {'<div style="color:#666;font-size:0.9rem;">' + message.get('cite','') + '</div><br>' if message.get('cite') else ''}
            {message['text']}
        </div>""", unsafe_allow_html=True)

# ====== Footer ======
st.markdown("---")
st.markdown(
    "<div style='text-align:center; font-size: 0.85rem; margin-top: 2rem;'>"
    "Crafted with \u2615 by <strong>Xixian Huang</strong>"
    "</div>",
    unsafe_allow_html=True
)