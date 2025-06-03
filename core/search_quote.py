import pandas as pd

# === 加载数据 ===
def load_scene_quote_data():
    """
    读取带有 scene_text 的 scene-level quote 数据。
    返回 DataFrame。
    """
    data_path = "data/scene_level_quote.pkl"
    df = pd.read_pickle(data_path)
    return df

# === 仅通过关键词查找 quote 对应的 scene ===
def search_quote_exact(query, df, top_k=1):
    """
    在 scene_text 中查找包含 query 的 scene。
    返回包含 quote、location 和 scene_text 的结果列表。
    """
    results = []

    matched_df = df[df["scene_text"].fillna("").str.contains(query, case=False, na=False)]

    if matched_df.empty:
        print(f"❌ No exact match found for: '{query}'")
        return []

    for _, row in matched_df.head(top_k).iterrows():
        result = {
            "quote": query,
            "location": {
                "play": row.get("play", ""),
                "act": row.get("act", ""),
                "scene": row.get("scene", "")
            },
            "scene_text": row.get("scene_text", "")
        }
        results.append(result)

    return results

# === 示例调用 ===
if __name__ == "__main__":
    df = load_scene_quote_data()
    query = "to be or not to be"  # 可替换为任意检索语句
    matches = search_quote_exact(query, df, top_k=1)

    for match in matches:
        print(f"\n🎭 {match['location']['play']} Act {match['location']['act']} Scene {match['location']['scene']}")
        print(f"📜 Quote: {match['quote']}")
        print(f"🖋️ Scene snippet:\n{match['scene_text'][:300]}...\n")