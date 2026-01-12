#!/bin/bash
# 01-system-update.sh
# Update and upgrade the system

set -e

echo "================================================"
echo "Step 1: Updating system packages"
echo "================================================"

# Update package lists
sudo apt-get update

# Upgrade all packages
sudo apt-get upgrade -y

# Install essential build tools
sudo apt-get install -y \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    curl \
    wget \
    git \
    vim \
    htop \
    tmux \
    jq \
    unzip

# Update kernel if needed
sudo apt-get dist-upgrade -y

# Install linux headers
sudo apt-get install -y linux-headers-$(uname -r)

echo "✓ System update completed"
