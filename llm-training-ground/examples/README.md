# LightOS Examples

Practical, runnable examples for the LightOS LLM Training Ground.

## 📁 Directory Structure

```
examples/
├── basic/              # Beginner-friendly examples
│   ├── 01_quick_finetune.py
│   ├── 02_code_generation.py
│   └── 03_code_explanation.py
├── advanced/           # Advanced techniques
│   ├── 01_custom_dataset_training.py
│   └── 02_multi_gpu_training.py
└── use-cases/          # Real-world applications
    ├── 01_customer_support_bot.py
    └── 02_code_review_assistant.py
```

## 🚀 Getting Started

### Prerequisites

All examples require LightOS to be installed:

```bash
sudo ./simple-deploy.sh
```

### Running Examples

```bash
# Navigate to examples directory
cd /opt/lightos/llm-training-ground/examples

# Run any example
python3 basic/01_quick_finetune.py
```

---

## 📚 Basic Examples

Perfect for beginners and quick start.

### 1. Quick Fine-Tune (`basic/01_quick_finetune.py`)

**What it does:** Fine-tunes Llama 3.1 8B on the Alpaca dataset in just a few lines.

**Requirements:**
- 8GB+ VRAM (or 6GB with 4-bit)
- 15GB disk space
- ~30 minutes

**Run:**
```bash
python3 basic/01_quick_finetune.py
```

**Learn:**
- Basic fine-tuning workflow
- Using pre-made datasets
- Saving and loading models

---

### 2. Code Generation (`basic/02_code_generation.py`)

**What it does:** Uses Qwen2.5-Coder to generate code from natural language.

**Requirements:**
- 6GB+ VRAM for 7B (or 2GB for 1.5B)
- ~5 minutes

**Run:**
```bash
python3 basic/02_code_generation.py
```

**Examples generated:**
- Fibonacci function
- FastAPI REST API
- Unit tests

**Learn:**
- Code generation from descriptions
- Multi-language support
- Test generation

---

### 3. Code Explanation (`basic/03_code_explanation.py`)

**What it does:** Uses GLM-4 to explain complex code and find bugs.

**Requirements:**
- 8GB+ VRAM (or 6GB with 4-bit)
- ~5 minutes

**Run:**
```bash
python3 basic/03_code_explanation.py
```

**Learn:**
- Code explanation
- Bug detection
- Code documentation

---

## 🎓 Advanced Examples

For users ready to dive deeper.

### 1. Custom Dataset Training (`advanced/01_custom_dataset_training.py`)

**What it does:** Complete workflow for training on your own data with advanced configurations.

**Requirements:**
- 12GB+ VRAM (or 8GB optimized)
- Custom dataset
- ~1 hour

**Run:**
```bash
python3 advanced/01_custom_dataset_training.py
```

**Learn:**
- Dataset preparation
- Advanced LoRA configuration
- Hyperparameter tuning
- Model evaluation

**Customize:**
```python
# Modify these in the script:
config.lora_r = 32          # Increase for more capacity
config.max_steps = 500      # More training
config.learning_rate = 1e-4 # Adjust learning rate
```

---

### 2. Multi-GPU Training (`advanced/02_multi_gpu_training.py`)

**What it does:** Distributed training across multiple GPUs using DeepSpeed.

**Requirements:**
- 2+ GPUs with 12GB+ VRAM each
- DeepSpeed installed
- ~30 minutes

**Run:**
```bash
python3 advanced/02_multi_gpu_training.py
```

**Learn:**
- Multi-GPU setup
- DeepSpeed configuration
- ZeRO optimization
- Performance monitoring

**Performance gain:**
- 2 GPUs: ~1.8x faster
- 4 GPUs: ~3.5x faster
- 8 GPUs: ~6.5x faster

---

## 💼 Use Case Examples

Real-world applications you can deploy.

### 1. Customer Support Bot (`use-cases/01_customer_support_bot.py`)

**What it does:** Builds and deploys a customer support chatbot.

**Requirements:**
- 8GB+ VRAM
- Customer data (or use provided examples)
- ~1 hour

**Run:**
```bash
python3 use-cases/01_customer_support_bot.py
```

**Features:**
- Fine-tuned on support conversations
- Interactive chat interface
- FastAPI deployment ready

