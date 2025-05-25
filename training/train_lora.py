from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments, DataCollatorForLanguageModeling
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import Dataset
import torch
import os

# === Paths and configs ===
BASE_MODEL = "mistralai/Mistral-7B-Instruct-v0.1"
DATA_PATH = "data/text/*.txt"
OUTPUT_DIR = "training/checkpoints/shakespeare-lora"

# === Load and preprocess .txt ===
def load_txt_as_dataset(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Split text into chunks (e.g., 512 tokens worth of text)
    lines = text.split("\n\n")  # Split on paragraph boundaries
    return Dataset.from_dict({"text": lines})

# === Tokenization function ===
def tokenize(example):
    return tokenizer(
        example["text"],
        truncation=True,
        padding="max_length",
        max_length=512,
        return_tensors="pt"
    )

# === Load tokenizer and base model ===
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
tokenizer.pad_token = tokenizer.eos_token  # Ensure pad_token exists

model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    load_in_4bit=True,
    device_map="auto",
    torch_dtype=torch.float16
)

model = prepare_model_for_kbit_training(model)

# === Setup LoRA ===
peft_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, peft_config)

# === Load and tokenize dataset ===
dataset = load_txt_as_dataset(DATA_PATH)
tokenized_dataset = dataset.map(tokenize, batched=True)

# === Training config ===
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=2,
    num_train_epochs=3,
    logging_dir="./logs",
    logging_steps=10,
    save_strategy="epoch",
    save_total_limit=1,
    fp16=True,
    optim="paged_adamw_8bit",
)

# === Trainer setup ===
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    tokenizer=tokenizer,
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False)
)

# === Train ===
trainer.train()

# === Save LoRA adapter ===
model.save_pretrained(OUTPUT_DIR)
print(f"✅ LoRA adapter saved to {OUTPUT_DIR}")
