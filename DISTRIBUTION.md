# LightOS Cross-Platform Distribution Strategy

**Goal:** Make LightOS easily installable on Windows, macOS, and Linux with multiple distribution methods.

## Distribution Methods Summary

| Method | Platform | Use Case | Installation Time |
|--------|----------|----------|-------------------|
| **pip** (Recommended) | All | Python users, developers | 30 seconds |
| **Docker** | All | Production, Kubernetes | 1 minute |
| **Homebrew** | macOS, Linux | Mac developers | 1 minute |
| **APT/DEB** | Ubuntu/Debian | Linux servers | 30 seconds |
| **Chocolatey/winget** | Windows | Windows users | 1 minute |
| **VM/OVA** | All | Enterprise, air-gapped | 5 minutes |
| **Binary releases** | All | No build tools | 1 minute |
| **One-click installer** | All | Desktop users | 2 minutes |

---

## 1. Python Package (pip) - RECOMMENDED ✅

**Supports:** Windows, macOS, Linux
**Best for:** Developers, Python users, CI/CD

### Installation

```bash
# Install from PyPI (when published)
pip install lightos-accelerated

# Or install from source
git clone https://github.com/lightiam/lightos.git
cd lightos/inference-subsystem/python-bindings
pip install -e .
```

### Usage

```python
from lightos_accelerated import LightDevice, DeviceType
device = LightDevice(DeviceType.NVIDIA, 0)
print(f"✅ LightOS ready: {device.get_properties().name}")
```

### Files Required
- `setup.py` - Build configuration
- `pyproject.toml` - Modern Python packaging
- `MANIFEST.in` - Include C++ sources
- `setup.cfg` - Metadata

---

## 2. Docker Container (Recommended for Production) ✅

**Supports:** Windows, macOS, Linux
**Best for:** Production deployments, Kubernetes, reproducible environments

### Installation

```bash
# Pull from Docker Hub (when published)
docker pull lightos/lightos-inference:latest

# Or build locally
docker build -f deployment/Dockerfile.optimized -t lightos:latest .
```

### Usage

```bash
# Run inference server
docker run -p 50051:50051 --gpus all lightos:latest

# Interactive Python session
docker run -it --gpus all lightos:latest python3
```

### Advantages
- ✅ <700MB container (90% smaller than alternatives)
- ✅ Identical environment across platforms
- ✅ Kubernetes ready
- ✅ No dependency conflicts

---

## 3. Homebrew (macOS + Linux)

**Supports:** macOS (Intel/Apple Silicon), Linux
**Best for:** Mac developers, homebrew users

### Installation

```bash
# Add LightOS tap
brew tap lightiam/lightos

# Install LightOS
brew install lightos

# Verify installation
lightos --version
```

### Usage

```bash
# Start gRPC server
lightos serve --port=50051

# Run inference
lightos infer --model=model.onnx --input=data.npy
```

### Files Required
- `Formula/lightos.rb` - Homebrew formula
- Binary release tarball

---

## 4. APT Package (Ubuntu/Debian)

**Supports:** Ubuntu 20.04+, Debian 11+
**Best for:** Linux servers, production deployments

### Installation

```bash
# Add LightOS repository
curl -fsSL https://packages.lightos.ai/gpg | sudo apt-key add -
echo "deb https://packages.lightos.ai/apt stable main" | sudo tee /etc/apt/sources.list.d/lightos.list

# Install
sudo apt update
sudo apt install lightos

# Verify
lightos --version
```

### Usage

```bash
# Start systemd service
sudo systemctl start lightos
sudo systemctl enable lightos

# Check status
sudo systemctl status lightos
```

### Files Required
- `debian/control` - Package metadata
- `debian/rules` - Build rules
- `debian/lightos.service` - systemd service

---

## 5. Windows Package Manager

### Option A: Chocolatey

```powershell
# Install via Chocolatey
choco install lightos

# Verify
lightos --version
```

### Option B: winget (Windows 11)

```powershell
# Install via winget
winget install LightOS.Inference

# Verify
lightos --version
```

### Files Required
- `lightos.nuspec` - Chocolatey package spec
- MSI installer for winget

---

## 6. VM/OVA Images (VirtualBox, VMware)

**Supports:** Windows, macOS, Linux (as host)
**Best for:** Enterprise, air-gapped environments, demos, training

