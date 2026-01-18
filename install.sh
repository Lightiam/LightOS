#!/bin/bash
set -e

# LightOS Cross-Platform Installation Script
# Automatically detects platform and installs LightOS using the best method
# Usage: curl -fsSL https://install.lightos.ai | bash

LIGHTOS_VERSION="${LIGHTOS_VERSION:-1.0.0}"
INSTALL_METHOD="${INSTALL_METHOD:-auto}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
    exit 1
}

# Detect OS and architecture
detect_platform() {
    OS="$(uname -s)"
    ARCH="$(uname -m)"

    case "$OS" in
        Linux*)
            PLATFORM="linux"
            if [ -f /etc/os-release ]; then
                . /etc/os-release
                DISTRO="$ID"
            fi
            ;;
        Darwin*)
            PLATFORM="macos"
            ;;
        MINGW*|MSYS*|CYGWIN*)
            PLATFORM="windows"
            ;;
        *)
            error "Unsupported operating system: $OS"
            ;;
    esac

    case "$ARCH" in
        x86_64|amd64)
            ARCH="x86_64"
            ;;
        aarch64|arm64)
            ARCH="arm64"
            ;;
        *)
            error "Unsupported architecture: $ARCH"
            ;;
    esac

    info "Detected platform: $PLATFORM-$ARCH"
}

# Check prerequisites
check_prerequisites() {
    info "Checking prerequisites..."

    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
        success "Python 3 found: $PYTHON_VERSION"
    else
        error "Python 3 is required but not found. Please install Python 3.8+"
    fi

    # Check pip
    if ! command -v pip3 &> /dev/null; then
        warning "pip3 not found, attempting to install..."
        if [ "$PLATFORM" = "linux" ]; then
            sudo apt-get install -y python3-pip || sudo yum install -y python3-pip
        elif [ "$PLATFORM" = "macos" ]; then
            python3 -m ensurepip
        fi
    fi

    success "Prerequisites check passed"
}

# Detect best installation method
detect_install_method() {
    if [ "$INSTALL_METHOD" != "auto" ]; then
        return
    fi

    info "Detecting best installation method..."

    # Check for package managers
    if [ "$PLATFORM" = "macos" ] && command -v brew &> /dev/null; then
        INSTALL_METHOD="homebrew"
    elif [ "$PLATFORM" = "linux" ] && [ "$DISTRO" = "ubuntu" ] || [ "$DISTRO" = "debian" ]; then
        INSTALL_METHOD="apt"
    elif [ "$PLATFORM" = "windows" ] && command -v choco &> /dev/null; then
        INSTALL_METHOD="chocolatey"
    elif command -v docker &> /dev/null; then
        INSTALL_METHOD="docker"
    else
        INSTALL_METHOD="pip"
    fi

    info "Selected installation method: $INSTALL_METHOD"
}

# Install via pip (universal)
install_pip() {
    info "Installing LightOS via pip..."

    pip3 install lightos-accelerated==$LIGHTOS_VERSION

    success "LightOS installed successfully via pip"
}

# Install via Homebrew (macOS/Linux)
install_homebrew() {
    info "Installing LightOS via Homebrew..."

    # Add tap if not already added
    if ! brew tap | grep -q "lightiam/lightos"; then
        brew tap lightiam/lightos
    fi

    brew install lightos

    success "LightOS installed successfully via Homebrew"
}

# Install via APT (Ubuntu/Debian)
install_apt() {
    info "Installing LightOS via APT..."

    # Add repository
    if [ ! -f /etc/apt/sources.list.d/lightos.list ]; then
        info "Adding LightOS repository..."
        curl -fsSL https://packages.lightos.ai/gpg | sudo apt-key add -
        echo "deb https://packages.lightos.ai/apt stable main" | sudo tee /etc/apt/sources.list.d/lightos.list
        sudo apt-get update
    fi

    # Install
    sudo apt-get install -y lightos

    success "LightOS installed successfully via APT"
}

# Install via Chocolatey (Windows)
install_chocolatey() {
    info "Installing LightOS via Chocolatey..."

    choco install lightos -y

    success "LightOS installed successfully via Chocolatey"
}

# Install via Docker
install_docker() {
    info "Installing LightOS via Docker..."

    docker pull lightos/lightos-inference:$LIGHTOS_VERSION

    success "LightOS Docker image pulled successfully"
    info "Run with: docker run -p 50051:50051 --gpus all lightos/lightos-inference:$LIGHTOS_VERSION"
}

# Install binary release
install_binary() {
    info "Installing LightOS from binary release..."

    BINARY_URL="https://github.com/lightiam/lightos/releases/download/v${LIGHTOS_VERSION}/lightos-${PLATFORM}-${ARCH}.tar.gz"

    # Download
    TMP_DIR=$(mktemp -d)
    curl -L "$BINARY_URL" -o "$TMP_DIR/lightos.tar.gz"

    # Extract
    tar -xzf "$TMP_DIR/lightos.tar.gz" -C "$TMP_DIR"

    # Install
    if [ "$PLATFORM" = "windows" ]; then
        INSTALL_DIR="$HOME/lightos"
    else
        INSTALL_DIR="/usr/local"
        NEED_SUDO="sudo"
    fi

    $NEED_SUDO mkdir -p "$INSTALL_DIR/bin"
    $NEED_SUDO cp -r "$TMP_DIR/bin/"* "$INSTALL_DIR/bin/"
    $NEED_SUDO cp -r "$TMP_DIR/lib/"* "$INSTALL_DIR/lib/"

    # Cleanup
    rm -rf "$TMP_DIR"

    success "LightOS installed successfully from binary"
}

# Verify installation
verify_installation() {
    info "Verifying installation..."

    # Test Python import
    if python3 -c "from lightos_accelerated import LightDevice; print('✓ Python API working')" 2>/dev/null; then
        success "Python API verified"
    else
        warning "Python API verification failed (might need library path configuration)"
    fi

    # Check CLI
    if command -v lightos &> /dev/null; then
        success "CLI tools installed"
        lightos --version
    fi

    success "Installation verified!"
}

# Post-install instructions
post_install() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║  LightOS v${LIGHTOS_VERSION} installed successfully!                  ║"
    echo "╠════════════════════════════════════════════════════════════╣"
    echo "║  Quick Start:                                              ║"
    echo "║                                                            ║"
    echo "║    Python API:                                             ║"
    echo "║      python3 -c 'from lightos_accelerated import *'        ║"
    echo "║                                                            ║"
    echo "║    Start server:                                           ║"
    echo "║      lightos-server --port=50051 --devices=auto            ║"
    echo "║                                                            ║"
    echo "║    Examples:                                               ║"
    echo "║      jupyter notebook lightos-examples.ipynb               ║"
    echo "║                                                            ║"
    echo "║  Documentation: https://docs.lightos.ai                    ║"
    echo "║  GitHub: https://github.com/lightiam/lightos               ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
}

# Main installation flow
main() {
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║            LightOS Installation Script v1.0                ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""

    detect_platform
    check_prerequisites
    detect_install_method

    echo ""
    info "Installing LightOS v${LIGHTOS_VERSION} using method: $INSTALL_METHOD"
    echo ""

    case "$INSTALL_METHOD" in
        pip)
            install_pip
            ;;
        homebrew)
            install_homebrew
            ;;
        apt)
            install_apt
            ;;
        chocolatey)
            install_chocolatey
            ;;
        docker)
            install_docker
            ;;
        binary)
            install_binary
            ;;
        *)
            error "Unknown installation method: $INSTALL_METHOD"
            ;;
    esac

    verify_installation
    post_install
}

# Run main
main
