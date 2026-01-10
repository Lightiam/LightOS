#!/bin/bash
# 10-validate.sh
# Validate LightOS installation

set -e

echo "================================================"
echo "Step 10: Validating installation"
echo "================================================"

# Check if LightOS commands exist
COMMANDS=("lightos" "lightos-train" "lightos-code")
for cmd in "${COMMANDS[@]}"; do
    if command -v $cmd &> /dev/null; then
        echo "✓ $cmd command found"
    else
        echo "✗ $cmd command NOT found"
        exit 1
    fi
done

# Check if venv exists
if [ -d "/opt/lightos/venv" ]; then
    echo "✓ Python virtual environment exists"
else
    echo "✗ Python virtual environment NOT found"
    exit 1
fi

# Check Python packages
source /opt/lightos/venv/bin/activate

PACKAGES=("torch" "transformers" "accelerate" "fastapi" "uvicorn")
for pkg in "${PACKAGES[@]}"; do
    if python3 -c "import $pkg" 2>/dev/null; then
        echo "✓ $pkg package installed"
    else
        echo "✗ $pkg package NOT installed"
        exit 1
    fi
done

# Check PyTorch version
TORCH_VERSION=$(python3 -c "import torch; print(torch.__version__)")
echo "✓ PyTorch version: $TORCH_VERSION"

# Check CUDA support (may not be available during build)
CUDA_AVAILABLE=$(python3 -c "import torch; print(torch.cuda.is_available())")
echo "  CUDA available: $CUDA_AVAILABLE (will be true on GPU instance)"

deactivate

# Check systemd services
SERVICES=("lightos-web" "lightos-api" "lightos-jupyter")
for svc in "${SERVICES[@]}"; do
    if systemctl is-enabled $svc &> /dev/null; then
        echo "✓ $svc service enabled"
    else
        echo "✗ $svc service NOT enabled"
        exit 1
    fi
done

# Check directories
DIRS=("/opt/lightos/models" "/opt/lightos/datasets" "/opt/lightos/logs")
for dir in "${DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "✓ Directory $dir exists"
    else
        echo "✗ Directory $dir NOT found"
        exit 1
    fi
done

# Check AWS configuration
if [ -f "/etc/lightos/aws/config.json" ]; then
    echo "✓ AWS configuration exists"
else
    echo "✗ AWS configuration NOT found"
    exit 1
fi

# Check CloudWatch agent
if [ -f "/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent" ]; then
    echo "✓ CloudWatch agent installed"
else
    echo "✗ CloudWatch agent NOT found"
    exit 1
fi

# Calculate disk usage
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
echo "  Disk usage: ${DISK_USAGE}%"

if [ $DISK_USAGE -gt 80 ]; then
    echo "⚠  Warning: High disk usage"
fi

echo "================================================"
echo "✅ All validations passed!"
echo "================================================"
echo ""
echo "AMI is ready for production use"
echo ""
echo "Installed Components:"
echo "  - LightOS v0.2.1"
echo "  - PyTorch $TORCH_VERSION"
echo "  - NVIDIA Driver 535"
echo "  - CUDA 12.3"
echo "  - CloudWatch Agent"
echo "  - Systemd Services"
echo ""