### Pre-configured VMs

**Three variants:**

#### A. **LightOS Minimal** (8GB disk, 4GB RAM)
- Ubuntu 22.04 LTS
- LightOS inference subsystem
- Python bindings
- CPU-only (no CUDA)
- **Use case:** Testing, development without GPU

#### B. **LightOS GPU** (20GB disk, 16GB RAM, 8GB VRAM)
- Ubuntu 22.04 LTS
- LightOS + CUDA 12.3
- NVIDIA drivers
- Pre-loaded models (ResNet50, BERT-base)
- **Use case:** GPU inference, production testing

#### C. **LightOS Enterprise** (40GB disk, 32GB RAM, 16GB VRAM)
- Ubuntu 22.04 LTS
- LightOS + CUDA + ROCm (AMD support)
- Kubernetes (k3s)
- Prometheus + Grafana dashboards
- Pre-loaded model zoo (50+ models)
- **Use case:** Enterprise deployment, training

### Installation

```bash
# Download OVA
wget https://downloads.lightos.ai/ova/lightos-gpu-v1.0.ova

# Import to VirtualBox
VBoxManage import lightos-gpu-v1.0.ova

# Start VM
VBoxManage startvm "LightOS-GPU"

# SSH into VM (default password: lightos)
ssh lightos@localhost -p 2222
```

### VM Credentials
- **Username:** `lightos`
- **Password:** `lightos123` (change on first login)
- **SSH Port:** 2222 (forwarded from host)
- **gRPC Port:** 50051
- **Web UI:** http://localhost:8080

### Files Required
- `packer/lightos-minimal.pkr.hcl` - Packer template
- `packer/lightos-gpu.pkr.hcl`
- `packer/lightos-enterprise.pkr.hcl`
- Provisioning scripts

---

## 7. Binary Releases (GitHub Releases)

**Supports:** All platforms
**Best for:** Users without build tools

### Pre-built Binaries

Download from GitHub Releases:

```bash
# Linux x86_64
wget https://github.com/lightiam/lightos/releases/download/v1.0.0/lightos-linux-x86_64.tar.gz
tar -xzf lightos-linux-x86_64.tar.gz
sudo mv lightos /usr/local/bin/

# macOS ARM64 (Apple Silicon)
wget https://github.com/lightiam/lightos/releases/download/v1.0.0/lightos-macos-arm64.tar.gz
tar -xzf lightos-macos-arm64.tar.gz
sudo mv lightos /usr/local/bin/

# Windows x86_64
curl -L -o lightos-windows-x86_64.zip https://github.com/lightiam/lightos/releases/download/v1.0.0/lightos-windows-x86_64.zip
unzip lightos-windows-x86_64.zip
# Add to PATH
```

### Platforms Supported
- ✅ Linux x86_64 (glibc 2.31+)
- ✅ Linux ARM64 (Raspberry Pi, Jetson)
- ✅ macOS x86_64 (Intel)
- ✅ macOS ARM64 (Apple Silicon M1/M2/M3)
- ✅ Windows x86_64 (Windows 10+)

---

## 8. One-Click Installers

### Windows Installer (.msi)

```powershell
# Download installer
curl -L -o LightOS-Setup.msi https://downloads.lightos.ai/LightOS-Setup-v1.0.msi

# Install (GUI or CLI)
msiexec /i LightOS-Setup.msi /qn

# Verify
lightos --version
```

**Features:**
- ✅ Automatic PATH configuration
- ✅ Start menu shortcuts
- ✅ Desktop icon (optional)
- ✅ CUDA detection and installation
- ✅ Python integration
- ✅ Uninstaller

### macOS Installer (.pkg)

```bash
# Download installer
curl -L -o LightOS-Installer.pkg https://downloads.lightos.ai/LightOS-Installer-v1.0.pkg

# Install
sudo installer -pkg LightOS-Installer.pkg -target /

# Verify
lightos --version
```

**Features:**
- ✅ Automatic PATH configuration
- ✅ Universal binary (Intel + Apple Silicon)
- ✅ Code signing
- ✅ Notarization for Gatekeeper
- ✅ Homebrew integration check

### Linux Installer (.AppImage)

