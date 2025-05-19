import re
import pickle

# Project Gutenberg 的剧本标题全集（大写匹配）
KNOWN_PLAYS = {
    "THE SONNETS", "ALL’S WELL THAT ENDS WELL", "THE TRAGEDY OF ANTONY AND CLEOPATRA",
    "AS YOU LIKE IT", "THE COMEDY OF ERRORS", "THE TRAGEDY OF CORIOLANUS", "CYMBELINE",
    "THE TRAGEDY OF HAMLET, PRINCE OF DENMARK", "THE FIRST PART OF KING HENRY THE FOURTH",
    "THE SECOND PART OF KING HENRY THE FOURTH", "THE LIFE OF KING HENRY THE FIFTH",
    "THE FIRST PART OF HENRY THE SIXTH", "THE SECOND PART OF KING HENRY THE SIXTH",
    "THE THIRD PART OF KING HENRY THE SIXTH", "KING HENRY THE EIGHTH", "THE LIFE AND DEATH OF KING JOHN",
    "THE TRAGEDY OF JULIUS CAESAR", "THE TRAGEDY OF KING LEAR", "LOVE’S LABOUR’S LOST",
    "THE TRAGEDY OF MACBETH", "MEASURE FOR MEASURE", "THE MERCHANT OF VENICE",
    "THE MERRY WIVES OF WINDSOR", "A MIDSUMMER NIGHT’S DREAM", "MUCH ADO ABOUT NOTHING",
    "THE TRAGEDY OF OTHELLO, THE MOOR OF VENICE", "PERICLES, PRINCE OF TYRE", "KING RICHARD THE SECOND",
    "KING RICHARD THE THIRD", "THE TRAGEDY OF ROMEO AND JULIET", "THE TAMING OF THE SHREW",
    "THE TEMPEST", "THE LIFE OF TIMON OF ATHENS", "THE TRAGEDY OF TITUS ANDRONICUS",
    "TROILUS AND CRESSIDA", "TWELFTH NIGHT; OR, WHAT YOU WILL", "THE TWO GENTLEMEN OF VERONA",
    "THE TWO NOBLE KINSMEN", "THE WINTER’S TALE", "A LOVER’S COMPLAINT", "THE PASSIONATE PILGRIM",
    "THE PHOENIX AND THE TURTLE", "THE RAPE OF LUCRECE", "VENUS AND ADONIS"
}

def load_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    if "*** START OF" in text:
        text = text.split("*** START OF")[-1]
    return text

def parse_lines(text: str):
    lines = text.splitlines()

    sentence_data = []
    scene_blocks = []

    current_play = "Unknown"
    current_act = "Unknown"
    current_scene = "Unknown"
    scene_buffer = []

    scene_id = 0

    act_pattern = re.compile(r"^ACT\s+[IVXLC]+\.?", re.IGNORECASE)
    scene_pattern = re.compile(r"^SCENE\s+[IVXLC]+\.?.*", re.IGNORECASE)

    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        # 检测 Play 标题
        if line.upper() in KNOWN_PLAYS:
            if scene_buffer:
                scene_blocks.append((scene_id, current_play, current_act, current_scene, "\n".join(scene_buffer)))
                scene_id += 1
                scene_buffer = []
            current_play = line.title()
            current_act = "Unknown"
            current_scene = "Unknown"
            continue

        if act_pattern.match(line):
            current_act = line.upper()
            continue

        if scene_pattern.match(line):
            if scene_buffer:
                scene_blocks.append((scene_id, current_play, current_act, current_scene, "\n".join(scene_buffer)))
                scene_id += 1
                scene_buffer = []
            current_scene = line.upper()
            continue

        # 保留正文（非全大写）
        if not line.isupper():
            sentence_data.append((len(sentence_data), line, current_play, current_act, current_scene))
            scene_buffer.append(line)

    if scene_buffer:
        scene_blocks.append((scene_id, current_play, current_act, current_scene, "\n".join(scene_buffer)))

    return sentence_data, scene_blocks

if __name__ == "__main__":
    text = load_text("data/source/Complete.txt")
    sentence_level, scene_level = parse_lines(text)

    # 保存纯文本（兼容旧的 faiss）
    with open("data/source/split_clean_lines_output.txt", "w", encoding="utf-8") as f:
        for item in sentence_level:
            f.write(item[1] + "\n")

    # 保存结构化数据
    with open("data/source/sentence_level_lines.pkl", "wb") as f:
        pickle.dump(sentence_level, f)

    with open("data/source/scene_level_blocks.pkl", "wb") as f:
        pickle.dump(scene_level, f)

    print(f"✅ Sentence lines: {len(sentence_level)}")
    print(f"✅ Scene blocks: {len(scene_level)}")
    print("🎉 Saved to:")
    print("- split_clean_lines_output.txt")
    print("- sentence_level_lines.pkl")
    print("- scene_level_blocks.pkl")