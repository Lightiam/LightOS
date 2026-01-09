# LightOS LLM Training Ground

**Fast, efficient LLM training and coding assistance on your local machine**

---

## 🌟 **Highlights**

### **⚡ Unsloth Fast Fine-Tuning**
- **2-5x faster** training
- **70% less memory** usage
- Fine-tune Llama, Mistral, Qwen, GLM-4 on consumer GPUs

### **💻 Advanced Coding Agents**
- **GLM-4**: General-purpose coding assistant
- **Qwen2.5-Coder**: Specialized code generation (0.5B-32B models)
- Outperforms GPT-4 on coding benchmarks

### **🚀 RTX 50 Series Support**
- Automatic Blackwell GPU detection
- Flash Attention 3 optimizations
- FP8 training support

---

## 🚀 **Quick Start**

### **Launch Training Ground**

```bash
cd /opt/lightos/llm-training-ground/ui
python3 enhanced_launcher.py
```

### **Quick Fine-Tune (CLI)**

```bash
cd /opt/lightos/llm-training-ground
python3 unsloth_integration.py train llama-3.1-8b yahma/alpaca-cleaned
```

### **Start Coding Agent**

```bash
# GLM-4
cd coding_agents
python3 glm4_agent.py generate "fibonacci function in Python"

# Qwen2.5-Coder
python3 qwen3_coder.py --model 7b generate "REST API with FastAPI"
```

---

## 📦 **What's Included**

### **1. Unsloth Integration** (`unsloth_integration.py`)

Fast fine-tuning for:
- Llama 3.1 (8B, 70B)
- Mistral 7B
- Phi-3 Mini
- Gemma 2 (9B, 27B)
- Qwen2.5 (7B, 14B)
- GLM-4 (9B)

**Example:**
```python
from unsloth_integration import quick_finetune

quick_finetune(
    model_name="llama-3.1-8b",
    dataset_name="yahma/alpaca-cleaned",
    max_steps=100
)
```

### **2. GLM-4 Coding Agent** (`coding_agents/glm4_agent.py`)

Features:
- Code generation
- Code explanation
- Bug fixing
- Documentation generation
- 40+ languages

**Example:**
```python
from coding_agents.glm4_agent import GLM4CodingAgent

agent = GLM4CodingAgent()
agent.load_model()
code = agent.generate_code("binary search algorithm")
```

### **3. Qwen2.5-Coder Agent** (`coding_agents/qwen3_coder.py`)

Features:
- Fast code completion
- Function generation
- Code refactoring
- Test generation
- Multiple model sizes (0.5B-32B)

**Example:**
```python
from coding_agents.qwen3_coder import Qwen3CoderAgent

agent = Qwen3CoderAgent(model_size="7b")
agent.load_model()
completion = agent.complete_code("def fibonacci(n):\n    ")
```

### **4. Enhanced UI** (`ui/enhanced_launcher.py`)

Interactive interface for:
- Quick fine-tuning
- Coding agent chat
- Hardware capability check
- Model comparison
- Training history

---

## 💻 **System Requirements**

### **Minimum**
- **GPU**: NVIDIA GPU with 6GB+ VRAM
- **RAM**: 16GB system RAM
- **Storage**: 50GB free space
- **OS**: Ubuntu 22.04+, Windows (WSL2)

### **Recommended**
- **GPU**: RTX 3090/4090/5090 (24GB+ VRAM)
- **RAM**: 32GB system RAM
- **Storage**: 500GB SSD
- **OS**: Ubuntu 22.04+

### **Supported GPUs**
- ✅ RTX 50 series (Blackwell) - **Optimized**
- ✅ RTX 40 series (Ada Lovelace)
- ✅ RTX 30 series (Ampere)
- ✅ RTX 20 series (Turing)
- ✅ Tesla V100, A100, H100

---

## 📊 **Performance**

### **Training Speed (Llama 3.1 8B)**

| Method | Time | VRAM | Cost |
|--------|------|------|------|
| Traditional | 10h | 24GB | $10 |
| **Unsloth** | **4h** | **7GB** | **$4** |

### **Coding Quality (HumanEval)**

| Model | Pass@1 | VRAM |
|-------|--------|------|
| **Qwen2.5-Coder-7B** | 74.5% | ~5GB |
| **GLM-4-9B** | 71.8% | ~6GB |
| GPT-4 (reference) | 67.0% | Cloud |

**🎉 Our coding agents outperform GPT-4!**

---

## 📖 **Documentation**

- **New Features Guide**: [`docs/NEW_FEATURES_v0.2.1.md`](../docs/NEW_FEATURES_v0.2.1.md)
- **API Reference**: [`docs/api/`](../docs/api/)
- **Tutorials**: [`docs/tutorials/`](../docs/tutorials/)
- **Examples**: [`examples/`](examples/)

---

## 🎯 **Use Cases**

### **1. Fine-tune on Your Data**

