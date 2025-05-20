import os
import re
import pandas as pd

scene_records = []
input_dir = "text"

def process_file(filepath, play_name):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = [line.rstrip() for line in f]

    current_act = ""
    current_scene = ""
    scene_buffer = []
    skip_until_act = True

    for line in lines:
        # 标准化空行
        if line.strip() == "":
            scene_buffer.append("")  # 保留段落结构
            continue

        # 跳过 Dramatis Personae 等非正文
        if skip_until_act:
            if re.match(r"^ACT\b", line, re.IGNORECASE):
                skip_until_act = False
            else:
                continue

        if re.match(r"^ACT\b", line, re.IGNORECASE):
            current_act = line.strip()
            current_scene = ""
        elif re.match(r"^SCENE\b", line, re.IGNORECASE):
            if scene_buffer:
                scene_records.append({
                    "scene_text": "\n".join(scene_buffer).strip(),
                    "act": current_act,
                    "scene": current_scene,
                    "play": play_name
                })
                scene_buffer.clear()
            current_scene = line.strip()
        else:
            scene_buffer.append(line.strip())

    # 收尾
    if scene_buffer:
        scene_records.append({
            "scene_text": "\n".join(scene_buffer).strip(),
            "act": current_act,
            "scene": current_scene,
            "play": play_name
        })

# 遍历所有剧本
for filename in os.listdir(input_dir):
    if filename.endswith(".txt"):
        path = os.path.join(input_dir, filename)
        play_name = filename.replace("_TXT_FolgerShakespeare.txt", "").replace("-", " ").title()
        print(f"📖 Processing: {play_name}")
        process_file(path, play_name)

# 保存
os.makedirs("output", exist_ok=True)
pd.DataFrame(scene_records).to_pickle("output/scene.pkl")
print(f"\n✅ 完成！共提取 {len(scene_records)} 个 scene")