```bash
# Download AppImage
wget https://downloads.lightos.ai/LightOS-x86_64.AppImage
chmod +x LightOS-x86_64.AppImage

# Run (no installation needed)
./LightOS-x86_64.AppImage --version

# Or install system-wide
./LightOS-x86_64.AppImage --install
```

**Features:**
- ✅ Single file, no dependencies
- ✅ Runs on any Linux distribution
- ✅ Desktop integration
- ✅ No root required

---

## 9. Cloud Images (AWS, Azure, GCP)

### AWS AMI

```bash
# Launch from AWS Marketplace
aws ec2 run-instances \
  --image-id ami-lightos-gpu \
  --instance-type p3.2xlarge \
  --key-name your-key
```

### Azure VM Image

```bash
# Deploy from Azure Marketplace
az vm create \
  --resource-group lightos-rg \
  --name lightos-vm \
  --image lightos-gpu-image \
  --size Standard_NC6
```

### GCP Image

```bash
# Create instance from image
gcloud compute instances create lightos-vm \
  --image=lightos-gpu-image \
  --machine-type=n1-standard-4 \
  --accelerator=type=nvidia-tesla-v100,count=1
```

---

## Comparison Matrix

| Feature | pip | Docker | Homebrew | APT | VM/OVA | Binary | Installer |
|---------|-----|--------|----------|-----|--------|--------|-----------|
| **Cross-platform** | ✅ | ✅ | ⚠️ Mac/Linux | ❌ Linux only | ✅ | ✅ | ✅ |
| **Install time** | 30s | 1m | 1m | 30s | 5m | 1m | 2m |
| **Disk space** | 100MB | 700MB | 150MB | 100MB | 8-40GB | 100MB | 120MB |
| **Auto-updates** | pip | Image tags | brew | apt | ❌ | ❌ | ✅ |
| **Dependencies** | Python | Docker | None | None | None | libc | None |
| **GPU support** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Offline install** | ⚠️ Wheels | ✅ | ❌ | ⚠️ Mirror | ✅ | ✅ | ✅ |
| **Air-gapped** | ⚠️ | ✅ | ❌ | ⚠️ | ✅ | ✅ | ✅ |

---

## Recommended Installation by Use Case

### Development & Testing
```bash
# Quick start for developers
pip install lightos-accelerated
```

### Production (Cloud)
```bash
# Kubernetes deployment
helm install lightos lightos/lightos-inference
```

### Production (On-Premise)
```bash
# Docker Compose
docker-compose up -d lightos
```

### Enterprise (Air-Gapped)
```
Download VM/OVA image → Import to hypervisor → Deploy
```

### Desktop Users
```
Download one-click installer → Run → Done
```

### CI/CD Pipelines
```yaml
# GitHub Actions
- uses: actions/setup-lightos@v1
  with:
    version: '1.0.0'
```

---

## Installation Files Overview

```
distribution/
├── python/
│   ├── setup.py                    # pip package
│   ├── pyproject.toml
│   └── MANIFEST.in
├── docker/
│   ├── Dockerfile.optimized        # <700MB container ✅
│   └── docker-compose.yml
├── homebrew/
│   └── lightos.rb                  # Homebrew formula
├── debian/
│   ├── control                     # DEB package
│   ├── rules
│   └── lightos.service
├── windows/
│   ├── lightos.nuspec              # Chocolatey
│   └── installer.wxs               # MSI installer (WiX)
├── packer/
│   ├── lightos-minimal.pkr.hcl     # VM templates
│   ├── lightos-gpu.pkr.hcl
│   └── lightos-enterprise.pkr.hcl
├── appimage/
│   └── AppImageBuilder.yml         # Linux AppImage
└── cloud/
    ├── aws-ami.pkr.hcl             # AWS AMI
    ├── azure-image.json            # Azure image
    └── gcp-image.json              # GCP image
```

---

## Next Steps

I'll now create the actual implementation files for:

1. ✅ **Python pip package** (setup.py, pyproject.toml)
2. ✅ **Homebrew formula** (lightos.rb)
3. ✅ **Debian package** (control, rules, systemd service)
4. ✅ **VM/OVA templates** (Packer configs)
5. ✅ **GitHub Actions** (Automated builds for all platforms)
6. ✅ **One-click installers** (MSI for Windows, PKG for macOS, AppImage for Linux)

Would you like me to proceed with creating these files?
