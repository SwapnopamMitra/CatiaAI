from transformers import GPT2LMHeadModel, GPT2Tokenizer, Trainer, TrainingArguments
from peft import get_peft_model, LoraConfig, TaskType
import json
import torch
from datasets import Dataset

# ✅ Load GPT-2 model and tokenizer
model_name = "gpt2"
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token  # GPT-2 needs this

# ✅ Apply LoRA (Reduces memory usage)
peft_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM, 
    r=8,  # Smaller r = lower memory usage
    lora_alpha=16, 
    lora_dropout=0.1
)
model = get_peft_model(model, peft_config)

# ✅ Load and tokenize dataset
with open("training_data.json", "r") as f:
    training_data = json.load(f)

dataset = Dataset.from_list(training_data)

def tokenize_function(example):
    tokenized = tokenizer(example["input"] + " " + example["output"], truncation=True, padding="max_length")
    tokenized["labels"] = tokenized["input_ids"].copy()  # Ensure labels are included
    return tokenized


tokenized_datasets = dataset.map(tokenize_function)

# ✅ Training settings
training_args = TrainingArguments(
     output_dir="../llm/trained_catia",
    per_device_train_batch_size=1,  # Adjust based on GPU RAM
    per_device_eval_batch_size=1,
    save_total_limit=2,
    num_train_epochs=3,  # You can increase this for better results
    logging_dir="./logs"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets
)

# ✅ Start training
trainer.train()

# ✅ Save fine-tuned model
model.save_pretrained("./trained_catia")
tokenizer.save_pretrained("./trained_catia")

print("🎉 Training Complete! Model Saved.")
