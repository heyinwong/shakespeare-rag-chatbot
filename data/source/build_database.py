import re
import sys
import os
import pickle

# === 添加项目根目录到 sys.path ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# === 导入 normalize 工具函数 ===
from core.textutils import normalize
from sklearn.feature_extraction.text import TfidfVectorizer


# === 加载结构化句子与场景 ===
with open("data/source/sentence_level_lines.pkl", "rb") as f:
    sentence_lines = pickle.load(f)  # (idx, text, play, act, scene)

with open("data/source/scene_level_blocks.pkl", "rb") as f:
    scene_blocks = pickle.load(f)  # (idx, play, act, scene, full_text)

# === 共用的 TF-IDF 设置（带 normalize）===
def build_vectorizer():
    return TfidfVectorizer(
        stop_words='english',
        ngram_range=(1, 3),
        analyzer='word',
        preprocessor=normalize  # ✅ 关键：统一文本处理方式
    )

# === 构建并保存句子级别索引 ===
sentence_vectorizer = build_vectorizer()
sentence_texts = [entry[1] for entry in sentence_lines]
sentence_matrix = sentence_vectorizer.fit_transform(sentence_texts)

with open("data/tfidf/tfidf_sentence_index.pkl", "wb") as f:
    pickle.dump({
        "vectorizer": sentence_vectorizer,
        "matrix": sentence_matrix,
        "metadata": sentence_lines
    }, f)
print("✅ Saved tfidf_sentence_index.pkl")

# === 构建并保存场景级别索引 ===
scene_vectorizer = build_vectorizer()
scene_texts = [entry[4] for entry in scene_blocks]
scene_matrix = scene_vectorizer.fit_transform(scene_texts)

with open("data/tfidf/tfidf_scene_index.pkl", "wb") as f:
    pickle.dump({
        "vectorizer": scene_vectorizer,
        "matrix": scene_matrix,
        "metadata": scene_blocks
    }, f)
print("✅ Saved tfidf_scene_index.pkl")