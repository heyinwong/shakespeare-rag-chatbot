# scene_level_index.py

import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

# === 加载场景数据 ===
scene_df = pd.read_pickle("output/scene.pkl")  # 你之前提取的场景结构

# === 加载 sentence-transformers 模型 ===
model = SentenceTransformer("all-MiniLM-L6-v2")

# === 编码所有 scene_text ===
print("📦 正在编码所有 scene 向量...")
scene_texts = scene_df["scene_text"].tolist()
scene_vectors = model.encode(scene_texts, show_progress_bar=True, batch_size=16)

# === 建立 FAISS 索引（L2 距离）===
index = faiss.IndexFlatL2(scene_vectors.shape[1])
index.add(scene_vectors)

# === 保存索引和数据 ===
faiss.write_index(index, "scene_level_quote.faiss")
scene_df.to_pickle("scene_level_quote.pkl")

print(f"✅ 索引构建完成！共 {len(scene_df)} 个场景")



