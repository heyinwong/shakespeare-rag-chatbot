import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer

# === 加载模型 ===
_model = SentenceTransformer("all-MiniLM-L6-v2")

# === 加载 FAISS 索引 + 对应数据表 ===
def load_faiss_index_quote(level="scene"):
    data_path = "data/scene_level_quote.pkl"
    index_path = "data/scene_level_quote.faiss"
    df = pd.read_pickle(data_path)
    index = faiss.read_index(index_path)
    return df, index

# === 提取 query 附近片段（截断上下文）===
def extract_snippet(scene_text, query, max_chars=5000):
    if not scene_text:
        return ""
    idx = scene_text.lower().find(query.lower())
    if idx == -1:
        return scene_text[:max_chars].strip()
    start = max(0, idx - max_chars // 2)
    end = min(len(scene_text), idx + max_chars // 2)
    return scene_text[start:end].strip()

# === 主检索函数 ===
def search_same(query, data_df, faiss_index, level="scene", top_k=10):
    query_vec = _model.encode([query])
    D, I = faiss_index.search(query_vec, top_k)

    results = []
    found_match = False
    print(f"\n🔍 Top {top_k} semantic matches for: '{query}'\n")

    for rank, idx in enumerate(I[0]):
        row = data_df.iloc[idx]
        scene_text = row.get("scene_text", "")

        if query.lower() in scene_text.lower():
            found_match = True

        if level == "quote":
            displayed_text = query  # ✅ 返回原始 query
        else:
            displayed_text = extract_snippet(scene_text, query, max_chars=5000)

        result = {
            "text": displayed_text,
            "index": idx,
            "play": row.get("play", ""),
            "act": row.get("act", ""),
            "scene": row.get("scene", ""),
            "score": float(D[0][rank]),
            "full_scene": scene_text if level == "scene" else None
        }

        print(f"{rank+1}. {result['score']:.4f} | {result['play']} {result['act']} {result['scene']}")
        print(f"{displayed_text[:120]}...\n")
        results.append(result)

    if not found_match:
        if "scene_text" not in data_df.columns:
            print("⚠️ 'scene_text' column not found. Skipping fallback.")
            return results

        fallback_df = data_df[data_df["scene_text"].fillna("").str.contains(query, case=False, na=False)]
        if not fallback_df.empty:
            row = fallback_df.iloc[0]
            fallback_text = query if level == "quote" else extract_snippet(row.get("scene_text", ""), query)
            result = {
                "text": fallback_text,
                "index": row.name,
                "play": row.get("play", ""),
                "act": row.get("act", ""),
                "scene": row.get("scene", ""),
                "score": -1.0,
                "full_scene": row.get("scene_text", "") if level == "scene" else None
            }
            print(f"Fallback Result: {result['play']} {result['act']} {result['scene']}")
            results = [result]
        else:
            print("❌ No fallback match found in full scene text.")

    return results