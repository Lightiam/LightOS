# Installation Guide

Get LightOS running on your system in minutes.

## System Requirements

### Minimum
- **OS**: Ubuntu 22.04+, Windows 10/11 (WSL2), macOS
- **RAM**: 8GB system RAM
- **Storage**: 20GB free space
- **GPU**: Optional (CPU mode available)

### Recommended
- **OS**: Ubuntu 22.04 LTS
- **RAM**: 16GB+ system RAM
- **Storage**: 100GB SSD
- **GPU**: NVIDIA GPU with 6GB+ VRAM (RTX 3060+)

### Optimal
- **OS**: Ubuntu 22.04 LTS
- **RAM**: 32GB+ system RAM
- **Storage**: 500GB NVMe SSD
- **GPU**: RTX 3090/4090/5090 (24GB+ VRAM)

## Installation Methods

### Method 1: Simple Install (Recommended)

For Ubuntu, WSL2, or any Linux:

```bash
# 1. Clone repository
git clone https://github.com/Lightiam/LightOS.git
cd LightOS

# 2. Run installer (takes 5-10 minutes)
sudo ./simple-deploy.sh

# 3. Launch
lightos
```

**What it installs:**
- Python virtual environment at `/opt/lightos/venv`
- PyTorch with GPU support
- Transformers, Unsloth, Accelerate
- LLM training ground
- Coding agents (GLM-4, Qwen2.5-Coder)
- System-wide launcher commands

### Method 2: Docker

Requires: Docker, Docker Compose, NVIDIA GPU (optional)

```bash
# 1. Clone repository
git clone https://github.com/Lightiam/LightOS.git
cd LightOS

# 2. Start container
docker-compose up

# 3. Access at http://localhost:8080
```

**Features:**
- Pre-configured environment
- GPU support (NVIDIA)
- Persistent volumes
- Easy updates

### Method 3: VirtualBox VM

See [VirtualBox Guide](../guides/virtualbox.md)

### Method 4: Bootable ISO

See [Edge Deployment Guide](../guides/edge-deployment.md)

## Post-Installation

### Verify Installation

```bash
# Check commands are available
which lightos
which lightos-train
which lightos-code

# Test Python environment
source /opt/lightos/venv/bin/activate
python3 -c "import torch; print(torch.__version__)"
python3 -c "import transformers; print(transformers.__version__)"
```

### Check GPU

```bash
# NVIDIA GPU
nvidia-smi

# Check CUDA in Python
python3 -c "import torch; print(torch.cuda.is_available())"
python3 -c "import torch; print(torch.cuda.get_device_name(0))"
```

### Launch LightOS

```bash
# Interactive UI
lightos

# Training interface
lightos-train

# Coding agent
lightos-code
```

## Troubleshooting

### GPU Not Detected

```bash
# Check NVIDIA drivers
nvidia-smi

# Install CUDA drivers
sudo apt update
sudo apt install nvidia-driver-535 nvidia-cuda-toolkit

# Verify CUDA
nvcc --version
```

### Command Not Found

```bash
# Check if installed
which lightos

# If not found, ensure /usr/local/bin is in PATH
echo $PATH | grep /usr/local/bin

# Re-run installer
cd ~/LightOS
sudo ./simple-deploy.sh
```

### Import Errors

```bash
# Activate virtual environment
source /opt/lightos/venv/bin/activate

# Reinstall dependencies
pip install --upgrade torch transformers accelerate

# For Unsloth
pip install unsloth
```

### Out of Disk Space

```bash
# Check disk usage
df -h

# Clean up
sudo apt clean
docker system prune -a

# Free at least 20GB before installing
```

## Next Steps

After installation:

1. **[Fine-Tuning Guide](../guides/fine-tuning.md)** - Train your first model
2. **[Coding Agents Guide](../guides/coding-agents.md)** - Generate code with AI
3. **[Examples](../examples/README.md)** - Run practical examples
4. **[API Reference](../api/README.md)** - Explore the API

## Updating LightOS

```bash
cd ~/LightOS
git pull origin main
sudo ./simple-deploy.sh
```

## Uninstalling

```bash
# Remove system commands
sudo rm /usr/local/bin/lightos*

# Remove installation directory
sudo rm -rf /opt/lightos

# Remove configuration
sudo rm -rf /etc/lightos
```

## Support

- **Issues**: https://github.com/Lightiam/LightOS/issues
- **Discussions**: https://github.com/Lightiam/LightOS/discussions
- **Documentation**: https://lightos.dev/docs
