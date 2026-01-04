# LightOS - Platform-Agnostic Operating System for AI Accelerators

**Write once. Run on NVIDIA, AMD, ARM, Intel, Apple, and future photonic NPUs.**

## Vision

LightOS is a platform-agnostic OS for AI accelerators, inspired by OpenCL.

### Supported Platforms
- ✅ NVIDIA GPUs (CUDA)
- ✅ AMD GPUs (ROCm)
- ✅ ARM GPUs (OpenCL)
- ✅ Intel XPUs (oneAPI)
- ✅ Apple Silicon (Metal)
- ✅ Future Photonic NPUs

## Benefits
- **Platform-agnostic**: One API for all hardware
- **Cost savings**: 27-30% with mixed clusters
- **No vendor lock-in**: Switch anytime
- **Future-proof**: Ready for photonic NPUs

## Quick Start
```c
lightos_context_t ctx = lightos_create_context(LIGHTOS_DEVICE_ANY);
// Works on NVIDIA, AMD, ARM, Intel, Apple!
```

## Links
- Website: https://lightrail.ink
- GitHub: https://github.com/Lightiam/LightOS

**LightOS: Write once. Run on any AI accelerator.**
