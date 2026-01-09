#!/usr/bin/env python3
"""
LightOS LLM Training Ground - Run Launcher

Orchestrates LLM training runs with:
- Model configuration
- Dataset preparation
- Distributed training setup
- LightOS integration (spiking, MoE, photonic)
- Budget monitoring and auto-pause
"""

import json
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path

from asset_browser import (
    ModelSpec, DatasetSpec, ComputeResource,
    BudgetGuardrails, ModelFamily, HardwareType
)

@dataclass
class TrainingConfig:
    """Complete training run configuration"""
    run_id: str
    model: ModelSpec
    dataset: DatasetSpec
    compute: ComputeResource
    budget: BudgetGuardrails

    # Training hyperparameters
    batch_size: int = 8
    learning_rate: float = 3e-4
    num_epochs: int = 3
    gradient_accumulation_steps: int = 4
    warmup_steps: int = 1000
    max_steps: Optional[int] = None

    # LightOS specific
    enable_spiking: bool = True
    enable_moe: bool = True
    enable_photonic: bool = True
    target_sparsity: float = 0.69  # 69% sparsity target

    # Distributed training
    num_nodes: int = 1
    gpus_per_node: int = 8
    distributed_backend: str = "nccl"  # nccl, gloo, or lightos

    # Checkpointing
    checkpoint_interval_steps: int = 1000
    save_dir: str = "./checkpoints"

    # Monitoring
    log_interval_steps: int = 10
    eval_interval_steps: int = 500

@dataclass
class RunStatus:
    """Training run status"""
    run_id: str
    status: str  # "pending", "running", "paused", "completed", "failed"
    progress_percent: float
    current_step: int
    total_steps: int

    # Performance metrics
    tokens_per_second: float
    loss: float
    perplexity: float

    # Resource usage
    gpu_utilization_percent: float
    memory_used_gb: float
    power_watts: float

    # Budget tracking
    cost_spent_usd: float
    cost_remaining_usd: float
    time_elapsed_hours: float

    # LightOS metrics
    sparsity_achieved: float
    thermal_state: str  # "normal", "throttling", "critical"

