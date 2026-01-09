"""
LightOS LLM Training Ground - Advanced Example 1
Custom Dataset Fine-Tuning

This example shows how to fine-tune a model on your own custom dataset
with advanced configuration options.

Requirements:
- 12GB+ VRAM (or 8GB with optimizations)
- Custom dataset in correct format
- CUDA-capable GPU

Time: Depends on dataset size and steps
"""

import sys
sys.path.append('/opt/lightos/llm-training-ground')

from unsloth_integration import UnslothTrainer, UnslothConfig
import json

# Step 1: Prepare your custom dataset
print("📝 Step 1: Preparing custom dataset...")

custom_data = [
    {
        "instruction": "What is LightOS?",
        "input": "",
        "output": "LightOS is a platform-agnostic neural compute engine that enables AI acceleration across NVIDIA, AMD, ARM, Intel, and photonic NPUs."
    },
    {
        "instruction": "How do I install LightOS?",
        "input": "",
        "output": "Run: sudo ./simple-deploy.sh in the LightOS directory. Installation takes 5-10 minutes."
    },
    {
        "instruction": "What coding agents are available?",
        "input": "",
        "output": "LightOS includes GLM-4 (71.8% HumanEval) and Qwen2.5-Coder (74.5% HumanEval), both beating GPT-4 on coding benchmarks."
    },
    # Add more examples here...
]

# Save dataset
with open('./custom_dataset.json', 'w') as f:
    json.dump(custom_data, f, indent=2)

print(f"✅ Created dataset with {len(custom_data)} examples")
print()

# Step 2: Configure advanced training
print("⚙️  Step 2: Configuring training...")

config = UnslothConfig(
    model_name="unsloth/llama-3-8b-bnb-4bit",
    max_seq_length=2048,
    load_in_4bit=True,

    # LoRA configuration
    lora_r=16,              # Rank (higher = more parameters)
    lora_alpha=16,          # Scaling factor
    lora_dropout=0.05,      # Dropout rate

    # Training hyperparameters
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    warmup_steps=10,
    max_steps=200,          # Adjust based on dataset size
    learning_rate=2e-4,

    # Optimizations
    use_gradient_checkpointing=True,
    use_flash_attention=True,
    fp16=True,

    # Logging
    logging_steps=10,
    save_steps=50,
)

print("Configuration:")
print(f"  Model: {config.model_name}")
print(f"  Max steps: {config.max_steps}")
print(f"  Batch size: {config.per_device_train_batch_size}")
print(f"  Learning rate: {config.learning_rate}")
print(f"  LoRA rank: {config.lora_r}")
print()

# Step 3: Initialize trainer
print("🚀 Step 3: Initializing trainer...")

trainer = UnslothTrainer(config.model_name, config)

# Step 4: Load model
print("📦 Step 4: Loading model...")
trainer.load_model()
print("✅ Model loaded")
print()

# Step 5: Add LoRA adapters
print("🔧 Step 5: Adding LoRA adapters...")
trainer.add_lora_adapters()
print("✅ LoRA adapters added")
print()

# Step 6: Load dataset
print("📊 Step 6: Loading dataset...")
trainer.load_dataset('./custom_dataset.json')
print("✅ Dataset loaded")
print()

# Step 7: Train!
print("🏃 Step 7: Starting training...")
print("This may take a while depending on your dataset size and GPU.")
print()

trainer.train('./models/custom-finetuned-model')

print()
print("✅ Training complete!")
print("Model saved to: ./models/custom-finetuned-model")
print()

# Step 8: Test the model
print("🧪 Step 8: Testing the model...")

from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained('./models/custom-finetuned-model')
tokenizer = AutoTokenizer.from_pretrained('./models/custom-finetuned-model')

# Test inference
prompt = "What is LightOS?"
inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=100)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)

print(f"Prompt: {prompt}")
print(f"Response: {response}")
print()

print("✅ All steps complete!")
print()
print("Next steps:")
print("  1. Test your model on more examples")
print("  2. Evaluate performance")
print("  3. Deploy to production")
