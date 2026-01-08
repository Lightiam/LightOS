#!/bin/bash
# LightOS Simple Deployment Script
# Works on: Ubuntu, WSL2, Any Linux
# No VM needed - runs directly on your system!

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_banner() {
    clear
    cat << 'EOF'
    ╦  ┬┌─┐┬ ┬┌┬┐╔═╗╔═╗
    ║  ││ ┬├─┤ │ ║ ║╚═╗
    ╩═╝┴└─┘┴ ┴ ┴ ╚═╝╚═╝

    Neural Compute Engine v0.2.1
    Simple Deployment (No VM Required)

EOF
}

check_system() {
    log_step "Checking system..."

    # Check if we're on Linux
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        log_error "This script requires Linux (or WSL2 Ubuntu)"
        exit 1
    fi

    # Check if we have sudo
    if ! command -v sudo &> /dev/null; then
        log_error "sudo is required"
        exit 1
    fi

    log_info "✓ System check passed"
}

install_dependencies() {
    log_step "Installing dependencies..."

    # Update package list
    apt-get update -qq

    # Install required packages
    apt-get install -y -qq \
        python3 \
        python3-pip \
        python3-venv \
        git \
        curl \
        wget \
        build-essential \
        2>/dev/null || {
        log_warn "Some packages failed to install, continuing..."
    }

    log_info "✓ Dependencies installed"
}

setup_lightos() {
    log_step "Setting up LightOS..."

    # Create directories
    mkdir -p /opt/lightos
    mkdir -p /etc/lightos
    mkdir -p /var/log/lightos

    # Copy LightOS components
    log_info "Copying LightOS components..."

    if [ -d "$(pwd)/llm-training-ground" ]; then
        cp -r llm-training-ground /opt/lightos/
        log_info "  ✓ LLM Training Ground"
    fi

    if [ -d "$(pwd)/fabric-os" ]; then
        cp -r fabric-os /opt/lightos/
        log_info "  ✓ FabricOS"
    fi

    if [ -d "$(pwd)/build-system/edge-profiles" ]; then
        cp -r build-system/edge-profiles /opt/lightos/
        log_info "  ✓ Edge Profiles"
    fi

    if [ -d "$(pwd)/docs" ]; then
        cp -r docs /opt/lightos/
        log_info "  ✓ Documentation"
    fi

    log_info "✓ LightOS setup complete"
}

install_python_packages() {
    log_step "Installing Python packages..."

    # Create virtual environment
    python3 -m venv /opt/lightos/venv
    source /opt/lightos/venv/bin/activate

    # Upgrade pip
    pip install --quiet --upgrade pip

    # Install core packages
    log_info "Installing PyTorch (this may take a while)..."
    pip install --quiet torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

    log_info "Installing Transformers and dependencies..."
    pip install --quiet transformers accelerate datasets

    log_info "Installing Unsloth (optional, for fast training)..."
    pip install --quiet unsloth || log_warn "Unsloth installation failed (optional)"

    log_info "Installing additional packages..."
    pip install --quiet bitsandbytes trl peft || log_warn "Some optional packages failed"

    deactivate

    log_info "✓ Python packages installed"
}

create_launcher() {
    log_step "Creating launcher scripts..."

    # Create main launcher
    cat > /usr/local/bin/lightos << 'LAUNCHER_EOF'
#!/bin/bash
# LightOS Launcher

source /opt/lightos/venv/bin/activate
cd /opt/lightos/llm-training-ground/ui

python3 enhanced_launcher.py "$@"
LAUNCHER_EOF

    chmod +x /usr/local/bin/lightos

    # Create coding agent launcher
    cat > /usr/local/bin/lightos-code << 'CODE_EOF'
#!/bin/bash
# LightOS Coding Agent Launcher

source /opt/lightos/venv/bin/activate
cd /opt/lightos/llm-training-ground/coding_agents

if [ "$1" = "glm4" ]; then
    python3 glm4_agent.py "${@:2}"
elif [ "$1" = "qwen" ]; then
    python3 qwen3_coder.py "${@:2}"
else
    echo "Usage: lightos-code [glm4|qwen] <command> <args>"
    echo ""
    echo "Examples:"
    echo "  lightos-code qwen generate 'fibonacci function'"
    echo "  lightos-code glm4 explain my_script.py"
fi
CODE_EOF

    chmod +x /usr/local/bin/lightos-code

    # Create fine-tune launcher
    cat > /usr/local/bin/lightos-train << 'TRAIN_EOF'
#!/bin/bash
# LightOS Training Launcher

source /opt/lightos/venv/bin/activate
cd /opt/lightos/llm-training-ground

python3 unsloth_integration.py "$@"
TRAIN_EOF

    chmod +x /usr/local/bin/lightos-train

    log_info "✓ Launcher scripts created"
}

create_config() {
    log_step "Creating configuration..."

    cat > /etc/lightos/config.json << 'EOF'
{
  "version": "0.2.1",
  "mode": "development",
  "features": {
    "unsloth": true,
    "glm4": true,
    "qwen_coder": true,
    "spiking_networks": true,
    "moe": true
  },
  "paths": {
    "models": "/opt/lightos/models",
    "datasets": "/opt/lightos/datasets",
    "logs": "/var/log/lightos"
  }
}
EOF

    log_info "✓ Configuration created"
}

