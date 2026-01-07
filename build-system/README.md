# LightOS Build System

Build bootable ISO images and container deployments for LightOS Neural Compute Engine.

## Quick Start

```bash
# Build x86-64 ISO
sudo ./lightos-builder.sh amd64 iso

# Build ARM64 ISO
sudo ./lightos-builder.sh arm64 iso

# Build container image
sudo ./lightos-builder.sh amd64 container

# Build everything
sudo ./lightos-builder.sh amd64 all
```

## Directory Structure

```
build-system/
├── lightos-builder.sh          # Main build script
├── edge-profiles/              # Hardware-specific configs
│   ├── raspberry-pi.conf       # Raspberry Pi 4/5
│   ├── jetson-nano.conf        # NVIDIA Jetson devices
│   └── intel-nuc.conf          # Intel NUC / edge servers
├── hardware-detection/         # Auto-detection system
│   └── detect-hardware.sh      # Hardware detection script
├── installer/                  # Installation scripts
│   └── install-lightos.sh      # Bare-metal installer
└── README.md                   # This file
```

## Build Requirements

### Ubuntu 22.04+ (Recommended)

```bash
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

### Fedora/RHEL

```bash
sudo dnf install -y \
    debootstrap \
    squashfs-tools \
    genisoimage \
    syslinux \
    qemu-user-static
```

## Usage

### Build ISO Image

```bash
sudo ./lightos-builder.sh [ARCHITECTURE] [BUILD_TYPE]
```

**Parameters**:
- `ARCHITECTURE`: `amd64` (x86-64) or `arm64` (ARM 64-bit)
- `BUILD_TYPE`: `iso`, `container`, or `all`

**Examples**:

```bash
# Build x86-64 ISO for Intel/AMD systems
sudo ./lightos-builder.sh amd64 iso

# Build ARM64 ISO for Raspberry Pi/Jetson
sudo ./lightos-builder.sh arm64 iso

# Build Docker container
sudo ./lightos-builder.sh amd64 container

# Build everything
sudo ./lightos-builder.sh amd64 all
```

### Output

Built images are in `output/`:
- `lightos-0.2.1-amd64.iso` - Bootable ISO image
- `lightos-0.2.1-amd64.iso.sha256` - Checksum file

### Testing ISO

```bash
# Test in QEMU
qemu-system-x86_64 \
    -cdrom output/lightos-0.2.1-amd64.iso \
    -m 4G \
    -smp 4 \
    -enable-kvm
```

## Edge Profiles

LightOS includes hardware-specific optimizations:

### Raspberry Pi (`raspberry-pi.conf`)
- **Target**: Raspberry Pi 4/5
- **Optimizations**: 80% sparsity, 15W TDP, INT8 quantization
- **Features**: Low-power inference, federated learning worker

### NVIDIA Jetson (`jetson-nano.conf`)
- **Target**: Jetson Nano/Xavier/Orin
- **Optimizations**: GPU acceleration, 75% sparsity, TensorRT
- **Features**: FP16 inference, 30W TDP, P2P model sharing

### Intel NUC (`intel-nuc.conf`)
- **Target**: Intel NUC, edge servers
- **Optimizations**: AVX-512, photonic NPU support, 69% sparsity
- **Features**: High performance, coordinator role, local HVAC

Profiles are automatically selected during first boot based on hardware detection.

## Hardware Detection

The hardware detection system automatically identifies:
- CPU architecture and features (AVX-512, NEON, etc.)
- GPU type (NVIDIA, AMD, Intel)
- Memory capacity
- Photonic NPU availability
- Network capabilities (10GbE, RDMA)

Detection runs automatically on first boot, or manually:

```bash
sudo /opt/lightos/hardware-detection/detect-hardware.sh
```

## Installation

### Method 1: USB Installation

```bash
# Write ISO to USB drive
sudo dd if=output/lightos-0.2.1-amd64.iso of=/dev/sdX bs=4M status=progress

