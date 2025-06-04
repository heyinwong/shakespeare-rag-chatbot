import pandas as pd

# === load data ===
def load_scene_quote_data():
    """
    read data wtih scene_text and scene-level quote
    return format as DataFrame。
    """
    data_path = "data/scene_level_quote.pkl"
    df = pd.read_pickle(data_path)
    return df

# === use key word searching to find the related scene with quote ===
def search_quote_exact(query, df, top_k=1):
    """
    find scene that contains query in scene_text 
    return result list with quote、location and scene_text 
    """
    results = []

    matched_df = df[df["scene_text"].fillna("").str.contains(query, case=False, na=False)]

    if matched_df.empty:
        print(f" No exact match found for: '{query}'")
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

# === example use ===
if __name__ == "__main__":
    df = load_scene_quote_data()
    query = "to be or not to be"  # can be any sentence
    matches = search_quote_exact(query, df, top_k=1)

    for match in matches:
        print(f"\n {match['location']['play']} Act {match['location']['act']} Scene {match['location']['scene']}")
        print(f" Quote: {match['quote']}")
        print(f" Scene snippet:\n{match['scene_text'][:300]}...\n")