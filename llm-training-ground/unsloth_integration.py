#!/usr/bin/env python3
"""
LightOS Unsloth Integration Module
Provides 2-5x faster LLM fine-tuning with 70% less memory usage

Features:
- Fast fine-tuning for Llama, Mistral, Qwen, GLM-4, and more
- 4-bit quantization for memory efficiency
- RTX 50 series (Blackwell) optimization
- Seamless integration with LightOS Training Ground
"""

import os
import sys
import torch
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
import json

# Check if running on supported hardware
def check_hardware_support():
    """Check if GPU supports Unsloth acceleration"""
    if not torch.cuda.is_available():
        print("⚠️  Warning: No CUDA GPU detected. Unsloth will run in CPU mode (slower)")
        return False

    gpu_name = torch.cuda.get_device_name(0)
    print(f"✓ GPU detected: {gpu_name}")

    # Check for Blackwell (RTX 50 series)
    if "RTX 50" in gpu_name or "RTX 51" in gpu_name or "RTX 52" in gpu_name:
        print("🚀 Blackwell GPU detected! Enabling advanced optimizations")
        return "blackwell"
    elif "RTX 40" in gpu_name or "RTX 30" in gpu_name:
        print("✓ Ampere/Ada GPU detected")
        return "ampere"
    else:
        print("✓ CUDA GPU available")
        return "cuda"

@dataclass
class UnslothConfig:
    """Configuration for Unsloth fine-tuning"""
    model_name: str
    max_seq_length: int = 2048
    load_in_4bit: bool = True
    use_gradient_checkpointing: bool = True
    use_flash_attention: bool = True
    dtype: Optional[str] = None  # Auto-detect

    # Fine-tuning hyperparameters
    learning_rate: float = 2e-4
    num_train_epochs: int = 3
    per_device_train_batch_size: int = 2
    gradient_accumulation_steps: int = 4
    warmup_steps: int = 5
    max_steps: int = 60

    # LoRA parameters
    lora_r: int = 16
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    target_modules: List[str] = None

    def __post_init__(self):
        if self.target_modules is None:
            self.target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                                   "gate_proj", "up_proj", "down_proj"]

class UnslothTrainer:
    """
    Fast LLM fine-tuning with Unsloth

    Example:
        trainer = UnslothTrainer("unsloth/llama-3-8b-bnb-4bit")
        trainer.load_dataset("alpaca")
        trainer.train()
        trainer.save_model("./output")
    """

    def __init__(self, model_name: str, config: Optional[UnslothConfig] = None):
        self.model_name = model_name
        self.config = config or UnslothConfig(model_name=model_name)
        self.model = None
        self.tokenizer = None
        self.trainer = None
        self.hardware_type = check_hardware_support()

    def load_model(self):
        """Load model with Unsloth optimizations"""
        try:
            from unsloth import FastLanguageModel
            from unsloth import is_bfloat16_supported
        except ImportError:
            print("❌ Unsloth not installed. Installing...")
            os.system("pip install unsloth")
            from unsloth import FastLanguageModel
            from unsloth import is_bfloat16_supported

        print(f"Loading model: {self.model_name}")

        # Auto-detect dtype
        dtype = None
        if self.config.dtype is None:
            dtype = torch.bfloat16 if is_bfloat16_supported() else torch.float16

        # Load with Unsloth optimizations
        self.model, self.tokenizer = FastLanguageModel.from_pretrained(
            model_name=self.model_name,
            max_seq_length=self.config.max_seq_length,
            dtype=dtype,
            load_in_4bit=self.config.load_in_4bit,
        )

        print("✓ Model loaded with Unsloth optimizations")
        print(f"  - 4-bit quantization: {self.config.load_in_4bit}")
        print(f"  - Flash Attention: {self.config.use_flash_attention}")
        print(f"  - Gradient Checkpointing: {self.config.use_gradient_checkpointing}")

    def add_lora_adapters(self):
        """Add LoRA adapters for parameter-efficient fine-tuning"""
        from unsloth import FastLanguageModel

        print("Adding LoRA adapters...")
        self.model = FastLanguageModel.get_peft_model(
            self.model,
            r=self.config.lora_r,
            target_modules=self.config.target_modules,
            lora_alpha=self.config.lora_alpha,
            lora_dropout=self.config.lora_dropout,
            bias="none",
            use_gradient_checkpointing=self.config.use_gradient_checkpointing,
            random_state=3407,
        )

        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in self.model.parameters())
        print(f"✓ LoRA adapters added")
        print(f"  - Trainable params: {trainable_params:,} ({100 * trainable_params / total_params:.2f}%)")

    def load_dataset(self, dataset_name: str, split: str = "train"):
        """Load dataset from Hugging Face"""
        from datasets import load_dataset

        print(f"Loading dataset: {dataset_name}")
        self.dataset = load_dataset(dataset_name, split=split)
        print(f"✓ Loaded {len(self.dataset)} examples")

    def format_dataset(self, formatting_func):
        """Apply formatting function to dataset"""
        print("Formatting dataset...")
        self.dataset = self.dataset.map(formatting_func, batched=True)
        print("✓ Dataset formatted")

    def train(self, output_dir: str = "./lightos_finetuned"):
        """Start fine-tuning"""
        from trl import SFTTrainer
        from transformers import TrainingArguments

        print("Starting fine-tuning...")

        # Optimize for Blackwell if available
        if self.hardware_type == "blackwell":
            print("🚀 Applying Blackwell-specific optimizations")
            self.config.per_device_train_batch_size = 4  # Larger batches
            self.config.use_flash_attention = True

        training_args = TrainingArguments(
            output_dir=output_dir,
            per_device_train_batch_size=self.config.per_device_train_batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            warmup_steps=self.config.warmup_steps,
            max_steps=self.config.max_steps,
            learning_rate=self.config.learning_rate,
            fp16=not torch.cuda.is_bf16_supported(),
            bf16=torch.cuda.is_bf16_supported(),
            logging_steps=1,
            optim="adamw_8bit",
            weight_decay=0.01,
            lr_scheduler_type="linear",
            seed=3407,
        )

        self.trainer = SFTTrainer(
            model=self.model,
            tokenizer=self.tokenizer,
            train_dataset=self.dataset,
            dataset_text_field="text",
            max_seq_length=self.config.max_seq_length,
            dataset_num_proc=2,
            packing=False,
            args=training_args,
        )

        print("Training started...")
        self.trainer.train()
        print("✓ Training complete!")

    def save_model(self, output_dir: str):
        """Save fine-tuned model"""
        print(f"Saving model to {output_dir}")
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        print("✓ Model saved!")

    def push_to_hub(self, repo_name: str, token: str):
        """Push model to Hugging Face Hub"""
        print(f"Pushing to Hugging Face: {repo_name}")
        self.model.push_to_hub(repo_name, token=token)
        self.tokenizer.push_to_hub(repo_name, token=token)
        print("✓ Model pushed to Hub!")

