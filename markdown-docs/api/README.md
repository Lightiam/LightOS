# LightOS API Reference

Complete API documentation for LightOS LLM Training Ground.

## Quick Links

- [Unsloth Integration](#unsloth-integration) - Fast fine-tuning
- [GLM-4 Coding Agent](#glm-4-coding-agent) - General coding assistant
- [Qwen2.5-Coder Agent](#qwen25-coder-agent) - Specialized code generation
- [CLI Commands](#cli-commands) - Command-line interface

---

## Unsloth Integration

Fast LLM fine-tuning (2-5x faster, 70% less memory).

### Quick Fine-Tune Function

```python
from unsloth_integration import quick_finetune

quick_finetune(
    model_name: str,
    dataset_name: str,
    output_dir: str = "./finetuned_model",
    max_steps: int = 60
)
```

**Parameters:**
- `model_name` (str): Model identifier
  - `"llama-3.1-8b"` - Llama 3.1 8B
  - `"mistral-7b"` - Mistral 7B
  - `"qwen-7b"` - Qwen 2.5 7B
  - `"glm-4-9b"` - GLM-4 9B
  - `"gemma-7b"` - Gemma 7B

- `dataset_name` (str): Dataset path or HuggingFace dataset
  - `"yahma/alpaca-cleaned"` - Alpaca dataset
  - `"path/to/your/data.json"` - Custom dataset

- `output_dir` (str, optional): Where to save the model
  - Default: `"./finetuned_model"`

- `max_steps` (int, optional): Training steps
  - Default: 60
  - Recommended: 100-500 for good quality

**Returns:**
- None (saves model to `output_dir`)

**Example:**
```python
from unsloth_integration import quick_finetune

# Fine-tune Llama 3.1 on Alpaca
quick_finetune(
    model_name="llama-3.1-8b",
    dataset_name="yahma/alpaca-cleaned",
    output_dir="./my_model",
    max_steps=100
)
```

---

### UnslothConfig Class

Configuration for advanced fine-tuning.

```python
from unsloth_integration import UnslothConfig

config = UnslothConfig(
    model_name: str = "unsloth/llama-3-8b-bnb-4bit",
    max_seq_length: int = 2048,
    load_in_4bit: bool = True,

    # LoRA parameters
    lora_r: int = 16,
    lora_alpha: int = 16,
    lora_dropout: float = 0.0,

    # Training parameters
    per_device_train_batch_size: int = 2,
    gradient_accumulation_steps: int = 4,
    warmup_steps: int = 5,
    max_steps: int = 60,
    learning_rate: float = 2e-4,

    # Optimizations
    use_gradient_checkpointing: bool = True,
    use_flash_attention: bool = True,
    fp16: bool = True,

    # Logging
    logging_steps: int = 1,
    save_steps: int = 50,
)
```

**Parameters:**

**Model Configuration:**
- `model_name` (str): HuggingFace model path
- `max_seq_length` (int): Maximum sequence length (default: 2048)
- `load_in_4bit` (bool): Use 4-bit quantization (default: True)

**LoRA Configuration:**
- `lora_r` (int): LoRA rank (default: 16)
  - Higher = more capacity, slower
  - Typical: 8, 16, 32
- `lora_alpha` (int): LoRA alpha (default: 16)
  - Usually same as `lora_r`
- `lora_dropout` (float): Dropout rate (default: 0.0)
  - Typical: 0.0, 0.05, 0.1

**Training Configuration:**
- `per_device_train_batch_size` (int): Batch size per GPU (default: 2)
- `gradient_accumulation_steps` (int): Gradient accumulation (default: 4)
- `warmup_steps` (int): Learning rate warmup (default: 5)
- `max_steps` (int): Total training steps (default: 60)
- `learning_rate` (float): Learning rate (default: 2e-4)

**Optimization:**
- `use_gradient_checkpointing` (bool): Save memory (default: True)
- `use_flash_attention` (bool): Faster attention (default: True)
- `fp16` (bool): Mixed precision training (default: True)

**Example:**
```python
from unsloth_integration import UnslothConfig, UnslothTrainer

# Create custom configuration
config = UnslothConfig(
    model_name="unsloth/llama-3-8b-bnb-4bit",
    max_seq_length=2048,
    lora_r=32,  # Higher capacity
    max_steps=200,  # More training
    learning_rate=1e-4  # Lower learning rate
)

# Use with trainer
trainer = UnslothTrainer(config.model_name, config)
trainer.load_model()
trainer.add_lora_adapters()
trainer.load_dataset("yahma/alpaca-cleaned")
trainer.train("./output")
```

---

### UnslothTrainer Class

Advanced fine-tuning with full control.

```python
from unsloth_integration import UnslothTrainer, UnslothConfig

trainer = UnslothTrainer(
    model_name: str,
    config: UnslothConfig = None
)
```

**Methods:**

#### `load_model()`
Load the model and tokenizer.

```python
trainer.load_model()
```

#### `add_lora_adapters()`
Add LoRA adapters to the model.

```python
trainer.add_lora_adapters()
```

#### `load_dataset(dataset_name: str)`
Load and prepare dataset.

```python
trainer.load_dataset("yahma/alpaca-cleaned")
# or
trainer.load_dataset("./my_data.json")
```

#### `train(output_dir: str = "./output")`
Start training.

```python
trainer.train("./my_finetuned_model")
```

#### `save_model(output_dir: str)`
Save the fine-tuned model.

```python
trainer.save_model("./my_model")
```

**Complete Example:**
```python
from unsloth_integration import UnslothTrainer, UnslothConfig

# Configure
config = UnslothConfig(
    model_name="unsloth/llama-3-8b-bnb-4bit",
    max_steps=100,
    learning_rate=2e-4
)

# Initialize
trainer = UnslothTrainer(config.model_name, config)

# Load model
trainer.load_model()

# Add LoRA
trainer.add_lora_adapters()

# Load data
trainer.load_dataset("yahma/alpaca-cleaned")

# Train
trainer.train("./output")

# Save
trainer.save_model("./my_finetuned_model")
```

---

## GLM-4 Coding Agent

General-purpose coding assistant (71.8% HumanEval).

### GLM4CodingAgent Class

```python
from coding_agents.glm4_agent import GLM4CodingAgent

agent = GLM4CodingAgent(
    model_name: str = "THUDM/glm-4-9b-chat",
    load_in_4bit: bool = True
)
```

**Parameters:**
- `model_name` (str): Model path (default: "THUDM/glm-4-9b-chat")
- `load_in_4bit` (bool): Use 4-bit quantization (default: True)

**Methods:**

#### `load_model()`
Load the model.

```python
agent.load_model()
```

#### `generate_code(prompt: str, language: str = "python", max_length: int = 2048) → str`
Generate code from description.

```python
code = agent.generate_code(
    "create a binary search function",
    language="python"
)
```

#### `explain_code(code: str, detail_level: str = "medium") → str`
Explain code.

```python
explanation = agent.explain_code(
    "def fib(n): return n if n <= 1 else fib(n-1) + fib(n-2)",
    detail_level="detailed"  # or "beginner", "medium", "expert"
)
```

#### `fix_bug(code: str) → str`
Find and fix bugs.

```python
fixed_code = agent.fix_bug("""
def avg(nums):
    return sum(nums) / len(nums)

print(avg([]))  # Will crash!
""")
```

#### `add_documentation(code: str, style: str = "google") → str`
Add documentation to code.

```python
documented = agent.add_documentation(
    "def add(a, b): return a + b",
    style="google"  # or "numpy", "sphinx"
)
```

**Complete Example:**
```python
from coding_agents.glm4_agent import GLM4CodingAgent

# Initialize
agent = GLM4CodingAgent(load_in_4bit=True)
agent.load_model()

# Generate code
code = agent.generate_code("REST API with FastAPI")

# Explain it
explanation = agent.explain_code(code)

# Add docs
documented = agent.add_documentation(code)

print(documented)
```

---

## Qwen2.5-Coder Agent

Specialized code generation (74.5% HumanEval, beats GPT-4).

### Qwen3CoderAgent Class

```python
from coding_agents.qwen3_coder import Qwen3CoderAgent

agent = Qwen3CoderAgent(
    model_size: str = "7b",
    load_in_4bit: bool = True
)
```

**Parameters:**
- `model_size` (str): Model size
  - `"0.5b"` - 0.5B parameters (lightweight)
  - `"1.5b"` - 1.5B parameters (balanced)
  - `"7b"` - 7B parameters (recommended)
  - `"14b"` - 14B parameters (high quality)
  - `"32b"` - 32B parameters (best quality)
- `load_in_4bit` (bool): Use 4-bit quantization

**Methods:**

#### `load_model()`
Load the model.

```python
agent.load_model()
```

#### `generate_code(prompt: str, language: str = "python", max_tokens: int = 1024) → str`
Generate code from description.

```python
code = agent.generate_code(
    "implement quicksort algorithm",
    language="python"
)
```

#### `complete_code(code_prefix: str, max_tokens: int = 512) → str`
Complete partial code.

```python
completion = agent.complete_code("""
def fibonacci(n):
    if n <= 1:
        return n
    # Complete this function
""")
```

#### `generate_function(description: str, language: str = "python") → str`
Generate a specific function.

```python
func = agent.generate_function(
    "validate email address with regex",
    language="python"
)
```

#### `refactor_code(code: str) → str`
Refactor code for better quality.

```python
refactored = agent.refactor_code("""
def f(x):
    if x > 0:
        return True
    else:
        return False
""")
```

#### `debug_code(code: str) → str`
Find and explain bugs.

```python
debug_info = agent.debug_code("""
def divide(a, b):
    return a / b  # Potential division by zero!

print(divide(10, 0))
""")
```

#### `generate_tests(code: str, framework: str = "pytest") → str`
Generate unit tests.

```python
tests = agent.generate_tests(
    "def add(a, b): return a + b",
    framework="pytest"  # or "unittest"
)
```

**Complete Example:**
```python
from coding_agents.qwen3_coder import Qwen3CoderAgent

# Initialize with 7B model
agent = Qwen3CoderAgent(model_size="7b", load_in_4bit=True)
agent.load_model()

# Generate a function
code = agent.generate_function("binary search algorithm")

# Refactor it
refactored = agent.refactor_code(code)

# Generate tests
tests = agent.generate_tests(refactored)

# Debug if needed
debug_info = agent.debug_code(refactored)

print("Code:", refactored)
print("Tests:", tests)
```

---

## CLI Commands

System-wide command-line tools.

### `lightos`

Main interactive launcher.

```bash
lightos
```

Launches the training ground UI with menu options.

---

### `lightos-train`

Fine-tuning command.

```bash
lightos-train <command> [options]
```

**Commands:**
- `list` - List available models
- `train <model> <dataset>` - Start fine-tuning
- `interactive` - Interactive wizard

**Options:**
- `--max-steps N` - Training steps (default: 60)
- `--batch-size N` - Batch size (default: 2)
- `--learning-rate LR` - Learning rate (default: 2e-4)
- `--output-dir PATH` - Output directory
- `--4bit` - Use 4-bit quantization
- `--flash-attention` - Enable Flash Attention

**Examples:**
```bash
# List models
lightos-train list

# Quick train
lightos-train train llama-3.1-8b alpaca

# Custom options
lightos-train train mistral-7b my_data.json \
  --max-steps 200 \
  --4bit \
  --output-dir ./my_model

# Interactive mode
lightos-train interactive
```

---

### `lightos-code`

Coding assistant command.

```bash
lightos-code [agent] <command> [args]
```

**Agents:**
- `glm4` - GLM-4 coding assistant
- `qwen` - Qwen2.5-Coder

**Commands:**
- `generate <description>` - Generate code
- `complete <file>` - Complete code
- `explain <file>` - Explain code
- `fix <file>` - Fix bugs
- `refactor <file>` - Refactor code
- `test <file>` - Generate tests
- `interactive` - Interactive REPL

**Options:**
- `--model-size SIZE` - Model size (qwen only: 0.5b, 1.5b, 7b, 14b, 32b)
- `--language LANG` - Programming language
- `--4bit` - Use 4-bit quantization

**Examples:**
```bash
# Generate code
lightos-code qwen generate "fibonacci function"

# Explain code
lightos-code glm4 explain my_script.py

# Fix bugs
lightos-code qwen fix buggy_code.py

# Generate tests
lightos-code qwen test calculator.py

# Interactive mode
lightos-code qwen interactive

# Use smaller model
lightos-code qwen generate "hello world" --model-size 1.5b
```

---

## Dataset Format

For custom datasets, use this format:

```json
[
  {
    "instruction": "Task description",
    "input": "Optional input context",
    "output": "Expected output"
  },
  {
    "instruction": "Another task",
    "input": "",
    "output": "Another output"
  }
]
```

**Example:**
```json
[
  {
    "instruction": "Write a function to calculate fibonacci numbers",
    "input": "",
    "output": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)"
  },
  {
    "instruction": "Explain this code",
    "input": "def add(a, b): return a + b",
    "output": "This is a simple function that takes two parameters and returns their sum."
  }
]
```

---

## Error Handling

All API functions may raise:

- `ValueError` - Invalid parameters
- `FileNotFoundError` - Dataset/model not found
- `RuntimeError` - GPU/memory errors
- `ImportError` - Missing dependencies

**Example:**
```python
try:
    agent = Qwen3CoderAgent(model_size="7b")
    agent.load_model()
    code = agent.generate_code("my prompt")
except RuntimeError as e:
    print(f"GPU error: {e}")
    # Try CPU mode or smaller model
    agent = Qwen3CoderAgent(model_size="1.5b")
except ImportError as e:
    print(f"Missing dependency: {e}")
    # Install: pip install unsloth transformers
```

---

## Performance Tips

### Memory Optimization

```python
# Use 4-bit quantization
agent = GLM4CodingAgent(load_in_4bit=True)

# Use smaller models
agent = Qwen3CoderAgent(model_size="1.5b")

# Reduce batch size
config = UnslothConfig(per_device_train_batch_size=1)
```

### Speed Optimization

```python
# Enable Flash Attention
config = UnslothConfig(use_flash_attention=True)

# Reduce sequence length
config = UnslothConfig(max_seq_length=1024)

# Use GPU
# Ensure CUDA is available: torch.cuda.is_available()
```

---

## Support

- **GitHub**: https://github.com/Lightiam/LightOS
- **Issues**: https://github.com/Lightiam/LightOS/issues
- **Examples**: `/opt/lightos/llm-training-ground/examples/`
- **Docs**: https://lightos.dev/docs
