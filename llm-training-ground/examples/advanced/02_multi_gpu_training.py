"""
LightOS LLM Training Ground - Advanced Example 2
Multi-GPU Training with DeepSpeed

This example demonstrates distributed training across multiple GPUs
using DeepSpeed for maximum performance.

Requirements:
- 2+ NVIDIA GPUs with 12GB+ VRAM each
- DeepSpeed installed (pip install deepspeed)
- CUDA 11.8+

Time: Significantly faster than single GPU
"""

import sys
sys.path.append('/opt/lightos/llm-training-ground')

from unsloth_integration import UnslothTrainer, UnslothConfig
import torch

print("🚀 Multi-GPU Training with DeepSpeed")
print()

# Check available GPUs
if torch.cuda.device_count() < 2:
    print("⚠️  Warning: This example requires 2+ GPUs")
    print(f"Found {torch.cuda.device_count()} GPU(s)")
    print()

# Display GPU information
print("📊 Available GPUs:")
for i in range(torch.cuda.device_count()):
    props = torch.cuda.get_device_properties(i)
    print(f"  GPU {i}: {props.name}")
    print(f"    Memory: {props.total_memory / 1024**3:.1f} GB")
    print(f"    Compute: {props.major}.{props.minor}")
print()

# DeepSpeed configuration
deepspeed_config = {
    "train_micro_batch_size_per_gpu": 1,
    "gradient_accumulation_steps": 4,
    "optimizer": {
        "type": "AdamW",
        "params": {
            "lr": 2e-4,
            "betas": [0.9, 0.999],
            "eps": 1e-8
        }
    },
    "scheduler": {
        "type": "WarmupLR",
        "params": {
            "warmup_min_lr": 0,
            "warmup_max_lr": 2e-4,
            "warmup_num_steps": 100
        }
    },
    "fp16": {
        "enabled": True,
        "loss_scale": 0,
        "loss_scale_window": 1000,
        "hysteresis": 2,
        "min_loss_scale": 1
    },
    "zero_optimization": {
        "stage": 2,  # ZeRO stage 2 for memory optimization
        "allgather_partitions": True,
        "allgather_bucket_size": 2e8,
        "overlap_comm": True,
        "reduce_scatter": True,
        "reduce_bucket_size": 2e8,
        "contiguous_gradients": True
    },
    "activation_checkpointing": {
        "partition_activations": True,
        "cpu_checkpointing": False,
        "contiguous_memory_optimization": True,
        "number_checkpoints": None,
        "synchronize_checkpoint_boundary": False,
        "profile": False
    },
    "wall_clock_breakdown": False
}

# Save DeepSpeed config
import json
with open('./deepspeed_config.json', 'w') as f:
    json.dump(deepspeed_config, f, indent=2)

print("✅ DeepSpeed configuration saved")
print()

# Configure training
config = UnslothConfig(
    model_name="unsloth/llama-3-8b-bnb-4bit",
    max_seq_length=2048,
    load_in_4bit=False,  # DeepSpeed handles optimization

    # Multi-GPU settings
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,

    # Training parameters
    max_steps=500,
    learning_rate=2e-4,
    warmup_steps=100,

    # Enable DeepSpeed
    deepspeed='./deepspeed_config.json',
)

print("⚙️  Training Configuration:")
print(f"  GPUs: {torch.cuda.device_count()}")
print(f"  Batch size per GPU: {config.per_device_train_batch_size}")
print(f"  Gradient accumulation: {config.gradient_accumulation_steps}")
print(f"  Effective batch size: {config.per_device_train_batch_size * config.gradient_accumulation_steps * torch.cuda.device_count()}")
print(f"  Max steps: {config.max_steps}")
print()

# Initialize trainer
print("🚀 Initializing multi-GPU trainer...")
trainer = UnslothTrainer(config.model_name, config)

# Load model (will be distributed across GPUs)
print("📦 Loading model across GPUs...")
trainer.load_model()
print("✅ Model distributed")
print()

# Add LoRA adapters
print("🔧 Adding LoRA adapters...")
trainer.add_lora_adapters()
print("✅ Adapters ready")
print()

# Load dataset
print("📊 Loading dataset...")
trainer.load_dataset("yahma/alpaca-cleaned")
print("✅ Dataset loaded")
print()

# Start training
print("🏃 Starting distributed training...")
print("Monitor GPU usage with: watch -n 1 nvidia-smi")
print()

trainer.train('./models/multi-gpu-finetuned')

print()
print("✅ Multi-GPU training complete!")
print("Model saved to: ./models/multi-gpu-finetuned")
print()

# Performance statistics
print("📊 Performance Statistics:")
print("  Check logs for:")
print("  - Training time")
print("  - Throughput (samples/second)")
print("  - GPU utilization")
print("  - Memory usage per GPU")