# Supported models for quick reference
SUPPORTED_MODELS = {
    "llama-3.1-8b": "unsloth/Meta-Llama-3.1-8B-bnb-4bit",
    "llama-3.1-70b": "unsloth/Meta-Llama-3.1-70B-bnb-4bit",
    "mistral-7b": "unsloth/mistral-7b-v0.3-bnb-4bit",
    "phi-3-mini": "unsloth/Phi-3-mini-4k-instruct",
    "gemma-2-9b": "unsloth/gemma-2-9b-bnb-4bit",
    "qwen2.5-7b": "unsloth/Qwen2.5-7B-bnb-4bit",
    "qwen2.5-14b": "unsloth/Qwen2.5-14B-bnb-4bit",
    "glm-4-9b": "unsloth/glm-4-9b-chat-bnb-4bit",
}

def list_supported_models():
    """List all pre-optimized Unsloth models"""
    print("Supported Models for Fast Fine-tuning:")
    print("=" * 60)
    for name, model_id in SUPPORTED_MODELS.items():
        print(f"  {name:20} → {model_id}")
    print("=" * 60)
    print("\nOr use any Hugging Face model ID")

def quick_finetune(
    model_name: str,
    dataset_name: str,
    output_dir: str = "./finetuned_model",
    max_steps: int = 60
):
    """
    Quick fine-tuning function for common use cases

    Args:
        model_name: Model identifier (e.g., 'llama-3.1-8b' or full HF path)
        dataset_name: Dataset from Hugging Face
        output_dir: Where to save the model
        max_steps: Number of training steps

    Example:
        quick_finetune("llama-3.1-8b", "yahma/alpaca-cleaned", max_steps=100)
    """
    # Resolve model name
    model_id = SUPPORTED_MODELS.get(model_name, model_name)

    # Create trainer
    config = UnslothConfig(model_name=model_id, max_steps=max_steps)
    trainer = UnslothTrainer(model_id, config)

    # Load and train
    trainer.load_model()
    trainer.add_lora_adapters()
    trainer.load_dataset(dataset_name)
    trainer.train(output_dir)
    trainer.save_model(output_dir)

    print(f"\n✓ Fine-tuning complete! Model saved to: {output_dir}")
    print(f"  Load with: FastLanguageModel.from_pretrained('{output_dir}')")

if __name__ == "__main__":
    # Example usage
    print("LightOS Unsloth Integration")
    print("=" * 60)

    if len(sys.argv) > 1:
        if sys.argv[1] == "list":
            list_supported_models()
        elif sys.argv[1] == "train":
            if len(sys.argv) < 4:
                print("Usage: unsloth_integration.py train <model> <dataset>")
                sys.exit(1)
            quick_finetune(sys.argv[2], sys.argv[3])
    else:
        list_supported_models()
        print("\nUsage:")
        print("  python unsloth_integration.py list              # List models")
        print("  python unsloth_integration.py train <model> <dataset>")
