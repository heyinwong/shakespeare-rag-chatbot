import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer

_model = SentenceTransformer("all-MiniLM-L6-v2")

def load_faiss_index_scene():
    data_path = "data/scene_level_quote.pkl"
    index_path = "data/scene_level_quote.faiss"
    df = pd.read_pickle(data_path)
    index = faiss.read_index(index_path)
    return df, index

def extract_snippet(scene_text, query, max_chars=5000):
    if not scene_text:
        return ""
    idx = scene_text.lower().find(query.lower())
    if idx == -1:
        return scene_text[:max_chars].strip()
    start = max(0, idx - max_chars // 2)
    end = min(len(scene_text), idx + max_chars // 2)
    return scene_text[start:end].strip()

# === find scene（no fallback）===
def search_scene(query, data_df, faiss_index, top_k=10):
    query_vec = _model.encode([query])
    D, I = faiss_index.search(query_vec, top_k)

    results = []
    print(f"\n Top {top_k} semantic matches for scene query: '{query}'\n")

    for rank, idx in enumerate(I[0]):
        row = data_df.iloc[idx]
        scene_text = row.get("scene_text", "")

        snippet = extract_snippet(scene_text, query, max_chars=5000)

        result = {
            "text": snippet,
            "index": idx,
            "play": row.get("play", ""),
            "act": row.get("act", ""),
            "scene": row.get("scene", ""),
            "score": float(D[0][rank]),
            "full_scene": scene_text
        }

        print(f"{rank+1}. {result['score']:.4f} | {result['play']} {result['act']} {result['scene']}")
        print(f"{snippet[:120]}\n")
        results.append(result)

    return results