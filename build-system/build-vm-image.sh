#!/bin/bash
# LightOS VM Image Builder
# Creates pre-configured VM images for VirtualBox, VMware, and KVM/QEMU

set -e

LIGHTOS_VERSION="0.2.1"
BUILD_DIR="$(pwd)/build-vm"
OUTPUT_DIR="$(pwd)/output-vm"
DISK_SIZE="20G"
MEMORY_MB="4096"
CPU_CORES="4"

# Color output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[VM-BUILDER]${NC} $1"
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
    VM Image Builder v0.2.1

    Creating pre-configured VM images for:
    • VirtualBox (.vdi + .ova)
    • VMware (.vmdk)
    • KVM/QEMU (.qcow2)
    • Vagrant (.box)

EOF
}

check_dependencies() {
    log_info "Checking dependencies..."

    local deps=(
        "qemu-img"
        "qemu-system-x86_64"
        "virt-install"
        "guestfish"
        "virt-sysprep"
    )

    local missing=()
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing+=("$dep")
        fi
    done

    if [ ${#missing[@]} -gt 0 ]; then
        log_warn "Missing optional dependencies: ${missing[*]}"
        log_info "Install with: sudo apt-get install qemu-kvm libvirt-daemon-system libguestfs-tools"
        read -p "Continue anyway? [y/N] " confirm
        if [ "$confirm" != "y" ]; then
            exit 1
        fi
    fi

    log_info "Dependencies check complete"
}

create_base_disk() {
    local format="$1"  # qcow2, vmdk, vdi
    local output_file="$2"

    log_step "Creating ${format} disk image (${DISK_SIZE})..."

    case "$format" in
        qcow2)
            qemu-img create -f qcow2 "$output_file" "$DISK_SIZE"
            ;;
        vmdk)
            qemu-img create -f vmdk -o subformat=streamOptimized "$output_file" "$DISK_SIZE"
            ;;
        vdi)
            qemu-img create -f vdi "$output_file" "$DISK_SIZE"
            ;;
        raw)
            qemu-img create -f raw "$output_file" "$DISK_SIZE"
            ;;
        *)
            log_warn "Unknown format: $format"
            return 1
            ;;
    esac

    log_info "Disk image created: $output_file"
}

install_system_to_disk() {
    local disk_image="$1"
    local iso_path="$2"

    log_step "Installing LightOS to disk image (this may take 10-15 minutes)..."

    # Check if ISO exists
    if [ ! -f "$iso_path" ]; then
        log_warn "ISO not found: $iso_path"
        log_info "Building ISO first..."
        cd "$(dirname "$0")" && cd ..
        sudo ./build-system/lightos-builder.sh amd64 iso
        iso_path="$(pwd)/output/lightos-${LIGHTOS_VERSION}-amd64.iso"
    fi

    # Create VM and install
    virt-install \
        --name lightos-temp-install \
        --memory "$MEMORY_MB" \
        --vcpus "$CPU_CORES" \
        --disk path="$disk_image",format=qcow2 \
        --cdrom "$iso_path" \
        --os-variant ubuntu22.04 \
        --graphics none \
        --console pty,target_type=serial \
        --extra-args 'console=ttyS0,115200n8 serial auto=true priority=critical preseed/url=http://example.com/preseed.cfg' \
        --wait=-1 \
        --noautoconsole &

    local install_pid=$!

    # Wait for installation to complete (or timeout after 20 minutes)
    log_info "Installation started (PID: $install_pid)"
    log_info "This will take approximately 10-15 minutes..."

    sleep 900  # Wait 15 minutes for installation

    # Clean up
    virsh destroy lightos-temp-install 2>/dev/null || true
    virsh undefine lightos-temp-install 2>/dev/null || true

    log_info "Installation complete"
}

