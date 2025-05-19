import re
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from core.textutils import normalize

# === 加载 TF-IDF vectorizer + matrix + metadata ===
def load_tfidf_index(level="sentence"):
    if level == "sentence":
        path = "data/tfidf/tfidf_sentence_index.pkl"
    elif level == "scene":
        path = "data/tfidf/tfidf_scene_index.pkl"
    else:
        raise ValueError("Invalid level. Use 'sentence' or 'scene'.")

    with open(path, "rb") as f:
        obj = pickle.load(f)
    return obj["vectorizer"], obj["matrix"], obj["metadata"]

# === 通用检索函数 ===
def search_similar(query, vectorizer, tfidf_matrix, metadata, level="sentence", top_k=5):
    norm_query = normalize(query)  # ★ 标准化查询文本
    query_vec = vectorizer.transform([norm_query])
    similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
    top_indices = similarities.argsort()[::-1][:top_k]

    results = []
    print("🔍 Top retrieved candidates:")
    for idx in top_indices:
        if level == "sentence":
            i, text, play, act, scene = metadata[idx]
        else:
            i, play, act, scene, text = metadata[idx]

        result = {
            "text": text,
            "index": i,
            "play": play,
            "act": act,
            "scene": scene,
            "score": float(similarities[idx])
        }
        print(f"{result['score']:.4f} | {text[:60]}...")
        results.append(result)

    return results