**Deploy:**
```bash
# After running the example:
uvicorn api:app --host 0.0.0.0 --port 8000
```

**Customize:**
- Add your own support conversations
- Adjust tone and style
- Add multi-language support

---

### 2. Code Review Assistant (`use-cases/02_code_review_assistant.py`)

**What it does:** Automated code review system for quality, security, and best practices.

**Requirements:**
- 8GB+ VRAM
- Code to review
- ~10 minutes

**Run:**
```bash
python3 use-cases/02_code_review_assistant.py
```

**Reviews:**
- Bug detection
- Security vulnerabilities
- Code style
- Best practices
- Quality scoring

**Output:**
- Markdown report
- Per-file scores
- Actionable suggestions

**Integrate:**
```bash
# Add to CI/CD:
python3 code_review_assistant.py --dir ./src --output review.md
```

---

## 🎯 Quick Reference

### By Goal

**I want to fine-tune a model:**
→ `basic/01_quick_finetune.py`
→ `advanced/01_custom_dataset_training.py`

**I want to generate code:**
→ `basic/02_code_generation.py`

**I want to understand code:**
→ `basic/03_code_explanation.py`

**I want to build a chatbot:**
→ `use-cases/01_customer_support_bot.py`

**I want automated code review:**
→ `use-cases/02_code_review_assistant.py`

**I have multiple GPUs:**
→ `advanced/02_multi_gpu_training.py`

---

### By Hardware

**6GB VRAM or less:**
- Use model size: 1.5B
- Enable 4-bit quantization
- Examples: 02_code_generation.py (with 1.5B)

**8-12GB VRAM:**
- Use model size: 7B
- Enable 4-bit quantization
- All basic examples

**16GB+ VRAM:**
- Use model size: 7B-14B
- All examples
- No quantization needed

**24GB+ VRAM (3090/4090):**
- Use model size: up to 32B
- All examples
- High-quality results

**Multi-GPU:**
- Use advanced/02_multi_gpu_training.py
- Larger models (70B+)
- Faster training

---

## 📖 Documentation

- **Main README**: `/opt/lightos/README.md`
- **Features Guide**: `/opt/lightos/docs/NEW_FEATURES_v0.2.1.md`
- **API Reference**: `/opt/lightos/llm-training-ground/README.md`
- **Launcher Guide**: `/opt/lightos/bin/README.md`

---

## 🛠️ Customization Tips

### Adjust Model Size

```python
# In any example, change:
agent = Qwen3CoderAgent(model_size="7b")  # Original
agent = Qwen3CoderAgent(model_size="1.5b")  # Smaller, faster
```

### Enable 4-bit Quantization

```python
# Reduces memory by ~70%
agent = GLM4CodingAgent(load_in_4bit=True)
```

### Adjust Training Steps

```python
# More steps = better quality, more time
quick_finetune(
    model_name="llama-3.1-8b",
    dataset_name="alpaca",
    max_steps=500  # Increase from 100
)
```

### Change Learning Rate

```python
config = UnslothConfig(
    learning_rate=1e-4  # Lower = more stable
    # or
    learning_rate=5e-4  # Higher = faster convergence
)
```

---

## 🐛 Troubleshooting

### Out of Memory

```python
# Use smaller model
agent = Qwen3CoderAgent(model_size="1.5b")

# Enable 4-bit
agent = GLM4CodingAgent(load_in_4bit=True)

# Reduce batch size
config.per_device_train_batch_size = 1
```

### Slow Performance

```bash
# Check GPU is being used
nvidia-smi

# Enable Flash Attention
config.use_flash_attention = True

# Use smaller sequence length
config.max_seq_length = 1024
```

### Import Errors

```bash
# Activate venv
source /opt/lightos/venv/bin/activate

# Install missing packages
pip install transformers torch accelerate
```

---

## 🤝 Contributing

Want to add an example?

1. Create your example script
2. Add clear docstring
3. Test it works
4. Submit PR to https://github.com/Lightiam/LightOS

---

## 📜 License

All examples are MIT licensed. Feel free to use, modify, and distribute.

---

## 🆘 Support

- **Issues**: https://github.com/Lightiam/LightOS/issues
- **Discussions**: https://github.com/Lightiam/LightOS/discussions
- **Docs**: https://lightos.dev/docs

---

**Happy coding with LightOS! 🚀**