install_system_to_disk_alternative() {
    local disk_image="$1"

    log_step "Installing LightOS to disk image using alternative method..."

    # Use guestfish to partition and install
    guestfish -a "$disk_image" <<EOF
run
part-init /dev/sda gpt
part-add /dev/sda p 1048576 524287999
part-add /dev/sda p 524288000 2621439999
part-add /dev/sda p 2621440000 -1
part-set-gpt-type /dev/sda 1 C12A7328-F81F-11D2-BA4B-00A0C93EC93B
mkfs fat /dev/sda1
mkfs ext4 /dev/sda2
mkfs ext4 /dev/sda3
mount /dev/sda3 /
mkdir /boot
mount /dev/sda2 /boot
mkdir /boot/efi
mount /dev/sda1 /boot/efi
EOF

    # Bootstrap Ubuntu
    log_info "Bootstrapping Ubuntu base system..."
    virt-builder ubuntu-22.04 \
        --output "$disk_image" \
        --size "$DISK_SIZE" \
        --format qcow2 \
        --hostname lightos-vm \
        --root-password password:lightos \
        --update \
        --install linux-image-generic,build-essential,python3,python3-pip,dkms,git

    log_info "Base system installed"
}

use_virt_builder() {
    local disk_image="$1"

    log_step "Building VM image with virt-builder..."

    virt-builder ubuntu-22.04 \
        --output "$disk_image" \
        --size "$DISK_SIZE" \
        --format qcow2 \
        --hostname lightos-vm \
        --root-password password:lightos \
        --update \
        --install linux-image-generic,build-essential,python3,python3-pip,dkms,git,curl,wget,vim,htop,systemd \
        --run-command 'useradd -m -s /bin/bash -G sudo lightos' \
        --run-command 'echo "lightos:lightos" | chpasswd' \
        --run-command 'mkdir -p /opt/lightos /etc/lightos' \
        --copy-in ../kernel/modules/lightos-core:/usr/src/ \
        --copy-in ../kernel/drivers/photonic:/usr/src/ \
        --copy-in ../fabric-os:/opt/lightos/ \
        --copy-in ../llm-training-ground:/opt/lightos/ \
        --copy-in ../build-system/edge-profiles:/opt/lightos/ \
        --copy-in ../build-system/hardware-detection:/opt/lightos/ \
        --firstboot-command 'systemctl enable lightrail-scheduler lightos-autopilot lightos-kvcache' \
        --firstboot-command '/opt/lightos/hardware-detection/detect-hardware.sh'

    log_info "VM image built successfully"
}

optimize_for_vm() {
    local disk_image="$1"

    log_step "Applying VM-specific optimizations..."

    # Use virt-sysprep for cleanup and optimization
    virt-sysprep -a "$disk_image" \
        --operations defaults,-ssh-hostkeys \
        --hostname lightos-vm \
        --enable user-account,customize

    # Install VM guest additions
    virt-customize -a "$disk_image" \
        --run-command 'apt-get update' \
        --install qemu-guest-agent,spice-vdagent,open-vm-tools \
        --run-command 'systemctl enable qemu-guest-agent' \
        --run-command 'echo "vm.swappiness = 10" >> /etc/sysctl.conf' \
        --run-command 'echo "GRUB_CMDLINE_LINUX=\"net.ifnames=0 biosdevname=0\"" >> /etc/default/grub' \
        --run-command 'update-grub'

    log_info "VM optimizations applied"
}

