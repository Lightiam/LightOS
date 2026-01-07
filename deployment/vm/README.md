# LightOS VM Deployment

Deploy LightOS Neural Compute Engine as a virtual machine on your PC.

## Quick Start

### VirtualBox (Easiest - Windows/macOS/Linux)

```bash
# 1. Build VM image
sudo ../../build-system/build-vm-image.sh vdi

# 2. Auto-setup and start
./setup-virtualbox.sh

# 3. Access at http://localhost:8080
```

### Vagrant (Developer Workflow)

```bash
# One command - builds and starts VM
vagrant up

# SSH into VM
vagrant ssh

# Access at http://localhost:8080
```

### KVM/QEMU (Linux - Best Performance)

```bash
# 1. Build QCOW2 image
sudo ../../build-system/build-vm-image.sh qcow2

# 2. Auto-setup and start
./setup-kvm.sh

# 3. Find VM IP: virsh domifaddr lightos-nce
```

## What's Included

✅ Pre-configured Ubuntu 22.04 LTS with LightOS
✅ All kernel modules and services
✅ LLM Training Ground UI (port 8080)
✅ Automatic hardware detection
✅ Guest additions (VirtualBox/VMware/KVM)

## System Requirements

- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 20GB (thin-provisioned, grows as needed)
- **CPU**: 2 cores minimum, 4 recommended
- **Virtualization**: VT-x/AMD-V enabled in BIOS

## Default Credentials

- **Username**: `lightos`
- **Password**: `lightos`

⚠️ **Change immediately after first login!**

## Build Options

Build specific VM image format:

```bash
# KVM/QEMU (.qcow2)
sudo ../../build-system/build-vm-image.sh qcow2

# VMware (.vmdk + .vmx)
sudo ../../build-system/build-vm-image.sh vmdk

# VirtualBox (.vdi)
sudo ../../build-system/build-vm-image.sh vdi

# VirtualBox OVA package
sudo ../../build-system/build-vm-image.sh ova

# Vagrant box
sudo ../../build-system/build-vm-image.sh vagrant

# All formats
sudo ../../build-system/build-vm-image.sh all
```

Output: `output-vm/lightos-0.2.1.*`

## Manual Setup

### VirtualBox

1. Import `lightos-0.2.1.ova` via File → Import Appliance
2. Or create new VM and attach `lightos-0.2.1.vdi`
3. Configure port forwarding: 2222→22, 8080→8080
4. Start VM

### VMware Workstation/Fusion

1. File → Open → Select `lightos-0.2.1.vmx`
2. Start VM

### KVM with virt-manager

1. Open virt-manager
2. New VM → Import existing disk
3. Select `lightos-0.2.1.qcow2`
4. OS: Ubuntu 22.04, RAM: 4GB, CPUs: 4
5. Start

### Direct QEMU

```bash
qemu-system-x86_64 \
    -drive file=../../output-vm/lightos-0.2.1.qcow2,format=qcow2 \
    -m 4G -smp 4 -enable-kvm \
    -net nic -net user,hostfwd=tcp::8080-:8080 \
    -vga qxl -display gtk
```

## Accessing Services

### From Host Machine

- **LLM Training Ground**: http://localhost:8080
- **SSH**: `ssh -p 2222 lightos@localhost` (if port forwarding configured)

### From Within VM

```bash
# Check services
systemctl status lightos-*

# View logs
journalctl -u lightos-autopilot -f

# Hardware detection report
cat /etc/lightos/hardware-report.json

# Start training
cd /opt/lightos/llm-training-ground/ui
python3 run_launcher.py
```

## Shared Folders

### VirtualBox

VM Settings → Shared Folders → Add folder

In VM:
```bash
sudo mount -t vboxsf ShareName /mnt/shared
```

### VMware

VM Settings → Options → Shared Folders → Enable

Automatically mounted in `/mnt/hgfs/`

### Vagrant

Automatically shares project directory as `/vagrant`

## Performance Tips

1. **Enable hardware virtualization** in BIOS (VT-x/AMD-V)
2. **Allocate more resources**:
   - 8GB RAM for better performance
   - 4+ CPU cores
3. **Use SSD** for VM storage
4. **Enable KVM acceleration** (Linux):
   ```bash
   # Check KVM is available
   lsmod | grep kvm
   # Use -enable-kvm flag with QEMU
   ```

## Troubleshooting

### VM Won't Start

- Enable VT-x/AMD-V in BIOS
- On Windows: Disable Hyper-V
- Check RAM allocation isn't too high

### Can't Access Web UI

```bash
# Check service status
systemctl status lightrail-scheduler

# Check port forwarding
# VirtualBox: VM Settings → Network → Port Forwarding
# KVM: virsh domifaddr lightos-nce

# Allow through firewall
sudo ufw allow 8080/tcp
```

### Slow Performance

- Enable hardware virtualization
- Increase CPU/RAM allocation
- Use paravirtualized drivers (virtio for KVM)
- Install guest additions:
  ```bash
  # VirtualBox
  sudo apt install virtualbox-guest-utils

  # VMware
  sudo apt install open-vm-tools
  ```

### Network Issues

**NAT (default)**: VM accessible from host only
- Requires port forwarding
- Good for development

**Bridged**: VM gets IP on local network
- Direct access from anywhere on network
- Good for multi-machine setups

## File Structure

```
deployment/vm/
├── README.md                 # This file
├── VM_DEPLOYMENT_GUIDE.md    # Comprehensive guide
├── setup-virtualbox.sh       # VirtualBox automation
├── setup-kvm.sh             # KVM automation
└── Vagrantfile              # Vagrant configuration
```

## Documentation

- **Comprehensive Guide**: [VM_DEPLOYMENT_GUIDE.md](VM_DEPLOYMENT_GUIDE.md)
- **Edge Deployment**: [../edge/EDGE_DEPLOYMENT_GUIDE.md](../edge/EDGE_DEPLOYMENT_GUIDE.md)
- **Build System**: [../../build-system/README.md](../../build-system/README.md)

## Use Cases

| Use Case | Recommended Platform | RAM | CPUs |
|----------|---------------------|-----|------|
| **Quick Testing** | VirtualBox | 2GB | 2 |
| **Development** | Vagrant | 4GB | 4 |
| **Performance Testing** | KVM | 8GB | 4 |
| **Multi-Node** | Vagrant + libvirt | 4GB/node | 2/node |

## Next Steps

1. **Change default passwords**
2. **Update system**: `sudo apt update && sudo apt upgrade`
3. **Explore LLM Training Ground**: http://localhost:8080
4. **Read full documentation**: `/opt/lightos/docs/`
5. **Try training a model**!

## Support

- **GitHub Issues**: https://github.com/your-org/LightOS/issues
- **Documentation**: Full guides in this directory
- **Community**: https://lightos.dev/community

---

**LightOS v0.2.1 - Neural Compute Engine**
*Virtual Machines for AI Development*
