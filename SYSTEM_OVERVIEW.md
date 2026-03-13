# LightOS v0.1 System Overview

## What is LightOS?

LightOS is an operating system for photonic AI accelerators that provides immediate performance improvements on current GPU/TPU clusters while preparing for next-generation photonic NPUs.

## Key Components

1. **Kernel Module** - Device abstraction and telemetry
2. **Agent Daemon** - Telemetry collection and Fabric OS integration
3. **Collectives Library** - Deterministic distributed operations
4. **Benchmark Service** - Performance tracking

## Architecture & Integration Layers

LightOS abstracts the hardware layer, sitting between diverse AI accelerators (NVIDIA CUDA, AMD ROCm, photonic NPUs) and the standard AI software stack.

### 1. Driver/Runtime Layer
- Acts as a hypervisor for AI compute.
- Sits completely below the framework layer, meaning workloads do not need to be aware of the underlying hardware format.
- Automatically handles dispatch to the optimal backend (e.g., CUDA → ROCm → photonic NPU).

### 2. Framework Layer
- **Full Compatibility:** Out-of-the-box support for PyTorch, TensorFlow, and JAX.
- Standard AI model code runs unchanged.
- **Integration Path:** Simply install the runtime (`pip install lightos-runtime`) and configure the backend device targets. LightOS automatically routes model code execution to the allocated accelerators.

### 3. Data Center Infrastructure Layer
- Exposes a robust REST/gRPC control plane API.
- Easily integrates with Kubernetes, SLURM, and other custom orchestrators.
- **Resource Management:** LightOS is added as a device plugin, causing physical and virtualized accelerators to appear as schedulable resources within the cluster.
- **Photonic-Ready:** Provides the first unified control layer designed to handle next-generation photonic NPU clusters, essentially providing the OS infrastructure that photonic data centers currently lack.

## Integration Paths by Environment

The deployment model scales depending on the infrastructure:

| Environment | Integration Path |
| :--- | :--- |
| **HPC / SLURM clusters** | LightOS SLURM plugin → device scheduling |
| **Kubernetes / cloud** | LightOS device plugin + container runtime shim |
| **Bare metal data centers** | LightOS as kernel module + userspace daemon |
| **Hyperscalers (Custom Silicon)** | Integration via LightOS HAL (Hardware Abstraction Layer) |
| **Photonic data centers** | Native NPU driver + LightOS photonic runtime |

## Version

v0.1.0 - Initial Release
