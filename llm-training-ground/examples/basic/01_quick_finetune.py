"""
LightOS LLM Training Ground - Basic Example 1
Quick Fine-Tuning with Unsloth

This example shows how to fine-tune Llama 3.1 8B on a custom dataset
in just a few lines of code.

Requirements:
- 8GB+ VRAM (or use 4-bit quantization for 6GB)
- 15GB free disk space
- CUDA-capable GPU (or CPU mode)

Time: ~30 minutes for 100 steps
"""

import sys
sys.path.append('/opt/lightos/llm-training-ground')

from unsloth_integration import quick_finetune

# Fine-tune Llama 3.1 on Alpaca dataset
print("🚀 Starting quick fine-tune...")
print("Model: Llama 3.1 8B")
print("Dataset: Alpaca (instruction following)")
print("Steps: 100")
print()

quick_finetune(
    model_name="llama-3.1-8b",
    dataset_name="yahma/alpaca-cleaned",
    output_dir="./models/llama-3.1-alpaca",
    max_steps=100
)

print()
print("✅ Fine-tuning complete!")
print("Model saved to: ./models/llama-3.1-alpaca")
print()
print("To use your model:")
print("  from transformers import AutoModelForCausalLM, AutoTokenizer")
print("  model = AutoModelForCausalLM.from_pretrained('./models/llama-3.1-alpaca')")
print("  tokenizer = AutoTokenizer.from_pretrained('./models/llama-3.1-alpaca')")
