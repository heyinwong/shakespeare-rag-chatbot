# 933 Assignment – Shakespeare AI (Local Model Version)

This is the code repository for the CSIT933 assignment, adapted from the earlier **Character Echoes** project.  
The current version removes all external API dependencies and fully supports **offline generation and retrieval** using open-source models.

---

## Features

- **Roleplay with Shakespearean Characters**  
  Converse with Hamlet, Lady Macbeth, Juliet, Othello, and more. Each character responds with their unique style and Shakespearean tone, powered by `flan-t5-small`.

- **Quote Search Engine (FAISS)**  
  Ask anything, and the system retrieves relevant lines from the entire Shakespeare corpus using `distilBERT` + `FAISS` vector search.

- **Scene Summarisation in Modern English**  
  The system automatically summarizes surrounding lines (scene context) using `flan-t5-small`.

- **Fully Offline (No API Key Needed)**  
  All retrieval and generation are handled locally. The original OpenAI API backend has been removed.

---

## Example Use Cases

- "Summarize Act 3 Scene 1 of Macbeth in modern English."
- "Hamlet, what do you think about revenge?"
- "Find a quote about fate in King Lear."
- "Juliet, what does love mean to you?"

---

## Project Structure

```
├── app.py                  # Streamlit frontend
├── core/
│   ├── loader.py           # Load characters, source files, prompts
│   ├── responder.py        # Local model inference (flan / distilBERT)
│   └── search.py           # FAISS-based quote retrieval
├── data/
│   ├── source/             # Shakespeare source .txt and processed files
│   ├── faiss/              # FAISS index + corresponding line metadata (.pkl)
│   └── character_prompts/  # Markdown prompts for roleplay characters
├── requirements.txt
└── README.md
```

---

## Setup Instructions (Local)

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the preprocessing steps (only needed once):

```bash
python data/source/split_clean_lines.py
python data/source/build_faiss_index.py
```

3. Run the app:

```bash
streamlit run app.py
```

---

## Modes of Interaction

- `Ask the Bard`

  - → **Quote Retrieval** (retrieves original Shakespeare line)
  - → **Scene Summary** (summarizes context in modern English)

- `Roleplay`
  - Choose a character and chat with them in their poetic tone

> All logic is handled locally using pre-trained models. No fine-tuning or external calls required.

---

## Deployment

This app can be deployed locally or on platforms like **Streamlit Cloud** or **Hugging Face Spaces**, provided the models and index files are uploaded.  
No API Key required. All dependencies are free and open source.

---

## Attribution

- Shakespeare texts from [Project Gutenberg](https://www.gutenberg.org/)
- Models:
  - `distilBERT` for embedding & quote retrieval
  - `flan-t5-small` for summarisation & roleplay
- Search backend: [FAISS](https://github.com/facebookresearch/faiss)
- Frontend: [Streamlit](https://streamlit.io)

---

## Author

**Xixian Huang**
