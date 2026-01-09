# Quick Start Guide

Get started with LightOS in 5 minutes.

## Installation

```bash
git clone https://github.com/Lightiam/LightOS.git
cd LightOS
sudo ./simple-deploy.sh
```

Wait 5-10 minutes for installation to complete.

## Your First Commands

### 1. Launch Interactive UI

```bash
lightos
```

You'll see a menu:
```
📚 TRAINING OPTIONS
  1. Quick Fine-tune with Unsloth (⚡ 2-5x faster)
  2. Custom Training Configuration

💻 CODING ASSISTANTS
  4. Start GLM-4 Coding Agent
  5. Start Qwen2.5-Coder Agent

🔧 SYSTEM
  8. Check Hardware Capabilities
```

### 2. Generate Code

```bash
lightos-code qwen generate "fibonacci function in python"
```

Output:
```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

### 3. Fine-Tune a Model

```bash
lightos-train train llama-3.1-8b alpaca
```

This will:
- Download Llama 3.1 8B model
- Load Alpaca dataset
- Fine-tune for 60 steps (~30 minutes)
- Save to `./models/llama-3.1-alpaca`

## Common Use Cases

### Generate a REST API

```bash
lightos-code qwen generate "FastAPI REST API with JWT authentication and PostgreSQL database"
```

### Explain Complex Code

Save this to `complex.py`:
```python
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)
```

Then:
```bash
lightos-code glm4 explain complex.py
```

### Build a Chatbot

```python
from llm_training_ground.unsloth_integration import quick_finetune

# Prepare your conversation data
# See examples/use-cases/01_customer_support_bot.py

quick_finetune(
    model_name="llama-3.1-8b",
    dataset_name="your_conversations.json",
    max_steps=200
)
```

## What's Next?

### Learn More

- **[Fine-Tuning Guide](../guides/fine-tuning.md)** - Deep dive into training
- **[Coding Agents](../guides/coding-agents.md)** - All coding features
- **[API Reference](../api/README.md)** - Complete API docs

### Run Examples

```bash
cd /opt/lightos/llm-training-ground/examples

# Basic: Quick fine-tune
python3 basic/01_quick_finetune.py

# Generate code
python3 basic/02_code_generation.py

# Build a chatbot
python3 use-cases/01_customer_support_bot.py
```

### Join Community

- **GitHub**: https://github.com/Lightiam/LightOS
- **Discussions**: https://github.com/Lightiam/LightOS/discussions
- **Issues**: https://github.com/Lightiam/LightOS/issues

## Performance Tips

### For Limited Memory (8GB VRAM)

```bash
# Use smaller models
lightos-code qwen generate "code" --model-size 1.5b

# Enable 4-bit quantization
lightos-train train llama-3.1-8b alpaca --4bit
```

### For Speed

```bash
# Use Flash Attention
lightos-train train llama-3.1-8b alpaca --flash-attention

# Reduce sequence length
lightos-train train llama-3.1-8b alpaca --max-seq-length 1024
```

### For Best Quality

```bash
# Use larger models
lightos-code qwen generate "code" --model-size 14b

# Train for more steps
lightos-train train llama-3.1-8b alpaca --max-steps 500
```

## Troubleshooting

### Out of Memory

- Use smaller model sizes (1.5B instead of 7B)
- Enable 4-bit quantization (`--4bit`)
- Reduce batch size (`--batch-size 1`)

### Slow Performance

- Check GPU is being used: `nvidia-smi`
- Enable Flash Attention (`--flash-attention`)
- Use GPU instead of CPU

### Command Not Found

```bash
# Ensure installation completed
which lightos

# If not found, re-run installer
cd ~/LightOS
sudo ./simple-deploy.sh
```

## Quick Reference

### Commands

```bash
lightos                    # Interactive UI
lightos-train             # Training wizard
lightos-code              # Coding assistant

# Training
lightos-train train <model> <dataset>
lightos-train list

# Coding
lightos-code qwen generate <description>
lightos-code glm4 explain <file>
lightos-code qwen fix <file>
```

### Python API

```python
# Fine-tuning
from unsloth_integration import quick_finetune
quick_finetune("llama-3.1-8b", "alpaca")

# Code generation
from coding_agents.qwen3_coder import Qwen3CoderAgent
agent = Qwen3CoderAgent()
agent.load_model()
code = agent.generate_code("your prompt")

# Code explanation
from coding_agents.glm4_agent import GLM4CodingAgent
agent = GLM4CodingAgent()
agent.load_model()
explanation = agent.explain_code("your code")
```

## Resources

- **Documentation**: All guides in `/opt/lightos/docs/`
- **Examples**: Runnable code in `/opt/lightos/llm-training-ground/examples/`
- **Quick Start**: `/opt/lightos/QUICKSTART.txt`
- **GitHub**: https://github.com/Lightiam/LightOS

---

**Happy coding with LightOS! 🚀**
