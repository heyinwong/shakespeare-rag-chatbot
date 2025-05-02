import streamlit as st
import os
from dotenv import load_dotenv
from utils.styles import set_custom_style
from core.loader import list_plays, load_play, search_quotes, list_characters, load_prompt
from core.responder import get_openai_response

# ========== Setup ==========
st.set_page_config(page_title="Whispers of Will", layout="centered")
set_custom_style()
load_dotenv()

# ========== State Initialization ==========
st.session_state.setdefault("chat_history", [])
st.session_state.setdefault("previous_character", None)
st.session_state.setdefault("previous_mode", "Ask the Bard")

# ========== Title ==========
st.markdown("<h1 class='bard-title'>Whispers of Will</h1>", unsafe_allow_html=True)

# ========== Mode Selection ==========
st.markdown("<div class='bard-label'>Choose mode:</div>", unsafe_allow_html=True)
interaction_mode = st.radio(
    "Choose mode",
    ["Ask the Bard", "Roleplay"],
    index=0,
    label_visibility="collapsed"
)

if interaction_mode != st.session_state.previous_mode:
    st.session_state.chat_history = []
    st.info(f"Switched to {interaction_mode} mode. Chat history cleared.")
st.session_state.previous_mode = interaction_mode

# ========== Play Loading ==========
def get_play_text():
    if interaction_mode == "Ask the Bard":
        st.markdown("<div class='bard-label'>Choose a Shakespeare play:</div>", unsafe_allow_html=True)
        plays = list_plays()
        default_index = next((i for i, p in enumerate(plays) if "complete works" in p.lower()), 0)
        selected = st.selectbox("Select a play", plays, index=default_index, label_visibility="collapsed")
        filename = "Complete" if "complete works" in selected.lower() else selected
        return load_play(filename), selected
    else:
        return load_play("Complete"), "Complete Works"

play_text, selected_play = get_play_text()

# ========== Language Style ==========
st.markdown("<div class='bard-label'>Choose your language style:</div>", unsafe_allow_html=True)
mode = st.radio(
    "Language style",
    ["Modern English", "Bard Speak"],
    index=0,
    label_visibility="collapsed"
)

# ========== Character Selection & Identity ==========
def get_character_identity():
    st.markdown("<div class='bard-label'>Choose a character to roleplay:</div>", unsafe_allow_html=True)
    characters = list_characters() + ["Custom"]
    selected = st.selectbox("Choose a character", characters, index=0, label_visibility="collapsed")
    if selected == "Custom":
        name = st.text_input("Enter a custom character name:", label_visibility="collapsed").strip()
        return name or "Someone You Desired", name
    return selected, ""

if interaction_mode == "Roleplay":
    display_name, custom_name = get_character_identity()
    current_identity = custom_name if custom_name else display_name
    if current_identity != st.session_state.previous_character:
        st.session_state.chat_history = []
        st.info(f"Chat history cleared — now speaking with {display_name}.")
    st.session_state.previous_character = current_identity
else:
    display_name = "The Bard"
    custom_name = ""

# ========== Prompt & Suggestion ==========
def build_prompt():
    if interaction_mode == "Roleplay":
        if display_name == "Custom":
            return (
                f"You are now roleplaying as {custom_name} from Shakespeare's works. "
                "Use references only from the Complete Works of Shakespeare to simulate this character's behavior and style.",
                "Ask the character about their thoughts, motivations, or dilemmas."
            )
        return load_prompt(display_name if display_name != "Custom" else "default")
    else:
        style = (
            "Explain clearly in modern English." if mode == "Modern English"
            else "Speak in poetic, Shakespearean language."
        )
        return (
            f"You are a wise Shakespearean assistant. You are currently referencing the play '{selected_play}'. {style}",
            "Ask for summaries, explain character motives, or find famous quotes."
        )

instruction, suggestion = build_prompt()

# ========== User Input ==========
st.markdown(f"<div class='bard-label'>Chat with {display_name}</div>", unsafe_allow_html=True)
st.markdown(
    f"<div class='bard-suggestion'>Try asking {display_name} something like:<br><em>“{suggestion}”</em></div>",
    unsafe_allow_html=True
)
user_input = st.text_area("Your message", height=130, label_visibility="collapsed")

# ========== Buttons ==========
col1, col2 = st.columns(2)
with col1:
    respond = st.button("Respond", use_container_width=True)
with col2:
    clear = st.button("Clear Chat", use_container_width=True)

if clear:
    st.session_state.chat_history = []
    st.rerun()

# ========== Generate Response ==========
if respond and user_input.strip():
    style_instruction = (
        "You must respond in clear, simple, modern English." if mode == "Modern English"
        else "You must respond in poetic, Shakespearean style, full of metaphors and rich language."
    )

    messages = [{"role": "system", "content": f"{style_instruction} {instruction}"}]
    for m in st.session_state.chat_history:
        messages.append({
            "role": "user" if m["role"] == "user" else "assistant",
            "content": m["text"]
        })

    if interaction_mode == "Ask the Bard":
        quotes = search_quotes(play_text, user_input)
        if quotes:
            quote_context = "\n\n".join(quotes)
            messages.append({"role": "system", "content": f"Relevant lines:\n\n{quote_context}"})

    messages.append({"role": "user", "content": user_input})

    with st.spinner("Summoning response..."):
        response = get_openai_response(messages)

    st.session_state.chat_history.append({"role": "user", "text": user_input})
    st.session_state.chat_history.append({"role": "bard", "text": response})

elif respond:
    st.warning("Please enter a message.")

# ========== Conversation History ==========
st.markdown(f"<div class='bard-label'>Conversation with {display_name}</div>", unsafe_allow_html=True)
for message in reversed(st.session_state.chat_history):
    if message["role"] == "user":
        st.markdown(f"""
            <div style='background-color: #ffffffdd; padding: 1rem; margin: 1rem 0; border-radius: 12px; text-align: right; color: #000; border: 1px solid #aaa; max-width: 80%; margin-left: auto;'>
                <strong>You:</strong><br>{message['text']}
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div style='background-color: #f9f1e7; padding: 1rem; margin: 1rem 0; border-radius: 12px; color: #2b1d0e; border: 2px solid #c76b3e; max-width: 80%; margin-right: auto;'>
                <strong>{display_name}:</strong><br>{message['text']}
            </div>""", unsafe_allow_html=True)

# ========== Footer ==========
st.markdown("---")
st.markdown(
    "<div style='text-align:center; font-size: 0.85rem; margin-top: 2rem;'>"
    "Crafted with ☕ by <strong>Xixian Huang</strong>"
    "</div>",
    unsafe_allow_html=True
)