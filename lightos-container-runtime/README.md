# LightOS Container Runtime

**Multi-vendor GPU container runtime for Docker and Kubernetes**

LightOS Container Runtime is a drop-in replacement for NVIDIA Container Runtime that supports **all GPU vendors**: NVIDIA, AMD, Intel, and Apple. It provides intelligent device scheduling, cost optimization, and seamless integration with Docker and Kubernetes.

---

## 🌟 Features

### Multi-Vendor Support
- **NVIDIA GPUs** - CUDA support
- **AMD GPUs** - ROCm support
- **Intel GPUs** - oneAPI support
- **Apple Silicon** - Metal support

### Intelligent Scheduling
- **Performance mode** - Select fastest available GPU
- **Cost mode** - Select cheapest GPU (for cloud deployments)
- **Balanced mode** - Optimize performance/cost ratio
- **Auto-detection** - Automatically discover and configure GPUs

### Container Integration
- **Docker runtime** - Works as `--runtime=lightos`
- **Kubernetes device plugin** - Native K8s integration
- **OCI hooks** - Standard container lifecycle hooks
- **Driver injection** - Automatic driver library mounting

### Advanced Features
- Cost tracking and reporting
- GPU utilization monitoring
- Multi-GPU support
- Device blacklisting/whitelisting
- VRAM requirements specification

---

## 📦 Installation

### Linux (Ubuntu/Debian/RHEL/Fedora)

```bash
cd lightos-container-runtime
sudo ./install/install-linux.sh
```

### Windows (WSL2 + Docker Desktop)

```powershell
# Run as Administrator
.\install\install-windows.ps1
```

### macOS (Docker Desktop)

```bash
./install/install-macos.sh
```

---

## 🚀 Quick Start

### Docker Usage

#### Basic Usage - Automatic GPU Selection

```bash
docker run --runtime=lightos pytorch/pytorch:latest python train.py
```

The runtime automatically:
1. Detects all available GPUs
2. Selects the best GPU based on strategy (default: balanced)
3. Injects necessary drivers and libraries
4. Sets environment variables

#### Advanced Usage - Specify Requirements

```bash
docker run --runtime=lightos \
  -e LIGHTOS_DEVICE_TYPE=nvidia \
  -e LIGHTOS_MIN_VRAM=8GB \
  -e LIGHTOS_STRATEGY=performance \
  pytorch/pytorch:latest python train.py
```

**Environment Variables:**
- `LIGHTOS_DEVICE_TYPE` - Preferred GPU vendor (`nvidia`, `amd`, `intel`, `apple`, `any`)
- `LIGHTOS_MIN_VRAM` - Minimum VRAM required (e.g., `8GB`, `16GB`)
- `LIGHTOS_STRATEGY` - Scheduling strategy (`performance`, `cost`, `balanced`)

#### Multi-GPU Support

```bash
docker run --runtime=lightos \
  -e LIGHTOS_DEVICE_TYPE=any \
  -e LIGHTOS_ENABLE_MULTI_GPU=true \
  -e LIGHTOS_MAX_GPU=2 \
  your-training-image:latest
```

### Kubernetes Usage

#### Deploy Device Plugin

```bash
kubectl apply -f k8s/lightos-device-plugin.yaml
```

#### Request GPUs in Pod Spec

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: gpu-pod
spec:
  containers:
  - name: cuda-container
    image: nvidia/cuda:11.8.0-base
    resources:
      limits:
        lightos.io/nvidia: 1    # Request NVIDIA GPU
        # OR
        lightos.io/amd: 1       # Request AMD GPU
        # OR
        lightos.io/intel: 1     # Request Intel GPU
```

---

## 🛠️ Configuration

### Runtime Configuration

Edit `/etc/lightos-runtime/config.json`:

```json
{
  "debug": false,
  "defaultStrategy": "balanced",
  "preferredVendor": "any",
  "enableMultiGPU": false,
  "maxGPUPerContainer": 1,
  "injectDrivers": true,
  "cudaPath": "/usr/local/cuda",
  "rocmPath": "/opt/rocm",
  "oneAPIPath": "/opt/intel/oneapi",
  "enableMetrics": true,
  "metricsPort": 9100,
  "enableCostTracking": true
}
```

**Configuration Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `defaultStrategy` | Default scheduling strategy | `balanced` |
| `preferredVendor` | Preferred GPU vendor | `any` |
| `enableMultiGPU` | Allow multiple GPUs per container | `false` |
| `maxGPUPerContainer` | Max GPUs per container | `1` |
| `injectDrivers` | Auto-inject driver libraries | `true` |
| `enableMetrics` | Enable Prometheus metrics | `true` |
| `enableCostTracking` | Track GPU costs | `true` |

### Docker Daemon Configuration

The installer automatically configures `/etc/docker/daemon.json`:

```json
{
  "runtimes": {
    "lightos": {
      "path": "/usr/bin/lightos-runtime",
      "runtimeArgs": []
    }
  }
}
```

After modifying, restart Docker:

```bash
sudo systemctl restart docker
```

---

## 📊 CLI Commands

### Detect Available GPUs

```bash
lightos-runtime detect
```

**Output:**
```
=== LightOS Accelerators Detected ===

Device 0:
  Type:       nvidia
  Name:       NVIDIA GeForce RTX 4090
  VRAM:       24.00 GB
  Compute:    8.9
  Driver:     535.129.03
  PCIe Bus:   0000:01:00.0
  Available:  true