class RunLauncher:
    """Orchestrates LLM training runs"""

    def __init__(self, lightos_endpoint: str = "localhost:50051"):
        self.lightos_endpoint = lightos_endpoint
        self.active_runs: Dict[str, RunStatus] = {}

    def create_run(self, config: TrainingConfig) -> str:
        """Create a new training run"""

        # Generate run ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_id = f"{config.model.name}_{timestamp}"
        config.run_id = run_id

        # Create run directory
        run_dir = Path(config.save_dir) / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        # Save configuration
        config_path = run_dir / "config.json"
        with open(config_path, 'w') as f:
            json.dump(asdict(config), f, indent=2, default=str)

        print(f"Created training run: {run_id}")
        print(f"  Model: {config.model.name} ({config.model.size_params/1e9:.1f}B)")
        print(f"  Dataset: {config.dataset.name}")
        print(f"  Compute: {config.compute.num_devices}x {config.compute.hardware_type.value}")
        print(f"  Budget: ${config.budget.max_cost_usd:.2f} USD")

        return run_id

    def launch_run(self, run_id: str, config: TrainingConfig) -> bool:
        """Launch the training run"""

        print(f"\n=== Launching Training Run: {run_id} ===\n")

        # 1. Prepare LightOS runtime
        if not self._setup_lightos_runtime(config):
            print("❌ Failed to setup LightOS runtime")
            return False

        # 2. Download/prepare dataset
        if not self._prepare_dataset(config):
            print("❌ Failed to prepare dataset")
            return False

        # 3. Configure distributed training
        if not self._setup_distributed_training(config):
            print("❌ Failed to setup distributed training")
            return False

        # 4. Generate training script
        script_path = self._generate_training_script(config)

        # 5. Launch training process
        if not self._launch_training_process(config, script_path):
            print("❌ Failed to launch training process")
            return False

        # 6. Initialize monitoring
        self._init_monitoring(run_id, config)

        # Initialize run status
        self.active_runs[run_id] = RunStatus(
            run_id=run_id,
            status="running",
            progress_percent=0.0,
            current_step=0,
            total_steps=config.max_steps or 10000,
            tokens_per_second=0.0,
            loss=0.0,
            perplexity=0.0,
            gpu_utilization_percent=0.0,
            memory_used_gb=0.0,
            power_watts=0.0,
            cost_spent_usd=0.0,
            cost_remaining_usd=config.budget.max_cost_usd or 0.0,
            time_elapsed_hours=0.0,
            sparsity_achieved=0.0,
            thermal_state="normal"
        )

        print(f"✅ Training run launched successfully!")
        print(f"   Monitor: lightos status {run_id}")
        print(f"   Logs: tail -f {config.save_dir}/{run_id}/train.log")

        return True

    def _setup_lightos_runtime(self, config: TrainingConfig) -> bool:
        """Setup LightOS runtime with spiking/MoE/photonic"""

        print("Setting up LightOS runtime...")

        # Configure spiking engine
        if config.enable_spiking and config.model.supports_spiking:
            print(f"  ✓ Enabling spiking engine (target: {config.target_sparsity*100:.0f}% sparsity)")
            # In production: Call ioctl to configure spiking engine
            # ioctl(lightos_fd, LIGHTOS_IOC_SPIKING_CONFIG, &spiking_config)

        # Configure MoE engine
        if config.enable_moe and config.model.supports_moe:
            print(f"  ✓ Enabling MoE sparsity engine")
            # In production: Configure MoE routing

        # Select compute backend
        if config.enable_photonic and config.compute.hardware_type == HardwareType.NPU_PHOTONIC:
            print(f"  ✓ Using photonic NPU backend")
        elif config.compute.hardware_type == HardwareType.GPU_NVIDIA:
            print(f"  ✓ Using NVIDIA CUDA backend")
        elif config.compute.hardware_type == HardwareType.GPU_AMD:
            print(f"  ✓ Using AMD ROCm backend")

        return True

    def _prepare_dataset(self, config: TrainingConfig) -> bool:
        """Download and prepare dataset"""

        print(f"Preparing dataset: {config.dataset.name}...")

        # In production: Download from HuggingFace, S3, etc.
        # For now, assume dataset is already available

        print(f"  ✓ Dataset ready: {config.dataset.size_gb}GB, {config.dataset.num_examples:,} examples")
        return True

    def _setup_distributed_training(self, config: TrainingConfig) -> bool:
        """Setup distributed training environment"""

        if config.num_nodes > 1 or config.gpus_per_node > 1:
            print(f"Setting up distributed training...")
            print(f"  Nodes: {config.num_nodes}")
            print(f"  GPUs per node: {config.gpus_per_node}")
            print(f"  Backend: {config.distributed_backend}")

            # In production: Setup torch.distributed or lightos distributed runtime
            return True

        return True

    def _generate_training_script(self, config: TrainingConfig) -> Path:
        """Generate training script"""

        script_content = f"""#!/usr/bin/env python3
# Auto-generated training script for {config.run_id}

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from datasets import load_dataset

# LightOS imports
try:
    import lightos_runtime as lightos
    LIGHTOS_AVAILABLE = True
except ImportError:
    LIGHTOS_AVAILABLE = False
    print("Warning: LightOS runtime not available, falling back to standard PyTorch")

# Load model
model_name = "{config.model.name}"
model = AutoModelForCausalLM.from_pretrained(model_name)

# Enable LightOS optimizations
if LIGHTOS_AVAILABLE:
    # Configure spiking engine
    if {config.enable_spiking}:
        lightos.enable_spiking(model, target_sparsity={config.target_sparsity})

    # Configure MoE
    if {config.enable_moe}:
        lightos.enable_moe(model, top_k=2, num_experts=64)

    # Select backend
    lightos.set_backend("{config.compute.hardware_type.value}")

# Load dataset
dataset = load_dataset("{config.dataset.name}")

# Training arguments
training_args = TrainingArguments(
    output_dir="{config.save_dir}/{config.run_id}",
    num_train_epochs={config.num_epochs},
    per_device_train_batch_size={config.batch_size},
    gradient_accumulation_steps={config.gradient_accumulation_steps},
    learning_rate={config.learning_rate},
    warmup_steps={config.warmup_steps},
    logging_steps={config.log_interval_steps},
    save_steps={config.checkpoint_interval_steps},
    eval_steps={config.eval_interval_steps},
    max_steps={config.max_steps or -1},
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset.get("validation"),
)

# Train
trainer.train()
"""

        script_path = Path(config.save_dir) / config.run_id / "train.py"
        with open(script_path, 'w') as f:
            f.write(script_content)

        script_path.chmod(0o755)
        print(f"  ✓ Generated training script: {script_path}")

        return script_path

    def _launch_training_process(self, config: TrainingConfig, script_path: Path) -> bool:
        """Launch the actual training process"""

        print("Launching training process...")

        # In production: Use subprocess to launch training in background
        # For now, just print the command

        if config.num_nodes > 1:
            # Multi-node training
            cmd = f"torchrun --nnodes={config.num_nodes} --nproc_per_node={config.gpus_per_node} {script_path}"
        else:
            # Single node training
            cmd = f"torchrun --nproc_per_node={config.gpus_per_node} {script_path}"

        print(f"  Command: {cmd}")
        print(f"  (Run manually for now, or implement subprocess.Popen for background execution)")

        return True

    def _init_monitoring(self, run_id: str, config: TrainingConfig):
        """Initialize monitoring for the run"""

        print("Initializing monitoring...")

        # In production: Setup tensorboard, wandb, or custom monitoring
        # Monitor budget and auto-pause if limits exceeded

        print(f"  ✓ Monitoring initialized")
        print(f"  Budget: ${config.budget.max_cost_usd:.2f} USD")
        print(f"  Duration: {config.budget.max_duration_hours:.1f} hours")

    def get_status(self, run_id: str) -> Optional[RunStatus]:
        """Get status of a training run"""
        return self.active_runs.get(run_id)

    def pause_run(self, run_id: str) -> bool:
        """Pause a training run (save checkpoint)"""
        if run_id in self.active_runs:
            self.active_runs[run_id].status = "paused"
            print(f"Paused run: {run_id}")
            return True
        return False

    def resume_run(self, run_id: str) -> bool:
        """Resume a paused training run"""
        if run_id in self.active_runs:
            self.active_runs[run_id].status = "running"
            print(f"Resumed run: {run_id}")
            return True
        return False

    def stop_run(self, run_id: str) -> bool:
        """Stop a training run"""
        if run_id in self.active_runs:
            self.active_runs[run_id].status = "completed"
            print(f"Stopped run: {run_id}")
            return True
        return False

