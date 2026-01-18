# LightOS Installation Guide for Windows

Complete step-by-step guide for installing LightOS on Windows 10/11.

---

## Choose Your Installation Method

| Method | Recommended For | Installation Time | Difficulty |
|--------|----------------|-------------------|------------|
| **[Python pip](#method-1-python-pip-recommended)** ⭐ | Developers, Python users | 2-5 minutes | ⭐ Easy |
| **[Chocolatey](#method-2-chocolatey)** | Windows power users | 3-5 minutes | ⭐ Easy |
| **[winget](#method-3-winget-windows-11)** | Windows 11 users | 2-3 minutes | ⭐ Easy |
| **[MSI Installer](#method-4-msi-installer-one-click)** | Desktop users, beginners | 3-5 minutes | ⭐ Very Easy |
| **[Docker Desktop](#method-5-docker-desktop)** | Production, containers | 5-10 minutes | ⭐⭐ Medium |
| **[From Source](#method-6-build-from-source)** | Contributors, advanced users | 15-30 minutes | ⭐⭐⭐ Advanced |

---

## Prerequisites

Before installing LightOS, ensure your system meets these requirements:

### System Requirements

**Minimum:**
- Windows 10 (64-bit) version 1909 or later
- 4GB RAM
- 2GB free disk space
- Python 3.8 or later (for pip installation)

**Recommended:**
- Windows 11 (64-bit)
- 8GB+ RAM
- 5GB free disk space
- NVIDIA GPU with CUDA 12.0+ (for GPU acceleration)

**Optimal (for GPU inference):**
- Windows 11 (64-bit)
- 16GB+ RAM
- NVIDIA RTX GPU (RTX 3060 or better)
- CUDA Toolkit 12.3+

### GPU Support

**NVIDIA GPUs:**
- Supported: GeForce RTX 20/30/40 series, Tesla, A100, H100
- Driver: 525.60.13 or later
- CUDA: 12.0 or later

**AMD GPUs:**
- Supported: Radeon RX 6000/7000 series, MI200/MI300
- ROCm: 5.0 or later (requires WSL2 on Windows)

**Intel GPUs:**
- Supported: Arc A-series, Data Center GPU Max
- oneAPI: 2023.0 or later

---

## Method 1: Python pip (Recommended) ⭐

**Best for:** Developers, Python users, CI/CD pipelines

### Step 1: Install Python

If you don't have Python installed:

1. **Download Python:**
   - Visit https://www.python.org/downloads/windows/
   - Download Python 3.11 or later (64-bit)

2. **Run the installer:**
   - ✅ **IMPORTANT:** Check "Add Python to PATH"
   - Click "Install Now"
   - Wait for installation to complete

3. **Verify Python installation:**
   ```powershell
   # Open PowerShell (Win + X, then press I)
   python --version
   # Should show: Python 3.11.x or later

   pip --version
   # Should show: pip 23.x.x or later
   ```

### Step 2: Install LightOS

Open PowerShell as Administrator (Win + X, then press A):

```powershell
# Install LightOS
pip install lightos-accelerated

# Verify installation
python -c "from lightos_accelerated import LightDevice; print('✅ LightOS installed successfully!')"
```

### Step 3: Install Optional Components

```powershell
# For gRPC server
pip install lightos-accelerated[server]

# For Jupyter notebooks
pip install lightos-accelerated[jupyter]

# For PyTorch integration
pip install lightos-accelerated[torch]

# Install everything
pip install lightos-accelerated[all]
```

### Step 4: Install CUDA (for NVIDIA GPUs)

If you have an NVIDIA GPU:

1. **Check if CUDA is already installed:**
   ```powershell
   nvcc --version
   ```

2. **If not installed, download CUDA Toolkit:**
   - Visit https://developer.nvidia.com/cuda-downloads
   - Select: Windows → x86_64 → 11 → exe (local)
   - Download and run the installer
   - Accept default installation path

3. **Verify CUDA installation:**
   ```powershell
   nvcc --version
   # Should show: Cuda compilation tools, release 12.3
   ```

### Step 5: Test Installation

```powershell
# Test Python API
python -c "from lightos_accelerated import LightDevice, DeviceType; device = LightDevice(DeviceType.NVIDIA, 0); print(f'Device: {device.get_properties().name}')"

# Start gRPC server (if installed server extras)
lightos-server --port=50051 --devices=auto
```

**Troubleshooting:**
- If you get "command not found" errors, restart PowerShell
- If Python is not found, ensure "Add to PATH" was checked during installation
- If CUDA is not found, restart your computer after CUDA installation

---

## Method 2: Chocolatey

**Best for:** Windows power users who already use Chocolatey

### Step 1: Install Chocolatey

If you don't have Chocolatey:

1. **Open PowerShell as Administrator** (Win + X, then press A)

2. **Run the installation command:**
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   ```

3. **Verify installation:**
   ```powershell
   choco --version
   ```

### Step 2: Install LightOS

```powershell
# Install LightOS
choco install lightos -y

# Verify installation
lightos --version
```

### Step 3: Install CUDA (Optional)

```powershell
# Install CUDA Toolkit via Chocolatey
choco install cuda -y
```

---

## Method 3: winget (Windows 11)

**Best for:** Windows 11 users who prefer the built-in package manager

### Step 1: Check winget

winget comes pre-installed on Windows 11:

```powershell
# Verify winget is available
winget --version
```

If not available, install from Microsoft Store: "App Installer"

### Step 2: Install LightOS

```powershell
# Search for LightOS
winget search LightOS

# Install LightOS
winget install LightOS.Inference

# Verify installation
lightos --version
```

---

## Method 4: MSI Installer (One-Click)

**Best for:** Desktop users, beginners, non-technical users

### Step 1: Download Installer

1. **Visit the releases page:**
   - https://github.com/lightiam/lightos/releases/latest

2. **Download the MSI installer:**
   - Look for `LightOS-Setup-v1.0.0.msi`
   - Click to download (approximately 120MB)

### Step 2: Run Installer

1. **Double-click the downloaded MSI file**

2. **Follow the installation wizard:**
   - Click "Next"
   - Accept the license agreement
   - Choose installation directory (default: `C:\Program Files\LightOS`)
   - Select components:
     - ✅ Core Inference Engine (required)
     - ✅ Python Bindings
     - ✅ gRPC Server
     - ✅ Documentation
     - ✅ Example Notebooks
     - ⬜ CUDA Support (check if you have NVIDIA GPU)
   - Click "Install"
   - Wait for installation (2-3 minutes)
   - Click "Finish"

3. **The installer will automatically:**
   - Add LightOS to your PATH
   - Create Start Menu shortcuts
   - Create desktop icon (if selected)
   - Install Visual C++ Redistributable (if needed)

### Step 3: Verify Installation

1. **Open Command Prompt or PowerShell:**
   ```powershell
   lightos --version
   ```

2. **Test Python integration:**
   ```powershell
   python -c "from lightos_accelerated import LightDevice; print('✅ Ready!')"
   ```

### Step 4: Launch LightOS

**Option A: Start Menu**
- Press Windows key
- Type "LightOS"
- Click "LightOS Server" or "LightOS Documentation"

**Option B: Desktop Icon**
- Double-click "LightOS Server" icon on desktop

**Option C: Command Line**
```powershell
lightos-server --port=50051
```

---

## Method 5: Docker Desktop

**Best for:** Production deployments, containerized environments, reproducible setups

### Step 1: Install Docker Desktop

1. **Download Docker Desktop:**
   - Visit https://www.docker.com/products/docker-desktop/
   - Download for Windows
   - Run the installer

2. **Enable WSL 2:**
   - Docker Desktop will prompt to enable WSL 2
   - Follow the instructions (requires restart)

3. **Verify installation:**
   ```powershell
   docker --version
   ```

### Step 2: Enable GPU Support (for NVIDIA GPUs)

If you have an NVIDIA GPU:

1. **Install NVIDIA drivers** (version 525.60.13+)

2. **Install NVIDIA Container Toolkit:**
   - Visit https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html
   - Follow Windows installation instructions

### Step 3: Pull LightOS Image

```powershell
# Pull latest LightOS image
docker pull lightos/lightos-inference:latest

# Verify image size (should be <700MB)
docker images lightos/lightos-inference
```

### Step 4: Run Container

```powershell
# CPU-only
docker run -d -p 50051:50051 --name lightos lightos/lightos-inference:latest

# With NVIDIA GPU
docker run -d -p 50051:50051 --gpus all --name lightos lightos/lightos-inference:latest

# With AMD GPU (requires ROCm in WSL2)
docker run -d -p 50051:50051 --device=/dev/kfd --device=/dev/dri --name lightos lightos/lightos-inference:latest
```

### Step 5: Verify Container

```powershell
# Check container status
docker ps

# View logs
docker logs lightos

# Test gRPC server
# Open browser to http://localhost:50051
```

### Step 6: Interactive Python Session

```powershell
# Enter container
docker exec -it lightos python3

# In Python shell:
>>> from lightos_accelerated import LightDevice, DeviceType
>>> device = LightDevice(DeviceType.NVIDIA, 0)
>>> print(device.get_properties().name)
```

---

## Method 6: Build from Source

**Best for:** Contributors, advanced users, custom builds

### Step 1: Install Build Tools

1. **Install Visual Studio 2022:**
   - Download from https://visualstudio.microsoft.com/downloads/
   - Install "Desktop development with C++"
   - Install "Python development" workload

2. **Install CMake:**
   ```powershell
   choco install cmake -y
   ```

3. **Install Git:**
   ```powershell
   choco install git -y
   ```

4. **Install Python:**
   ```powershell
   choco install python311 -y
   ```

### Step 2: Clone Repository

```powershell
# Clone LightOS repository
git clone https://github.com/lightiam/lightos.git
cd lightos
```

### Step 3: Build C++ Core

```powershell
# Navigate to core directory
cd inference-subsystem\core

# Configure with CMake
cmake -B build -G "Visual Studio 17 2022" -A x64 `
  -DCMAKE_BUILD_TYPE=Release `
  -DBUILD_PYTHON_BINDINGS=ON `
  -DBUILD_TESTING=OFF

# Build (use all CPU cores)
cmake --build build --config Release --parallel

# Install
cmake --install build --prefix install
```

### Step 4: Build Python Bindings

```powershell
# Navigate to Python bindings
cd ..\python-bindings

# Install in development mode
pip install -e .
```

### Step 5: Verify Build

```powershell
# Test import
python -c "from lightos_accelerated import LightDevice; print('Build successful!')"

# Run tests
cd ..\..\tests
pytest
```

---

## Post-Installation Steps

### 1. Verify GPU Detection

```powershell
# Check if NVIDIA GPU is detected
lightos --list-devices

# Or in Python
python -c "from lightos_accelerated import LightDevice, DeviceType; device = LightDevice(DeviceType.NVIDIA, 0); print(f'GPU: {device.get_properties().name}')"
```

### 2. Download Example Notebooks

```powershell
# Clone examples
git clone https://github.com/lightiam/lightos.git lightos-examples
cd lightos-examples\inference-subsystem\notebooks

# Install Jupyter
pip install jupyter

# Launch notebook
jupyter notebook LightOS_QuickStart.ipynb
```

### 3. Start Inference Server

```powershell
# Start server with auto device detection
lightos-server --port=50051 --devices=auto

# Or specify NVIDIA GPU
lightos-server --port=50051 --devices=nvidia

# With specific GPU ID
lightos-server --port=50051 --devices=nvidia --device-id=0
```

### 4. Test Inference

Create a test file `test_inference.py`:

```python
from lightos_accelerated import *
import numpy as np

# Initialize device
device = LightDevice(DeviceType.NVIDIA, 0)
print(f"Device: {device.get_properties().name}")
print(f"Memory: {device.get_properties().total_memory_gb} GB")
print(f"Temperature: {device.get_temperature()}°C")

# Create execution graph
graph = ExecutionGraph(device)

# Add operations (simple linear layer)
input_id = graph.add_tensor([1, 784], np.float32, "input")
weight_id = graph.add_tensor([784, 128], np.float32, "weight")
output_id = graph.add_tensor([1, 128], np.float32, "output")

matmul = GraphOp(OpType.MATMUL, "fc1", inputs=[input_id, weight_id], outputs=[output_id])
relu = GraphOp(OpType.RELU, "relu", inputs=[output_id], outputs=[output_id])

graph.add_op(matmul)
graph.add_op(relu)

# Optimize and execute
print("\nOptimizing graph...")
graph.optimize()

print("Executing inference...")
governor = PowerGovernor(device)
success = governor.submit_job(graph, priority=1)

print(f"\n✅ Inference complete!")
print(f"Final temperature: {device.get_temperature()}°C")
```

Run it:
```powershell
python test_inference.py
```

---

## Troubleshooting

### Problem: "Python is not recognized"

**Solution:**
1. Reinstall Python and check "Add Python to PATH"
2. Or manually add Python to PATH:
   - Search for "Environment Variables" in Start Menu
   - Click "Environment Variables"
   - Under "User variables", find "Path"
   - Click "Edit" → "New"
   - Add: `C:\Users\<YourUsername>\AppData\Local\Programs\Python\Python311`
   - Add: `C:\Users\<YourUsername>\AppData\Local\Programs\Python\Python311\Scripts`
   - Click "OK" and restart PowerShell

### Problem: "CUDA not found" or "No GPU detected"

**Solution:**
1. Check NVIDIA driver:
   ```powershell
   nvidia-smi
   ```
2. If command not found, install NVIDIA drivers from https://www.nvidia.com/drivers
3. Install CUDA Toolkit: https://developer.nvidia.com/cuda-downloads
4. Restart computer
5. Verify:
   ```powershell
   nvcc --version
   ```

### Problem: "ImportError: DLL load failed"

**Solution:**
1. Install Visual C++ Redistributable:
   - Download from https://aka.ms/vs/17/release/vc_redist.x64.exe
   - Run and install
2. Restart computer
3. Try importing again

### Problem: "Permission denied" during installation

**Solution:**
1. Run PowerShell as Administrator (Win + X, then press A)
2. Run installation command again

### Problem: MSI installer fails

**Solution:**
1. Uninstall any previous LightOS installation:
   - Settings → Apps → LightOS → Uninstall
2. Delete installation directory: `C:\Program Files\LightOS`
3. Delete user data: `C:\Users\<YourUsername>\.lightos`
4. Run MSI installer again

### Problem: Docker container won't start

**Solution:**
1. Check Docker Desktop is running (system tray icon)
2. Enable WSL 2:
   ```powershell
   wsl --set-default-version 2
   ```
3. Restart Docker Desktop
4. Try running container again

### Problem: "Out of memory" errors

**Solution:**
1. Close other applications
2. Reduce batch size in your model
3. Use CPU instead of GPU:
   ```python
   device = LightDevice(DeviceType.CPU, 0)
   ```
4. Upgrade RAM (minimum 8GB recommended)

---

## Uninstallation

### pip
```powershell
pip uninstall lightos-accelerated
```

### Chocolatey
```powershell
choco uninstall lightos -y
```

### winget
```powershell
winget uninstall LightOS.Inference
```

### MSI Installer
1. Settings → Apps → LightOS → Uninstall
2. Or run: `C:\Program Files\LightOS\uninstall.exe`

### Docker
```powershell
docker stop lightos
docker rm lightos
docker rmi lightos/lightos-inference
```

---

## Next Steps

After installation:

1. **📚 Read the documentation:**
   - Visit https://docs.lightos.ai
   - Or open locally: `C:\Program Files\LightOS\docs\index.html`

2. **💻 Try example notebooks:**
   ```powershell
   cd C:\Program Files\LightOS\examples
   jupyter notebook LightOS_QuickStart.ipynb
   ```

3. **🚀 Deploy to production:**
   - See Kubernetes guide: https://docs.lightos.ai/guides/kubernetes.html
   - Docker deployment: https://docs.lightos.ai/guides/docker-deployment.html

4. **🎓 Join the community:**
   - GitHub: https://github.com/lightiam/lightos
   - Discussions: https://github.com/lightiam/lightos/discussions

---

## Need Help?

- **Documentation:** https://docs.lightos.ai
- **GitHub Issues:** https://github.com/lightiam/lightos/issues
- **Discussions:** https://github.com/lightiam/lightos/discussions
- **Email:** support@lightos.ai

---

**Installation complete!** 🎉

You now have LightOS running on Windows with:
- ✅ High-performance AI inference (35,000x faster than pure Python)
- ✅ Hardware-agnostic execution (NVIDIA, AMD, Intel, CPU)
- ✅ Graph-based optimization (15-30% speedup)
- ✅ Thermal-aware scheduling (prevents throttling)
