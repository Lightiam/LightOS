#!/bin/bash
# 02-install-nvidia.sh
# Install NVIDIA drivers and CUDA toolkit

set -e

echo "================================================"
echo "Step 2: Installing NVIDIA drivers and CUDA"
echo "================================================"

# Add NVIDIA package repository
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update

# Install NVIDIA driver (version 535 for broad compatibility)
sudo apt-get install -y nvidia-driver-535 nvidia-utils-535

# Install CUDA toolkit
sudo apt-get install -y nvidia-cuda-toolkit cuda-toolkit-12-3

# Install cuDNN
sudo apt-get install -y libcudnn8 libcudnn8-dev

# Install NCCL for multi-GPU support
sudo apt-get install -y libnccl2 libnccl-dev

# Verify installation (will fail during build without GPU, but will work at runtime)
echo "NVIDIA driver installation completed"
echo "Note: nvidia-smi will work after reboot on GPU instance"

# Create nvidia-smi symlink
sudo ln -sf /usr/bin/nvidia-smi /usr/local/bin/nvidia-smi || true

echo "✓ NVIDIA drivers installed"
