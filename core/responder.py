from llama_cpp import Llama
import os

# === Load quantized Mistral-7B-Instruct ===
MODEL_PATH = ("models/mistral-7b-instruct-v0.1.Q4_K_M.gguf")

llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=2048,
    n_threads=4,
    n_gpu_layers=20,
    use_mlock=True,
    chat_format="chatml",  # ✅ 强制指定 Mistral instruct 格式
    verbose=True            # ✅ 可选，debug 时查看 token 输出
)

# === Inference Function ===
def get_model_response(prompt: str, temperature=0.3, top_p=0.9, max_new_tokens=512):
    try:
        output = llm(
            prompt,
            max_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            echo=False,
        )
        return output["choices"][0]["text"].strip()
    except Exception as e:
        return f"⚠️ Error: {str(e)}"