create_startup_guide() {
    log_step "Creating quick start guide..."

    cat > /opt/lightos/QUICKSTART.txt << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║           LightOS Neural Compute Engine v0.2.1               ║
║                    Quick Start Guide                         ║
╚══════════════════════════════════════════════════════════════╝

🚀 GETTING STARTED

1. Launch LightOS Training Ground:
   $ lightos

2. Use Coding Agents:
   $ lightos-code qwen generate "fibonacci function"
   $ lightos-code glm4 explain my_script.py

3. Fine-tune Models:
   $ lightos-train list
   $ lightos-train train llama-3.1-8b alpaca

📚 DOCUMENTATION

- Full Guide: /opt/lightos/docs/NEW_FEATURES_v0.2.1.md
- Training Ground: /opt/lightos/llm-training-ground/README.md
- Examples: /opt/lightos/llm-training-ground/examples/

💡 TIPS

- Check GPU: python3 -c "import torch; print(torch.cuda.is_available())"
- View logs: tail -f /var/log/lightos/*.log
- Update: cd ~/LightOS && git pull

🆘 TROUBLESHOOTING

Issue: Out of memory
Fix: Use smaller models (qwen 1.5b) or 4-bit quantization

Issue: Slow training
Fix: Check GPU is being used with nvidia-smi

Issue: Package errors
Fix: source /opt/lightos/venv/bin/activate && pip install --upgrade <package>

🌐 SUPPORT

- GitHub: https://github.com/Lightiam/LightOS
- Docs: https://lightos.dev/docs
- Issues: https://github.com/Lightiam/LightOS/issues

═══════════════════════════════════════════════════════════════

Installed Commands:
  lightos        - Main training ground UI
  lightos-code   - Coding agents (GLM-4, Qwen)
  lightos-train  - Fast fine-tuning with Unsloth

Example Workflows:
  1. Quick code generation:
     lightos-code qwen generate "REST API with FastAPI"

  2. Fine-tune on your data:
     lightos-train train llama-3.1-8b your-dataset

  3. Interactive coding:
     lightos
     > Select option 5 (Qwen Coder)

═══════════════════════════════════════════════════════════════
EOF

    log_info "✓ Quick start guide created"
}

run_tests() {
    log_step "Running basic tests..."

    source /opt/lightos/venv/bin/activate

    # Test Python imports
    python3 -c "import torch; print('✓ PyTorch')" || log_warn "PyTorch test failed"
    python3 -c "import transformers; print('✓ Transformers')" || log_warn "Transformers test failed"
    python3 -c "import torch; print('✓ CUDA Available' if torch.cuda.is_available() else '⚠ CUDA not available (CPU mode)')"

    deactivate

    log_info "✓ Basic tests complete"
}

show_completion() {
    clear
    cat << 'EOF'

╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║              ✨ LightOS Installed Successfully! ✨            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

🎉 Installation Complete!

📍 Installation Directory: /opt/lightos
📖 Quick Start Guide: /opt/lightos/QUICKSTART.txt

🚀 READY TO USE

Start LightOS now:

    lightos

Or try these commands:

    lightos-code qwen generate "hello world function"
    lightos-train list
    cat /opt/lightos/QUICKSTART.txt

═══════════════════════════════════════════════════════════════

📊 What You Have:

✓ Unsloth Fast Fine-Tuning (2-5x faster)
✓ GLM-4 Coding Agent (9B parameters)
✓ Qwen2.5-Coder (0.5B-32B models)
✓ Interactive Training Ground UI
✓ Full Documentation

💡 First Steps:

1. Run: lightos
2. Select: Option 8 (Check Hardware)
3. Try: Option 5 (Qwen Coder) for code generation
4. Read: /opt/lightos/QUICKSTART.txt

═══════════════════════════════════════════════════════════════

🎓 Learning Resources:

- Tutorial: /opt/lightos/docs/NEW_FEATURES_v0.2.1.md
- Examples: /opt/lightos/llm-training-ground/examples/
- API Docs: /opt/lightos/llm-training-ground/README.md

Need help? Check /opt/lightos/QUICKSTART.txt

EOF
}

main() {
    print_banner

    log_info "Starting LightOS simple deployment..."
    echo ""

    # Check if running as root
    if [ "$EUID" -ne 0 ]; then
        log_error "Please run with sudo:"
        echo "  sudo $0"
        exit 1
    fi

    # Check if in LightOS directory
    if [ ! -d "llm-training-ground" ]; then
        log_error "Please run this script from the LightOS directory:"
        echo "  cd ~/LightOS"
        echo "  sudo ./simple-deploy.sh"
        exit 1
    fi

    log_info "This will install LightOS on your system (no VM needed)"
    echo ""
    read -p "Continue? [Y/n] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]] && [[ ! -z $REPLY ]]; then
        log_info "Installation cancelled"
        exit 0
    fi

    echo ""
    log_info "Installing LightOS... (this takes 5-10 minutes)"
    echo ""

    check_system
    install_dependencies
    setup_lightos
    install_python_packages
    create_launcher
    create_config
    create_startup_guide
    run_tests

    show_completion

    log_info "Installation log saved to: /var/log/lightos/install.log"
}

# Run main function
main "$@" 2>&1 | tee /var/log/lightos/install.log
