import pickle

with open("data/source/sentence_level_lines.pkl", "rb") as f:
    lines = pickle.load(f)

target = "to be or not to be"
matches = [entry for entry in lines if target in entry[1].lower()]

for match in matches:
    print("✅ FOUND:", match)