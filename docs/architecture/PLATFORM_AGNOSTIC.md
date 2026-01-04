# LightOS Platform-Agnostic Architecture

## Vision

LightOS is a platform-agnostic operating system for AI accelerators, inspired by OpenCL.

**Supported Platforms:**
- ✅ NVIDIA GPUs (CUDA)
- ✅ AMD GPUs (ROCm/OpenCL)
- ✅ ARM GPUs (Mali/OpenCL)
- ✅ Intel XPUs (oneAPI/OpenCL)
- ✅ Apple Silicon (Metal)
- ✅ Future Photonic NPUs (LightRail AI)

## Benefits
- Platform-agnostic API (one codebase for all hardware)
- 27-30% cost savings with mixed clusters
- No vendor lock-in
- Future-proof for photonic NPUs

## Architecture
```
ML Frameworks → LightOS Unified Runtime → CUDA|ROCm|OpenCL|Metal → Hardware
```

See full documentation for details.
