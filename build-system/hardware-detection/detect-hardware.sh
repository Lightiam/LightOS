#!/bin/bash
# LightOS Hardware Detection System
# Automatically detects hardware platform and applies optimal configuration

set -e

LIGHTOS_CONFIG_DIR="/etc/lightos"
EDGE_PROFILES_DIR="/opt/lightos/edge-profiles"
DETECTED_PROFILE=""

# Color output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[HW-DETECT]${NC} $1"
}

log_detail() {
    echo -e "${BLUE}[HW-DETECT]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[HW-DETECT]${NC} $1"
}

detect_architecture() {
    local arch=$(uname -m)

    case "$arch" in
        x86_64|amd64)
            echo "amd64"
            ;;
        aarch64|arm64)
            echo "arm64"
            ;;
        armv7l)
            echo "armv7"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

detect_cpu_info() {
    local cpu_model=$(grep -m1 "model name" /proc/cpuinfo | cut -d: -f2 | xargs)
    local cpu_cores=$(nproc)
    local cpu_freq=$(lscpu | grep "CPU max MHz" | awk '{print $4}' | cut -d. -f1)

    log_detail "CPU: $cpu_model"
    log_detail "Cores: $cpu_cores"
    log_detail "Max Frequency: ${cpu_freq} MHz"

    # Detect CPU features
    local features=""
    if grep -q avx512 /proc/cpuinfo; then
        features="$features AVX-512"
    elif grep -q avx2 /proc/cpuinfo; then
        features="$features AVX2"
    fi

    if grep -q neon /proc/cpuinfo; then
        features="$features NEON"
    fi

    if [ -n "$features" ]; then
        log_detail "CPU Features:$features"
    fi
}

detect_gpu() {
    log_info "Detecting GPU..."

    # NVIDIA GPU
    if command -v nvidia-smi &> /dev/null; then
        local gpu_name=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -n1)
        log_detail "NVIDIA GPU detected: $gpu_name"
        echo "nvidia"
        return 0
    fi

    # AMD GPU
    if lspci | grep -i "VGA.*AMD" > /dev/null; then
        local gpu_name=$(lspci | grep -i "VGA.*AMD" | cut -d: -f3 | xargs)
        log_detail "AMD GPU detected: $gpu_name"
        echo "amd"
        return 0
    fi

    # Intel integrated GPU
    if lspci | grep -i "VGA.*Intel" > /dev/null; then
        local gpu_name=$(lspci | grep -i "VGA.*Intel" | cut -d: -f3 | xargs)
        log_detail "Intel GPU detected: $gpu_name"
        echo "intel"
        return 0
    fi

    log_detail "No discrete GPU detected"
    echo "none"
}

detect_memory() {
    local total_mem=$(free -m | awk 'NR==2{print $2}')
    log_detail "Total Memory: ${total_mem} MB"
    echo "$total_mem"
}

detect_platform() {
    log_info "Detecting hardware platform..."

    # Check device tree for ARM boards
    if [ -f /proc/device-tree/model ]; then
        local model=$(cat /proc/device-tree/model)
        log_detail "Device Model: $model"

        case "$model" in
            *"Raspberry Pi"*)
                echo "raspberry-pi"
                return 0
                ;;
            *"Jetson"*)
                echo "nvidia-jetson"
                return 0
                ;;
        esac
    fi

    # Check DMI information for x86 systems
    if [ -f /sys/class/dmi/id/product_name ]; then
        local product=$(cat /sys/class/dmi/id/product_name)
        log_detail "Product: $product"

        case "$product" in
            *"NUC"*)
                echo "intel-nuc"
                return 0
                ;;
            *"ThinkPad"*|*"ThinkCentre"*)
                echo "lenovo-edge"
                return 0
                ;;
            *"OptiPlex"*|*"PowerEdge"*)
                echo "dell-edge"
                return 0
                ;;
        esac
    fi

    # Fallback: generic platform based on architecture
    local arch=$(detect_architecture)
    if [ "$arch" = "amd64" ]; then
        echo "generic-x86"
    elif [ "$arch" = "arm64" ]; then
        echo "generic-arm"
    else
        echo "generic"
    fi
}

detect_photonic_npu() {
    log_info "Scanning for photonic NPU..."

    # Check for PCIe devices with photonic NPU vendor IDs
    # (This is a placeholder - real vendor IDs would be needed)
    if lspci -nn | grep -E "1234:5678|abcd:ef01" > /dev/null; then
        local device=$(lspci -nn | grep -E "1234:5678|abcd:ef01" | cut -d: -f3 | xargs)
        log_detail "Photonic NPU detected: $device"
        echo "true"
        return 0
    fi

    # Check for custom photonic devices via sysfs
    if [ -d /sys/class/photonic_npu ]; then
        log_detail "Photonic NPU detected via sysfs"
        echo "true"
        return 0
    fi

    log_detail "No photonic NPU detected"
    echo "false"
}

