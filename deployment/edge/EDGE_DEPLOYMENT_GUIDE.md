# LightOS Edge Deployment Guide

**Version**: 0.2.1
**Last Updated**: January 2026

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [System Requirements](#system-requirements)
4. [Building LightOS ISO](#building-lightos-iso)
5. [Installation Methods](#installation-methods)
6. [Edge Device Profiles](#edge-device-profiles)
7. [Hardware Detection](#hardware-detection)
8. [Container Deployment](#container-deployment)
9. [Configuration](#configuration)
10. [Performance Optimization](#performance-optimization)
11. [Troubleshooting](#troubleshooting)

---

## Overview

LightOS can now be deployed as a **complete, bootable operating system** for edge computing devices. This deployment methodology provides:

- ✅ **Bare-metal performance** - Direct hardware access without virtualization overhead
- ✅ **Universal compatibility** - Runs on x86-64, ARM64, Raspberry Pi, Jetson, Intel NUC
- ✅ **Auto-configuration** - Intelligent hardware detection and optimization
- ✅ **Edge-optimized** - Power-efficient, low-latency, federated learning ready
- ✅ **Neural compute** - Spiking networks, MoE, Photonic NPU support

### Architecture

```
┌─────────────────────────────────────────────────┐
│           LightOS Neural Compute Engine          │
├─────────────────────────────────────────────────┤
│  LLM Training Ground  │  Infrastructure Autopilot│
├─────────────────────────────────────────────────┤
│  Spiking Engine │ MoE Module │ Photonic Driver  │
├─────────────────────────────────────────────────┤
│        LightRail Scheduler │ KV Cache            │
├─────────────────────────────────────────────────┤
│               Kernel Modules                     │
├─────────────────────────────────────────────────┤
│           Linux Kernel (6.x)                     │
├─────────────────────────────────────────────────┤
│               Hardware Layer                     │
│   x86-64 │ ARM64 │ GPU │ Photonic NPU           │
└─────────────────────────────────────────────────┘
```

---

## Quick Start

### 30-Second Deployment

```bash
# 1. Build LightOS ISO (requires Ubuntu 22.04+)
cd /path/to/LightOS
sudo ./build-system/lightos-builder.sh amd64 iso

# 2. Write to USB drive
sudo dd if=output/lightos-0.2.1-amd64.iso of=/dev/sdX bs=4M status=progress

# 3. Boot from USB and install
# Select "Install LightOS to Disk" from boot menu

# 4. After reboot, hardware auto-detection runs
# Access LLM Training Ground at http://localhost:8080
```

---

## System Requirements

### Minimum Requirements

| Component | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| **CPU** | 2 cores, 1.5 GHz | 4+ cores, 2.5+ GHz | ARM64 or x86-64 |
| **RAM** | 2 GB | 8+ GB | 4GB for serious workloads |
| **Storage** | 16 GB | 128+ GB | SSD strongly recommended |
| **Network** | 100 Mbps | 1+ Gbps | Required for distributed training |

### Supported Hardware Platforms

#### x86-64 Platforms
- ✅ Intel NUC (all generations)
- ✅ Dell OptiPlex / PowerEdge (edge servers)
- ✅ HP ProDesk / ProLiant MicroServer
- ✅ Lenovo ThinkCentre / ThinkStation
- ✅ Generic x86-64 desktop/server hardware
- ✅ VMware / VirtualBox / KVM (for testing)

#### ARM64 Platforms
- ✅ Raspberry Pi 4 (4GB+ RAM recommended)
- ✅ Raspberry Pi 5
- ✅ NVIDIA Jetson Nano
- ✅ NVIDIA Jetson Xavier NX
- ✅ NVIDIA Jetson Orin
- ✅ Ampere Altra / Altra Max servers

#### Accelerators (Optional)
- ✅ NVIDIA GPUs (CUDA 11+)
- ✅ AMD GPUs (ROCm)
- ✅ Intel integrated GPUs
- ✅ Photonic NPUs (auto-detected)

---

## Building LightOS ISO

### Prerequisites

Install build dependencies on Ubuntu 22.04+:

```bash
sudo apt-get update
sudo apt-get install -y \
    debootstrap \
    squashfs-tools \
    genisoimage \
    syslinux \
    isolinux \
    qemu-user-static \
    binfmt-support \
    grub-efi-amd64-bin \
    grub-pc-bin
```

### Build for x86-64

```bash
cd /path/to/LightOS
sudo ./build-system/lightos-builder.sh amd64 iso
```

**Build time**: 15-30 minutes (depending on hardware)
**Output**: `output/lightos-0.2.1-amd64.iso` (~1.5 GB)

### Build for ARM64

```bash
# Requires ARM64 host or QEMU user-mode emulation
sudo ./build-system/lightos-builder.sh arm64 iso
```

**Build time**: 30-60 minutes
**Output**: `output/lightos-0.2.1-arm64.iso`

### Build All Formats

```bash
# Build ISO + Container image
sudo ./build-system/lightos-builder.sh amd64 all
```

### Verify ISO

```bash
# Check SHA256 checksum
sha256sum -c output/lightos-0.2.1-amd64.iso.sha256

# Test in QEMU
qemu-system-x86_64 \
    -cdrom output/lightos-0.2.1-amd64.iso \
    -m 4G \
    -smp 4 \
    -enable-kvm
```

---

## Installation Methods

### Method 1: USB Installation (Recommended)

#### 1. Write ISO to USB Drive

**Linux**:
```bash
# Find USB device (e.g., /dev/sdb)
lsblk

# Write ISO (CAUTION: This erases USB drive!)
sudo dd if=output/lightos-0.2.1-amd64.iso of=/dev/sdX bs=4M status=progress
sync
```

**Windows**:
- Use [Rufus](https://rufus.ie/) or [balenaEtcher](https://www.balena.io/etcher/)
- Select LightOS ISO
- Select USB drive
- Click "Start"

**macOS**:
```bash
# Find USB device
diskutil list

# Unmount (not eject!)
diskutil unmountDisk /dev/diskN

# Write ISO
sudo dd if=lightos-0.2.1-amd64.iso of=/dev/rdiskN bs=4m
```

#### 2. Boot from USB

1. Insert USB drive into target machine
2. Reboot and enter BIOS/UEFI (usually F2, F12, DEL, or ESC)
3. Set USB as first boot device
4. Save and exit

#### 3. Install to Disk

Boot menu options:
- **Start LightOS** - Live mode (try without installing)
- **Install LightOS to Disk** - Full installation
- **Start LightOS (Safe Mode)** - For troubleshooting

Select "Install LightOS to Disk" and follow the installer prompts.

**Installation time**: 5-15 minutes

#### 4. First Boot

After installation:
1. Remove USB drive
2. Reboot
3. Hardware auto-detection runs automatically
4. Login: `lightos` / `lightos` (change password immediately!)

### Method 2: PXE Network Boot

For deploying to multiple edge devices:

```bash
# Setup PXE server (separate guide)
./deployment/edge/pxe-server-setup.sh

# Configure DHCP to point to PXE server
# Boot edge devices via network
```

### Method 3: Direct Disk Image

For embedded systems without optical drives:

```bash
# Write directly to disk (CAUTION!)
sudo ./build-system/installer/install-lightos.sh
```

---

## Edge Device Profiles

LightOS automatically detects hardware and applies optimal configurations.

### Raspberry Pi Profile

**Target**: Raspberry Pi 4/5
**Optimizations**:
- 80% sparsity target (power efficiency)
- Delta encoding for spiking networks
- 4 MoE experts, top-k=1
- INT8 quantization
- 15W TDP limit

**Config**: `/etc/lightos/edge.conf` (auto-applied)

### NVIDIA Jetson Profile

**Target**: Jetson Nano / Xavier / Orin
**Optimizations**:
- GPU acceleration enabled
- 75% sparsity target
- 8 MoE experts, top-k=2
- FP16 quantization
- TensorRT optimization
- 30W TDP limit

**Manual override**:
```bash
sudo cp /opt/lightos/edge-profiles/jetson-nano.conf /etc/lightos/edge.conf
sudo systemctl restart lightos-*
```

### Intel NUC Profile

**Target**: Intel NUC, edge servers
**Optimizations**:
- AVX-512 acceleration (if available)
- Photonic NPU support
- 69% sparsity target
- 16 MoE experts, top-k=2
- INT8/FP16 quantization
- 65W TDP limit
- Can act as federated learning coordinator

**Features**:
- Local HVAC control (single rack)
- High-performance inference
- Multi-GPU support

---

## Hardware Detection

### Automatic Detection

On first boot, LightOS runs comprehensive hardware detection:

```bash
# View detection results
cat /etc/lightos/hardware-report.json

# Example output:
{
  "architecture": "amd64",
  "platform": "intel-nuc",
  "memory_mb": 32768,
  "gpu": "nvidia",
  "photonic_npu": false,
  "selected_profile": "intel-nuc",
  "cpu_info": {
    "model": "Intel Core i7-12700H",
    "cores": 14,
    "threads": 20
  }
}
```

### Manual Detection

Re-run hardware detection:

```bash
sudo /opt/lightos/hardware-detection/detect-hardware.sh
```

### Override Profile

Force a specific profile:

```bash
# List available profiles
ls /opt/lightos/edge-profiles/

# Apply profile
sudo cp /opt/lightos/edge-profiles/jetson-nano.conf /etc/lightos/edge.conf
sudo systemctl restart lightos-*
```

---

## Container Deployment

For lightweight deployment without full OS install:

### Docker

```bash
# Build container
cd /path/to/LightOS
docker build -f build-system/Dockerfile.edge -t lightos:edge .

# Run container
docker run -d \
    --name lightos-edge \
    --privileged \
    -v /lib/modules:/lib/modules:ro \
    -p 8080:8080 \
    -p 50051:50051 \
    lightos:edge
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: lightos-edge
spec:
  selector:
    matchLabels:
      app: lightos
  template:
    metadata:
      labels:
        app: lightos
    spec:
      containers:
      - name: lightos
        image: lightos:edge
        securityContext:
          privileged: true
        ports:
        - containerPort: 8080
        - containerPort: 50051
        volumeMounts:
        - name: modules
          mountPath: /lib/modules
          readOnly: true
      volumes:
      - name: modules
        hostPath:
          path: /lib/modules
```

---

## Configuration

### System Configuration

**Main config**: `/etc/lightos/edge.conf`

```ini
[edge]
mode = edge
max_memory_mb = 4096
max_cpu_cores = 4
max_power_watts = 25

[spiking]
enabled = true
target_sparsity_percent = 75
encoding_method = delta

[moe]
enabled = true
num_experts = 8
top_k = 1

[autopilot]
mode = local_only
thermal_monitoring = true
```

### Service Management

```bash
# Check service status
systemctl status lightos-*

# View logs
journalctl -u lightos-autopilot -f
journalctl -u lightrail-scheduler -f

# Restart services
sudo systemctl restart lightos-autopilot
```

### LLM Training Ground

Access at: `http://localhost:8080` or `http://<device-ip>:8080`

Configuration: `/opt/lightos/llm-training-ground/ui/config.yaml`

---

## Performance Optimization

### CPU Optimization

```bash
# Set performance governor
for i in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    echo performance | sudo tee $i
done

# Enable turbo boost (Intel)
echo 0 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo
```

### Memory Optimization

```bash
# Optimize for low-latency
echo 10 | sudo tee /proc/sys/vm/swappiness
echo 1 | sudo tee /proc/sys/vm/overcommit_memory

# Huge pages for ML workloads
echo 2048 | sudo tee /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages
```

### Network Optimization

```bash
# Increase network buffers
sudo sysctl -w net.core.rmem_max=134217728
sudo sysctl -w net.core.wmem_max=134217728
```

### Thermal Management

```bash
# Monitor temperatures
watch -n 1 'cat /sys/class/thermal/thermal_zone*/temp | awk "{print \$1/1000 \"°C\"}"'

# View thermal throttling
journalctl -u lightos-autopilot | grep throttle
```

---

## Troubleshooting

### Boot Issues

**Problem**: System won't boot from USB
**Solution**:
- Ensure Secure Boot is disabled in BIOS
- Try different USB port (USB 2.0 often more compatible)
- Re-write ISO to USB drive
- Verify ISO checksum

**Problem**: Kernel panic on boot
**Solution**:
- Boot in safe mode (select from boot menu)
- Add `nomodeset` to kernel parameters
- Check hardware compatibility

### Kernel Module Issues

**Problem**: `lightos_core` module won't load
**Solution**:
```bash
# Check kernel version compatibility
uname -r
ls /lib/modules/$(uname -r)

# Rebuild modules
cd /usr/src/lightos-0.2.1
sudo dkms build -m lightos -v 0.2.1
sudo dkms install -m lightos -v 0.2.1
```

### Service Issues

**Problem**: LightOS services failing to start
**Solution**:
```bash
# Check service status
systemctl status lightos-autopilot.service

# View detailed logs
journalctl -xe -u lightos-autopilot

# Check module dependencies
lsmod | grep lightos
```

### Performance Issues

**Problem**: High CPU usage
**Solution**:
```bash
# Check which service is consuming CPU
top -H

# Reduce MoE experts in /etc/lightos/edge.conf
num_experts = 4

# Increase sparsity target
target_sparsity_percent = 85
```

**Problem**: Out of memory
**Solution**:
```bash
# Check memory usage
free -h

# Reduce KV cache size in edge.conf
kv_cache_memory_mb = 256

# Enable zram compression
sudo apt install zram-config
```

### Network Issues

**Problem**: Can't access LLM Training Ground UI
**Solution**:
```bash
# Check if service is running
sudo netstat -tulpn | grep 8080

# Allow through firewall
sudo ufw allow 8080/tcp

# Restart service
sudo systemctl restart lightrail-scheduler
```

---

## Hardware-Specific Guides

### Raspberry Pi 4/5

```bash
# Enable hardware acceleration
sudo raspi-config
# Select: Performance Options → GPU Memory → 256MB

# Optimize for ML workloads
echo "arm_boost=1" | sudo tee -a /boot/config.txt
sudo reboot
```

### NVIDIA Jetson

```bash
# Install CUDA toolkit
sudo apt install nvidia-jetpack

# Set power mode to maximum performance
sudo nvpmodel -m 0
sudo jetson_clocks

# Verify GPU
nvidia-smi
```

### Intel NUC

```bash
# Install Intel drivers
sudo apt install intel-gpu-tools

# Check CPU features
lscpu | grep -E "avx|sse"

# Monitor GPU usage
intel_gpu_top
```

---

## Next Steps

After successful deployment:

1. **Change default passwords**:
   ```bash
   passwd lightos
   sudo passwd root
   ```

2. **Update system**:
   ```bash
   sudo apt update && sudo apt upgrade
   ```

3. **Configure networking** for your environment

4. **Test LLM Training Ground**:
   - Open http://localhost:8080
   - Browse model catalog
   - Launch test training run

5. **Set up federated learning** (optional):
   - Configure coordinator node
   - Register worker nodes
   - Launch distributed training

6. **Monitor performance**:
   ```bash
   tail -f /var/log/lightos/edge-metrics.log
   ```

---

## Support

- **Documentation**: `/opt/lightos/docs/`
- **GitHub Issues**: https://github.com/your-org/LightOS/issues
- **Community Forum**: https://lightos.dev/forum

---

**LightOS v0.2.1 - Neural Compute Engine**
*Bringing AI to the Edge*