# Boot from USB and select "Install LightOS to Disk"
```

### Method 2: Direct Installation

```bash
# Run installer directly
sudo ./installer/install-lightos.sh
```

### Method 3: Container Deployment

```bash
# Build and run container
docker build -f Dockerfile.edge -t lightos:edge .
docker run -d --privileged -p 8080:8080 lightos:edge
```

## Customization

### Custom Packages

Edit `lightos-builder.sh` and add packages to the debootstrap `--include` list:

```bash
--include="systemd,python3,your-package-here"
```

### Custom Configuration

Modify edge profiles in `edge-profiles/`:

```ini
[spiking]
target_sparsity_percent = 85  # Increase for more efficiency

[moe]
num_experts = 16              # More experts for larger models
```

### Custom Services

Add systemd services to `lightos-builder.sh` in the `install_lightos_services()` function.

## Build Times

Approximate build times on modern hardware:

| Build Type | Architecture | Time | Size |
|------------|--------------|------|------|
| ISO | amd64 | 15-30 min | ~1.5 GB |
| ISO | arm64 | 30-60 min | ~1.4 GB |
| Container | amd64 | 10-15 min | ~800 MB |

## Troubleshooting

### Build Fails

**Problem**: Missing dependencies
```bash
# Check what's missing
./lightos-builder.sh amd64 iso
# Install missing packages listed in error
```

**Problem**: Insufficient disk space
```bash
# Clean up build artifacts
sudo rm -rf build/ output/
# Requires ~10 GB free space
```

### ISO Won't Boot

**Problem**: Secure Boot enabled
- Disable Secure Boot in BIOS/UEFI
- Or sign bootloader with your own keys

**Problem**: USB not bootable
```bash
# Make ISO hybrid bootable
sudo isohybrid output/lightos-0.2.1-amd64.iso
```

### Kernel Modules Not Building

**Problem**: DKMS fails on first boot
```bash
# Install kernel headers
sudo apt install linux-headers-$(uname -r)

# Rebuild manually
cd /usr/src/lightos-0.2.1
sudo dkms build -m lightos -v 0.2.1
sudo dkms install -m lightos -v 0.2.1
```

## Advanced Usage

### Cross-Compilation

Build ARM64 image on x86-64 host:

```bash
# Install QEMU user-mode emulation
sudo apt install qemu-user-static binfmt-support

# Build ARM64 ISO
sudo ./lightos-builder.sh arm64 iso
```

### Custom Kernel

Replace the kernel in `create_base_rootfs()`:

```bash
# Build custom kernel
cd /path/to/linux-source
make deb-pkg

# Install in rootfs
sudo dpkg -i --root="${ROOTFS_DIR}" linux-image-*.deb
```

### Minimal Build

For extremely resource-constrained devices:

```bash
# Edit lightos-builder.sh
# Change debootstrap variant to 'minbase'
--variant=minbase
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Build LightOS

on: [push]

jobs:
  build:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y debootstrap squashfs-tools genisoimage
      - name: Build ISO
        run: sudo ./build-system/lightos-builder.sh amd64 iso
      - name: Upload artifact
        uses: actions/upload-artifact@v2
        with:
          name: lightos-iso
          path: output/lightos-*.iso
```

### GitLab CI

```yaml
build:
  image: ubuntu:22.04
  script:
    - apt-get update && apt-get install -y debootstrap squashfs-tools genisoimage
    - ./build-system/lightos-builder.sh amd64 iso
  artifacts:
    paths:
      - output/lightos-*.iso
```

## Contributing

To add support for new hardware:

1. Create new profile in `edge-profiles/`
2. Add detection logic in `hardware-detection/detect-hardware.sh`
3. Test on target hardware
4. Submit pull request

## License

LightOS is released under the MIT License. See LICENSE file for details.

---

**LightOS Build System v0.2.1**
*Build Once, Deploy Everywhere*