create_vm_profile() {
    local profile_path="$1"

    log_step "Creating VM-optimized profile..."

    cat > "$profile_path" << 'EOF'
# LightOS VM Profile - Optimized for Virtual Machines

[hardware]
arch = amd64
platform = virtual-machine
min_memory_mb = 2048
min_storage_gb = 20
supports_photonic = false
supports_gpu = false
virtualized = true

[spiking]
enabled = true
target_sparsity_percent = 69
encoding_method = delta
max_neurons = 5000000
batch_size = 64

[moe]
enabled = true
num_experts = 8
top_k = 2
expert_capacity_factor = 1.25
load_balancing = true

[inference]
max_batch_size = 64
max_sequence_length = 2048
quantization = int8
kv_cache_memory_mb = 2048

[power]
# VM power management (host-controlled)
max_tdp_watts = 100
thermal_throttle_temp_c = 90
shutdown_temp_c = 100
enable_dvfs = false

[networking]
federation_enabled = true
federation_role = worker
coordinator_discovery = mdns
low_bandwidth_mode = false

[storage]
cache_size_mb = 2048
log_retention_days = 14
compress_logs = true

[vm]
# VM-specific settings
guest_additions = true
shared_folders = true
clipboard_sharing = true
drag_and_drop = true
EOF

    log_info "VM profile created"
}

convert_to_vmdk() {
    local source_qcow2="$1"
    local output_vmdk="$2"

    log_step "Converting to VMware VMDK format..."

    qemu-img convert -f qcow2 -O vmdk -o subformat=streamOptimized \
        "$source_qcow2" "$output_vmdk"

    log_info "VMDK created: $output_vmdk"
}

convert_to_vdi() {
    local source_qcow2="$1"
    local output_vdi="$2"

    log_step "Converting to VirtualBox VDI format..."

    qemu-img convert -f qcow2 -O vdi "$source_qcow2" "$output_vdi"

    log_info "VDI created: $output_vdi"
}

create_virtualbox_ova() {
    local vdi_path="$1"
    local output_ova="$2"

    log_step "Creating VirtualBox OVA package..."

    # Create OVF descriptor
    cat > "${BUILD_DIR}/lightos.ovf" << EOF
<?xml version="1.0"?>
<Envelope ovf:version="1.0" xml:lang="en-US">
  <References>
    <File ovf:href="$(basename "$vdi_path")" ovf:id="file1"/>
  </References>
  <DiskSection>
    <Info>Virtual disk information</Info>
    <Disk ovf:capacity="20" ovf:diskId="vmdisk1" ovf:fileRef="file1" ovf:format="http://www.vmware.com/interfaces/specifications/vmdk.html#streamOptimized"/>
  </DiskSection>
  <VirtualSystem ovf:id="LightOS">
    <Info>LightOS Neural Compute Engine v${LIGHTOS_VERSION}</Info>
    <Name>LightOS</Name>
    <OperatingSystemSection ovf:id="94">
      <Info>Ubuntu 22.04 LTS 64-bit</Info>
    </OperatingSystemSection>
    <VirtualHardwareSection>
      <Info>Virtual hardware requirements</Info>
      <Item>
        <rasd:Caption>4 virtual CPUs</rasd:Caption>
        <rasd:Description>Number of Virtual CPUs</rasd:Description>
        <rasd:InstanceID>1</rasd:InstanceID>
        <rasd:ResourceType>3</rasd:ResourceType>
        <rasd:VirtualQuantity>4</rasd:VirtualQuantity>
      </Item>
      <Item>
        <rasd:AllocationUnits>MegaBytes</rasd:AllocationUnits>
        <rasd:Caption>4096 MB of memory</rasd:Caption>
        <rasd:Description>Memory Size</rasd:Description>
        <rasd:InstanceID>2</rasd:InstanceID>
        <rasd:ResourceType>4</rasd:ResourceType>
        <rasd:VirtualQuantity>4096</rasd:VirtualQuantity>
      </Item>
      <Item>
        <rasd:Caption>disk1</rasd:Caption>
        <rasd:HostResource>ovf:/disk/vmdisk1</rasd:HostResource>
        <rasd:InstanceID>3</rasd:InstanceID>
        <rasd:Parent>4</rasd:Parent>
        <rasd:ResourceType>17</rasd:ResourceType>
      </Item>
    </VirtualHardwareSection>
  </VirtualSystem>
</Envelope>
EOF

    # Create OVA (tar archive)
    cd "${BUILD_DIR}"
    tar -cvf "$output_ova" lightos.ovf "$(basename "$vdi_path")"
    cd - > /dev/null

    log_info "OVA package created: $output_ova"
}

