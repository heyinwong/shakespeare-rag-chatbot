from transformers import AutoModelForCausalLM
from peft import PeftModel
import subprocess
import os

def merge_and_convert(base_model_path, lora_path, merged_dir, gguf_out, convert_script, quant="q4_k_m"):
    print("🔁 Loading base and LoRA model...")
    model = AutoModelForCausalLM.from_pretrained(base_model_path, torch_dtype="auto", device_map="auto")
    model = PeftModel.from_pretrained(model, lora_path)
    model = model.merge_and_unload()

    print("💾 Saving merged model...")
    model.save_pretrained(merged_dir)

    print("⚙️ Converting to GGUF...")
    subprocess.run([
        "python3", convert_script,
        "--model-dir", merged_dir,
        "--outfile", gguf_out,
        "--outtype", quant
    ], check=True)
    print("✅ Done.")

# === Run ===
if __name__ == "__main__":
    merge_and_convert(
        base_model_path="mistralai/Mistral-7B-Instruct-v0.1",
        lora_path="checkpoints/shakespeare-lora",
        merged_dir="merged-mistral",
        gguf_out="models/mistral-lora.q4_k_m.gguf",
        convert_script="llama.cpp/convert.py"
    )
