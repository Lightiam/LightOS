#!/bin/bash
# LightOS Image Builder
# Builds bootable ISO and disk images for x86_64 and ARM64 architectures

set -e

LIGHTOS_VERSION="0.2.1"
BUILD_DIR="$(pwd)/build"
OUTPUT_DIR="$(pwd)/output"
ROOTFS_DIR="${BUILD_DIR}/rootfs"
ISO_DIR="${BUILD_DIR}/iso"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_banner() {
    cat << 'EOF'
    ╦  ┬┌─┐┬ ┬┌┬┐╔═╗╔═╗
    ║  ││ ┬├─┤ │ ║ ║╚═╗
    ╩═╝┴└─┘┴ ┴ ┴ ╚═╝╚═╝
    Neural Compute Engine v0.2.1

    Features:
    • Spiking Neural Networks (>69% sparsity)
    • MoE Conditional Computation
    • Photonic NPU Support
    • Infrastructure Autopilot (DRL HVAC)
    • LLM Training Ground
    • Multi-Hardware Agnostic

EOF
}

check_dependencies() {
    log_info "Checking build dependencies..."

    local deps=(
        "debootstrap"
        "squashfs-tools"
        "genisoimage"
        "syslinux"
        "isolinux"
        "qemu-user-static"
        "binfmt-support"
    )

    local missing=()
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null && ! dpkg -s "$dep" &> /dev/null 2>&1; then
            missing+=("$dep")
        fi
    done

    if [ ${#missing[@]} -gt 0 ]; then
        log_error "Missing dependencies: ${missing[*]}"
        log_info "Install with: sudo apt-get install ${missing[*]}"
        return 1
    fi

    log_info "All dependencies satisfied"
    return 0
}

create_base_rootfs() {
    local arch="$1"
    local suite="jammy"  # Ubuntu 22.04 LTS

    log_info "Creating base rootfs for ${arch}..."

    mkdir -p "${ROOTFS_DIR}"

    sudo debootstrap --arch="${arch}" \
        --variant=minbase \
        --include="systemd,systemd-sysv,linux-image-generic,grub-pc,network-manager,openssh-server,python3,python3-pip,build-essential,dkms" \
        "${suite}" \
        "${ROOTFS_DIR}" \
        http://archive.ubuntu.com/ubuntu/

    log_info "Base rootfs created"
}

install_lightos_kernel() {
    log_info "Installing LightOS kernel modules..."

    # Copy kernel modules
    sudo mkdir -p "${ROOTFS_DIR}/usr/src/lightos-${LIGHTOS_VERSION}"
    sudo cp -r kernel/modules/lightos-core "${ROOTFS_DIR}/usr/src/lightos-${LIGHTOS_VERSION}/"
    sudo cp -r kernel/drivers/photonic "${ROOTFS_DIR}/usr/src/lightos-${LIGHTOS_VERSION}/"

    # Create module loading configuration
    sudo tee "${ROOTFS_DIR}/etc/modules-load.d/lightos.conf" > /dev/null << EOF
# LightOS Neural Compute Engine modules
lightos_core
photonic_driver
EOF

    # Create DKMS configuration
    sudo tee "${ROOTFS_DIR}/usr/src/lightos-${LIGHTOS_VERSION}/dkms.conf" > /dev/null << EOF
PACKAGE_NAME="lightos"
PACKAGE_VERSION="${LIGHTOS_VERSION}"
AUTOINSTALL="yes"

BUILT_MODULE_NAME[0]="lightos_core"
BUILT_MODULE_LOCATION[0]="modules/lightos-core/"
DEST_MODULE_LOCATION[0]="/kernel/drivers/lightos/"

BUILT_MODULE_NAME[1]="photonic_driver"
BUILT_MODULE_LOCATION[1]="drivers/photonic/"
DEST_MODULE_LOCATION[1]="/kernel/drivers/photonic/"

BUILD_DEPENDS="build-essential linux-headers"
EOF

    log_info "Kernel modules installed"
}

install_lightos_services() {
    log_info "Installing LightOS services..."

    # Copy FabricOS components
    sudo mkdir -p "${ROOTFS_DIR}/opt/lightos"
    sudo cp -r fabric-os/lightrail-scheduler "${ROOTFS_DIR}/opt/lightos/"
    sudo cp -r fabric-os/kv-cache "${ROOTFS_DIR}/opt/lightos/"
    sudo cp -r fabric-os/metrics-collector "${ROOTFS_DIR}/opt/lightos/"
    sudo cp -r fabric-os/infrastructure-autopilot "${ROOTFS_DIR}/opt/lightos/"

    # Copy LLM Training Ground
    sudo cp -r llm-training-ground "${ROOTFS_DIR}/opt/lightos/"

    # Create systemd service for LightRail scheduler
    sudo tee "${ROOTFS_DIR}/etc/systemd/system/lightrail-scheduler.service" > /dev/null << EOF
[Unit]
Description=LightOS LightRail AI Scheduler
After=network.target lightos-modules.service

[Service]
Type=simple
ExecStart=/opt/lightos/lightrail-scheduler/scheduler
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Create systemd service for Infrastructure Autopilot
    sudo tee "${ROOTFS_DIR}/etc/systemd/system/lightos-autopilot.service" > /dev/null << EOF
[Unit]
Description=LightOS Infrastructure Autopilot (DRL HVAC Controller)
After=network.target lightos-modules.service

[Service]
Type=simple
ExecStart=/opt/lightos/infrastructure-autopilot/autopilot_daemon
Restart=always
RestartSec=10
Environment="AUTOPILOT_MODE=baseline"
Environment="AUTOPILOT_SAFETY_ENABLED=1"

[Install]
WantedBy=multi-user.target
EOF

    # Create systemd service for KV cache
    sudo tee "${ROOTFS_DIR}/etc/systemd/system/lightos-kvcache.service" > /dev/null << EOF
[Unit]
Description=LightOS Distributed KV Cache
After=network.target lightos-modules.service

[Service]
Type=simple
ExecStart=/opt/lightos/kv-cache/kvcache_server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Enable services
    sudo chroot "${ROOTFS_DIR}" systemctl enable lightrail-scheduler.service
    sudo chroot "${ROOTFS_DIR}" systemctl enable lightos-autopilot.service
    sudo chroot "${ROOTFS_DIR}" systemctl enable lightos-kvcache.service

    log_info "Services installed and enabled"
}

configure_edge_optimizations() {
    log_info "Applying edge computing optimizations..."

    # Create edge configuration
    sudo tee "${ROOTFS_DIR}/etc/lightos/edge.conf" > /dev/null << EOF
# LightOS Edge Computing Configuration

[edge]
# Deployment mode: cloud, edge, hybrid
mode = edge

# Resource constraints for edge devices
max_memory_mb = 4096
max_cpu_cores = 4
max_power_watts = 25

[spiking]
# Enable spiking neural networks for power efficiency
enabled = true
target_sparsity_percent = 75
encoding_method = delta

[moe]
# Mixture of Experts configuration
enabled = true
num_experts = 8
top_k = 1
load_balancing = true

[photonic]
# Photonic NPU (if available)
auto_detect = true
fallback_to_cpu = true

[autopilot]
# Infrastructure autopilot (limited on edge)
mode = local_only
hvac_control = false
thermal_monitoring = true

[networking]
# Edge-optimized networking
low_latency_mode = true
compression_enabled = true
federation_enabled = true
EOF

    # Optimize kernel parameters for edge
    sudo tee "${ROOTFS_DIR}/etc/sysctl.d/99-lightos-edge.conf" > /dev/null << EOF
# LightOS Edge Computing Kernel Parameters

# Memory management for constrained devices
vm.swappiness = 10
vm.dirty_ratio = 10
vm.dirty_background_ratio = 5

# Network optimizations
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 87380 67108864
net.ipv4.tcp_wmem = 4096 65536 67108864

# CPU scheduler optimizations
kernel.sched_migration_cost_ns = 5000000
kernel.sched_autogroup_enabled = 0
EOF

    # Create resource monitoring script
    sudo tee "${ROOTFS_DIR}/opt/lightos/bin/monitor-resources.sh" > /dev/null << 'EOF'
#!/bin/bash
# LightOS Edge Resource Monitor

while true; do
    CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    MEM=$(free | grep Mem | awk '{print ($3/$2) * 100.0}')
    TEMP=$(cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null || echo "0")
    TEMP_C=$(echo "scale=1; $TEMP/1000" | bc)

    echo "[$(date '+%Y-%m-%d %H:%M:%S')] CPU: ${CPU}% | MEM: ${MEM}% | TEMP: ${TEMP_C}°C"

    # Log to metrics collector
    echo "{\"timestamp\": $(date +%s), \"cpu\": $CPU, \"memory\": $MEM, \"temp\": $TEMP_C}" >> /var/log/lightos/edge-metrics.log

    sleep 5
done
EOF
    sudo chmod +x "${ROOTFS_DIR}/opt/lightos/bin/monitor-resources.sh"

    log_info "Edge optimizations applied"
}

create_boot_configuration() {
    log_info "Creating boot configuration..."

    # Create GRUB configuration
    sudo tee "${ROOTFS_DIR}/etc/default/grub" > /dev/null << EOF
GRUB_DEFAULT=0
GRUB_TIMEOUT=5
GRUB_DISTRIBUTOR="LightOS"
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"
GRUB_CMDLINE_LINUX="lightos.mode=edge lightos.autostart=true"
GRUB_GFXMODE=1024x768
GRUB_BACKGROUND=/boot/grub/lightos-bg.png
EOF

    # Set hostname
    echo "lightos-edge" | sudo tee "${ROOTFS_DIR}/etc/hostname" > /dev/null

    # Set root password (default: lightos)
    echo "root:lightos" | sudo chroot "${ROOTFS_DIR}" chpasswd

    log_info "Boot configuration created"
}

create_iso_image() {
    local arch="$1"

    log_info "Creating ISO image for ${arch}..."

    mkdir -p "${ISO_DIR}"
    mkdir -p "${OUTPUT_DIR}"

    # Create squashfs filesystem
    log_info "Compressing rootfs to squashfs..."
    sudo mksquashfs "${ROOTFS_DIR}" "${ISO_DIR}/live/filesystem.squashfs" \
        -comp xz -b 1M -Xdict-size 100% \
        -e boot

    # Copy kernel and initrd
    sudo cp "${ROOTFS_DIR}/boot/vmlinuz-"* "${ISO_DIR}/live/vmlinuz"
    sudo cp "${ROOTFS_DIR}/boot/initrd.img-"* "${ISO_DIR}/live/initrd"

    # Create isolinux configuration
    mkdir -p "${ISO_DIR}/isolinux"
    sudo cp /usr/lib/ISOLINUX/isolinux.bin "${ISO_DIR}/isolinux/"
    sudo cp /usr/lib/syslinux/modules/bios/ldlinux.c32 "${ISO_DIR}/isolinux/"
    sudo cp /usr/lib/syslinux/modules/bios/menu.c32 "${ISO_DIR}/isolinux/"

    cat > "${ISO_DIR}/isolinux/isolinux.cfg" << EOF
DEFAULT menu.c32
PROMPT 0
TIMEOUT 50

MENU TITLE LightOS ${LIGHTOS_VERSION} - Neural Compute Engine

LABEL lightos
    MENU LABEL Start LightOS
    KERNEL /live/vmlinuz
    APPEND initrd=/live/initrd boot=live quiet splash lightos.mode=edge

LABEL lightos-safe
    MENU LABEL Start LightOS (Safe Mode)
    KERNEL /live/vmlinuz
    APPEND initrd=/live/initrd boot=live nomodeset

LABEL install
    MENU LABEL Install LightOS to Disk
    KERNEL /live/vmlinuz
    APPEND initrd=/live/initrd boot=live install

LABEL memtest
    MENU LABEL Memory Test
    KERNEL memtest
EOF

    # Create ISO
    local iso_name="lightos-${LIGHTOS_VERSION}-${arch}.iso"
    log_info "Building ISO: ${iso_name}"

    sudo genisoimage -r -V "LightOS ${LIGHTOS_VERSION}" \
        -cache-inodes -J -l \
        -b isolinux/isolinux.bin \
        -c isolinux/boot.cat \
        -no-emul-boot -boot-load-size 4 -boot-info-table \
        -o "${OUTPUT_DIR}/${iso_name}" \
        "${ISO_DIR}"

    # Make ISO bootable
    sudo isohybrid "${OUTPUT_DIR}/${iso_name}"

    # Calculate checksum
    sha256sum "${OUTPUT_DIR}/${iso_name}" > "${OUTPUT_DIR}/${iso_name}.sha256"

    log_info "ISO created: ${OUTPUT_DIR}/${iso_name}"
    log_info "Checksum: $(cat ${OUTPUT_DIR}/${iso_name}.sha256)"
}

build_edge_container() {
    log_info "Building edge container image..."

    cat > "${BUILD_DIR}/Dockerfile.edge" << 'EOF'
FROM ubuntu:22.04

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    build-essential \
    linux-headers-generic \
    kmod \
    && rm -rf /var/lib/apt/lists/*

# Copy LightOS components
COPY rootfs/opt/lightos /opt/lightos
COPY rootfs/etc/lightos /etc/lightos
COPY rootfs/usr/src/lightos-* /usr/src/

# Install Python dependencies for LLM Training Ground
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    pip3 install transformers datasets accelerate

# Set up entrypoint
COPY edge-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/edge-entrypoint.sh

EXPOSE 8080 50051

ENTRYPOINT ["/usr/local/bin/edge-entrypoint.sh"]
CMD ["lightos-edge"]
EOF

    cat > "${BUILD_DIR}/edge-entrypoint.sh" << 'EOF'
#!/bin/bash
set -e

echo "Starting LightOS Edge Container..."

# Load kernel modules (if host allows)
if [ -d /lib/modules ]; then
    modprobe lightos_core 2>/dev/null || echo "Note: Running in userspace mode (kernel modules not available)"
fi

# Start services
/opt/lightos/lightrail-scheduler/scheduler &
/opt/lightos/kv-cache/kvcache_server &

# Start resource monitor
/opt/lightos/bin/monitor-resources.sh &

# Start LLM Training Ground UI
cd /opt/lightos/llm-training-ground/ui
python3 -m http.server 8080 &

echo "LightOS Edge is running"
exec "$@"
EOF

    log_info "Edge container configuration created"
}

cleanup() {
    log_info "Cleaning up build artifacts..."
    sudo umount "${ROOTFS_DIR}/proc" 2>/dev/null || true
    sudo umount "${ROOTFS_DIR}/sys" 2>/dev/null || true
    sudo umount "${ROOTFS_DIR}/dev" 2>/dev/null || true
}

main() {
    local arch="${1:-amd64}"
    local build_type="${2:-iso}"

    print_banner

    trap cleanup EXIT

    case "$build_type" in
        iso)
            check_dependencies || exit 1
            create_base_rootfs "$arch"
            install_lightos_kernel
            install_lightos_services
            configure_edge_optimizations
            create_boot_configuration
            create_iso_image "$arch"
            ;;
        container)
            build_edge_container
            ;;
        all)
            check_dependencies || exit 1
            create_base_rootfs "$arch"
            install_lightos_kernel
            install_lightos_services
            configure_edge_optimizations
            create_boot_configuration
            create_iso_image "$arch"
            build_edge_container
            ;;
        *)
            log_error "Unknown build type: $build_type"
            echo "Usage: $0 [amd64|arm64] [iso|container|all]"
            exit 1
            ;;
    esac

    log_info "Build complete!"
    echo ""
    echo "Next steps:"
    echo "  1. Test ISO: qemu-system-x86_64 -cdrom output/lightos-${LIGHTOS_VERSION}-${arch}.iso -m 4G"
    echo "  2. Write to USB: sudo dd if=output/lightos-${LIGHTOS_VERSION}-${arch}.iso of=/dev/sdX bs=4M status=progress"
    echo "  3. Boot on hardware and enjoy LightOS!"
}

if [ "$EUID" -ne 0 ]; then
    log_warn "This script requires root privileges. Some steps may fail."
    log_info "Consider running with sudo."
fi

main "$@"
