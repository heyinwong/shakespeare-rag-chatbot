# CSIT933 Assignment – Shakespeare AI Assistant (Local Model Edition)

This is the final implementation for the CSIT933 Shakespeare Chatbot assignment.  
It supports multi-turn question answering, quote interpretation, and scene summarisation—all **fully offline** using open-source small models.

---

## Key Features

- **Quote Reterival Understanding**

  - Retrieve famous lines using FAISS semantic search (MiniLM)
  - Explain context, speaker, and meaning with Mistral-7B

- **Scene Summarisation**

  - Locate scene excerpts and generate modern-English summaries

- **Multi-turn General QA**

  - Answer factual or thematic questions about Shakespeare's plays
  - Keeps memory of recent conversation summaries

- **Fully Local**
  - No OpenAI / API keys needed
  - Models run offline using `mistral-7b-instruct.Q4_K_M.gguf` + SentenceTransformers (MiniLM)

---

## Project Structure

```
├── app.py                      # Streamlit frontend
├── core/
│   ├── responder.py            # Mistral-7B local inference (llama-cpp)
│   ├── search_quote.py         # Quote-level semantic search
│   ├── match_scene.py          # Scene-level search & summarisation
├── data/
│   ├── scene_level_quote.pkl   # FAISS metadata (Folger corpus)
│   ├── scene_level_quote.faiss # FAISS index (MiniLM)
│   └── text/                   # Text file of Shakespeare's work
├── models/
│   └── mistral-7b-instruct...  # Quantized GGUF file (Q4_K_M)
├── utils/
│   └── styles.py               # UI customization
├── requirements.txt
└── README.md
```

---

## Setup Instructions

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

2. **Download Model**
   Download a quantized Mistral model and place it in the `models/` directory.
   For this project, we use `Mistral-7B-Instruct-v0.1.Q4_K_M` (GGUF format).
   You can find the model on Hugging Face here:
   [https://huggingface.co/itlwas/Mistral-7B-Instruct-v0.1-Q4_K_M-GGUF](https://huggingface.co/itlwas/Mistral-7B-Instruct-v0.1-Q4_K_M-GGUF)

   > Ensure the downloaded `.gguf` model file is saved in the `./models/` folder and that the file name matches the path specified in `responder.py`.

3. **Run the app**

```bash
streamlit run app.py
```

---

## Capabilities by Assignment Requirement

| Task Description                                    | Supported |
| --------------------------------------------------- | --------- |
| Scene summarisation in modern English               | ✅        |
| Retrieval and explanation of famous quotes          | ✅        |
| General questions about characters/events/themes    | ✅        |
| Multi-turn memory using summarised exchange history | ✅        |

---

## Models Used

- **Retrieval**: `sentence-transformers/all-MiniLM-L6-v2`
- **Generation**: `mistral-7b-instruct.Q4_K_M.gguf` via `llama-cpp-python`
- **Data Source**: Cleaned text from the [Folger Shakespeare Library](https://www.folger.edu/)

---

## Dependencies

- `streamlit`
- `sentence-transformers`
- `faiss-cpu`
- `llama-cpp-python`
- `pandas`
- `torch` (MPS/CPU/GPU backend)

---

## Author

**Xixian Huang**  
University of Wollongong  
CSIT933 – Assignment 2, 2025