create_vagrant_box() {
    local qcow2_path="$1"
    local output_box="$2"

    log_step "Creating Vagrant box..."

    # Create Vagrant metadata
    cat > "${BUILD_DIR}/metadata.json" << EOF
{
  "provider": "libvirt",
  "format": "qcow2",
  "virtual_size": 20
}
EOF

    # Create Vagrantfile
    cat > "${BUILD_DIR}/Vagrantfile" << 'EOF'
Vagrant.configure("2") do |config|
  config.vm.base_mac = nil
  config.vm.hostname = "lightos"

  config.vm.provider :libvirt do |libvirt|
    libvirt.driver = "kvm"
    libvirt.memory = 4096
    libvirt.cpus = 4
  end

  config.vm.synced_folder ".", "/vagrant", type: "9p", disabled: false
end
EOF

    # Package as Vagrant box
    cd "${BUILD_DIR}"
    tar -czf "$output_box" metadata.json Vagrantfile -C "$(dirname "$qcow2_path")" "$(basename "$qcow2_path")"
    cd - > /dev/null

    log_info "Vagrant box created: $output_box"
}

create_vmware_vmx() {
    local vmdk_path="$1"
    local output_vmx="${vmdk_path%.vmdk}.vmx"

    log_step "Creating VMware configuration..."

    cat > "$output_vmx" << EOF
.encoding = "UTF-8"
config.version = "8"
virtualHW.version = "19"
vmci0.present = "TRUE"
hpet0.present = "TRUE"
displayName = "LightOS Neural Compute Engine"
guestOS = "ubuntu-64"
memsize = "$MEMORY_MB"
numvcpus = "$CPU_CORES"
powerType.powerOff = "soft"
powerType.suspend = "soft"
powerType.reset = "soft"

scsi0.present = "TRUE"
scsi0.virtualDev = "lsilogic"
scsi0:0.present = "TRUE"
scsi0:0.fileName = "$(basename "$vmdk_path")"
scsi0:0.deviceType = "disk"

ethernet0.present = "TRUE"
ethernet0.connectionType = "nat"
ethernet0.virtualDev = "e1000"
ethernet0.wakeOnPcktRcv = "FALSE"
ethernet0.addressType = "generated"

usb.present = "TRUE"
ehci.present = "TRUE"
sound.present = "FALSE"

tools.syncTime = "TRUE"
tools.upgrade.policy = "upgradeAtPowerCycle"
EOF

    log_info "VMware configuration created: $output_vmx"
}

