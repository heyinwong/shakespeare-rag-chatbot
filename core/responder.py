from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

# === Device Setup ===
device = (
    torch.device("mps") if torch.backends.mps.is_available()
    else torch.device("cuda") if torch.cuda.is_available()
    else torch.device("cpu")
)

# === Load Model & Tokenizer ===
tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-large")
model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-large")
model.to(device)
model.eval()

# === Inference Function ===
def get_flan_response(prompt: str, max_new_tokens=200):
    try:
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(device)
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,             # ✅ 开启采样模式
                temperature=0.7,            # ✅ 控制创意程度（0.7 通常比较平衡）
                top_p=0.9                   # ✅ 核采样
            )
        return tokenizer.decode(outputs[0], skip_special_tokens=True)
    except Exception as e:
        return f"⚠️ Error: {str(e)}"