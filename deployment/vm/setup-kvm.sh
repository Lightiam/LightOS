#!/bin/bash
# Quick setup script for LightOS on KVM/QEMU

set -e

VM_NAME="lightos-nce"
VM_MEMORY="4096"
VM_CPUS="4"
VM_DISK=""
VM_NETWORK="default"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[KVM-SETUP]${NC} $1"
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
    KVM/QEMU Quick Setup

EOF
}

check_kvm() {
    log_step "Checking KVM installation..."

    if ! command -v virsh &> /dev/null; then
        log_warn "KVM/libvirt not found!"
        echo ""
        echo "Install KVM:"
        echo "  Ubuntu/Debian: sudo apt install qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virt-manager"
        echo "  Fedora: sudo dnf install @virtualization"
        echo "  Arch: sudo pacman -S qemu libvirt virt-manager"
        exit 1
    fi

    # Check if KVM module is loaded
    if ! lsmod | grep -q kvm; then
        log_warn "KVM kernel module not loaded!"
        echo "Load with: sudo modprobe kvm-intel (or kvm-amd)"
        exit 1
    fi

    # Check if user is in libvirt group
    if ! groups | grep -q libvirt; then
        log_warn "Current user not in 'libvirt' group"
        echo "Add with: sudo usermod -a -G libvirt $USER"
        echo "Then logout and login again"
    fi

    log_info "KVM detected and ready"
}

create_vm_virt_install() {
    local disk_image="$1"

    log_step "Creating VM with virt-install..."

    virt-install \
        --name "$VM_NAME" \
        --memory "$VM_MEMORY" \
        --vcpus "$VM_CPUS" \
        --disk path="$disk_image",format=qcow2,bus=virtio \
        --import \
        --os-variant ubuntu22.04 \
        --network network=default,model=virtio \
        --graphics spice \
        --console pty,target_type=serial \
        --noautoconsole

    log_info "VM created successfully"
}

create_vm_virsh() {
    local disk_image="$1"

    log_step "Creating VM with virsh..."

    # Create XML definition
    cat > /tmp/lightos-vm.xml << EOF
<domain type='kvm'>
  <name>$VM_NAME</name>
  <memory unit='MiB'>$VM_MEMORY</memory>
  <vcpu>$VM_CPUS</vcpu>
  <os>
    <type arch='x86_64' machine='pc'>hvm</type>
    <boot dev='hd'/>
  </os>
  <features>
    <acpi/>
    <apic/>
  </features>
  <cpu mode='host-passthrough'/>
  <clock offset='utc'/>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>restart</on_crash>
  <devices>
    <emulator>/usr/bin/qemu-system-x86_64</emulator>
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2'/>
      <source file='$disk_image'/>
      <target dev='vda' bus='virtio'/>
    </disk>
    <interface type='network'>
      <source network='default'/>
      <model type='virtio'/>
    </interface>
    <serial type='pty'>
      <target port='0'/>
    </serial>
    <console type='pty'>
      <target type='serial' port='0'/>
    </console>
    <channel type='unix'>
      <target type='virtio' name='org.qemu.guest_agent.0'/>
    </channel>
    <input type='tablet' bus='usb'/>
    <graphics type='spice' autoport='yes'/>
    <video>
      <model type='qxl'/>
    </video>
  </devices>
</domain>
EOF

    # Define and start VM
    virsh define /tmp/lightos-vm.xml
    rm /tmp/lightos-vm.xml

    log_info "VM defined successfully"
}

setup_port_forwarding() {
    log_step "Setting up port forwarding..."

    # Get VM IP
    local vm_ip=""
    local retries=0
    while [ -z "$vm_ip" ] && [ $retries -lt 30 ]; do
        vm_ip=$(virsh domifaddr "$VM_NAME" 2>/dev/null | grep -oP '(\d+\.){3}\d+' | head -1)
        if [ -z "$vm_ip" ]; then
            sleep 2
            ((retries++))
        fi
    done

    if [ -n "$vm_ip" ]; then
        log_info "VM IP: $vm_ip"
        echo ""
        echo "Access services:"
        echo "  • SSH: ssh lightos@$vm_ip"
        echo "  • Web UI: http://$vm_ip:8080"
    else
        log_warn "Could not detect VM IP address"
        log_info "Find it with: virsh domifaddr $VM_NAME"
    fi
}

start_vm() {
    log_step "Starting VM..."

    virsh start "$VM_NAME"

    log_info "VM started!"
    echo ""
    echo "Manage VM:"
    echo "  • Console: virt-manager or virsh console $VM_NAME"
    echo "  • Status: virsh list"
    echo "  • Stop: virsh shutdown $VM_NAME"
    echo "  • Delete: virsh undefine $VM_NAME && virsh vol-delete --pool default lightos-0.2.1.qcow2"
    echo ""

    # Wait for VM to get IP
    sleep 5
    setup_port_forwarding

    echo ""
    echo "Default credentials:"
    echo "  • Username: lightos"
    echo "  • Password: lightos"
    echo ""
    log_warn "Change the default password after first login!"
}

run_with_qemu() {
    local disk_image="$1"

    log_step "Running with QEMU directly..."

    qemu-system-x86_64 \
        -drive file="$disk_image",format=qcow2,if=virtio \
        -m "$VM_MEMORY" \
        -smp "$VM_CPUS" \
        -enable-kvm \
        -cpu host \
        -net nic,model=virtio \
        -net user,hostfwd=tcp::2222-:22,hostfwd=tcp::8080-:8080 \
        -vga qxl \
        -display gtk \
        &

    log_info "VM started with QEMU"
    echo ""
    echo "Access services:"
    echo "  • SSH: ssh -p 2222 lightos@localhost"
    echo "  • Web UI: http://localhost:8080"
}

main() {
    local method="${1:-virt-install}"  # virt-install, virsh, qemu

    print_banner
    check_kvm

    # Find disk image
    local disk_image=""
    if [ -f "output-vm/lightos-0.2.1.qcow2" ]; then
        disk_image="$(realpath output-vm/lightos-0.2.1.qcow2)"
    else
        log_warn "No QCOW2 image found!"
        echo ""
        echo "Build VM image first:"
        echo "  sudo ./build-system/build-vm-image.sh qcow2"
        exit 1
    fi

    log_info "Using disk image: $disk_image"

    case "$method" in
        virt-install)
            create_vm_virt_install "$disk_image"
            start_vm
            ;;
        virsh)
            create_vm_virsh "$disk_image"
            start_vm
            ;;
        qemu)
            run_with_qemu "$disk_image"
            ;;
        *)
            echo "Usage: $0 [virt-install|virsh|qemu]"
            exit 1
            ;;
    esac
}

main "$@"
