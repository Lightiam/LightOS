# LightOS VM Deployment Guide

**Version**: 0.2.1
**Last Updated**: January 2026

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [VirtualBox Deployment](#virtualbox-deployment)
4. [VMware Deployment](#vmware-deployment)
5. [KVM/QEMU Deployment](#kvmqemu-deployment)
6. [Vagrant Deployment](#vagrant-deployment)
7. [Building VM Images](#building-vm-images)
8. [Configuration](#configuration)
9. [Performance Tuning](#performance-tuning)
10. [Troubleshooting](#troubleshooting)

---

## Overview

LightOS can be deployed as pre-configured virtual machine images for:
- ✅ **VirtualBox** (.vdi, .ova) - Cross-platform, beginner-friendly
- ✅ **VMware** (.vmdk, .vmx) - Workstation, Fusion, ESXi
- ✅ **KVM/QEMU** (.qcow2) - Linux hypervisor, best performance
- ✅ **Vagrant** (.box) - Development workflow automation

### Why Use VM Deployment?

- 🚀 **Quick testing** - Up and running in 5 minutes
- 🔒 **Isolated environment** - No impact on host system
- 📦 **Pre-configured** - All components ready to use
- 💻 **Cross-platform** - Works on Windows, macOS, Linux
- 🔄 **Snapshots** - Easy rollback and experimentation

---

## Quick Start

### Option 1: VirtualBox (Easiest)

```bash
# 1. Build VM image
sudo ./build-system/build-vm-image.sh vdi

# 2. Import and start
./deployment/vm/setup-virtualbox.sh

# 3. Access at http://localhost:8080
```

### Option 2: Vagrant (Developer Workflow)

```bash
# 1. Navigate to deployment directory
cd deployment/vm/

# 2. Start VM
vagrant up

# 3. SSH into VM
vagrant ssh

# 4. Access at http://localhost:8080
```

### Option 3: KVM/QEMU (Linux, Best Performance)

```bash
# 1. Build QCOW2 image
sudo ./build-system/build-vm-image.sh qcow2

# 2. Create and start VM
./deployment/vm/setup-kvm.sh

# 3. Access via VM IP
```

---

## VirtualBox Deployment

### Prerequisites

**Windows**:
- Download and install [VirtualBox](https://www.virtualbox.org/)
- Version 6.1+ recommended

**macOS**:
```bash
brew install --cask virtualbox
```

**Linux**:
```bash
# Ubuntu/Debian
sudo apt install virtualbox

# Fedora
sudo dnf install VirtualBox

# Arch
sudo pacman -S virtualbox
```

### Method 1: Import OVA (Recommended)

1. **Build OVA**:
   ```bash
   sudo ./build-system/build-vm-image.sh ova
   ```

2. **Import**:
   - Open VirtualBox
   - File → Import Appliance
   - Select `output-vm/lightos-0.2.1.ova`
   - Click Import
   - Wait 2-3 minutes

3. **Configure** (optional):
   - Right-click VM → Settings
   - System: Adjust RAM/CPUs
   - Network: Add port forwarding (see below)

4. **Start**:
   - Click Start
   - Login: `lightos` / `lightos`

### Method 2: Use VDI Directly

1. **Build VDI**:
   ```bash
   sudo ./build-system/build-vm-image.sh vdi
   ```

2. **Create VM**:
   - Open VirtualBox
   - Click "New"
   - Name: LightOS
   - Type: Linux
   - Version: Ubuntu (64-bit)
   - Memory: 4096 MB
   - Use existing hard disk: Select `output-vm/lightos-0.2.1.vdi`
   - Create

3. **Configure**:
   - Settings → Network → Adapter 1 → Advanced → Port Forwarding:
     - SSH: Host Port 2222 → Guest Port 22
     - Web: Host Port 8080 → Guest Port 8080

4. **Start VM**

### Method 3: Automated Setup

```bash
# One command setup
./deployment/vm/setup-virtualbox.sh
```

This script will:
- Detect VirtualBox installation
- Find and import VM image
- Configure port forwarding
- Start VM

### Accessing Services

From host machine:

```bash
# SSH
ssh -p 2222 lightos@localhost

# Web UI
open http://localhost:8080  # macOS
xdg-open http://localhost:8080  # Linux
start http://localhost:8080  # Windows
```

### Shared Folders

To share files between host and VM:

1. **Configure in VirtualBox**:
   - VM Settings → Shared Folders
   - Add folder (e.g., `~/LightOS-Data`)
   - Auto-mount: Yes
   - Access: Full

2. **In VM**:
   ```bash
   # Install guest additions (if not already)
   sudo apt install virtualbox-guest-utils virtualbox-guest-dkms

   # Mount (automatic on reboot)
   sudo mount -t vboxsf LightOS-Data /mnt/shared
   ```

---

## VMware Deployment

### Prerequisites

- **VMware Workstation** (Windows/Linux) or **VMware Fusion** (macOS)
- Version 15+ recommended

### Build VMDK Image

```bash
sudo ./build-system/build-vm-image.sh vmdk
```

This creates:
- `output-vm/lightos-0.2.1.vmdk` - Virtual disk
- `output-vm/lightos-0.2.1.vmx` - VM configuration

### Import and Start

1. **Open VMware**
2. **File → Open**
3. **Select** `output-vm/lightos-0.2.1.vmx`
4. **Power On**

### Configuration

Edit `lightos-0.2.1.vmx` to adjust:

```ini
# Memory (in MB)
memsize = "8192"

# CPU cores
numvcpus = "8"

# Network
ethernet0.connectionType = "nat"
# or "bridged" for direct network access
```

### VMware Tools

Pre-installed in the image:
```bash
# Check status
systemctl status open-vm-tools

# Update if needed
sudo apt install open-vm-tools open-vm-tools-desktop
```

---

## KVM/QEMU Deployment

### Prerequisites

**Ubuntu/Debian**:
```bash
sudo apt install qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virt-manager
sudo usermod -a -G libvirt $USER
# Logout and login
```

**Fedora**:
```bash
sudo dnf install @virtualization
sudo systemctl start libvirtd
sudo systemctl enable libvirtd
```

**Arch**:
```bash
sudo pacman -S qemu libvirt virt-manager
sudo systemctl start libvirtd
sudo systemctl enable libvirtd
```

### Build QCOW2 Image

```bash
sudo ./build-system/build-vm-image.sh qcow2
```

Output: `output-vm/lightos-0.2.1.qcow2`

### Method 1: Using virt-manager (GUI)

1. **Open virt-manager**
2. **Create new VM**:
   - File → New Virtual Machine
   - Import existing disk image
   - Browse to `lightos-0.2.1.qcow2`
   - OS: Ubuntu 22.04
   - Memory: 4096 MB
   - CPUs: 4
   - Finish

3. **Start VM**

### Method 2: Using virt-install (CLI)

```bash
virt-install \
    --name lightos-nce \
    --memory 4096 \
    --vcpus 4 \
    --disk path=output-vm/lightos-0.2.1.qcow2,format=qcow2,bus=virtio \
    --import \
    --os-variant ubuntu22.04 \
    --network network=default,model=virtio \
    --graphics spice \
    --noautoconsole

# Connect to console
virt-viewer lightos-nce
```

### Method 3: Using virsh (XML)

```bash
# Create VM definition
cat > lightos-vm.xml << EOF
<domain type='kvm'>
  <name>lightos-nce</name>
  <memory unit='GiB'>4</memory>
  <vcpu>4</vcpu>
  <os>
    <type arch='x86_64'>hvm</type>
    <boot dev='hd'/>
  </os>
  <devices>
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2'/>
      <source file='$(pwd)/output-vm/lightos-0.2.1.qcow2'/>
      <target dev='vda' bus='virtio'/>
    </disk>
    <interface type='network'>
      <source network='default'/>
      <model type='virtio'/>
    </interface>
    <graphics type='spice'/>
  </devices>
</domain>
EOF

# Define and start
virsh define lightos-vm.xml
virsh start lightos-nce
```

### Method 4: Direct QEMU

```bash
qemu-system-x86_64 \
    -drive file=output-vm/lightos-0.2.1.qcow2,format=qcow2,if=virtio \
    -m 4G \
    -smp 4 \
    -enable-kvm \
    -cpu host \
    -net nic,model=virtio \
    -net user,hostfwd=tcp::2222-:22,hostfwd=tcp::8080-:8080 \
    -vga qxl \
    -display gtk
```

### Method 5: Automated Setup

```bash
./deployment/vm/setup-kvm.sh
```

### Managing KVM VMs

```bash
# List VMs
virsh list --all

# Start
virsh start lightos-nce

# Stop
virsh shutdown lightos-nce

# Force stop
virsh destroy lightos-nce

# Delete
virsh undefine lightos-nce
```

---

## Vagrant Deployment

### Prerequisites

Install Vagrant:

**All platforms**:
- Download from [vagrantup.com](https://www.vagrantup.com/downloads)

**Or via package manager**:
```bash
# macOS
brew install vagrant

# Ubuntu/Debian
sudo apt install vagrant

# Fedora
sudo dnf install vagrant
```

### Quick Start

```bash
# 1. Navigate to VM deployment directory
cd deployment/vm/

# 2. Start VM (first run will provision)
vagrant up

# 3. SSH into VM
vagrant ssh

# 4. Access LLM Training Ground
# From host: http://localhost:8080
```

### Vagrant Commands

```bash
# Check VM status
vagrant status

# Stop VM
vagrant halt

# Restart VM
vagrant reload

# Delete VM
vagrant destroy

# SSH into VM
vagrant ssh

# Run provisioner again
vagrant provision

# Package VM as box
vagrant package --output lightos.box
```

### Using Custom Vagrant Box

If you built a Vagrant box:

```bash
# Add box to Vagrant
vagrant box add lightos output-vm/lightos-0.2.1.box

# Create Vagrantfile
cat > Vagrantfile << 'EOF'
Vagrant.configure("2") do |config|
  config.vm.box = "lightos"
  config.vm.network "forwarded_port", guest: 8080, host: 8080
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "4096"
    vb.cpus = 4
  end
end
EOF

# Start
vagrant up
```

### Multi-Machine Setup (Federated Learning)

```ruby
# Vagrantfile for 3-node cluster
Vagrant.configure("2") do |config|
  config.vm.box = "lightos"

  # Coordinator node
  config.vm.define "coordinator" do |coord|
    coord.vm.hostname = "lightos-coord"
    coord.vm.network "private_network", ip: "192.168.50.10"
    coord.vm.provider "virtualbox" do |vb|
      vb.memory = "8192"
      vb.cpus = 4
    end
  end

  # Worker nodes
  (1..2).each do |i|
    config.vm.define "worker#{i}" do |worker|
      worker.vm.hostname = "lightos-worker#{i}"
      worker.vm.network "private_network", ip: "192.168.50.#{10+i}"
      worker.vm.provider "virtualbox" do |vb|
        vb.memory = "4096"
        vb.cpus = 2
      end
    end
  end
end
```

Start cluster:
```bash
vagrant up
```

---

## Building VM Images

### Prerequisites

```bash
# Ubuntu/Debian
sudo apt install qemu-utils libguestfs-tools virt-builder

# Fedora
sudo dnf install qemu-img guestfs-tools virt-install
```

### Build All Formats

```bash
sudo ./build-system/build-vm-image.sh all
```

This creates:
- `lightos-0.2.1.qcow2` - KVM/QEMU (2-3 GB)
- `lightos-0.2.1.vmdk` - VMware (2-3 GB)
- `lightos-0.2.1.vdi` - VirtualBox (2-3 GB)
- `lightos-0.2.1.box` - Vagrant (2-3 GB compressed)

### Build Specific Format

```bash
# KVM/QEMU
sudo ./build-system/build-vm-image.sh qcow2

# VMware
sudo ./build-system/build-vm-image.sh vmdk

# VirtualBox
sudo ./build-system/build-vm-image.sh vdi

# Vagrant
sudo ./build-system/build-vm-image.sh vagrant
```

### Build Time

Approximate build times:
- **QCOW2**: 10-15 minutes
- **VMDK**: 12-18 minutes (includes conversion)
- **VDI**: 12-18 minutes (includes conversion)
- **OVA**: 15-20 minutes (includes packaging)
- **Vagrant**: 15-20 minutes (includes testing)

### Customization

Edit `build-system/build-vm-image.sh` to customize:

```bash
# VM specifications
DISK_SIZE="20G"       # Disk size
MEMORY_MB="4096"      # RAM
CPU_CORES="4"         # CPU cores

# Additional packages
--install package1,package2,package3

# Custom scripts
--run-command 'your-command-here'
```

---

## Configuration

### System Resources

Recommended specifications:

| Use Case | RAM | CPUs | Disk | Notes |
|----------|-----|------|------|-------|
| **Testing** | 2GB | 2 | 20GB | Minimal |
| **Development** | 4GB | 4 | 30GB | Recommended |
| **Training (small)** | 8GB | 4 | 50GB | For small models |
| **Training (large)** | 16GB+ | 8+ | 100GB+ | For large models |

### Adjust Resources

**VirtualBox**:
- VM Settings → System → Base Memory / Processors

**VMware**:
- VM Settings → Hardware → Memory / Processors

**KVM**:
```bash
virsh edit lightos-nce
# Modify <memory> and <vcpu> values
```

**Vagrant**:
```ruby
config.vm.provider "virtualbox" do |vb|
  vb.memory = "8192"
  vb.cpus = 8
end
```

### Network Configuration

#### NAT (Default)
- VM accessible from host only
- Port forwarding required for services

#### Bridged
- VM gets IP on local network
- Direct access from other devices

**VirtualBox**:
- Settings → Network → Attached to: Bridged Adapter

**KVM**:
```bash
virsh edit lightos-nce
# Change <interface type='network'> to <interface type='bridge'>
```

### LightOS Configuration

Inside VM, edit `/etc/lightos/edge.conf`:

```ini
[spiking]
target_sparsity_percent = 75  # Adjust for VM overhead

[moe]
num_experts = 4  # Reduce for lower memory

[inference]
max_batch_size = 32  # Adjust based on VM RAM
```

Restart services:
```bash
sudo systemctl restart lightos-*
```

---

## Performance Tuning

### Enable Nested Virtualization

For testing LightOS containers within VM:

**KVM on Intel**:
```bash
sudo modprobe -r kvm_intel
sudo modprobe kvm_intel nested=1
echo "options kvm_intel nested=1" | sudo tee /etc/modprobe.d/kvm.conf
```

**KVM on AMD**:
```bash
sudo modprobe -r kvm_amd
sudo modprobe kvm_amd nested=1
echo "options kvm_amd nested=1" | sudo tee /etc/modprobe.d/kvm.conf
```

**VirtualBox**:
```bash
VBoxManage modifyvm LightOS --nested-hw-virt on
```

**VMware**:
Add to `.vmx`:
```ini
vhv.enable = "TRUE"
```

### Use Paravirtualized Drivers

**KVM**: Already using VirtIO (optimal)

**VirtualBox**: Install Guest Additions
```bash
sudo apt install virtualbox-guest-utils virtualbox-guest-dkms
```

**VMware**: Install VMware Tools
```bash
sudo apt install open-vm-tools open-vm-tools-desktop
```

### CPU Pinning (KVM)

For better performance:
```bash
virsh vcpupin lightos-nce 0 0
virsh vcpupin lightos-nce 1 1
virsh vcpupin lightos-nce 2 2
virsh vcpupin lightos-nce 3 3
```

### Storage Optimization

**Use SSD**: Store VM images on SSD for better I/O

**Disable disk cache** (KVM):
```xml
<disk type='file' device='disk'>
  <driver name='qemu' type='qcow2' cache='none' io='native'/>
  ...
</disk>
```

### Memory Ballooning

**KVM**: Enable virtio-balloon
```xml
<devices>
  <memballoon model='virtio'/>
</devices>
```

---

## Troubleshooting

### VM Won't Start

**Problem**: VT-x/AMD-V not available

**Solution**:
1. Enable virtualization in BIOS/UEFI
2. On Windows, disable Hyper-V:
   ```
   bcdedit /set hypervisorlaunchtype off
   ```
3. Reboot

**Problem**: Not enough memory

**Solution**: Reduce VM memory allocation or close other applications

### Slow Performance

**Problem**: VM is slow

**Solutions**:
1. Enable hardware virtualization (KVM, VT-x)
2. Allocate more CPUs/RAM
3. Use paravirtualized drivers
4. Store VM on SSD
5. Disable unnecessary services in guest

**Problem**: Disk I/O slow

**Solution**:
- Use virtio/paravirtualized disk drivers
- Disable disk sync: `-drive cache=unsafe` (testing only)
- Preallocate disk space

### Network Issues

**Problem**: Can't access web UI

**Solutions**:
1. Check port forwarding configuration
2. Verify service is running:
   ```bash
   systemctl status lightrail-scheduler
   ```
3. Check firewall in guest:
   ```bash
   sudo ufw allow 8080/tcp
   ```
4. Test from inside VM:
   ```bash
   curl http://localhost:8080
   ```

**Problem**: Can't SSH to VM

**Solution**:
1. Check SSH service:
   ```bash
   systemctl status sshd
   ```
2. Verify port forwarding (NAT) or IP address (bridged)
3. Check SSH key permissions

### Guest Additions/Tools

**Problem**: Shared folders not working

**Solution**:
```bash
# VirtualBox
sudo apt install virtualbox-guest-utils
sudo adduser $USER vboxsf
sudo mount -t vboxsf ShareName /mnt/shared

# VMware
sudo apt install open-vm-tools
sudo systemctl restart open-vm-tools
```

### Resource Constraints

**Problem**: Out of memory

**Solution**:
1. Reduce MoE expert count: Edit `/etc/lightos/edge.conf`
2. Reduce batch size
3. Enable swap:
   ```bash
   sudo fallocate -l 4G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

**Problem**: Disk full

**Solution**:
1. Clean up logs:
   ```bash
   sudo journalctl --vacuum-time=7d
   ```
2. Remove old packages:
   ```bash
   sudo apt autoremove
   ```
3. Expand disk (see hypervisor documentation)

---

## Comparison: VM vs Bare-Metal vs Cloud

| Aspect | VM | Bare-Metal | Cloud |
|--------|-------|------------|-------|
| **Setup Time** | 5-10 min | 30 min | 15 min |
| **Performance** | Good | Excellent | Very Good |
| **Portability** | Excellent | Low | Medium |
| **Cost** | Free | Hardware cost | Pay-per-use |
| **Use Case** | Development, testing | Production edge | Production cloud |

---

## Next Steps

After deploying your VM:

1. **Change default passwords**:
   ```bash
   passwd
   sudo passwd root
   ```

2. **Update system**:
   ```bash
   sudo apt update && sudo apt upgrade
   ```

3. **Access LLM Training Ground**:
   - http://localhost:8080

4. **Test training run**:
   ```bash
   cd /opt/lightos/llm-training-ground/ui
   python3 run_launcher.py
   ```

5. **Explore documentation**:
   ```bash
   ls /opt/lightos/docs/
   ```

---

## Support

- **VM Issues**: Check hypervisor documentation
- **LightOS Issues**: See `EDGE_DEPLOYMENT_GUIDE.md`
- **GitHub**: https://github.com/your-org/LightOS/issues

---

**LightOS v0.2.1 - Neural Compute Engine**
*Virtual Machines for AI Development*