detect_network_capabilities() {
    log_info "Detecting network capabilities..."

    local has_10g=false
    local has_rdma=false

    # Check for 10GbE interfaces
    for iface in /sys/class/net/*; do
        if [ -f "$iface/speed" ]; then
            local speed=$(cat "$iface/speed" 2>/dev/null || echo "0")
            if [ "$speed" -ge 10000 ]; then
                has_10g=true
                log_detail "10GbE interface detected: $(basename $iface)"
            fi
        fi
    done

    # Check for RDMA devices
    if [ -d /sys/class/infiniband ] && [ "$(ls -A /sys/class/infiniband)" ]; then
        has_rdma=true
        log_detail "RDMA/InfiniBand detected"
    fi

    echo "$has_10g,$has_rdma"
}

select_edge_profile() {
    local platform="$1"
    local arch="$2"
    local memory_mb="$3"
    local gpu="$4"
    local photonic="$5"

    log_info "Selecting optimal edge profile..."

    # Direct platform matches
    case "$platform" in
        raspberry-pi)
            echo "raspberry-pi"
            return 0
            ;;
        nvidia-jetson)
            echo "jetson-nano"
            return 0
            ;;
        intel-nuc)
            echo "intel-nuc"
            return 0
            ;;
    esac

    # Heuristic-based selection
    if [ "$photonic" = "true" ]; then
        log_detail "Photonic NPU available - selecting high-performance profile"
        echo "intel-nuc"
        return 0
    fi

    if [ "$gpu" = "nvidia" ] && [ "$arch" = "arm64" ]; then
        log_detail "NVIDIA GPU + ARM64 - selecting Jetson profile"
        echo "jetson-nano"
        return 0
    fi

    if [ "$arch" = "arm64" ] && [ "$memory_mb" -lt 4096 ]; then
        log_detail "Low-memory ARM64 - selecting Raspberry Pi profile"
        echo "raspberry-pi"
        return 0
    fi

    if [ "$arch" = "amd64" ]; then
        log_detail "x86-64 platform - selecting Intel NUC profile"
        echo "intel-nuc"
        return 0
    fi

    # Fallback
    log_warn "Could not determine optimal profile, using generic"
    echo "generic"
}

apply_profile() {
    local profile="$1"
    local profile_path="${EDGE_PROFILES_DIR}/${profile}.conf"

    if [ ! -f "$profile_path" ]; then
        log_warn "Profile not found: $profile_path"
        return 1
    fi

    log_info "Applying edge profile: $profile"

    # Copy profile to active configuration
    cp "$profile_path" "${LIGHTOS_CONFIG_DIR}/active-profile.conf"

    # Create symlink for easy reference
    ln -sf "${LIGHTOS_CONFIG_DIR}/active-profile.conf" "${LIGHTOS_CONFIG_DIR}/edge.conf"

    log_info "Profile applied successfully"
}

generate_hardware_report() {
    local arch="$1"
    local platform="$2"
    local memory_mb="$3"
    local gpu="$4"
    local photonic="$5"
    local profile="$6"

    cat > "${LIGHTOS_CONFIG_DIR}/hardware-report.json" << EOF
{
  "detection_timestamp": "$(date -Iseconds)",
  "architecture": "$arch",
  "platform": "$platform",
  "memory_mb": $memory_mb,
  "gpu": "$gpu",
  "photonic_npu": $photonic,
  "selected_profile": "$profile",
  "cpu_info": {
    "model": "$(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2 | xargs)",
    "cores": $(nproc),
    "threads": $(lscpu | grep '^CPU(s):' | awk '{print $2}')
  },
  "kernel": "$(uname -r)",
  "lightos_version": "0.2.1"
}
EOF

    log_info "Hardware report generated: ${LIGHTOS_CONFIG_DIR}/hardware-report.json"
}

configure_kernel_modules() {
    local profile="$1"

    log_info "Configuring kernel modules for $profile..."

    # Load LightOS core modules
    modprobe lightos_core 2>/dev/null || log_warn "lightos_core module not available (may need compilation)"

    # Load photonic driver if available
    if grep -q "supports_photonic = true" "${LIGHTOS_CONFIG_DIR}/active-profile.conf" 2>/dev/null; then
        modprobe photonic_driver 2>/dev/null || log_warn "photonic_driver module not available"
    fi

    log_info "Kernel modules configured"
}

optimize_system_parameters() {
    local profile="$1"

    log_info "Applying system optimizations for $profile..."

    # Apply sysctl parameters
    if [ -f /etc/sysctl.d/99-lightos-edge.conf ]; then
        sysctl -p /etc/sysctl.d/99-lightos-edge.conf > /dev/null 2>&1
    fi

    # Set CPU governor based on profile
    local cpu_cores=$(nproc)
    for i in $(seq 0 $((cpu_cores - 1))); do
        if [ -f "/sys/devices/system/cpu/cpu${i}/cpufreq/scaling_governor" ]; then
            echo "performance" > "/sys/devices/system/cpu/cpu${i}/cpufreq/scaling_governor" 2>/dev/null || true
        fi
    done

    log_info "System optimizations applied"
}

main() {
    log_info "LightOS Hardware Detection System v0.2.1"
    echo ""

    # Create config directory if it doesn't exist
    mkdir -p "$LIGHTOS_CONFIG_DIR"

    # Detect hardware
    local arch=$(detect_architecture)
    detect_cpu_info
    local memory_mb=$(detect_memory)
    local gpu=$(detect_gpu)
    local photonic=$(detect_photonic_npu)
    local platform=$(detect_platform)
    detect_network_capabilities

    echo ""
    log_info "Hardware Detection Summary:"
    log_detail "Architecture: $arch"
    log_detail "Platform: $platform"
    log_detail "Memory: ${memory_mb} MB"
    log_detail "GPU: $gpu"
    log_detail "Photonic NPU: $photonic"
    echo ""

    # Select and apply profile
    local profile=$(select_edge_profile "$platform" "$arch" "$memory_mb" "$gpu" "$photonic")
    apply_profile "$profile"

    # Generate hardware report
    generate_hardware_report "$arch" "$platform" "$memory_mb" "$gpu" "$photonic" "$profile"

    # Configure system
    configure_kernel_modules "$profile"
    optimize_system_parameters "$profile"

    echo ""
    log_info "Hardware detection complete!"
    log_info "Active profile: $profile"
    log_info "Configuration: ${LIGHTOS_CONFIG_DIR}/edge.conf"
    echo ""
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo)"
    exit 1
fi

main "$@"