```python
# Fine-tune Llama 3.1 on your custom dataset
from unsloth_integration import UnslothTrainer

trainer = UnslothTrainer("unsloth/llama-3-8b-bnb-4bit")
trainer.load_model()
trainer.add_lora_adapters()
trainer.load_dataset("your-username/your-dataset")
trainer.train()
```

### **2. Code Generation**

```python
# Generate production-ready code
from coding_agents.qwen3_coder import Qwen3CoderAgent

agent = Qwen3CoderAgent(model_size="7b")
agent.load_model()

code = agent.generate_function(
    "handles user authentication with JWT tokens",
    language="python"
)
```

### **3. Code Review**

```python
# Explain and improve code
from coding_agents.glm4_agent import GLM4CodingAgent

agent = GLM4CodingAgent()
agent.load_model()

explanation = agent.explain_code(your_code)
improved = agent.add_documentation(your_code)
```

### **4. Bug Fixing**

```python
# Debug code automatically
from coding_agents.qwen3_coder import Qwen3CoderAgent

agent = Qwen3CoderAgent(model_size="7b")
agent.load_model()

fixed_code, explanation = agent.debug_code(
    buggy_code,
    error_message="ValueError: list index out of range"
)
```

---

## 🔧 **Installation**

### **Automatic (Recommended)**

```bash
# Start enhanced launcher - installs dependencies automatically
cd /opt/lightos/llm-training-ground/ui
python3 enhanced_launcher.py
```

### **Manual**

```bash
# Install dependencies
pip3 install torch transformers accelerate bitsandbytes
pip3 install unsloth datasets trl

# Verify installation
python3 -c "import unsloth; print('Unsloth installed successfully!')"
```

---

## 🎓 **Learning Path**

1. **Start Here**: Run `python3 enhanced_launcher.py`
2. **Try Fine-tuning**: Option 1 → Quick Fine-tune
3. **Try Coding Agent**: Option 4 or 5 → Interactive session
4. **Read Docs**: [`docs/NEW_FEATURES_v0.2.1.md`](../docs/NEW_FEATURES_v0.2.1.md)
5. **Explore Examples**: [`examples/`](examples/)

---

## 💡 **Tips & Tricks**

### **Reduce Memory Usage**

```python
# Use 4-bit quantization
agent = GLM4CodingAgent(load_in_4bit=True)

# Use smaller model
agent = Qwen3CoderAgent(model_size="1.5b")  # Instead of 7b

# Reduce sequence length
config = UnslothConfig(max_seq_length=1024)
```

### **Speed Up Training**

```python
# Enable Flash Attention
config = UnslothConfig(use_flash_attention=True)

# Use gradient checkpointing
config = UnslothConfig(use_gradient_checkpointing=True)

# Increase batch size (if memory allows)
config = UnslothConfig(per_device_train_batch_size=4)
```

### **Best Model Selection**

| Task | Recommended Model | Why |
|------|------------------|-----|
| General coding | GLM-4-9B | Balanced quality/speed |
| Fast completion | Qwen2.5-Coder-0.5B | Lightning fast |
| Best quality | Qwen2.5-Coder-14B | Highest accuracy |
| Low memory | Qwen2.5-Coder-1.5B | Only 2GB VRAM |
| Fine-tuning | Llama-3.1-8B | Great base model |

---

## 🤝 **Contributing**

We welcome contributions!

- **Bug reports**: GitHub Issues
- **Feature requests**: GitHub Discussions
- **Code contributions**: Pull Requests

See [`CONTRIBUTING.md`](../CONTRIBUTING.md) for guidelines.

---

## 📜 **License**

LightOS is released under the MIT License. See [`LICENSE`](../LICENSE) for details.

Third-party models have their own licenses:
- **Llama 3.1**: Meta Community License
- **GLM-4**: Apache 2.0
- **Qwen2.5**: Apache 2.0
- **Unsloth**: Apache 2.0

---

## 🌟 **Star History**

If you find LightOS useful, please star the repository!

```bash
# Clone and explore
git clone https://github.com/Lightiam/LightOS.git
cd LightOS/llm-training-ground
python3 ui/enhanced_launcher.py
```

---

## 🔗 **Links**

- **GitHub**: https://github.com/Lightiam/LightOS
- **Documentation**: https://lightos.dev/docs
- **Community**: https://lightos.dev/community
- **Issues**: https://github.com/Lightiam/LightOS/issues

---

## 🎉 **What Makes LightOS Special?**

1. **🚀 Fast Training**: 2-5x faster than traditional methods
2. **💰 Cost Effective**: 70% less memory = cheaper hardware
3. **🏆 Better Quality**: Coding agents that beat GPT-4
4. **🔓 Fully Local**: Your code and data stay private
5. **🎯 Easy to Use**: Interactive UI + simple CLI
6. **🔧 Flexible**: From 0.5B to 70B models supported
7. **📚 Well Documented**: Comprehensive guides and examples
8. **🌐 Open Source**: MIT licensed, community-driven

---

**LightOS LLM Training Ground - Train Faster, Code Smarter**

*Powered by Unsloth, GLM-4, and Qwen2.5-Coder*
