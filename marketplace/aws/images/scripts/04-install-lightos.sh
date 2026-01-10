#!/bin/bash
# 04-install-lightos.sh
# Install LightOS from source

set -e

echo "================================================"
echo "Step 4: Installing LightOS v${LIGHTOS_VERSION}"
echo "================================================"

# Copy LightOS to /opt
sudo cp -r /tmp/LightOS /opt/lightos
cd /opt/lightos

# Run the simple deployment script
sudo chmod +x simple-deploy.sh
sudo ./simple-deploy.sh

# Verify installation
if [ -f "/usr/local/bin/lightos" ]; then
    echo "✓ LightOS launcher installed"
else
    echo "✗ LightOS launcher not found"
    exit 1
fi

# Create models and datasets directories
sudo mkdir -p /opt/lightos/{models,datasets,logs}
sudo chown -R ubuntu:ubuntu /opt/lightos/{models,datasets,logs}

# Install LightOS Python packages
source /opt/lightos/venv/bin/activate

# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install transformers and related
pip install \
    transformers \
    accelerate \
    datasets \
    tokenizers \
    sentencepiece \
    protobuf

# Install Unsloth
pip install "unsloth[cu121] @ git+https://github.com/unslothai/unsloth.git"

# Install additional ML libraries
pip install \
    bitsandbytes \
    peft \
    trl \
    einops \
    xformers

# Install web framework dependencies
pip install \
    fastapi \
    uvicorn \
    websockets \
    pydantic

deactivate

echo "✓ LightOS installed successfully"

# Display version
/opt/lightos/venv/bin/python3 -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')"
