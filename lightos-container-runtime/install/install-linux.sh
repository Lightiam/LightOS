#!/bin/bash
# LightOS Container Runtime Installer for Linux
# Supports: Ubuntu, Debian, RHEL, Fedora, CentOS

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
║                                                               ║
║     Multi-Vendor GPU Runtime for Docker & Kubernetes         ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
echo -e "${COLOR_RESET}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${COLOR_RED}Please run as root (use sudo)${COLOR_RESET}"
    exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
else
    echo -e "${COLOR_RED}Cannot detect OS${COLOR_RESET}"
    exit 1
fi

echo -e "${COLOR_GREEN}✓ Detected OS: $OS $VER${COLOR_RESET}"

# Install dependencies
echo -e "\n${COLOR_BLUE}Installing dependencies...${COLOR_RESET}"

case $OS in
    ubuntu|debian)
        apt-get update
        apt-get install -y \
            curl \
            jq \
            pciutils \
            make \
            gcc \
            git
        ;;

    rhel|centos|fedora)
        yum install -y \
            curl \
            jq \
            pciutils \
            make \
            gcc \
            git
        ;;

    *)
        echo -e "${COLOR_YELLOW}Warning: Unsupported OS, attempting generic install${COLOR_RESET}"
        ;;
esac

echo -e "${COLOR_GREEN}✓ Dependencies installed${COLOR_RESET}"

# Install Go (required for building)
echo -e "\n${COLOR_BLUE}Checking Go installation...${COLOR_RESET}"

if ! command -v go &> /dev/null; then
    echo "Installing Go..."
    GO_VERSION="1.21.0"
    curl -sL "https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz" | tar -C /usr/local -xzf -
    export PATH=$PATH:/usr/local/go/bin
    echo 'export PATH=$PATH:/usr/local/go/bin' >> /etc/profile.d/go.sh
fi

echo -e "${COLOR_GREEN}✓ Go installed: $(go version)${COLOR_RESET}"

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

install -m 755 lightos-runtime /usr/bin/lightos-runtime

echo -e "${COLOR_GREEN}✓ Binary installed to /usr/bin/lightos-runtime${COLOR_RESET}"

# Install hooks
echo -e "\n${COLOR_BLUE}Installing OCI hooks...${COLOR_RESET}"

mkdir -p /usr/libexec/oci/hooks.d
install -m 755 hooks/prestart /usr/libexec/oci/hooks.d/lightos-prestart
install -m 755 hooks/poststop /usr/libexec/oci/hooks.d/lightos-poststop

echo -e "${COLOR_GREEN}✓ Hooks installed${COLOR_RESET}"

# Create config directory
echo -e "\n${COLOR_BLUE}Creating configuration...${COLOR_RESET}"

mkdir -p /etc/lightos-runtime

cat > /etc/lightos-runtime/config.json << 'ENDCONFIG'
{
  "debug": false,
  "logFile": "/var/log/lightos-runtime.log",
  "runtimePath": "/usr/bin/runc",
  "defaultStrategy": "balanced",
  "preferredVendor": "any",
  "enableMultiGPU": false,
  "maxGPUPerContainer": 1,
  "injectDrivers": true,
  "cudaPath": "/usr/local/cuda",
  "rocmPath": "/opt/rocm",
  "oneAPIPath": "/opt/intel/oneapi",
  "enableMetrics": true,
  "metricsPort": 9100,
  "metricsPath": "/metrics",
  "enableCostTracking": true
}
ENDCONFIG

echo -e "${COLOR_GREEN}✓ Configuration created${COLOR_RESET}"

# Configure Docker daemon
echo -e "\n${COLOR_BLUE}Configuring Docker daemon...${COLOR_RESET}"

if command -v docker &> /dev/null; then
    /usr/bin/lightos-runtime configure

    echo -e "${COLOR_YELLOW}Restarting Docker daemon...${COLOR_RESET}"
    systemctl restart docker || service docker restart

    echo -e "${COLOR_GREEN}✓ Docker configured${COLOR_RESET}"
else
    echo -e "${COLOR_YELLOW}Docker not found, skipping Docker configuration${COLOR_RESET}"
fi

# Create systemd service for metrics
echo -e "\n${COLOR_BLUE}Creating systemd service...${COLOR_RESET}"

cat > /etc/systemd/system/lightos-metrics.service << 'ENDSERVICE'
[Unit]
Description=LightOS Container Runtime Metrics
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/lightos-runtime metrics-server
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
ENDSERVICE

systemctl daemon-reload
systemctl enable lightos-metrics.service || true

echo -e "${COLOR_GREEN}✓ Systemd service created${COLOR_RESET}"

# Detect devices
echo -e "\n${COLOR_BLUE}Detecting accelerators...${COLOR_RESET}"

/usr/bin/lightos-runtime detect || echo -e "${COLOR_YELLOW}No accelerators detected (this is OK if you don't have GPUs)${COLOR_RESET}"

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
echo "  # Run with specific GPU type:"
echo "  docker run --runtime=lightos \\"
echo "    -e LIGHTOS_DEVICE_TYPE=nvidia \\"
echo "    -e LIGHTOS_MIN_VRAM=8GB \\"
echo "    -e LIGHTOS_STRATEGY=performance \\"
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