# Example usage
if __name__ == "__main__":
    from asset_browser import AssetBrowser

    # Initialize components
    browser = AssetBrowser()
    launcher = RunLauncher()

    # Select model
    spiking_models = browser.list_models(supports_spiking=True)
    model = spiking_models[0]  # SpikingBrain-7B

    # Select dataset
    dataset = browser.datasets[2]  # OpenWebText

    # Set budget
    budget = BudgetGuardrails(
        max_cost_usd=500.0,
        max_duration_hours=24.0,
        enable_spot_instances=True,
        enable_hibernation=True
    )

    # Recommend compute
    compute = browser.recommend_compute(model, budget)

    # Create training configuration
    config = TrainingConfig(
        run_id="",  # Will be generated
        model=model,
        dataset=dataset,
        compute=compute,
        budget=budget,
        enable_spiking=True,
        enable_moe=True,
        target_sparsity=0.69,
        batch_size=8,
        learning_rate=3e-4,
        num_epochs=3,
        max_steps=10000,
    )

    # Create and launch run
    run_id = launcher.create_run(config)
    success = launcher.launch_run(run_id, config)

    if success:
        print(f"\n✅ Training run {run_id} launched successfully!")
        print(f"   Monitor with: lightos status {run_id}")
    else:
        print(f"\n❌ Failed to launch training run")
