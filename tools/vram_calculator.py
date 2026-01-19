#!/usr/bin/env python3
"""
LightOS LLM VRAM Calculator
Estimate GPU memory requirements for running Large Language Models

Features:
- Calculate VRAM for model inference and training
- Support for all quantization formats (FP32, FP16, BF16, FP8, INT8, INT4)
- KV cache memory estimation
- Batch size and context length optimization
- Multi-GPU memory distribution
- GPU recommendations based on requirements
"""

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from enum import Enum


class Precision(Enum):
    """Supported precision formats"""
    FP32 = 4  # 32-bit floating point (4 bytes)
    FP16 = 2  # 16-bit floating point (2 bytes)
    BF16 = 2  # Brain float 16 (2 bytes)
    FP8 = 1   # 8-bit floating point (1 byte)
    INT8 = 1  # 8-bit integer (1 byte)
    INT4 = 0.5  # 4-bit integer (0.5 bytes)
    INT2 = 0.25  # 2-bit integer (0.25 bytes)


class GPUType(Enum):
    """Common GPU types with VRAM capacity"""
    RTX_3060 = 12
    RTX_3090 = 24
    RTX_4060_TI = 16
    RTX_4070 = 12
    RTX_4070_TI = 12
    RTX_4080 = 16
    RTX_4090 = 24
    A100_40GB = 40
    A100_80GB = 80
    H100 = 80
    H100_NVL = 188  # Dual GPU
    MI300X = 192
    APPLE_M1_MAX = 64
    APPLE_M2_ULTRA = 192
    APPLE_M3_MAX = 128


@dataclass
class ModelConfig:
    """LLM model configuration"""
    name: str
    parameters_billions: float
    hidden_size: int
    num_layers: int
    num_attention_heads: int
    vocab_size: int = 50000
    intermediate_size: Optional[int] = None

    def __post_init__(self):
        if self.intermediate_size is None:
            # FFN intermediate size is typically 4x hidden size
            self.intermediate_size = self.hidden_size * 4


# Popular model configurations
POPULAR_MODELS = {
    "Llama-3.1-8B": ModelConfig("Llama-3.1-8B", 8.0, 4096, 32, 32),
    "Llama-3.1-70B": ModelConfig("Llama-3.1-70B", 70.0, 8192, 80, 64),
    "Llama-3.1-405B": ModelConfig("Llama-3.1-405B", 405.0, 16384, 126, 128),
    "Qwen-2.5-7B": ModelConfig("Qwen-2.5-7B", 7.0, 3584, 28, 28),
    "Qwen-2.5-72B": ModelConfig("Qwen-2.5-72B", 72.0, 8192, 80, 64),
    "DeepSeek-R1-7B": ModelConfig("DeepSeek-R1-7B", 7.0, 4096, 30, 32),
    "DeepSeek-R1-67B": ModelConfig("DeepSeek-R1-67B", 67.0, 8192, 64, 64),
    "Mistral-7B": ModelConfig("Mistral-7B", 7.0, 4096, 32, 32),
    "Mixtral-8x7B": ModelConfig("Mixtral-8x7B", 47.0, 4096, 32, 32),  # 8 experts, ~47B active
    "Phi-3-Mini": ModelConfig("Phi-3-Mini", 3.8, 3072, 32, 32),
    "Gemma-2-9B": ModelConfig("Gemma-2-9B", 9.0, 3584, 42, 16),
    "Gemma-2-27B": ModelConfig("Gemma-2-27B", 27.0, 4608, 46, 32),
}


@dataclass
class VRAMEstimate:
    """VRAM usage breakdown"""
    model_weights_gb: float
    kv_cache_gb: float
    activation_memory_gb: float
    optimizer_states_gb: float  # For training
    gradient_memory_gb: float  # For training
    overhead_gb: float
    total_gb: float

    def __str__(self) -> str:
        return f"""
VRAM Breakdown:
  Model Weights:     {self.model_weights_gb:>8.2f} GB
  KV Cache:          {self.kv_cache_gb:>8.2f} GB
  Activations:       {self.activation_memory_gb:>8.2f} GB
  Optimizer States:  {self.optimizer_states_gb:>8.2f} GB
  Gradients:         {self.gradient_memory_gb:>8.2f} GB
  Overhead (10%):    {self.overhead_gb:>8.2f} GB
  ─────────────────────────────
  Total VRAM:        {self.total_gb:>8.2f} GB
"""