Device 1:
  Type:       amd
  Name:       AMD Radeon RX 7900 XTX
  VRAM:       24.00 GB
  Compute:    gfx1100
  Driver:     6.0.0
  PCIe Bus:   0000:03:00.0
  Available:  true
```

### View Runtime Info

```bash
lightos-runtime info
```

### Configure Docker Daemon

```bash
sudo lightos-runtime configure
```

---

## 🎯 Use Cases

### 1. Multi-Cloud GPU Management

Run the same container image across different cloud providers without modification:

```bash
# AWS (NVIDIA T4)
docker run --runtime=lightos -e LIGHTOS_DEVICE_TYPE=nvidia app:latest

# Azure (AMD MI25)
docker run --runtime=lightos -e LIGHTOS_DEVICE_TYPE=amd app:latest

# GCP (NVIDIA A100)
docker run --runtime=lightos -e LIGHTOS_DEVICE_TYPE=nvidia app:latest
```

### 2. Cost Optimization

Automatically select the cheapest available GPU:

```bash
docker run --runtime=lightos \
  -e LIGHTOS_STRATEGY=cost \
  -e LIGHTOS_MIN_VRAM=16GB \
  training-job:latest
```

### 3. Heterogeneous Cluster

Run workloads on mixed GPU clusters:

```yaml
# Kubernetes deployment that can run on any GPU
apiVersion: apps/v1
kind: Deployment
metadata:
  name: inference-service
spec:
  replicas: 10
  template:
    spec:
      containers:
      - name: model-server
        image: model-server:latest
        resources:
          limits:
            lightos.io/nvidia: 1  # Will use NVIDIA if available
            lightos.io/amd: 1     # Otherwise try AMD
            lightos.io/intel: 1   # Otherwise try Intel
```

### 4. Development on Apple Silicon

Develop GPU workloads on M1/M2/M3 Macs:

```bash
docker run --runtime=lightos \
  -e LIGHTOS_DEVICE_TYPE=apple \
  tensorflow:latest python train.py
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Container Application                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  LightOS Container Runtime                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │            Device Detection & Selection                │ │
│  │  - Auto-detect all GPUs                               │ │
│  │  - Apply scheduling strategy                          │ │
│  │  - Match requirements (VRAM, type, cost)              │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Driver Injection                          │ │
│  │  - CUDA libraries (NVIDIA)                            │ │
│  │  - ROCm libraries (AMD)                               │ │
│  │  - oneAPI libraries (Intel)                           │ │
│  │  - Metal framework (Apple)                            │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              OCI Spec Modification                     │ │
│  │  - Device files (/dev/nvidia0, /dev/dri/card0, etc.)  │ │
│  │  - Environment variables                              │ │
│  │  - Library mounts                                     │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Base Runtime (runc)                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│             GPU Drivers (CUDA/ROCm/oneAPI/Metal)            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Physical GPUs                              │
│  NVIDIA │ AMD │ Intel │ Apple                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 Comparison with NVIDIA Container Runtime

| Feature | NVIDIA Container Runtime | LightOS Container Runtime |
|---------|-------------------------|--------------------------|
| NVIDIA GPU Support | ✅ | ✅ |
| AMD GPU Support | ❌ | ✅ |
| Intel GPU Support | ❌ | ✅ |
| Apple Silicon Support | ❌ | ✅ |
| Intelligent Scheduling | ❌ | ✅ |
| Cost Optimization | ❌ | ✅ |
| Multi-vendor Clusters | ❌ | ✅ |
| Kubernetes Integration | ✅ | ✅ |
| Docker Integration | ✅ | ✅ |

---

## 🔧 Troubleshooting

### No GPUs Detected

```bash
# Check if drivers are installed
nvidia-smi          # For NVIDIA
rocm-smi            # For AMD
sycl-ls             # For Intel
system_profiler     # For Apple (macOS)

# Check permissions
ls -la /dev/nvidia* /dev/dri/* /dev/kfd

# Enable debug logging
export LIGHTOS_DEBUG=true
docker run --runtime=lightos your-image:latest
```

### Runtime Not Available in Docker

```bash
# Reconfigure Docker daemon
sudo lightos-runtime configure
sudo systemctl restart docker

# Verify runtime is registered
docker info | grep -A 5 Runtimes
```

### Kubernetes Device Plugin Not Working

```bash
# Check if plugin is running
kubectl get pods -n kube-system | grep lightos

# Check logs
kubectl logs -n kube-system lightos-device-plugin-xxxxx

# Verify device resources
kubectl describe node <node-name> | grep lightos.io
```

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

Apache 2.0 License - see [LICENSE](../LICENSE) for details.

---

## 🙏 Acknowledgments

- Inspired by [NVIDIA Container Runtime](https://github.com/NVIDIA/nvidia-container-runtime)
- Built with [Go](https://golang.org/)
- Uses [OCI Runtime Specification](https://github.com/opencontainers/runtime-spec)

---

## 📞 Support

- **Documentation**: https://github.com/Lightiam/LightOS
- **Issues**: https://github.com/Lightiam/LightOS/issues
- **Discussions**: https://github.com/Lightiam/LightOS/discussions

---

**Made with ❤️ by the LightOS Team**
