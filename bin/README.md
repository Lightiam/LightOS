# LightOS Launcher Scripts

This directory contains the launcher scripts that will be installed to `/usr/local/bin/` during installation.

## Scripts

### 1. `lightos` - Main Launcher
Interactive UI for the LLM Training Ground

**Usage:**
```bash
lightos
```

**What it does:**
- Starts the enhanced training ground UI
- Provides menu-driven access to all features
- Allows quick fine-tuning, coding agents, and system checks

---

### 2. `lightos-code` - Coding Agent Launcher
AI-assisted coding with GLM-4 or Qwen2.5-Coder

**Usage:**
```bash
lightos-code [glm4|qwen] <command> <args>
```

**Agents:**
- **glm4** - GLM-4 9B (71.8% HumanEval pass rate)
- **qwen** - Qwen2.5-Coder (74.5% HumanEval, beats GPT-4)

**Commands:**
- `generate <description>` - Generate code from natural language
- `complete <file>` - Complete partial code
- `explain <file>` - Explain existing code
- `fix <file>` - Find and fix bugs
- `refactor <file>` - Refactor code
- `test <file>` - Generate unit tests
- `interactive` - Start interactive REPL

**Examples:**
```bash
# Generate code
lightos-code qwen generate "REST API with FastAPI and JWT auth"

# Explain code
lightos-code glm4 explain my_app.py

# Complete code
lightos-code qwen complete unfinished.py

# Fix bugs
lightos-code glm4 fix buggy_script.py

# Generate tests
lightos-code qwen test calculator.py

# Interactive mode
lightos-code qwen interactive
```

**Options:**
- `--model-size SIZE` - Qwen model size (0.5b, 1.5b, 7b, 14b, 32b)
- `--language LANG` - Target programming language
- `--4bit` - Use 4-bit quantization (saves memory)

---

### 3. `lightos-train` - Fast Training Launcher
Fine-tune LLMs with Unsloth (2-5x faster, 70% less memory)

**Usage:**
```bash
lightos-train <command> [options]
```

**Commands:**
- `list` - List available models
- `train <model> <dataset>` - Start fine-tuning
- `interactive` - Interactive training wizard
- `benchmark` - Performance benchmarks

**Supported Models:**
- `llama-3.1-8b` - Meta Llama 3.1 (8B parameters)
- `mistral-7b` - Mistral 7B
- `qwen-7b` - Qwen 2.5 (7B parameters)
- `glm-4-9b` - GLM-4 (9B parameters)
- `gemma-7b` - Google Gemma (7B parameters)

**Datasets:**
- `alpaca` - Alpaca instruction following
- `code-alpaca` - Code instruction dataset
- `<path/to/file.json>` - Your custom dataset

**Examples:**
```bash
# List available models
lightos-train list

# Quick fine-tune Llama 3.1
lightos-train train llama-3.1-8b alpaca

# Custom dataset with options
lightos-train train mistral-7b my_data.json \
  --max-steps 100 \
  --batch-size 4 \
  --4bit

# Interactive wizard
lightos-train interactive
```

**Options:**
- `--max-steps N` - Training steps (default: 60)
- `--batch-size N` - Batch size (default: 2)
- `--learning-rate LR` - Learning rate (default: 2e-4)
- `--output-dir PATH` - Save location
- `--4bit` - 4-bit quantization
- `--flash-attention` - Enable Flash Attention

**Performance:**
| Method | Time | VRAM | Cost |
|--------|------|------|------|
| Traditional | 10h | 24GB | $10 |
| **LightOS** | **4h** | **7GB** | **$4** |

---

## Installation

These scripts are automatically installed to `/usr/local/bin/` when you run:

```bash
sudo ./simple-deploy.sh
```

After installation, you can use them from anywhere:

```bash
lightos
lightos-code qwen generate "hello world"
lightos-train list
```

---

## Manual Installation

If you want to install manually:

```bash
# Copy to system bin
sudo cp bin/lightos /usr/local/bin/
sudo cp bin/lightos-code /usr/local/bin/
sudo cp bin/lightos-train /usr/local/bin/

# Make executable
sudo chmod +x /usr/local/bin/lightos*

# Verify
which lightos
lightos --help
```

---

## Requirements

All scripts require:
- Python 3.8+
- Virtual environment at `/opt/lightos/venv/`
- LightOS components installed to `/opt/lightos/`

These are automatically set up by `simple-deploy.sh`.

---

## Troubleshooting

### Command not found
```bash
# Check if installed
which lightos

# If not found, run:
sudo ./simple-deploy.sh
```

### Permission denied
```bash
# Make executable
sudo chmod +x /usr/local/bin/lightos*
```

### Import errors
```bash
# Activate venv and check
source /opt/lightos/venv/bin/activate
python3 -c "import torch, transformers, unsloth"
```

### Out of memory
Use smaller models or 4-bit quantization:
```bash
lightos-code qwen generate "code" --model-size 1.5b --4bit
lightos-train train llama-3.1-8b alpaca --4bit --batch-size 1
```

---

## Quick Reference

**Code Generation:**
```bash
lightos-code qwen generate "your description"
```

**Code Explanation:**
```bash
lightos-code glm4 explain your_file.py
```

**Fine-Tuning:**
```bash
lightos-train train llama-3.1-8b alpaca
```

**Interactive Mode:**
```bash
lightos
```

---

## Examples by Use Case

### 1. Generate a Python Function
```bash
lightos-code qwen generate "function that validates email addresses with regex"
```

### 2. Debug Code
```bash
lightos-code glm4 fix broken_script.py
```

### 3. Fine-Tune for Your Domain
```bash
# Prepare dataset (JSONL format)
cat > my_data.jsonl << EOF
{"instruction": "What is LightOS?", "output": "LightOS is a neural compute engine..."}
{"instruction": "How to install?", "output": "Run sudo ./simple-deploy.sh"}
EOF

# Fine-tune
lightos-train train llama-3.1-8b my_data.jsonl --max-steps 200
```

### 4. Generate Tests
```bash
lightos-code qwen test my_app.py
```

### 5. Refactor Legacy Code
```bash
lightos-code glm4 refactor legacy_code.py
```

---

## Performance Tips

1. **Use appropriate model size:**
   - Development/testing: 0.5B-1.5B
   - Production quality: 7B-14B
   - Best results: 32B+ (requires GPU)

2. **Enable optimizations:**
   - Always use `--4bit` for memory efficiency
   - Use `--flash-attention` for speed
   - Reduce `--batch-size` if OOM

3. **GPU vs CPU:**
   - GPU: 10-100x faster, required for 7B+ models
   - CPU: Works for small models (0.5B-1.5B)

4. **Check resources:**
   ```bash
   # GPU memory
   nvidia-smi

   # System memory
   free -h

   # Disk space
   df -h /opt/lightos
   ```

---

## See Also

- [Main README](../README.md)
- [New Features Guide](../docs/NEW_FEATURES_v0.2.1.md)
- [LLM Training Ground](../llm-training-ground/README.md)
- [Quick Start Guide](../docs/QUICKSTART.md)
