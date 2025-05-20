import streamlit as st
import os
import re
import html
from dotenv import load_dotenv
from utils.styles import set_custom_style
from core.search_quote import load_faiss_index_quote, search_same
from core.responder import get_model_response
from core.match_scene import load_faiss_index_scene, search_scene
st.set_page_config(page_title="Whispers of Will", layout="centered")
set_custom_style()
load_dotenv()

def extract_quoted_phrase(text: str) -> str:
    matches = re.findall(r'"(.*?)"', text)
    return matches[0] if matches else ""

def filter_relevant_quote(results, user_input):
    quote_match = re.search(r'"(.+?)"', user_input)
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

def is_scene_summary(text: str) -> bool:
    keywords = ["summarise", "summarize", "summary", "what happened", "explain the scene"]
    return any(k in text.lower() for k in keywords)

def has_quoted_phrase(text: str) -> bool:
    return bool(re.findall(r'"(.*?)"', text))

def safe_truncate(text, max_chars=6000):
    truncated = text[:max_chars]
    last_period = truncated.rfind(".")
    if last_period != -1 and last_period > max_chars * 0.6:
        return truncated[:last_period+1]
    return truncated

def summarize_exchange(user_input: str, bard_response: str) -> str:
    summarization_prompt = f"""
You are a concise assistant. Summarize the following Q&A in one short sentence (under 20 words), stating only what the user asked about.

Question: {user_input}
Answer: {bard_response}
Summary:""".strip()

    summary = get_model_response(
        summarization_prompt,
        temperature=0.3,
        top_p=0.8,
        max_new_tokens=50
    )
    print("[DEBUG] Memory summary:", summary.strip())
    return summary.strip()

def handle_bard_query(user_input: str):
    if is_scene_summary(user_input):
        mode = "scene"
    elif has_quoted_phrase(user_input):
        mode = "quote"
    else:
        mode = "general"

    print(f"[DEBUG] Mode: {mode}")

    memory_prefix = ""
    if "memory_chain" in st.session_state and st.session_state.memory_chain:
        recent_memories = "\n".join(st.session_state.memory_chain[-5:])
        memory_prefix = f"""Conversation so far (summary of past exchanges):
{recent_memories}

Now the user asks:
"{user_input}""".strip()

    if mode == "scene":
        level = "scene"
        df, index = load_faiss_index_scene()
        raw_results = search_scene(user_input, df, index, top_k=3)
        if raw_results:
            r = raw_results[0]
            scene_text = safe_truncate(r['text'])
            base_prompt = f"""
You are a Shakespeare expert.

The following is a scene excerpt from one of Shakespeare's plays.

Scene: {r['act']}, {r['scene']} from {r['play']}

Content:
{scene_text}

Your task is to summarise this scene in plain modern English, in 3-5 sentences. Also mention the play and the scene.

Base your summary strictyly on the content provided. Do not invent characters, events, or dialogue that are not present in the excerpt.

Do not use markdown formatiing, ehadings, or stylised text.
""".strip()
        else:
            base_prompt = f"""
You are a Shakespeare expert.

The user asked to summarise a scene: "{user_input}"

Unfortunately, no matching scene was found. Please respond based on your general knowledge of Shakespeare's plays.
""".strip()

    elif mode == "quote":
        level = "sentence"
        quote_text = extract_quoted_phrase(user_input)
        df, index = load_faiss_index_quote(level)
        raw_results = search_same(quote_text, df, index, level=level, top_k=3)
        results = filter_relevant_quote(raw_results, user_input)
        if results:
            r = results[0]
            base_prompt = f"""
You are a Shakespeare expert.

The user is asking about this quote:

"{quote_text}"

It appears in {r['play']}, {r['act']}, {r['scene']}.

Please always answer the user where the quote appears and explain what it means in plain modern English and why it is important or well-known. Keep your tone helpful and natural.
""".strip()
        else:
            base_prompt = f"""
The user asked: "{user_input}"

Unfortunately, no matching quote was found. Please respond using your general knowledge of Shakespeare's works.
""".strip()

    else:
        base_prompt = f"""
You are a helpful Shakespeare expert.

The user asked: "{user_input}"

Please answer clearly and accurately, referring to known facts or themes from Shakespeare's plays. If appropriate, mention the character, act, or scene—but only if you are confident.
""".strip()

    final_prompt = f"{memory_prefix}\n\n{base_prompt}" if memory_prefix else base_prompt
    print("[DEBUG] Final prompt:\n", final_prompt[:800] + "..." if len(final_prompt) > 800 else final_prompt)

    response = get_model_response(final_prompt, temperature=0.2, top_p=0.9, max_new_tokens=512)

    if "memory_chain" not in st.session_state:
        st.session_state.memory_chain = []
    summary = summarize_exchange(user_input, response)
    st.session_state.memory_chain.append(summary)

    return response

# ====== UI Layout ======
st.title("Whispers of Will")
st.markdown("<div class='bard-label'>Ask something:</div>", unsafe_allow_html=True)
user_input = st.text_area("Your question", height=130, label_visibility="collapsed")

col1, col2 = st.columns(2)
with col1:
    respond = st.button("Respond", use_container_width=True)
with col2:
    clear = st.button("Clear", use_container_width=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "memory_chain" not in st.session_state:
    st.session_state.memory_chain = []

if clear:
    st.session_state.chat_history = []
    st.session_state.memory_chain = []
    st.rerun()

if respond and user_input.strip():
    with st.spinner("Summoning response..."):
        response = handle_bard_query(user_input)
    st.session_state.chat_history.append({"role": "user", "text": user_input})
    st.session_state.chat_history.append({"role": "bard", "text": response})

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
        escaped = html.escape(message['text'])
        st.markdown(f"""
        <div style='background-color: #f9f1e7; padding: 1rem; margin: 1rem 0; border-radius: 12px; color: #2b1d0e; border: 2px solid #c76b3e; max-width: 80%; margin-right: auto;'>
            <strong>The Bard:</strong><br><pre style='white-space: pre-wrap; margin: 0;'>{escaped}</pre>
        </div>""", unsafe_allow_html=True)

# ====== Footer ======
st.markdown("---")
st.markdown(
    "<div style='text-align:center; font-size: 0.85rem; margin-top: 2rem;'>"
    "Crafted with ☕ by <strong>Xixian Huang</strong>"
    "</div>",
    unsafe_allow_html=True
)