create_readme() {
    local output_file="$1"

    cat > "$output_file" << 'EOF'
# LightOS VM Images

Pre-configured virtual machine images for LightOS Neural Compute Engine v0.2.1

## Quick Start

### VirtualBox

1. **Import OVA** (Easiest):
   - Open VirtualBox
   - File → Import Appliance
   - Select `lightos-0.2.1.ova`
   - Import and Start

2. **Or use VDI**:
   - Create new VM (Ubuntu 64-bit)
   - Use existing disk: `lightos-0.2.1.vdi`
   - RAM: 4GB, CPUs: 4
   - Start

### VMware (Workstation/Fusion/Player)

1. Open VMware
2. File → Open → Select `lightos-0.2.1.vmx`
3. Start VM

### KVM/QEMU

```bash
qemu-system-x86_64 \
    -drive file=lightos-0.2.1.qcow2,format=qcow2 \
    -m 4G -smp 4 \
    -enable-kvm \
    -net nic -net user,hostfwd=tcp::8080-:8080
```

### Vagrant

```bash
vagrant box add lightos lightos-0.2.1.box
vagrant init lightos
vagrant up
```

## Default Credentials

- **Username**: `lightos`
- **Password**: `lightos`
- **Root password**: `lightos`

⚠️ **Change these passwords immediately after first login!**

## System Specs

- **OS**: Ubuntu 22.04 LTS with LightOS Neural Compute Engine
- **Disk**: 20GB (thin-provisioned)
- **RAM**: 4GB (configurable)
- **CPUs**: 4 cores (configurable)

## What's Included

✅ Spiking Neural Networks (>69% sparsity)
✅ MoE Sparsity Module
✅ LightRail AI Scheduler
✅ Distributed KV Cache
✅ Infrastructure Autopilot
✅ LLM Training Ground (http://localhost:8080)
✅ QEMU Guest Agent (for KVM)
✅ Open VM Tools (for VMware)

## First Boot

On first boot, hardware auto-detection runs automatically.

View detection results:
```bash
cat /etc/lightos/hardware-report.json
```

## Accessing Services

- **LLM Training Ground**: http://localhost:8080
- **SSH**: Port 22 (if port forwarding configured)

From host machine:
```bash
# If you configured port forwarding
ssh -p 2222 lightos@localhost
```

## Shared Folders (Optional)

### VirtualBox
1. VM Settings → Shared Folders
2. Add folder from host
3. In VM: `sudo mount -t vboxsf ShareName /mnt/shared`

### VMware
1. VM Settings → Options → Shared Folders
2. Enable and add folders
3. In VM: Automatically mounted in `/mnt/hgfs/`

## Performance Tips

1. **Enable KVM acceleration** (Linux hosts):
   - Ensure KVM module loaded: `lsmod | grep kvm`
   - Use `-enable-kvm` flag with QEMU

2. **Allocate more resources**:
   - Increase RAM to 8GB for better performance
   - Add more CPU cores if available

3. **Use SSD for VM storage**:
   - Store VM images on SSD for faster I/O

## Troubleshooting

**Problem**: VM won't start
- Ensure virtualization enabled in BIOS (VT-x/AMD-V)
- Check RAM/CPU allocation isn't too high

**Problem**: Can't access web UI
- Check VM network: `ip addr`
- Verify service: `systemctl status lightrail-scheduler`
- Configure port forwarding: Host:8080 → Guest:8080

**Problem**: Slow performance
- Enable hardware virtualization
- Increase RAM allocation
- Use paravirtualized drivers (virtio)

## Next Steps

1. Change default passwords: `passwd`
2. Update system: `sudo apt update && sudo apt upgrade`
3. Access LLM Training Ground: http://localhost:8080
4. Start training models!

## Documentation

- `/opt/lightos/docs/` - Full documentation
- `EDGE_DEPLOYMENT_GUIDE.md` - Deployment guide
- `NEURAL_COMPUTE_ENGINE.md` - Architecture details

## Support

- GitHub: https://github.com/your-org/LightOS
- Documentation: https://lightos.dev/docs

---

**LightOS v0.2.1 - Neural Compute Engine**
*AI Infrastructure for Everyone*
EOF

    log_info "README created: $output_file"
}

main() {
    local format="${1:-all}"  # qcow2, vmdk, vdi, ova, vagrant, all

    print_banner

    check_dependencies

    mkdir -p "$BUILD_DIR" "$OUTPUT_DIR"

    # Create VM-specific profile
    create_vm_profile "${BUILD_DIR}/vm-profile.conf"

    case "$format" in
        qcow2)
            log_info "Building QCOW2 image for KVM/QEMU..."
            local qcow2_path="${OUTPUT_DIR}/lightos-${LIGHTOS_VERSION}.qcow2"
            use_virt_builder "$qcow2_path"
            optimize_for_vm "$qcow2_path"
            ;;

        vmdk)
            log_info "Building VMDK image for VMware..."
            local qcow2_path="${BUILD_DIR}/lightos-temp.qcow2"
            local vmdk_path="${OUTPUT_DIR}/lightos-${LIGHTOS_VERSION}.vmdk"
            use_virt_builder "$qcow2_path"
            optimize_for_vm "$qcow2_path"
            convert_to_vmdk "$qcow2_path" "$vmdk_path"
            create_vmware_vmx "$vmdk_path"
            ;;

        vdi|ova)
            log_info "Building VDI/OVA image for VirtualBox..."
            local qcow2_path="${BUILD_DIR}/lightos-temp.qcow2"
            local vdi_path="${OUTPUT_DIR}/lightos-${LIGHTOS_VERSION}.vdi"
            local ova_path="${OUTPUT_DIR}/lightos-${LIGHTOS_VERSION}.ova"
            use_virt_builder "$qcow2_path"
            optimize_for_vm "$qcow2_path"
            convert_to_vdi "$qcow2_path" "$vdi_path"
            if [ "$format" = "ova" ]; then
                create_virtualbox_ova "$vdi_path" "$ova_path"
            fi
            ;;

        vagrant)
            log_info "Building Vagrant box..."
            local qcow2_path="${OUTPUT_DIR}/lightos-${LIGHTOS_VERSION}.qcow2"
            local box_path="${OUTPUT_DIR}/lightos-${LIGHTOS_VERSION}.box"
            use_virt_builder "$qcow2_path"
            optimize_for_vm "$qcow2_path"
            create_vagrant_box "$qcow2_path" "$box_path"
            ;;

        all)
            log_info "Building all VM image formats..."

            # Build base QCOW2
            local qcow2_path="${OUTPUT_DIR}/lightos-${LIGHTOS_VERSION}.qcow2"
            use_virt_builder "$qcow2_path"
            optimize_for_vm "$qcow2_path"

            # Convert to other formats
            local vmdk_path="${OUTPUT_DIR}/lightos-${LIGHTOS_VERSION}.vmdk"
            local vdi_path="${OUTPUT_DIR}/lightos-${LIGHTOS_VERSION}.vdi"
            local ova_path="${OUTPUT_DIR}/lightos-${LIGHTOS_VERSION}.ova"
            local box_path="${OUTPUT_DIR}/lightos-${LIGHTOS_VERSION}.box"

            convert_to_vmdk "$qcow2_path" "$vmdk_path"
            create_vmware_vmx "$vmdk_path"

            convert_to_vdi "$qcow2_path" "$vdi_path"
            # create_virtualbox_ova "$vdi_path" "$ova_path"

            create_vagrant_box "$qcow2_path" "$box_path"
            ;;

        *)
            echo "Usage: $0 [qcow2|vmdk|vdi|ova|vagrant|all]"
            exit 1
            ;;
    esac

    # Create README
    create_readme "${OUTPUT_DIR}/README.txt"

    # Calculate checksums
    cd "$OUTPUT_DIR"
    sha256sum lightos-${LIGHTOS_VERSION}.* > SHA256SUMS 2>/dev/null || true
    cd - > /dev/null

    echo ""
    log_info "════════════════════════════════════════"
    log_info "   VM Image Build Complete! ✓"
    log_info "════════════════════════════════════════"
    echo ""
    echo "Output directory: $OUTPUT_DIR"
    echo ""
    ls -lh "$OUTPUT_DIR"/lightos-${LIGHTOS_VERSION}.* 2>/dev/null || ls -lh "$OUTPUT_DIR"
    echo ""
    echo "Quick Test:"
    echo "  VirtualBox: Import lightos-${LIGHTOS_VERSION}.ova"
    echo "  KVM/QEMU:   qemu-system-x86_64 -drive file=lightos-${LIGHTOS_VERSION}.qcow2 -m 4G -smp 4 -enable-kvm"
    echo "  VMware:     Open lightos-${LIGHTOS_VERSION}.vmx"
    echo "  Vagrant:    vagrant box add lightos-${LIGHTOS_VERSION}.box"
    echo ""
}

if [ "$EUID" -eq 0 ]; then
    log_warn "Running as root - some operations may require non-root"
fi

main "$@"
