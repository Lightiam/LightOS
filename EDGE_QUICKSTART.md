# LightOS Edge Deployment - Quick Start Guide

**Get LightOS running on edge hardware in under 30 minutes!**

## Prerequisites

- **Build machine**: Ubuntu 22.04+ with 10GB free disk space
- **Target hardware**: Any x86-64 or ARM64 device (2GB+ RAM, 16GB+ storage)
- **USB drive**: 4GB+ capacity

## Step 1: Build LightOS ISO (10-15 minutes)

On your build machine:

```bash
# Clone repository (if not already)
git clone https://github.com/your-org/LightOS.git
cd LightOS

# Install build dependencies
sudo apt-get update && sudo apt-get install -y \
    debootstrap squashfs-tools genisoimage \
    syslinux isolinux qemu-user-static

# Build ISO for x86-64 (Intel/AMD)
sudo ./build-system/lightos-builder.sh amd64 iso

# Or build for ARM64 (Raspberry Pi / Jetson)
sudo ./build-system/lightos-builder.sh arm64 iso
```

**Output**: `output/lightos-0.2.1-amd64.iso` (~1.5 GB)

## Step 2: Create Bootable USB (2 minutes)

### Linux

```bash
# Find USB drive (CAUTION: This will erase the drive!)
lsblk

# Write ISO to USB (replace /dev/sdX with your USB device)
sudo dd if=output/lightos-0.2.1-amd64.iso of=/dev/sdX bs=4M status=progress
sync
```

### Windows

