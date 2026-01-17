/**
 * LightOS C++/CLI Wrapper - Managed .NET Interface
 *
 * This C++/CLI wrapper enables C# applications (Windows Forms, WPF, etc.)
 * to interact with the native C++ LightOS Inference Subsystem.
 *
 * Architecture:
 * - C# Application (managed)
 *   ↓
 * - C++/CLI Wrapper (mixed native/managed) ← THIS FILE
 *   ↓
 * - Native C++23 LightOS Core (unmanaged)
 *   ↓
 * - CUDA/Photonic NPU (hardware)
 *
 * @file LightOS.Interop.h
 * @author LightRail AI - Principal Kernel Architect
 * @version 1.0.0
 */

#pragma once

// Include native C++ headers
#include "../core/include/light_accelerator.hpp"
#include "../core/include/power_governor.hpp"
#include "../core/include/tile_engine.hpp"

using namespace System;
using namespace System::Collections::Generic;
using namespace System::Runtime::InteropServices;

namespace LightOS {
namespace Interop {

// ============================================================================
// Managed Enums (exposed to C#)
// ============================================================================

public enum class DeviceType {
    Unknown = 0,
    NvidiaGPU = 1,
    AmdGPU = 2,
    IntelGPU = 3,
    PhotonicNPU = 4,
    TPU = 5,
    GenericOpenCL = 6
};

public enum class SchedulingPolicy {
    FIFO = 0,
    ThermalAware = 1,
    PowerEfficient = 2,
    LatencyOptimal = 3,
    PredictiveCooling = 4
};

public enum class Precision {
    FP32 = 0,
    FP16 = 1,
    BF16 = 2,
    FP8_E4M3 = 3,
    FP8_E5M2 = 4,
    INT8 = 5,
    INT4 = 6,
    Binary = 7
};

// ============================================================================
// Managed Structures (C# compatible)
// ============================================================================

[StructLayout(LayoutKind::Sequential)]
public value struct DeviceProperties {
    DeviceType Type;
    String^ Name;
    UInt64 ComputeUnits;
    UInt32 MaxThreadsPerBlock;
    UInt32 WarpSize;
    UInt64 GlobalMemorySize;
    UInt64 SharedMemoryPerBlock;
    UInt64 L2CacheSize;
    UInt32 MemoryBusWidth;
    float MaxTemperatureCelsius;
    float TdpWatts;
    float CurrentTemperature;
    float CurrentPowerDraw;
    UInt32 MziCount;
    UInt32 WdmChannels;
    float OpticalPowerMw;
    UInt32 PcieGen;
    UInt32 PcieLanes;
    float InterconnectBandwidthGbps;
};

[StructLayout(LayoutKind::Sequential)]
public value struct ThermalState {
    float TemperatureCelsius;
    float ThermalInertia;
    float SmClockStability;
    float PowerDrawWatts;
    float PowerLimitWatts;
    DateTime Timestamp;
};

[StructLayout(LayoutKind::Sequential)]
public value struct Statistics {
    UInt64 TotalJobsCompleted;
    UInt64 ThermalThrottleEvents;
    UInt64 PredictiveCoolingTriggers;
    UInt64 JobMigrations;
    float AvgTemperatureC;
    float AvgPowerWatts;
    float AvgUtilization;
    Int64 AvgQueueTimeMs;
};

// ============================================================================
// Managed Device Class (C# accessible)
// ============================================================================

public ref class LightDevice {
public:
    LightDevice(DeviceType type, UInt32 deviceId);
    ~LightDevice();
    !LightDevice();  // Finalizer

    // Device Properties
    DeviceProperties GetProperties();
    DeviceType GetDeviceType();
    String^ GetArchitecture();

    // Memory Management
    UInt64 AllocateMemory(UInt64 sizeBytes);
    void DeallocateMemory(UInt64 handle);
    void CopyHostToDevice(UInt64 deviceHandle, array<Byte>^ hostData);
    array<Byte>^ CopyDeviceToHost(UInt64 deviceHandle, UInt64 sizeBytes);

    // Thermal & Power
    float GetTemperature();
    float GetPowerDraw();
    float GetUtilization();
    void SetPowerLimit(float watts);
    void SetClockFrequency(UInt32 mhz);

private:
    lightos::inference::LightAccelerator* native_;
};

// ============================================================================
// Managed PowerGovernor Class
// ============================================================================

public ref class PowerGovernor {
public:
    PowerGovernor();
    PowerGovernor(SchedulingPolicy policy, float globalPowerBudgetWatts);
    ~PowerGovernor();
    !PowerGovernor();

    // Device Management
    void RegisterDevice(LightDevice^ device);
    void UnregisterDevice(UInt64 deviceHandle);

    // Job Submission
    UInt64 SubmitInferenceJob(
        String^ modelName,
        UInt32 batchSize,
        UInt32 sequenceLength,
        Precision precision
    );

    // Scheduling Control
    void StartScheduler();
    void StopScheduler();

    // Thermal Management
    void ApplyThermalThrottling(UInt64 deviceHandle, float targetTemp);
    void TriggerPredictiveCooling(UInt64 deviceHandle);

    // Telemetry
    ThermalState GetThermalState(UInt64 deviceHandle);
    float GetGlobalPowerDraw();
    UInt64 GetPendingJobs();

    // Statistics
    Statistics GetStatistics();

private:
    lightos::inference::PowerGovernor* native_;
};

// ============================================================================
// Managed Inference Executor
// ============================================================================

public ref class InferenceExecutor {
public:
    InferenceExecutor(LightDevice^ device, PowerGovernor^ governor);
    ~InferenceExecutor();
    !InferenceExecutor();

    // Configuration
    void ConfigureTiles(UInt32 tileM, UInt32 tileN, UInt32 tileK);
    void ConfigureQuantization(Precision inputPrecision, Precision weightPrecision);
    void SetBatchSize(UInt32 batchSize);

    // Inference Execution
    UInt64 Submit(array<Byte>^ inputData);
    array<Byte>^ WaitForResult(UInt64 requestId);
    bool IsComplete(UInt64 requestId);

    // Statistics
    property float AvgLatencyMs { float get(); }
    property float AvgThroughputTokensPerSec { float get(); }
    property float ModelFLOPSUtilization { float get(); }

private:
    lightos::inference::InferenceExecutor* native_;
};

// ============================================================================
// Device Enumeration (Static Methods)
// ============================================================================

public ref class DeviceManager {
public:
    static List<DeviceProperties>^ EnumerateDevices();
    static LightDevice^ AutoSelectDevice(UInt64 requiredMemoryGB, float maxPowerBudgetWatts);
    static UInt32 GetDeviceCount();
    static DeviceProperties GetDeviceProperties(UInt32 deviceId);
};

// ============================================================================
// Event Delegates (for UI callbacks)
// ============================================================================

public delegate void ThermalEventHandler(UInt64 deviceHandle, float temperature, String^ severity);
public delegate void JobCompletionHandler(UInt64 jobId, bool success, String^ errorMessage);
public delegate void PowerEventHandler(float totalPowerWatts, float avgUtilization);

// ============================================================================
// Telemetry Monitor (with events)
// ============================================================================

public ref class TelemetryMonitor {
public:
    TelemetryMonitor(PowerGovernor^ governor);
    ~TelemetryMonitor();

    // Events
    event ThermalEventHandler^ OnThermalWarning;
    event ThermalEventHandler^ OnThermalCritical;
    event JobCompletionHandler^ OnJobCompleted;
    event PowerEventHandler^ OnPowerUpdate;

    // Control
    void Start(UInt32 intervalMs);
    void Stop();

private:
    void MonitorThread();

    PowerGovernor^ governor_;
    System::Threading::Thread^ thread_;
    bool running_;
    UInt32 interval_ms_;
};

} // namespace Interop
} // namespace LightOS
