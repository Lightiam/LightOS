#!/bin/bash
# LightOS Container Runtime Installer for macOS
# Requires: Docker Desktop for Mac

set -e

COLOR_RESET='\033[0m'
COLOR_GREEN='\033[0;32m'
COLOR_BLUE='\033[0;34m'
COLOR_YELLOW='\033[1;33m'
COLOR_RED='\033[0;31m'

echo -e "${COLOR_BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║          LightOS Container Runtime Installer                 ║
║                         macOS                                 ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
echo -e "${COLOR_RESET}"

# Check if running on macOS
if [ "$(uname)" != "Darwin" ]; then
    echo -e "${COLOR_RED}This script is for macOS only${COLOR_RESET}"
    exit 1
fi

# Check for Homebrew
echo -e "\n${COLOR_BLUE}Checking Homebrew...${COLOR_RESET}"

if ! command -v brew &> /dev/null; then
    echo -e "${COLOR_YELLOW}Homebrew not found. Installing...${COLOR_RESET}"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

echo -e "${COLOR_GREEN}✓ Homebrew installed${COLOR_RESET}"

# Install dependencies
echo -e "\n${COLOR_BLUE}Installing dependencies...${COLOR_RESET}"

brew install go jq git

echo -e "${COLOR_GREEN}✓ Dependencies installed${COLOR_RESET}"

# Check Docker Desktop
echo -e "\n${COLOR_BLUE}Checking Docker Desktop...${COLOR_RESET}"

if ! command -v docker &> /dev/null; then
    echo -e "${COLOR_RED}Docker Desktop not found${COLOR_RESET}"
    echo -e "${COLOR_YELLOW}Please install Docker Desktop for Mac:${COLOR_RESET}"
    echo -e "${COLOR_YELLOW}  https://www.docker.com/products/docker-desktop${COLOR_RESET}"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${COLOR_RED}Docker Desktop is not running${COLOR_RESET}"
    echo -e "${COLOR_YELLOW}Please start Docker Desktop${COLOR_RESET}"
    exit 1
fi

echo -e "${COLOR_GREEN}✓ Docker Desktop running${COLOR_RESET}"

# Build runtime binary
echo -e "\n${COLOR_BLUE}Building LightOS runtime...${COLOR_RESET}"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$REPO_ROOT"

# Initialize Go module if needed
if [ ! -f "go.mod" ]; then
    go mod init github.com/Lightiam/LightOS/lightos-container-runtime
    go mod tidy
fi

# Build main runtime
go build -o lightos-runtime ./cmd/lightos-runtime/

if [ ! -f "lightos-runtime" ]; then
    echo -e "${COLOR_RED}Failed to build runtime${COLOR_RESET}"
    exit 1
fi

echo -e "${COLOR_GREEN}✓ Runtime built successfully${COLOR_RESET}"

# Install binary
echo -e "\n${COLOR_BLUE}Installing runtime binary...${COLOR_RESET}"

sudo install -m 755 lightos-runtime /usr/local/bin/lightos-runtime

echo -e "${COLOR_GREEN}✓ Binary installed to /usr/local/bin/lightos-runtime${COLOR_RESET}"

# Create config directory
echo -e "\n${COLOR_BLUE}Creating configuration...${COLOR_RESET}"

sudo mkdir -p /etc/lightos-runtime

sudo tee /etc/lightos-runtime/config.json > /dev/null << 'ENDCONFIG'
{
  "debug": false,
  "logFile": "/var/log/lightos-runtime.log",
  "runtimePath": "/usr/bin/runc",
  "defaultStrategy": "balanced",
  "preferredVendor": "apple",
  "enableMultiGPU": false,
  "maxGPUPerContainer": 1,
  "injectDrivers": true,
  "cudaPath": "/usr/local/cuda",
  "rocmPath": "/opt/rocm",
  "oneAPIPath": "/opt/intel/oneapi",
  "enableMetrics": true,
  "metricsPort": 9100,
  "metricsPath": "/metrics",
  "enableCostTracking": false
}
ENDCONFIG

echo -e "${COLOR_GREEN}✓ Configuration created${COLOR_RESET}"

# Note about Docker Desktop integration
echo -e "\n${COLOR_YELLOW}Note: Docker Desktop for Mac integration${COLOR_RESET}"
echo -e "Docker Desktop for Mac runs in a lightweight VM."
echo -e "The LightOS runtime will work inside the VM."
echo ""
echo -e "To configure Docker Desktop:"
echo -e "  1. Open Docker Desktop preferences"
echo -e "  2. Go to Docker Engine"
echo -e "  3. Add the following to the configuration:"
echo ""
echo -e '  "runtimes": {'
echo -e '    "lightos": {'
echo -e '      "path": "/usr/local/bin/lightos-runtime"'
echo -e '    }'
echo -e '  }'
echo ""

# Detect devices
echo -e "\n${COLOR_BLUE}Detecting accelerators...${COLOR_RESET}"

/usr/local/bin/lightos-runtime detect || echo -e "${COLOR_YELLOW}Detection may be limited on macOS${COLOR_RESET}"

# Installation complete
echo -e "\n${COLOR_GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║          ✓ Installation Complete!                            ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
echo -e "${COLOR_RESET}"

echo -e "${COLOR_BLUE}Usage:${COLOR_RESET}"
echo ""
echo "  # Run container with automatic GPU selection:"
echo "  docker run --runtime=lightos your-image:latest"
echo ""
echo "  # Run with Apple Silicon GPU:"
echo "  docker run --runtime=lightos \\"
echo "    -e LIGHTOS_DEVICE_TYPE=apple \\"
echo "    your-image:latest"
echo ""
echo "  # Detect available devices:"
echo "  lightos-runtime detect"
echo ""
echo "  # View runtime info:"
echo "  lightos-runtime info"
echo ""
echo -e "${COLOR_BLUE}Documentation:${COLOR_RESET} https://github.com/Lightiam/LightOS"
echo ""
echo -e "${COLOR_GREEN}Happy computing! 🚀${COLOR_RESET}"