class VRAMCalculator:
    """Calculate VRAM requirements for LLM inference and training"""

    @staticmethod
    def calculate_model_size(
        parameters_billions: float,
        precision: Precision
    ) -> float:
        """Calculate model weight size in GB"""
        bytes_per_param = precision.value
        total_bytes = parameters_billions * 1e9 * bytes_per_param
        return total_bytes / (1024 ** 3)  # Convert to GB

    @staticmethod
    def calculate_kv_cache(
        batch_size: int,
        sequence_length: int,
        num_layers: int,
        hidden_size: int,
        num_attention_heads: int,
        precision: Precision,
        kv_cache_precision: Optional[Precision] = None
    ) -> float:
        """
        Calculate KV cache memory requirement.

        KV cache stores key and value vectors for all tokens in context:
        - 2 tensors (key + value) per layer
        - Shape: [batch_size, num_heads, sequence_length, head_dim]
        """
        if kv_cache_precision is None:
            kv_cache_precision = precision

        head_dim = hidden_size // num_attention_heads

        # KV cache per layer: batch * seq_len * num_heads * head_dim * 2 (K and V)
        kv_elements_per_layer = batch_size * sequence_length * num_attention_heads * head_dim * 2

        # Total across all layers
        total_kv_elements = kv_elements_per_layer * num_layers

        # Convert to bytes
        total_bytes = total_kv_elements * kv_cache_precision.value

        return total_bytes / (1024 ** 3)  # Convert to GB

    @staticmethod
    def calculate_activation_memory(
        batch_size: int,
        sequence_length: int,
        hidden_size: int,
        num_layers: int,
        precision: Precision
    ) -> float:
        """
        Calculate activation memory for forward pass.

        Activations include intermediate results stored for backprop:
        - Attention outputs
        - FFN intermediate activations
        - Layer norm outputs
        """
        # Approximate activation memory per token
        # Includes attention output, FFN intermediate (4x hidden), layer norms
        activation_per_token = hidden_size * 6  # Conservative estimate

        total_activations = batch_size * sequence_length * activation_per_token * num_layers
        total_bytes = total_activations * precision.value

        return total_bytes / (1024 ** 3)

    @staticmethod
    def calculate_optimizer_states(
        parameters_billions: float,
        precision: Precision,
        optimizer: str = "AdamW"
    ) -> float:
        """
        Calculate optimizer state memory (for training).

        AdamW stores:
        - Momentum (1st moment): FP32
        - Variance (2nd moment): FP32
        Total: 8 bytes per parameter
        """
        if optimizer.lower() == "adamw":
            # AdamW: 2 states (momentum + variance) in FP32
            bytes_per_param = 8  # 2 * 4 bytes (FP32)
        elif optimizer.lower() == "sgd":
            # SGD with momentum: 1 state in FP32
            bytes_per_param = 4
        else:
            bytes_per_param = 8  # Default to AdamW

        total_bytes = parameters_billions * 1e9 * bytes_per_param
        return total_bytes / (1024 ** 3)

    @staticmethod
    def calculate_gradient_memory(
        parameters_billions: float,
        precision: Precision
    ) -> float:
        """Calculate gradient memory (for training)"""
        # Gradients typically stored in FP32 for stability
        bytes_per_param = 4  # FP32
        total_bytes = parameters_billions * 1e9 * bytes_per_param
        return total_bytes / (1024 ** 3)

    @staticmethod
    def estimate_inference(
        model: ModelConfig,
        batch_size: int = 1,
        context_length: int = 2048,
        precision: Precision = Precision.FP16,
        kv_cache_precision: Optional[Precision] = None
    ) -> VRAMEstimate:
        """Estimate VRAM for inference"""

        # Model weights
        model_weights = VRAMCalculator.calculate_model_size(
            model.parameters_billions, precision
        )

        # KV cache
        kv_cache = VRAMCalculator.calculate_kv_cache(
            batch_size, context_length,
            model.num_layers, model.hidden_size, model.num_attention_heads,
            precision, kv_cache_precision
        )

        # Activation memory (minimal for inference)
        activation_memory = VRAMCalculator.calculate_activation_memory(
            batch_size, context_length,
            model.hidden_size, model.num_layers, precision
        ) * 0.1  # Only 10% needed for inference

        # No optimizer/gradients for inference
        optimizer_states = 0.0
        gradient_memory = 0.0

        # Subtotal
        subtotal = model_weights + kv_cache + activation_memory

        # Overhead (framework, CUDA context, etc.)
        overhead = subtotal * 0.1

        # Total
        total = subtotal + overhead

        return VRAMEstimate(
            model_weights_gb=model_weights,
            kv_cache_gb=kv_cache,
            activation_memory_gb=activation_memory,
            optimizer_states_gb=optimizer_states,
            gradient_memory_gb=gradient_memory,
            overhead_gb=overhead,
            total_gb=total
        )

    @staticmethod
    def estimate_training(
        model: ModelConfig,
        batch_size: int = 8,
        sequence_length: int = 2048,
        precision: Precision = Precision.BF16,
        optimizer: str = "AdamW"
    ) -> VRAMEstimate:
        """Estimate VRAM for training/fine-tuning"""

        # Model weights
        model_weights = VRAMCalculator.calculate_model_size(
            model.parameters_billions, precision
        )

        # KV cache
        kv_cache = VRAMCalculator.calculate_kv_cache(
            batch_size, sequence_length,
            model.num_layers, model.hidden_size, model.num_attention_heads,
            precision
        )

        # Activation memory (full for training)
        activation_memory = VRAMCalculator.calculate_activation_memory(
            batch_size, sequence_length,
            model.hidden_size, model.num_layers, precision
        )

        # Optimizer states
        optimizer_states = VRAMCalculator.calculate_optimizer_states(
            model.parameters_billions, precision, optimizer
        )

        # Gradients
        gradient_memory = VRAMCalculator.calculate_gradient_memory(
            model.parameters_billions, precision
        )

        # Subtotal
        subtotal = (model_weights + kv_cache + activation_memory +
                   optimizer_states + gradient_memory)

        # Overhead
        overhead = subtotal * 0.1

        # Total
        total = subtotal + overhead

        return VRAMEstimate(
            model_weights_gb=model_weights,
            kv_cache_gb=kv_cache,
            activation_memory_gb=activation_memory,
            optimizer_states_gb=optimizer_states,
            gradient_memory_gb=gradient_memory,
            overhead_gb=overhead,
            total_gb=total
        )

    @staticmethod
    def recommend_gpus(vram_required_gb: float) -> List[Tuple[str, int]]:
        """
        Recommend GPUs that can handle the VRAM requirement.
        Returns list of (GPU name, number of GPUs needed)
        """
        recommendations = []

        for gpu in GPUType:
            num_gpus_needed = math.ceil(vram_required_gb / gpu.value)
            if num_gpus_needed <= 8:  # Max 8 GPUs practical
                recommendations.append((gpu.name, num_gpus_needed))

        # Sort by number of GPUs needed (ascending)
        recommendations.sort(key=lambda x: x[1])

        return recommendations

    @staticmethod
    def calculate_max_batch_size(
        model: ModelConfig,
        gpu_vram_gb: float,
        context_length: int = 2048,
        precision: Precision = Precision.FP16,
        mode: str = "inference"
    ) -> int:
        """Calculate maximum batch size that fits in VRAM"""

        batch_size = 1
        max_batch_size = 1

        # Binary search for max batch size
        for bs in range(1, 1024):
            if mode == "inference":
                estimate = VRAMCalculator.estimate_inference(
                    model, bs, context_length, precision
                )
            else:
                estimate = VRAMCalculator.estimate_training(
                    model, bs, context_length, precision
                )

            if estimate.total_gb <= gpu_vram_gb * 0.95:  # Leave 5% headroom
                max_batch_size = bs
            else:
                break

        return max_batch_size


