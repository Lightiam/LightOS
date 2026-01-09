#!/bin/bash
# LightOS Bare Metal Installer
# Installs LightOS to physical hardware or VM

set -e

LIGHTOS_VERSION="0.2.1"
INSTALL_DEVICE=""
INSTALL_MODE="auto"  # auto, custom, expert
HOSTNAME="lightos-edge"
ROOT_PASSWORD="lightos"
CREATE_USER=true
USERNAME="lightos"
USER_PASSWORD="lightos"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INSTALLER]${NC} $1"
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

    ┌─────────────────────────────────────┐
    │       BARE METAL INSTALLER          │
    └─────────────────────────────────────┘

EOF
}

show_warning() {
    echo ""
    log_warn "⚠️  WARNING ⚠️"
    echo ""
    echo "This installer will:"
    echo "  1. ERASE all data on the selected disk"
    echo "  2. Create new partitions"
    echo "  3. Install LightOS bootloader and system"
    echo ""
    log_warn "ALL EXISTING DATA WILL BE LOST!"
    echo ""
}

detect_disks() {
    log_info "Detecting available disks..."
    echo ""

    local disks=()
    for disk in /sys/block/sd* /sys/block/nvme* /sys/block/mmcblk*; do
        if [ -e "$disk" ]; then
            local dev_name=$(basename "$disk")
            local size=$(cat "$disk/size" 2>/dev/null || echo "0")
            local size_gb=$((size / 2 / 1024 / 1024))

            if [ $size_gb -gt 0 ]; then
                local model=""
                if [ -f "$disk/device/model" ]; then
                    model=$(cat "$disk/device/model" | xargs)
                fi

                disks+=("/dev/$dev_name")
                echo "  [$((${#disks[@]}))] /dev/$dev_name - ${size_gb}GB${model:+ ($model)}"
            fi
        fi
    done

    if [ ${#disks[@]} -eq 0 ]; then
        log_error "No suitable disks found!"
        exit 1
    fi

    echo ""
    read -p "Select disk number [1]: " disk_num
    disk_num=${disk_num:-1}

    if [ $disk_num -lt 1 ] || [ $disk_num -gt ${#disks[@]} ]; then
        log_error "Invalid selection"
        exit 1
    fi

    INSTALL_DEVICE="${disks[$((disk_num - 1))]}"
    log_info "Selected: $INSTALL_DEVICE"
}

confirm_installation() {
    echo ""
    log_warn "You are about to install LightOS on: $INSTALL_DEVICE"
    read -p "Type 'yes' to continue: " confirmation

    if [ "$confirmation" != "yes" ]; then
        log_info "Installation cancelled"
        exit 0
    fi
}

partition_disk() {
    log_info "Partitioning disk: $INSTALL_DEVICE"

    # Unmount any existing partitions
    umount ${INSTALL_DEVICE}* 2>/dev/null || true

    # Create partition table
    parted -s "$INSTALL_DEVICE" mklabel gpt

    # Create EFI partition (512MB)
    parted -s "$INSTALL_DEVICE" mkpart ESP fat32 1MiB 513MiB
    parted -s "$INSTALL_DEVICE" set 1 esp on

    # Create boot partition (1GB)
    parted -s "$INSTALL_DEVICE" mkpart primary ext4 513MiB 1537MiB

    # Create root partition (rest of disk)
    parted -s "$INSTALL_DEVICE" mkpart primary ext4 1537MiB 100%

    # Wait for kernel to re-read partition table
    partprobe "$INSTALL_DEVICE"
    sleep 2

    log_info "Partitioning complete"
}

format_partitions() {
    log_info "Formatting partitions..."

    # Determine partition naming scheme
    if [[ "$INSTALL_DEVICE" == *"nvme"* ]] || [[ "$INSTALL_DEVICE" == *"mmcblk"* ]]; then
        local efi_part="${INSTALL_DEVICE}p1"
        local boot_part="${INSTALL_DEVICE}p2"
        local root_part="${INSTALL_DEVICE}p3"
    else
        local efi_part="${INSTALL_DEVICE}1"
        local boot_part="${INSTALL_DEVICE}2"
        local root_part="${INSTALL_DEVICE}3"
    fi

    # Format EFI partition
    mkfs.fat -F32 -n EFI "$efi_part"

    # Format boot partition
    mkfs.ext4 -L boot "$boot_part"

    # Format root partition
    mkfs.ext4 -L root "$root_part"

    log_info "Formatting complete"

    # Export partition variables for later use
    export EFI_PART="$efi_part"
    export BOOT_PART="$boot_part"
    export ROOT_PART="$root_part"
}

mount_partitions() {
    log_info "Mounting partitions..."

    # Mount root
    mkdir -p /mnt/lightos
    mount "$ROOT_PART" /mnt/lightos

    # Mount boot
    mkdir -p /mnt/lightos/boot
    mount "$BOOT_PART" /mnt/lightos/boot

    # Mount EFI
    mkdir -p /mnt/lightos/boot/efi
    mount "$EFI_PART" /mnt/lightos/boot/efi

    log_info "Partitions mounted"
}

install_base_system() {
    log_info "Installing base system (this may take several minutes)..."

    # If running from ISO, copy filesystem
    if [ -f /run/live/medium/live/filesystem.squashfs ]; then
        log_info "Copying system from ISO..."
        unsquashfs -f -d /mnt/lightos /run/live/medium/live/filesystem.squashfs
    else
        # Fallback: debootstrap
        log_info "Bootstrapping Ubuntu base system..."
        debootstrap --arch=amd64 jammy /mnt/lightos http://archive.ubuntu.com/ubuntu/
    fi

    log_info "Base system installed"
}

configure_system() {
    log_info "Configuring system..."

    # Set hostname
    echo "$HOSTNAME" > /mnt/lightos/etc/hostname

    # Configure hosts file
    cat > /mnt/lightos/etc/hosts << EOF
127.0.0.1   localhost
127.0.1.1   $HOSTNAME

# LightOS Neural Compute Engine
# Infrastructure Autopilot enabled

::1         localhost ip6-localhost ip6-loopback
ff02::1     ip6-allnodes
ff02::2     ip6-allrouters
EOF

    # Configure fstab
    local root_uuid=$(blkid -s UUID -o value "$ROOT_PART")
    local boot_uuid=$(blkid -s UUID -o value "$BOOT_PART")
    local efi_uuid=$(blkid -s UUID -o value "$EFI_PART")

    cat > /mnt/lightos/etc/fstab << EOF
# /etc/fstab: LightOS filesystem table
UUID=$root_uuid  /          ext4  defaults,noatime  0  1
UUID=$boot_uuid  /boot      ext4  defaults          0  2
UUID=$efi_uuid   /boot/efi  vfat  umask=0077        0  1
EOF

    # Set root password
    echo "root:$ROOT_PASSWORD" | chroot /mnt/lightos chpasswd

    # Create user
    if [ "$CREATE_USER" = true ]; then
        chroot /mnt/lightos useradd -m -s /bin/bash -G sudo "$USERNAME"
        echo "$USERNAME:$USER_PASSWORD" | chroot /mnt/lightos chpasswd

        # Add user to lightos group
        chroot /mnt/lightos groupadd lightos 2>/dev/null || true
        chroot /mnt/lightos usermod -a -G lightos "$USERNAME"
    fi

    # Configure network
    cat > /mnt/lightos/etc/netplan/01-lightos.yaml << EOF
network:
  version: 2
  renderer: networkd
  ethernets:
    all:
      match:
        name: en*
      dhcp4: true
      dhcp6: true
EOF

    log_info "System configuration complete"
}

install_bootloader() {
    log_info "Installing GRUB bootloader..."

    # Bind mount system directories
    mount --bind /dev /mnt/lightos/dev
    mount --bind /dev/pts /mnt/lightos/dev/pts
    mount --bind /proc /mnt/lightos/proc
    mount --bind /sys /mnt/lightos/sys

    # Install GRUB for UEFI
    chroot /mnt/lightos apt-get update
    chroot /mnt/lightos apt-get install -y grub-efi-amd64 grub-efi-amd64-signed shim-signed

    # Install GRUB
    chroot /mnt/lightos grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=LightOS --recheck

    # Configure GRUB
    cat > /mnt/lightos/etc/default/grub << EOF
GRUB_DEFAULT=0
GRUB_TIMEOUT=5
GRUB_DISTRIBUTOR="LightOS"
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash lightos.mode=edge"
GRUB_CMDLINE_LINUX=""
GRUB_GFXMODE=1024x768
EOF

    # Update GRUB configuration
    chroot /mnt/lightos update-grub

    # Unmount bind mounts
    umount /mnt/lightos/sys
    umount /mnt/lightos/proc
    umount /mnt/lightos/dev/pts
    umount /mnt/lightos/dev

    log_info "Bootloader installed"
}

install_lightos_components() {
    log_info "Installing LightOS Neural Compute Engine components..."

    # Kernel modules will be built on first boot via DKMS
    # Services are already in /opt/lightos from base system

    # Enable LightOS services
    chroot /mnt/lightos systemctl enable lightrail-scheduler.service
    chroot /mnt/lightos systemctl enable lightos-autopilot.service
    chroot /mnt/lightos systemctl enable lightos-kvcache.service

    # Create first-boot script for hardware detection
    cat > /mnt/lightos/etc/systemd/system/lightos-firstboot.service << EOF
[Unit]
Description=LightOS First Boot Configuration
After=network.target
ConditionPathExists=!/var/lib/lightos/firstboot.done

[Service]
Type=oneshot
ExecStart=/opt/lightos/hardware-detection/detect-hardware.sh
ExecStartPost=/usr/bin/touch /var/lib/lightos/firstboot.done
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

    chroot /mnt/lightos systemctl enable lightos-firstboot.service

    log_info "LightOS components installed"
}

create_welcome_message() {
    cat > /mnt/lightos/etc/motd << 'EOF'

    ╦  ┬┌─┐┬ ┬┌┬┐╔═╗╔═╗
    ║  ││ ┬├─┤ │ ║ ║╚═╗
    ╩═╝┴└─┘┴ ┴ ┴ ╚═╝╚═╝
    Neural Compute Engine v0.2.1

Welcome to LightOS - Edge Computing Ready!

System Information:
  • Hardware Profile: Run 'cat /etc/lightos/hardware-report.json'
  • LLM Training Ground: http://localhost:8080
  • System Metrics: /var/log/lightos/edge-metrics.log

Quick Start:
  • Check system status: systemctl status lightos-*
  • View autopilot logs: journalctl -u lightos-autopilot
  • Launch training run: cd /opt/lightos/llm-training-ground/ui && python3 run_launcher.py

Documentation: /opt/lightos/docs/

EOF
}

cleanup() {
    log_info "Cleaning up..."

    sync

    # Unmount all
    umount /mnt/lightos/boot/efi 2>/dev/null || true
    umount /mnt/lightos/boot 2>/dev/null || true
    umount /mnt/lightos 2>/dev/null || true

    log_info "Cleanup complete"
}

installation_complete() {
    echo ""
    echo ""
    log_info "═══════════════════════════════════════════"
    log_info "   LightOS Installation Complete! ✓"
    log_info "═══════════════════════════════════════════"
    echo ""
    echo "Installation Summary:"
    echo "  • Device: $INSTALL_DEVICE"
    echo "  • Hostname: $HOSTNAME"
    echo "  • Default Username: $USERNAME"
    echo "  • Default Password: $USER_PASSWORD"
    echo ""
    log_warn "Please change default passwords after first boot!"
    echo ""
    echo "Next Steps:"
    echo "  1. Remove installation media"
    echo "  2. Reboot the system"
    echo "  3. LightOS will auto-detect your hardware"
    echo "  4. Access LLM Training Ground at http://localhost:8080"
    echo ""
    read -p "Press Enter to reboot..."
    reboot
}

main() {
    print_banner
    show_warning

    detect_disks
    confirm_installation

    partition_disk
    format_partitions
    mount_partitions

    install_base_system
    configure_system
    install_bootloader
    install_lightos_components
    create_welcome_message

    cleanup
    installation_complete
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_error "This installer must be run as root"
    exit 1
fi

main "$@"
