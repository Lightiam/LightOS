#!/bin/bash
# Quick setup script for LightOS on VirtualBox

set -e

VM_NAME="LightOS-NCE"
VM_DISK=""
VM_MEMORY="4096"
VM_CPUS="4"
VM_NETWORK="nat"
VBOX_VERSION=""

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[VBOX-SETUP]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_banner() {
    cat << 'EOF'
    ╦  ┬┌─┐┬ ┬┌┬┐╔═╗╔═╗
    ║  ││ ┬├─┤ │ ║ ║╚═╗
    ╩═╝┴└─┘┴ ┴ ┴ ╚═╝╚═╝
    VirtualBox Quick Setup

EOF
}

check_virtualbox() {
    log_step "Checking VirtualBox installation..."

    if ! command -v VBoxManage &> /dev/null; then
        log_warn "VirtualBox not found!"
        echo ""
        echo "Install VirtualBox:"
        echo "  Ubuntu/Debian: sudo apt install virtualbox"
        echo "  Fedora: sudo dnf install VirtualBox"
        echo "  macOS: brew install --cask virtualbox"
        echo "  Windows: Download from https://www.virtualbox.org/"
        exit 1
    fi

    VBOX_VERSION=$(VBoxManage --version | cut -d'r' -f1)
    log_info "VirtualBox $VBOX_VERSION detected"
}

import_ova() {
    local ova_file="$1"

    log_step "Importing OVA file..."

    VBoxManage import "$ova_file" \
        --vsys 0 \
        --vmname "$VM_NAME" \
        --memory "$VM_MEMORY" \
        --cpus "$VM_CPUS"

    log_info "OVA imported successfully"
}

create_vm_from_vdi() {
    local vdi_file="$1"

    log_step "Creating VM from VDI..."

    # Create VM
    VBoxManage createvm \
        --name "$VM_NAME" \
        --ostype Ubuntu_64 \
        --register

    # Configure VM
    VBoxManage modifyvm "$VM_NAME" \
        --memory "$VM_MEMORY" \
        --cpus "$VM_CPUS" \
        --vram 128 \
        --graphicscontroller vmsvga \
        --boot1 disk \
        --boot2 none \
        --boot3 none \
        --boot4 none \
        --audio none \
        --usb on \
        --mouse usbtablet

    # Create SATA controller
    VBoxManage storagectl "$VM_NAME" \
        --name "SATA Controller" \
        --add sata \
        --controller IntelAhci \
        --portcount 2 \
        --bootable on

    # Attach disk
    VBoxManage storageattach "$VM_NAME" \
        --storagectl "SATA Controller" \
        --port 0 \
        --device 0 \
        --type hdd \
        --medium "$vdi_file"

    # Configure network
    VBoxManage modifyvm "$VM_NAME" \
        --nic1 nat \
        --nictype1 82540EM \
        --cableconnected1 on

    # Port forwarding for SSH and LLM Training Ground
    VBoxManage modifyvm "$VM_NAME" \
        --natpf1 "ssh,tcp,,2222,,22" \
        --natpf1 "web,tcp,,8080,,8080"

    log_info "VM created successfully"
}

configure_shared_folder() {
    local host_path="$1"
    local share_name="${2:-lightos-share}"

    log_step "Configuring shared folder..."

    VBoxManage sharedfolder add "$VM_NAME" \
        --name "$share_name" \
        --hostpath "$host_path" \
        --automount

    log_info "Shared folder configured: $share_name"
    log_info "In VM: sudo mount -t vboxsf $share_name /mnt/shared"
}

enable_guest_additions() {
    log_step "Guest Additions are pre-installed in the image"
    log_info "To update: sudo apt install virtualbox-guest-utils virtualbox-guest-dkms"
}

start_vm() {
    log_step "Starting VM..."

    VBoxManage startvm "$VM_NAME" --type gui

    log_info "VM started!"
    echo ""
    echo "Access LightOS:"
    echo "  • Console: VirtualBox window"
    echo "  • SSH: ssh -p 2222 lightos@localhost"
    echo "  • Web UI: http://localhost:8080"
    echo ""
    echo "Default credentials:"
    echo "  • Username: lightos"
    echo "  • Password: lightos"
    echo ""
    log_warn "Change the default password after first login!"
}

main() {
    print_banner
    check_virtualbox

    # Detect image type
    local image_file=""
    if [ -f "output-vm/lightos-0.2.1.ova" ]; then
        image_file="output-vm/lightos-0.2.1.ova"
        log_info "Found OVA file: $image_file"
        import_ova "$image_file"
    elif [ -f "output-vm/lightos-0.2.1.vdi" ]; then
        image_file="output-vm/lightos-0.2.1.vdi"
        log_info "Found VDI file: $image_file"
        VM_DISK="$(realpath "$image_file")"
        create_vm_from_vdi "$VM_DISK"
    else
        log_warn "No VM image found!"
        echo ""
        echo "Build VM image first:"
        echo "  sudo ./build-system/build-vm-image.sh vdi"
        exit 1
    fi

    # Configure port forwarding
    log_step "Configuring port forwarding..."
    VBoxManage modifyvm "$VM_NAME" \
        --natpf1 "ssh,tcp,,2222,,22" \
        --natpf1 "web,tcp,,8080,,8080" 2>/dev/null || true

    echo ""
    read -p "Start VM now? [Y/n] " start_now
    if [ "$start_now" != "n" ]; then
        start_vm
    else
        log_info "VM ready. Start with: VBoxManage startvm '$VM_NAME'"
    fi
}

main "$@"
