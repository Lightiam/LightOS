#!/usr/bin/env python3
"""
LightOS LLM Training Ground - Universal Asset Browser

Provides a unified interface for browsing and selecting:
- Model families (LFM2.5, SpikingBrain-7B, Llama, GPT, etc.)
- Datasets (HuggingFace, custom, cloud storage)
- Compute resources (GPUs, NPUs, Photonic accelerators)
- Budget guardrails (cost limits, time limits)
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class ModelFamily(Enum):
    """Supported model architectures"""
    SPIKING_BRAIN = "spiking-brain"     # LightOS native spiking models
    LFM = "lfm"                         # Large Foundation Models
    LLAMA = "llama"                     # Meta's Llama family
    GPT = "gpt"                         # GPT-style transformers
    MIXTRAL = "mixtral"                 # MoE models
    BERT = "bert"                       # Encoder-only models
    T5 = "t5"                           # Encoder-decoder models
    CUSTOM = "custom"                   # User-defined architectures

class HardwareType(Enum):
    """Available compute backends"""
    GPU_NVIDIA = "nvidia-gpu"
    GPU_AMD = "amd-gpu"
    TPU_GOOGLE = "google-tpu"
    NPU_INTEL = "intel-npu"
    NPU_ARM = "arm-npu"
    NPU_PHOTONIC = "photonic-npu"      # LightOS photonic accelerators
    CPU = "cpu"
    AUTO = "auto"                       # LightOS chooses optimal

@dataclass
class ModelSpec:
    """Model specification"""
    family: ModelFamily
    name: str
    size_params: int                    # Number of parameters (e.g., 7B)
    context_length: int                 # Max sequence length
    supports_spiking: bool              # Can use spiking engine
    supports_moe: bool                  # Can use MoE sparsity
    memory_required_gb: float
    description: str

@dataclass
class DatasetSpec:
    """Dataset specification"""
    name: str
    source: str                         # "huggingface", "s3", "gcs", "local"
    size_gb: float
    num_examples: int
    languages: List[str]
    license: str
    description: str

@dataclass
class ComputeResource:
    """Compute resource specification"""
    hardware_type: HardwareType
    num_devices: int
    device_memory_gb: float
    interconnect_bandwidth_gbps: float
    cost_per_hour: float
    location: str                       # Data center location

@dataclass
class BudgetGuardrails:
    """Budget constraints for training run"""
    max_cost_usd: Optional[float] = None
    max_duration_hours: Optional[float] = None
    max_energy_kwh: Optional[float] = None
    max_carbon_kg: Optional[float] = None
    enable_spot_instances: bool = True
    enable_hibernation: bool = True     # Pause on budget limits

class AssetBrowser:
    """Universal asset browser for LLM training"""

    def __init__(self):
        self.models = self._load_model_catalog()
        self.datasets = self._load_dataset_catalog()
        self.compute_resources = self._discover_compute_resources()

    def _load_model_catalog(self) -> List[ModelSpec]:
        """Load available model specifications"""
        return [
            ModelSpec(
                family=ModelFamily.SPIKING_BRAIN,
                name="SpikingBrain-7B",
                size_params=7_000_000_000,
                context_length=8192,
                supports_spiking=True,
                supports_moe=True,
                memory_required_gb=14.0,
                description="LightOS native spiking transformer with 69% sparsity"
            ),
            ModelSpec(
                family=ModelFamily.SPIKING_BRAIN,
                name="SpikingBrain-70B",
                size_params=70_000_000_000,
                context_length=32768,
                supports_spiking=True,
                supports_moe=True,
                memory_required_gb=140.0,
                description="Large spiking model with ultra-long context"
            ),
            ModelSpec(
                family=ModelFamily.LFM,
                name="LFM2.5-13B",
                size_params=13_000_000_000,
                context_length=16384,
                supports_spiking=False,
                supports_moe=True,
                memory_required_gb=26.0,
                description="Large Foundation Model 2.5 - 13B parameters"
            ),
            ModelSpec(
                family=ModelFamily.LLAMA,
                name="Llama-3.1-8B",
                size_params=8_000_000_000,
                context_length=128_000,
                supports_spiking=False,
                supports_moe=False,
                memory_required_gb=16.0,
                description="Meta Llama 3.1 with 128K context"
            ),
            ModelSpec(
                family=ModelFamily.MIXTRAL,
                name="Mixtral-8x7B",
                size_params=47_000_000_000,
                context_length=32768,
                supports_spiking=False,
                supports_moe=True,
                memory_required_gb=90.0,
                description="MoE model with 8 experts, 2 active per token"
            ),
        ]

    def _load_dataset_catalog(self) -> List[DatasetSpec]:
        """Load available datasets"""
        return [
            DatasetSpec(
                name="RedPajama-Data-V2",
                source="huggingface",
                size_gb=30000,
                num_examples=30_000_000_000,
                languages=["en"],
                license="Apache 2.0",
                description="30T tokens of web data, books, code"
            ),
            DatasetSpec(
                name="The Stack v2",
                source="huggingface",
                size_gb=3000,
                num_examples=67_000_000,
                languages=["multilingual-code"],
                license="Various OSS",
                description="900+ programming languages"
            ),
            DatasetSpec(
                name="OpenWebText",
                source="huggingface",
                size_gb=40,
                num_examples=8_000_000,
                languages=["en"],
                license="Public Domain",
                description="Web scrape similar to GPT-2 training set"
            ),
        ]

    def _discover_compute_resources(self) -> List[ComputeResource]:
        """Discover available compute resources"""
        # In production, would query LightOS runtime for actual hardware
        return [
            ComputeResource(
                hardware_type=HardwareType.GPU_NVIDIA,
                num_devices=8,
                device_memory_gb=80.0,  # A100 80GB
                interconnect_bandwidth_gbps=600,  # NVLink
                cost_per_hour=24.0,  # ~$3/hr per GPU
                location="us-east-1"
            ),
            ComputeResource(
                hardware_type=HardwareType.NPU_PHOTONIC,
                num_devices=4,
                device_memory_gb=128.0,
                interconnect_bandwidth_gbps=10000,  # Optical interconnect!
                cost_per_hour=15.0,  # Cheaper due to efficiency
                location="us-west-2-lightos"
            ),
            ComputeResource(
                hardware_type=HardwareType.GPU_AMD,
                num_devices=8,
                device_memory_gb=64.0,  # MI250X
                interconnect_bandwidth_gbps=400,
                cost_per_hour=18.0,
                location="us-east-2"
            ),
        ]

    def list_models(self, family: Optional[ModelFamily] = None,
                   max_params: Optional[int] = None,
                   supports_spiking: Optional[bool] = None) -> List[ModelSpec]:
        """Filter and list available models"""
        filtered = self.models

        if family:
            filtered = [m for m in filtered if m.family == family]

        if max_params:
            filtered = [m for m in filtered if m.size_params <= max_params]

        if supports_spiking is not None:
            filtered = [m for m in filtered if m.supports_spiking == supports_spiking]

        return filtered

    def list_datasets(self, min_size_gb: Optional[float] = None,
                     language: Optional[str] = None) -> List[DatasetSpec]:
        """Filter and list available datasets"""
        filtered = self.datasets

        if min_size_gb:
            filtered = [d for d in filtered if d.size_gb >= min_size_gb]

        if language:
            filtered = [d for d in filtered if language in d.languages]

        return filtered

    def recommend_compute(self, model: ModelSpec, budget: BudgetGuardrails) -> ComputeResource:
        """Recommend optimal compute resource for model + budget"""

        # Filter by memory requirements
        suitable = [r for r in self.compute_resources
                   if r.device_memory_gb * r.num_devices >= model.memory_required_gb]

        if not suitable:
            raise ValueError(f"No compute resources with sufficient memory for {model.name}")

        # Filter by budget
        if budget.max_cost_usd and budget.max_duration_hours:
            max_hourly_cost = budget.max_cost_usd / budget.max_duration_hours
            suitable = [r for r in suitable if r.cost_per_hour <= max_hourly_cost]

        if not suitable:
            raise ValueError("No compute resources within budget constraints")

        # Prefer photonic for spiking models
        if model.supports_spiking:
            photonic = [r for r in suitable if r.hardware_type == HardwareType.NPU_PHOTONIC]
            if photonic:
                return min(photonic, key=lambda x: x.cost_per_hour)

        # Otherwise, choose cheapest that meets requirements
        return min(suitable, key=lambda x: x.cost_per_hour)

    def estimate_cost(self, model: ModelSpec, dataset: DatasetSpec,
                     compute: ComputeResource, training_steps: int) -> Dict[str, float]:
        """Estimate training cost"""

        # Simple estimation (production would use more sophisticated model)
        tokens_per_second = 1000 * compute.num_devices  # Mock
        total_tokens = dataset.num_examples * 512  # Assume 512 tokens/example
        training_time_hours = (total_tokens / tokens_per_second) / 3600

        cost_usd = training_time_hours * compute.cost_per_hour
        energy_kwh = training_time_hours * (compute.num_devices * 0.3)  # 300W per device
        carbon_kg = energy_kwh * 0.4  # 0.4 kg CO2/kWh (US average)

        return {
            "estimated_duration_hours": training_time_hours,
            "estimated_cost_usd": cost_usd,
            "estimated_energy_kwh": energy_kwh,
            "estimated_carbon_kg": carbon_kg,
        }

# Example usage
if __name__ == "__main__":
    browser = AssetBrowser()

    # List spiking models
    print("=== Available Spiking Models ===")
    spiking_models = browser.list_models(supports_spiking=True)
    for model in spiking_models:
        print(f"  {model.name}: {model.size_params/1e9:.1f}B params, "
              f"{model.context_length} ctx, {model.memory_required_gb}GB RAM")

    # List datasets
    print("\n=== Available Datasets ===")
    for dataset in browser.list_datasets():
        print(f"  {dataset.name}: {dataset.size_gb}GB, {dataset.num_examples:,} examples")

    # Recommend compute
    print("\n=== Compute Recommendation ===")
    model = spiking_models[0]  # SpikingBrain-7B
    budget = BudgetGuardrails(max_cost_usd=1000.0, max_duration_hours=48.0)

    compute = browser.recommend_compute(model, budget)
    print(f"  Recommended: {compute.num_devices}x {compute.hardware_type.value}")
    print(f"  Cost: ${compute.cost_per_hour:.2f}/hr")
    print(f"  Location: {compute.location}")

    # Estimate cost
    dataset = browser.datasets[2]  # OpenWebText
    estimate = browser.estimate_cost(model, dataset, compute, training_steps=10000)
    print(f"\n=== Cost Estimate ===")
    print(f"  Duration: {estimate['estimated_duration_hours']:.1f} hours")
    print(f"  Cost: ${estimate['estimated_cost_usd']:.2f}")
    print(f"  Energy: {estimate['estimated_energy_kwh']:.1f} kWh")
    print(f"  Carbon: {estimate['estimated_carbon_kg']:.1f} kg CO2")
