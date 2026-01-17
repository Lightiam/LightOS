/**
 * LightOS Inference Subsystem - Platform-Agnostic Abstraction Layer
 *
 * Module 1: The LightShim - Decouple inference logic from hardware
 *
 * This abstraction allows LightOS to run on:
 * - NVIDIA H100 GPUs (today) via CUDA/PTX
 * - LightRail Photonic NPUs (tomorrow) via Photonic Instructions
 * - AMD GPUs via ROCm/HIP
 * - Intel GPUs via SYCL/oneAPI
 *
 * @file light_accelerator.hpp
 * @author LightRail AI - Principal Kernel Architect
 * @version 1.0.0
 */

#pragma once

#include <cstdint>
#include <memory>
#include <span>
#include <mdspan>
#include <string_view>
#include <expected>
#include <vector>
#include <concepts>
#include <atomic>
#include <chrono>

namespace lightos::inference {

// ============================================================================
// Forward Declarations
// ============================================================================

class LightAccelerator;
class JITCompiler;
class DeviceMemory;
template<typename T> class Tensor;

// ============================================================================
// Platform-Agnostic Types (C++23)
// ============================================================================

using DeviceHandle = std::uint64_t;
using StreamHandle = std::uint64_t;
using MemoryHandle = std::uint64_t;
using KernelHandle = std::uint64_t;

// Use std::mdspan for multi-dimensional array abstraction
template<typename T, std::size_t Rank>
using mdspan_t = std::mdspan<T, std::dextents<std::size_t, Rank>>;

// ============================================================================
// Error Handling (C++23 std::expected)
// ============================================================================

enum class AcceleratorError {
    SUCCESS = 0,
    DEVICE_NOT_FOUND,
    OUT_OF_MEMORY,
    COMPILATION_FAILED,
    KERNEL_LAUNCH_FAILED,
    INVALID_DEVICE,
    THERMAL_LIMIT_EXCEEDED,
    POWER_CAP_EXCEEDED,
    UNSUPPORTED_OPERATION,
    INVALID_ARCHITECTURE
};

template<typename T>
using Result = std::expected<T, AcceleratorError>;

// ============================================================================
// Device Enumeration & Abstraction
// ============================================================================

enum class DeviceType : std::uint8_t {
    UNKNOWN = 0,
    NVIDIA_GPU,      // H100, A100, RTX 4090, etc.
    AMD_GPU,         // MI300X, etc.
    INTEL_GPU,       // Ponte Vecchio, etc.
    PHOTONIC_NPU,    // LightRail Photonic Neural Compute Engine
    TPU,             // Google TPU
    GENERIC_OPENCL   // Fallback
};

enum class MemoryType : std::uint8_t {
    HOST_PAGEABLE,
    HOST_PINNED,
    DEVICE_GLOBAL,      // HBM (High Bandwidth Memory)
    DEVICE_SHARED,      // SRAM / L1 Cache
    DEVICE_CONSTANT,
    UNIFIED_MANAGED
};

struct DeviceProperties {
    DeviceType type;
    std::string_view name;

    // Compute Capabilities
    std::size_t compute_units;           // SMs for NVIDIA, CUs for AMD
    std::uint32_t max_threads_per_block;
    std::uint32_t warp_size;             // 32 for NVIDIA, 64 for AMD

    // Memory Hierarchy
    std::size_t global_memory_size;      // HBM capacity (bytes)
    std::size_t shared_memory_per_block; // L1/SRAM per block
    std::size_t l2_cache_size;
    std::uint32_t memory_bus_width;      // bits

    // Thermal & Power
    float max_temperature_celsius;       // Thermal limit
    float tdp_watts;                     // Thermal Design Power
    float current_temperature;
    float current_power_draw;

    // Photonic-Specific (for LightRail NPU)
    std::uint32_t mzi_count;            // Mach-Zehnder Interferometers
    std::uint32_t wdm_channels;         // Wavelength-Division Multiplexing
    float optical_power_mw;             // Optical power budget

