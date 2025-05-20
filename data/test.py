# search_scene.py

import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

# === 加载模型、索引、数据 ===
model = SentenceTransformer("all-MiniLM-L6-v2")
scene_df = pd.read_pickle("scene_level_quote.pkl")
index = faiss.read_index("scene_level_quote.faiss")

# === 搜索函数 ===
def search(query, top_k=10):
    query_vec = model.encode([query])
    D, I = index.search(query_vec, top_k)

    print(f"\n🎯 Showing top {top_k} semantic matches for '{query}':\n")
    found = False

    for idx in I[0]:
        row = scene_df.iloc[idx]
        text = row["scene_text"]
        if query.lower() in text.lower():
            found = True
            print("\n==============================")
            print(f"🎭 {row['play']}\n🎬 {row['act']} | {row['scene']}")
            print("------------------------------")
            print(text[:1000])
            print("... ✅ 包含查询词")
    
    if not found:
        print("❌ Top-k 中无精准命中，转为全文搜索 fallback...\n")

        fallback = scene_df[scene_df["scene_text"].str.contains(query, case=False)]
        if not fallback.empty:
            best = fallback.iloc[0]
            print("\n==============================")
            print(f"🎭 {best['play']}\n🎬 {best['act']} | {best['scene']}")
            print("------------------------------")
            print(best['scene_text'][:1000])
            print("... ✅ fallback 精准命中")
        else:
            print("❌ 全文搜索中也未找到包含该关键词的 scene。")



# === CLI 主循环 ===
if __name__ == "__main__":
    while True:
        query = input("\n🔍 Query (or Enter to quit): ").strip()
        if not query:
            break
        search(query)



