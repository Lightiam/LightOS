#!/usr/bin/env python3
"""
LightOS Enhanced Training Ground Launcher
Unified interface for LLM training, coding agents, and fine-tuning

New Features:
- Unsloth fast fine-tuning (2-5x faster, 70% less memory)
- GLM-4 coding agent
- Qwen2.5-Coder coding assistant
- RTX 50 series (Blackwell) optimizations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dataclasses import dataclass
from typing import Optional, List, Dict
import json

# Import new modules
from unsloth_integration import UnslothTrainer, SUPPORTED_MODELS, quick_finetune
from coding_agents.glm4_agent import GLM4CodingAgent
from coding_agents.qwen3_coder import Qwen3CoderAgent

@dataclass
class TrainingMode:
    """Training mode configuration"""
    STANDARD = "standard"  # Traditional fine-tuning
    UNSLOTH = "unsloth"    # Fast fine-tuning with Unsloth
    CODING_AGENT = "coding_agent"  # Load coding agent for assistance

class EnhancedTrainingGround:
    """
    Enhanced LLM Training Ground with cutting-edge features

    Features:
    1. Unsloth Fast Fine-tuning
       - 2-5x faster training
       - 70% less memory usage
       - Supports Llama, Mistral, Qwen, GLM-4, etc.

    2. Coding Agents
       - GLM-4: General coding assistant
       - Qwen2.5-Coder: Specialized code generation

    3. Hardware Optimizations
       - RTX 50 series (Blackwell) support
       - Automatic GPU detection and optimization
    """

    def __init__(self):
        self.mode = None
        self.trainer = None
        self.coding_agent = None

    def show_menu(self):
        """Display main menu"""
        print("\n" + "="*70)
        print(" " * 15 + "🚀 LightOS Training Ground v0.2.1")
        print("="*70)
        print("\nWhat would you like to do?\n")

        print("📚 TRAINING OPTIONS")
        print("  1. Quick Fine-tune with Unsloth (⚡ 2-5x faster)")
        print("  2. Custom Training Configuration")
        print("  3. Load Pre-trained Model")

        print("\n💻 CODING ASSISTANTS")
        print("  4. Start GLM-4 Coding Agent")
        print("  5. Start Qwen2.5-Coder Agent")
        print("  6. Compare Coding Agents")

        print("\n🔧 UTILITIES")
        print("  7. List Supported Models")
        print("  8. Check Hardware Capabilities")
        print("  9. View Training History")

        print("\n  0. Exit")
        print("="*70)

    def quick_finetune_wizard(self):
        """Interactive wizard for quick fine-tuning"""
        print("\n⚡ Unsloth Quick Fine-tune Wizard")
        print("="*70)

        # List models
        print("\nAvailable Models:")
        for i, (name, model_id) in enumerate(SUPPORTED_MODELS.items(), 1):
            print(f"  {i}. {name}")

        model_choice = input("\nSelect model (number or name): ").strip()

        # Parse choice
        if model_choice.isdigit():
            idx = int(model_choice) - 1
            model_name = list(SUPPORTED_MODELS.keys())[idx]
        else:
            model_name = model_choice

        # Dataset
        print("\nPopular Datasets:")
        print("  1. alpaca (yahma/alpaca-cleaned)")
        print("  2. code-alpaca (code instruction tuning)")
        print("  3. custom (enter your own)")

        dataset_choice = input("Select dataset: ").strip()

        if dataset_choice == "1":
            dataset_name = "yahma/alpaca-cleaned"
        elif dataset_choice == "2":
            dataset_name = "iamtarun/code_instructions_120k_alpaca"
        else:
            dataset_name = input("Enter dataset name (HuggingFace ID): ").strip()

        # Training steps
        max_steps = input("\nTraining steps [60]: ").strip()
        max_steps = int(max_steps) if max_steps else 60

        # Output directory
        output_dir = input("Output directory [./finetuned_model]: ").strip()
        output_dir = output_dir if output_dir else "./finetuned_model"

        # Confirm
        print("\n" + "="*70)
        print("Configuration Summary:")
        print(f"  Model: {model_name}")
        print(f"  Dataset: {dataset_name}")
        print(f"  Training Steps: {max_steps}")
        print(f"  Output: {output_dir}")
        print("="*70)

        confirm = input("\nStart training? [Y/n]: ").strip().lower()
        if confirm in ['', 'y', 'yes']:
            print("\n🚀 Starting training...")
            quick_finetune(model_name, dataset_name, output_dir, max_steps)
        else:
            print("Training cancelled")

    def start_coding_agent(self, agent_type: str):
        """Start a coding agent"""
        print(f"\n💻 Starting {agent_type} Coding Agent...")
        print("="*70)

        if agent_type == "glm4":
            agent = GLM4CodingAgent()
            agent.load_model()
            self.coding_agent = agent

            print("\n✓ GLM-4 Coding Agent Ready!")
            print("\nCapabilities:")
            print("  - Code generation and completion")
            print("  - Code explanation")
            print("  - Bug fixing")
            print("  - Documentation generation")

        elif agent_type == "qwen":
            print("\nSelect Model Size:")
            print("  1. 0.5B (fastest, lightweight)")
            print("  2. 1.5B (balanced)")
            print("  3. 7B (recommended)")
            print("  4. 14B (high quality)")
            print("  5. 32B (best quality)")

            size_choice = input("Choice [3]: ").strip()
            size_map = {"1": "0.5b", "2": "1.5b", "3": "7b", "4": "14b", "5": "32b"}
            size = size_map.get(size_choice, "7b")

            agent = Qwen3CoderAgent(model_size=size)
            agent.load_model()
            self.coding_agent = agent

            print(f"\n✓ Qwen2.5-Coder ({size}) Ready!")
            print("\nCapabilities:")
            print("  - Code completion")
            print("  - Function generation")
            print("  - Code refactoring")
            print("  - Test generation")

        # Interactive mode
        self.coding_agent_interactive()

    def coding_agent_interactive(self):
        """Interactive coding agent session"""
        print("\n" + "="*70)
        print("Interactive Coding Session")
        print("="*70)
        print("\nCommands:")
        print("  generate <description>  - Generate code")
        print("  explain <file.py>       - Explain code")
        print("  fix <file.py> <error>   - Fix bug")
        print("  complete <code>         - Complete code")
        print("  chat <message>          - Free-form chat")
        print("  exit                    - Exit session")
        print("="*70 + "\n")

        while True:
            try:
                user_input = input(">>> ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['exit', 'quit']:
                    print("Goodbye!")
                    break

                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""

                if command == "generate":
                    code = self.coding_agent.generate_code(args)
                    print("\n" + "─"*70)
                    print(code)
                    print("─"*70 + "\n")

                elif command == "explain":
                    with open(args, 'r') as f:
                        code = f.read()
                    explanation = self.coding_agent.explain_code(code)
                    print("\n" + "─"*70)
                    print(explanation)
                    print("─"*70 + "\n")

                elif command == "complete":
                    if hasattr(self.coding_agent, 'complete_code'):
                        completion = self.coding_agent.complete_code(args)
                        print("\n" + "─"*70)
                        print(args + completion)
                        print("─"*70 + "\n")
                    else:
                        print("Complete not supported by this agent")

                elif command == "chat":
                    response = self.coding_agent.chat(args)
                    print("\n" + "─"*70)
                    print(response)
                    print("─"*70 + "\n")

                else:
                    print(f"Unknown command: {command}")

            except KeyboardInterrupt:
                print("\n\nSession interrupted")
                break
            except Exception as e:
                print(f"Error: {e}")

    def compare_agents(self):
        """Compare coding agents side-by-side"""
        print("\n🔍 Coding Agent Comparison")
        print("="*70)

        print("\n┌─────────────────┬─────────────────┬──────────────────┐")
        print("│ Feature         │ GLM-4           │ Qwen2.5-Coder    │")
        print("├─────────────────┼─────────────────┼──────────────────┤")
        print("│ Model Size      │ 9B              │ 0.5B-32B         │")
        print("│ Languages       │ 40+             │ 40+              │")
        print("│ Code Quality    │ ★★★★☆           │ ★★★★★            │")
        print("│ Speed           │ ★★★☆☆           │ ★★★★★            │")
        print("│ Memory Usage    │ ~6GB (4-bit)    │ 1-20GB (varies)  │")
        print("│ Function Calling│ ✓               │ ✗                │")
        print("│ Best For        │ General coding  │ Code generation  │")
        print("└─────────────────┴─────────────────┴──────────────────┘")

        print("\n💡 Recommendations:")
        print("  - Use GLM-4 for: General coding tasks, chat-based coding")
        print("  - Use Qwen2.5-Coder for: Fast code generation, completion")
        print("  - Use Qwen 0.5B/1.5B for: Resource-constrained devices")
        print("  - Use Qwen 7B+ for: High-quality code generation")

    def check_hardware(self):
        """Check hardware capabilities"""
        print("\n🖥️  Hardware Capabilities")
        print("="*70)

        import torch

        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9

            print(f"✓ GPU: {gpu_name}")
            print(f"✓ VRAM: {gpu_memory:.1f} GB")

            # Check for Blackwell
            if "RTX 50" in gpu_name or "RTX 51" in gpu_name:
                print("✓ Blackwell GPU Detected! 🚀")
                print("\n  Optimizations Available:")
                print("  - Flash Attention 3")
                print("  - FP8 training")
                print("  - Larger batch sizes")
                print("  - Faster inference")
            elif "RTX 40" in gpu_name:
                print("✓ Ada Lovelace GPU")
                print("  - Flash Attention 2 available")
            elif "RTX 30" in gpu_name:
                print("✓ Ampere GPU")
                print("  - Good performance with Unsloth")

            # Recommendations
            print("\n📊 Recommended Settings:")
            if gpu_memory < 8:
                print("  - Use 4-bit quantization")
                print("  - Model size: Up to 7B parameters")
                print("  - Batch size: 1-2")
            elif gpu_memory < 16:
                print("  - Use 4-bit quantization")
                print("  - Model size: Up to 13B parameters")
                print("  - Batch size: 2-4")
            else:
                print("  - Can use full precision or 8-bit")
                print("  - Model size: Up to 70B parameters (with quantization)")
                print("  - Batch size: 4-8+")

        else:
            print("⚠️  No CUDA GPU detected")
            print("  Training will be slow on CPU")
            print("\n💡 Consider:")
            print("  - Using smaller models (0.5B-1.5B)")
            print("  - Cloud GPU instances")
            print("  - External GPU via eGPU")

    def list_models(self):
        """List all supported models"""
        print("\n📚 Supported Models")
        print("="*70)

        print("\n🔥 Unsloth Fast Fine-tuning:")
        for name, model_id in SUPPORTED_MODELS.items():
            print(f"  ✓ {name:20} ({model_id})")

        print("\n💻 Coding Agents:")
        print("  ✓ GLM-4-9B           (THUDM/glm-4-9b-chat)")
        print("  ✓ Qwen2.5-Coder-0.5B (Qwen/Qwen2.5-Coder-0.5B-Instruct)")
        print("  ✓ Qwen2.5-Coder-1.5B (Qwen/Qwen2.5-Coder-1.5B-Instruct)")
        print("  ✓ Qwen2.5-Coder-7B   (Qwen/Qwen2.5-Coder-7B-Instruct)")
        print("  ✓ Qwen2.5-Coder-14B  (Qwen/Qwen2.5-Coder-14B-Instruct)")
        print("  ✓ Qwen2.5-Coder-32B  (Qwen/Qwen2.5-Coder-32B-Instruct)")

    def run(self):
        """Main application loop"""
        while True:
            self.show_menu()

            try:
                choice = input("\nYour choice: ").strip()

                if choice == "0":
                    print("\n👋 Goodbye!")
                    break

                elif choice == "1":
                    self.quick_finetune_wizard()

                elif choice == "2":
                    print("Custom training configuration (coming soon)")

                elif choice == "3":
                    print("Load pre-trained model (coming soon)")

                elif choice == "4":
                    self.start_coding_agent("glm4")

                elif choice == "5":
                    self.start_coding_agent("qwen")

                elif choice == "6":
                    self.compare_agents()

                elif choice == "7":
                    self.list_models()

                elif choice == "8":
                    self.check_hardware()

                elif choice == "9":
                    print("Training history (coming soon)")

                else:
                    print("Invalid choice. Please try again.")

                input("\nPress Enter to continue...")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")
                input("Press Enter to continue...")

if __name__ == "__main__":
    app = EnhancedTrainingGround()
    app.run()