    // PCI-E / Interconnect
    std::uint32_t pcie_gen;             // PCIe generation
    std::uint32_t pcie_lanes;
    float interconnect_bandwidth_gbps;
};

// ============================================================================
// Generic LightAccelerator Device Class
// ============================================================================

class LightAccelerator {
public:
    // Factory pattern for device creation
    static Result<std::unique_ptr<LightAccelerator>> create(DeviceType type, std::uint32_t device_id = 0);

    virtual ~LightAccelerator() = default;

    // Device Introspection
    virtual Result<DeviceProperties> get_properties() const = 0;
    virtual DeviceType get_type() const noexcept = 0;
    virtual std::string_view get_architecture() const noexcept = 0;

    // Memory Management (Abstracted)
    virtual Result<MemoryHandle> allocate(std::size_t size_bytes, MemoryType type) = 0;
    virtual Result<void> deallocate(MemoryHandle handle) = 0;
    virtual Result<void> copy_h2d(MemoryHandle dst, const void* src, std::size_t size) = 0;
    virtual Result<void> copy_d2h(void* dst, MemoryHandle src, std::size_t size) = 0;
    virtual Result<void> copy_d2d(MemoryHandle dst, MemoryHandle src, std::size_t size) = 0;

    // Asynchronous Memory Operations
    virtual Result<void> copy_h2d_async(MemoryHandle dst, const void* src, std::size_t size, StreamHandle stream) = 0;
    virtual Result<void> copy_d2h_async(void* dst, MemoryHandle src, std::size_t size, StreamHandle stream) = 0;

    // Stream Management (CUDA-like abstraction)
    virtual Result<StreamHandle> create_stream() = 0;
    virtual Result<void> destroy_stream(StreamHandle stream) = 0;
    virtual Result<void> synchronize_stream(StreamHandle stream) = 0;
    virtual Result<void> synchronize_device() = 0;

    // JIT Compilation Interface
    virtual Result<KernelHandle> compile_kernel(
        std::string_view source_code,
        std::string_view kernel_name,
        std::span<const std::string_view> compile_options = {}
    ) = 0;

    // Kernel Launch (Generic)
    struct LaunchConfig {
        std::uint32_t grid_dim_x, grid_dim_y, grid_dim_z;
        std::uint32_t block_dim_x, block_dim_y, block_dim_z;
        std::uint32_t shared_memory_bytes;
        StreamHandle stream;
    };

    virtual Result<void> launch_kernel(
        KernelHandle kernel,
        const LaunchConfig& config,
        std::span<const void*> args
    ) = 0;

    // Thermal & Power Telemetry
    virtual Result<float> get_temperature() const = 0;
    virtual Result<float> get_power_draw() const = 0;
    virtual Result<float> get_utilization() const = 0;  // 0.0 to 1.0

    // Power Capping
    virtual Result<void> set_power_limit(float watts) = 0;
    virtual Result<float> get_power_limit() const = 0;

    // Clock Control
    virtual Result<void> set_clock_frequency(std::uint32_t mhz) = 0;
    virtual Result<std::uint32_t> get_clock_frequency() const = 0;
};

// ============================================================================
// JIT Compilation Abstraction (NVRTC-like for all platforms)
// ============================================================================

class JITCompiler {
public:
    virtual ~JITCompiler() = default;

    // Compile high-level linear algebra to platform-specific code
    // - For NVIDIA: Compiles to PTX using NVRTC/nvJitLink
    // - For Photonic NPU: Compiles to Photonic Instructions
    // - For AMD: Compiles to GCN/CDNA ISA via HIP RTC
    virtual Result<std::vector<std::uint8_t>> compile(
        std::string_view source,
        DeviceType target,
        std::span<const std::string_view> options = {}
    ) = 0;

    // Tiled Matrix Multiplication (High-Level Abstraction)
    struct MatMulConfig {
        std::uint32_t tile_m, tile_n, tile_k;
        bool use_tensor_cores;  // Use TensorCores/MatrixCores if available
        bool use_fp8;           // Use FP8 for H100/Blackwell
        bool use_int4;          // Use INT4 for extreme quantization
    };

