#!/bin/bash
# LightOS Docker Entrypoint

set -e

# Display welcome message
cat /etc/motd

# Activate virtual environment
source /lightos/venv/bin/activate

# Check GPU availability
echo "🖥️  Hardware Check:"
python3 -c "import torch; print('  ✓ CUDA Available' if torch.cuda.is_available() else '  ⚠️  CPU Mode (No GPU detected)')"
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader | while read line; do
        echo "  ✓ GPU: $line"
    done
fi
echo ""

# Execute command
exec "$@"
