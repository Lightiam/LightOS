#!/bin/bash
# 03-install-dependencies.sh
# Install Python and other dependencies

set -e

echo "================================================"
echo "Step 3: Installing Python and dependencies"
echo "================================================"

# Install Python 3.10
sudo apt-get install -y \
    python3.10 \
    python3.10-dev \
    python3-pip \
    python3-venv

# Make Python 3.10 the default
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

# Upgrade pip
python3 -m pip install --upgrade pip setuptools wheel

# Install essential Python packages
python3 -m pip install \
    numpy \
    scipy \
    pandas \
    matplotlib \
    scikit-learn

# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "/tmp/awscliv2.zip"
unzip /tmp/awscliv2.zip -d /tmp
sudo /tmp/aws/install
rm -rf /tmp/aws /tmp/awscliv2.zip

# Install Docker
sudo apt-get install -y \
    docker.io \
    docker-compose

# Add ubuntu user to docker group
sudo usermod -aG docker ubuntu

# Install Node.js (for web UI)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install monitoring tools
sudo apt-get install -y \
    sysstat \
    iotop \
    nethogs

echo "✓ Dependencies installed"