    virtual Result<KernelHandle> compile_tiled_matmul(
        const MatMulConfig& config,
        DeviceType target
    ) = 0;

    // Get compilation log
    virtual std::string_view get_log() const noexcept = 0;
};

// ============================================================================
// Tensor Abstraction (Host + Device)
// ============================================================================

template<typename T>
class Tensor {
public:
    // CUDA Concepts Abstraction:
    // - Warps: Hidden in kernel implementation
    // - Coalesced Access: Automatic via contiguous layout
    // - Bank Conflicts: Avoided by proper tile sizes

    Tensor(LightAccelerator& device, std::span<const std::size_t> shape, MemoryType location)
        : device_(device), shape_(shape.begin(), shape.end()), location_(location) {

        size_ = 1;
        for (auto dim : shape_) size_ *= dim;

        auto result = device_.allocate(size_ * sizeof(T), location);
        if (!result) {
            throw std::runtime_error("Failed to allocate tensor memory");
        }
        handle_ = *result;
    }

    ~Tensor() {
        device_.deallocate(handle_);
    }

    // No copy (memory ownership)
    Tensor(const Tensor&) = delete;
    Tensor& operator=(const Tensor&) = delete;

    // Move semantics
    Tensor(Tensor&& other) noexcept
        : device_(other.device_), handle_(other.handle_),
          shape_(std::move(other.shape_)), size_(other.size_), location_(other.location_) {
        other.handle_ = 0;
    }

    // Upload data from host
    Result<void> upload(const T* host_data, StreamHandle stream = 0) {
        if (stream == 0) {
            return device_.copy_h2d(handle_, host_data, size_ * sizeof(T));
        } else {
            return device_.copy_h2d_async(handle_, host_data, size_ * sizeof(T), stream);
        }
    }

    // Download data to host
    Result<void> download(T* host_data, StreamHandle stream = 0) {
        if (stream == 0) {
            return device_.copy_d2h(host_data, handle_, size_ * sizeof(T));
        } else {
            return device_.copy_d2h_async(host_data, handle_, size_ * sizeof(T), stream);
        }
    }

    MemoryHandle handle() const noexcept { return handle_; }
    std::span<const std::size_t> shape() const noexcept { return shape_; }
    std::size_t size() const noexcept { return size_; }

private:
    LightAccelerator& device_;
    MemoryHandle handle_ = 0;
    std::vector<std::size_t> shape_;
    std::size_t size_ = 0;
    MemoryType location_;
};

// ============================================================================
// Platform-Specific Implementations (To be implemented separately)
// ============================================================================

class NVIDIAAccelerator : public LightAccelerator {
public:
    explicit NVIDIAAccelerator(std::uint32_t device_id);

    // Implement all virtual methods using CUDA Runtime API
    // Use NVRTC for JIT compilation to PTX
    // Use cuBLAS for optimized matrix operations

    Result<DeviceProperties> get_properties() const override;
    DeviceType get_type() const noexcept override { return DeviceType::NVIDIA_GPU; }
    std::string_view get_architecture() const noexcept override;

    // ... implement all other methods
};

class PhotonicAccelerator : public LightAccelerator {
public:
    explicit PhotonicAccelerator(std::uint32_t device_id);

    // Implement using LightRail Photonic NPU driver
    // Use Photonic Instruction Compiler
    // Leverage optical interconnects for I/O

    Result<DeviceProperties> get_properties() const override;
    DeviceType get_type() const noexcept override { return DeviceType::PHOTONIC_NPU; }
    std::string_view get_architecture() const noexcept override { return "LightRail-1"; }

    // Photonic-specific optimizations
    Result<void> calibrate_phase_shifters();
    Result<float> get_optical_power() const;
};

// ============================================================================
// Utility Functions
// ============================================================================

// Enumerate all available devices
Result<std::vector<DeviceProperties>> enumerate_devices();

// Auto-select best device based on workload
Result<std::unique_ptr<LightAccelerator>> auto_select_device(
    std::size_t required_memory_gb = 0,
    float max_power_budget_watts = 0
);

} // namespace lightos::inference