def main():
    """Example usage"""
    print("=" * 70)
    print("LightOS LLM VRAM Calculator")
    print("=" * 70)
    print()

    # Example 1: Llama-3.1-8B inference
    print("Example 1: Llama-3.1-8B Inference (FP16)")
    print("-" * 70)
    model = POPULAR_MODELS["Llama-3.1-8B"]
    estimate = VRAMCalculator.estimate_inference(
        model,
        batch_size=1,
        context_length=4096,
        precision=Precision.FP16
    )
    print(estimate)

    # GPU recommendations
    print("GPU Recommendations:")
    recommendations = VRAMCalculator.recommend_gpus(estimate.total_gb)
    for i, (gpu_name, num_gpus) in enumerate(recommendations[:5], 1):
        gpu_vram = GPUType[gpu_name].value * num_gpus
        print(f"  {i}. {num_gpus}x {gpu_name.replace('_', ' ')} ({gpu_vram} GB total)")
    print()

    # Example 2: Llama-3.1-70B with INT4 quantization
    print("Example 2: Llama-3.1-70B Inference (INT4 quantized)")
    print("-" * 70)
    model = POPULAR_MODELS["Llama-3.1-70B"]
    estimate = VRAMCalculator.estimate_inference(
        model,
        batch_size=1,
        context_length=8192,
        precision=Precision.INT4,
        kv_cache_precision=Precision.FP16
    )
    print(estimate)

    # Calculate max batch size for RTX 4090
    max_bs = VRAMCalculator.calculate_max_batch_size(
        model,
        gpu_vram_gb=24,
        context_length=8192,
        precision=Precision.INT4
    )
    print(f"Maximum batch size on RTX 4090 (24GB): {max_bs}")
    print()

    # Example 3: Training Qwen-2.5-7B
    print("Example 3: Qwen-2.5-7B Training (BF16, AdamW)")
    print("-" * 70)
    model = POPULAR_MODELS["Qwen-2.5-7B"]
    estimate = VRAMCalculator.estimate_training(
        model,
        batch_size=4,
        sequence_length=2048,
        precision=Precision.BF16,
        optimizer="AdamW"
    )
    print(estimate)

    # GPU recommendations
    print("GPU Recommendations for Training:")
    recommendations = VRAMCalculator.recommend_gpus(estimate.total_gb)
    for i, (gpu_name, num_gpus) in enumerate(recommendations[:5], 1):
        gpu_vram = GPUType[gpu_name].value * num_gpus
        print(f"  {i}. {num_gpus}x {gpu_name.replace('_', ' ')} ({gpu_vram} GB total)")
    print()


if __name__ == "__main__":
    main()
