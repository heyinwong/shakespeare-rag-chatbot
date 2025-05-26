from llama_cpp import Llama
import os

# === Load quantized Mistral-7B-Instruct ===
MODEL_PATH = ("models/phi-2-chat.q4_k_m.gguf")

llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=2048,
    n_threads=4,
    n_gpu_layers=20,
    use_mlock=True,
    chat_format=None,  # ← Alpaca-style prompts
    verbose=True
)


# === Inference Function ===
def get_model_response(prompt: str, temperature=0.0, top_p=0.3, max_new_tokens=512):
    try:
        formatted_prompt = f"### Instruction:\n{prompt}\n\n### Response:\n"
        output = llm(
            formatted_prompt,
            max_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            echo=False,
            top_k=10,
            repeat_penalty=1.2,
            stop=["\n\n", "Assistant:", "Input:", "Response:", "```python", "Best regards"]
        )
        return output["choices"][0]["text"].strip()
    except Exception as e:
        return f"Error: {str(e)}"
