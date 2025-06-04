# scene_level_index.py

import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

# === load scene data ===
scene_df = pd.read_pickle("output/scene.pkl")  # scene structure we previously build

# === load sentence-transformers ===
model = SentenceTransformer("all-MiniLM-L6-v2")

# === encode all scene_text ===
print(" building scene vector database...")
scene_texts = scene_df["scene_text"].tolist()
scene_vectors = model.encode(scene_texts, show_progress_bar=True, batch_size=16)

# === build FAISS indexing（L2 distance）===
index = faiss.IndexFlatL2(scene_vectors.shape[1])
index.add(scene_vectors)

# === save index and data ===
faiss.write_index(index, "scene_level_quote.faiss")
scene_df.to_pickle("scene_level_quote.pkl")

print(f"Building complete! Total {len(scene_df)} scenes")