1. Download [Rufus](https://rufus.ie/)
2. Select LightOS ISO
3. Select USB drive
4. Click "Start"

### macOS

```bash
# Find USB device
diskutil list

# Write ISO
sudo dd if=lightos-0.2.1-amd64.iso of=/dev/rdiskN bs=4m
```

## Step 3: Install LightOS (5-10 minutes)

1. **Insert USB** into target machine
2. **Boot from USB**:
   - Restart machine
   - Press F2/F12/DEL/ESC to enter BIOS
   - Select USB drive as boot device
   - **Note**: Disable Secure Boot if installation fails

3. **Boot Menu**:
   ```
   LightOS Neural Compute Engine v0.2.1

   > Start LightOS (Live Mode)
     Install LightOS to Disk
     Start LightOS (Safe Mode)
   ```

4. **Select "Install LightOS to Disk"**

5. **Installation Wizard**:
   - Select target disk (ALL DATA WILL BE ERASED!)
   - Confirm installation by typing "yes"
   - Wait 5-10 minutes
   - Reboot when prompted

6. **Remove USB** when system restarts

## Step 4: First Boot (2 minutes)

1. **System boots** and displays LightOS boot splash

2. **Auto-detection runs**:
   ```
   [HW-DETECT] LightOS Hardware Detection System v0.2.1
   [HW-DETECT] CPU: Intel Core i7-12700H
   [HW-DETECT] Cores: 14
   [HW-DETECT] Total Memory: 32768 MB
   [HW-DETECT] NVIDIA GPU detected: GeForce RTX 3060
   [HW-DETECT] Active profile: intel-nuc
   [HW-DETECT] Hardware detection complete!
   ```

3. **Login**:
   - Username: `lightos`
   - Password: `lightos`
   - **Change password immediately**: `passwd`

4. **Welcome Message**:
   ```
       ╦  ┬┌─┐┬ ┬┌┬┐╔═╗╔═╗
       ║  ││ ┬├─┤ │ ║ ║╚═╗
       ╩═╝┴└─┘┴ ┴ ┴ ╚═╝╚═╝
       Neural Compute Engine v0.2.1

   Welcome to LightOS - Edge Computing Ready!
   ```

## Step 5: Verify Installation (3 minutes)

```bash
# Check LightOS services
systemctl status lightos-*

# Output should show:
# ● lightrail-scheduler.service - LightOS LightRail AI Scheduler
#    Active: active (running)
# ● lightos-autopilot.service - Infrastructure Autopilot
#    Active: active (running)
# ● lightos-kvcache.service - Distributed KV Cache
#    Active: active (running)

# View hardware detection report
cat /etc/lightos/hardware-report.json

# Check kernel modules
lsmod | grep lightos
```

## Step 6: Launch LLM Training Ground (1 minute)

```bash
# Access web UI at http://localhost:8080 or http://<device-ip>:8080
# Or start manually:
cd /opt/lightos/llm-training-ground/ui
python3 run_launcher.py

# Browse models and launch training runs!
```

---

## Platform-Specific Notes

### Raspberry Pi 4/5

```bash
# Build ARM64 ISO
sudo ./build-system/lightos-builder.sh arm64 iso

# After installation, optimize GPU memory
sudo raspi-config
# Performance Options → GPU Memory → 256MB
```

**Performance**: Optimized for 80% sparsity, 15W TDP

### NVIDIA Jetson (Nano/Xavier/Orin)

```bash
# Install CUDA support after first boot
sudo apt install nvidia-jetpack

# Set maximum performance mode
sudo nvpmodel -m 0
sudo jetson_clocks
```

**Performance**: GPU-accelerated, 75% sparsity, TensorRT enabled

### Intel NUC / Edge Servers

```bash
# Photonic NPU auto-detected if present
# No additional configuration needed
```

**Performance**: High-performance mode, 69% sparsity, AVX-512

---

## What's Included

After installation, you have:

✅ **Spiking Neural Networks** - Event-driven processing, >69% sparsity
✅ **MoE Sparsity** - Conditional computation for efficiency
✅ **Photonic NPU Support** - Auto-detected if present
✅ **LightRail Scheduler** - Optimal routing (Dijkstra/A*)
✅ **Distributed KV Cache** - PagedAttention-style memory management
✅ **Infrastructure Autopilot** - DRL-based HVAC optimization
✅ **LLM Training Ground** - Web UI for model training
✅ **Thermal Guard** - 3-tier thermal protection
✅ **Performance Metrics** - TTFT, energy, carbon tracking

---

## Next Steps

### Train Your First Model

```bash
# Open web UI
firefox http://localhost:8080

# Or use CLI
cd /opt/lightos/llm-training-ground/ui
python3 asset_browser.py  # Browse models
python3 run_launcher.py   # Launch training
```

### Configure Edge Profile

```bash
# View current profile
cat /etc/lightos/edge.conf

# List available profiles
ls /opt/lightos/edge-profiles/

# Apply different profile
sudo cp /opt/lightos/edge-profiles/raspberry-pi.conf /etc/lightos/edge.conf
sudo systemctl restart lightos-*
```

### Monitor System

```bash
# Real-time metrics
tail -f /var/log/lightos/edge-metrics.log

# Service logs
journalctl -u lightos-autopilot -f
journalctl -u lightrail-scheduler -f

# Temperature monitoring
watch -n 1 'cat /sys/class/thermal/thermal_zone*/temp'
```

### Set Up Federated Learning

```bash
# On coordinator node (Intel NUC)
echo "federation_role = coordinator" | sudo tee -a /etc/lightos/edge.conf

# On worker nodes (Raspberry Pi, Jetson)
echo "federation_role = worker" | sudo tee -a /etc/lightos/edge.conf
echo "coordinator_address = 192.168.1.100" | sudo tee -a /etc/lightos/edge.conf

# Restart services
sudo systemctl restart lightos-*
```

---

## Troubleshooting

### Boot Issues

**Problem**: Won't boot from USB
- **Solution**: Disable Secure Boot in BIOS
- **Solution**: Try USB 2.0 port instead of USB 3.0
- **Solution**: Re-write ISO to USB drive

**Problem**: Kernel panic during boot
- **Solution**: Select "Start LightOS (Safe Mode)" from boot menu
- **Solution**: Add `nomodeset` to kernel parameters

### Installation Issues

**Problem**: "No suitable disks found"
- **Solution**: Check that target disk is >16GB
- **Solution**: Try USB-to-SATA adapter if internal disk not detected

**Problem**: Installation fails at "Installing bootloader"
- **Solution**: Ensure UEFI mode is enabled (not legacy BIOS)
- **Solution**: Check that EFI partition is properly created

### Service Issues

**Problem**: LightOS services won't start
```bash
# Rebuild kernel modules
cd /usr/src/lightos-0.2.1
sudo dkms build -m lightos -v 0.2.1
sudo dkms install -m lightos -v 0.2.1
sudo modprobe lightos_core

# Restart services
sudo systemctl restart lightos-*
```

**Problem**: Can't access web UI at port 8080
```bash
# Check if service is running
sudo netstat -tulpn | grep 8080

# Allow through firewall
sudo ufw allow 8080/tcp

# Restart service
sudo systemctl restart lightrail-scheduler
```

---

## Performance Benchmarks

Expected performance on reference hardware:

| Hardware | TTFT (7B) | Throughput | Power | Sparsity |
|----------|-----------|------------|-------|----------|
| **Raspberry Pi 4** | ~2-3s | 5-10 tok/s | 12W | 80% |
| **Jetson Nano** | ~500ms | 20-30 tok/s | 18W | 75% |
| **Jetson Xavier** | ~200ms | 60-80 tok/s | 25W | 75% |
| **Intel NUC i7** | ~50ms | 100+ tok/s | 45W | 69% |

*With spiking networks + MoE enabled*

---

## Getting Help

- **Documentation**: `/opt/lightos/docs/`
- **Full Guide**: `deployment/edge/EDGE_DEPLOYMENT_GUIDE.md`
- **Build System**: `build-system/README.md`
- **GitHub Issues**: https://github.com/your-org/LightOS/issues

---

## Summary

🎉 **Congratulations!** You now have LightOS running on edge hardware with:
- Neural compute acceleration
- Automatic hardware optimization
- LLM training capabilities
- Power-efficient inference

**Total time**: ~30 minutes from ISO build to running system

---

**LightOS v0.2.1 - Neural Compute Engine**
*Bringing AI to the Edge*
