/**
 * LightOS C++/CLI Wrapper - Implementation
 *
 * @file LightOS.Interop.cpp
 * @author LightRail AI - Principal Kernel Architect
 * @version 1.0.0
 */

#include "LightOS.Interop.h"
#include <msclr/marshal_cppstd.h>

using namespace System;
using namespace System::Runtime::InteropServices;
using namespace msclr::interop;

namespace LightOS {
namespace Interop {

// ============================================================================
// Helper Functions (Marshalling)
// ============================================================================

static lightos::inference::DeviceType MarshalDeviceType(DeviceType type) {
    switch (type) {
        case DeviceType::NvidiaGPU: return lightos::inference::DeviceType::NVIDIA_GPU;
        case DeviceType::AmdGPU: return lightos::inference::DeviceType::AMD_GPU;
        case DeviceType::IntelGPU: return lightos::inference::DeviceType::INTEL_GPU;
        case DeviceType::PhotonicNPU: return lightos::inference::DeviceType::PHOTONIC_NPU;
        case DeviceType::TPU: return lightos::inference::DeviceType::TPU;
        default: return lightos::inference::DeviceType::UNKNOWN;
    }
}

static DeviceType MarshalDeviceType(lightos::inference::DeviceType type) {
    switch (type) {
        case lightos::inference::DeviceType::NVIDIA_GPU: return DeviceType::NvidiaGPU;
        case lightos::inference::DeviceType::AMD_GPU: return DeviceType::AmdGPU;
        case lightos::inference::DeviceType::INTEL_GPU: return DeviceType::IntelGPU;
        case lightos::inference::DeviceType::PHOTONIC_NPU: return DeviceType::PhotonicNPU;
        case lightos::inference::DeviceType::TPU: return DeviceType::TPU;
        default: return DeviceType::Unknown;
    }
}

static DeviceProperties MarshalDeviceProperties(const lightos::inference::DeviceProperties& native) {
    DeviceProperties managed;
    managed.Type = MarshalDeviceType(native.type);
    managed.Name = gcnew String(native.name.data());
    managed.ComputeUnits = native.compute_units;
    managed.MaxThreadsPerBlock = native.max_threads_per_block;
    managed.WarpSize = native.warp_size;
    managed.GlobalMemorySize = native.global_memory_size;
    managed.SharedMemoryPerBlock = native.shared_memory_per_block;
    managed.L2CacheSize = native.l2_cache_size;
    managed.MemoryBusWidth = native.memory_bus_width;
    managed.MaxTemperatureCelsius = native.max_temperature_celsius;
    managed.TdpWatts = native.tdp_watts;
    managed.CurrentTemperature = native.current_temperature;
    managed.CurrentPowerDraw = native.current_power_draw;
    managed.MziCount = native.mzi_count;
    managed.WdmChannels = native.wdm_channels;
    managed.OpticalPowerMw = native.optical_power_mw;
    managed.PcieGen = native.pcie_gen;
    managed.PcieLanes = native.pcie_lanes;
    managed.InterconnectBandwidthGbps = native.interconnect_bandwidth_gbps;
    return managed;
}

// ============================================================================
// LightDevice Implementation
// ============================================================================

LightDevice::LightDevice(DeviceType type, UInt32 deviceId) {
    auto nativeType = MarshalDeviceType(type);
    auto result = lightos::inference::LightAccelerator::create(nativeType, deviceId);

    if (!result) {
        throw gcnew Exception("Failed to create device");
    }

    native_ = result->release();
}

LightDevice::~LightDevice() {
    this->!LightDevice();
}

LightDevice::!LightDevice() {
    if (native_) {
        delete native_;
        native_ = nullptr;
    }
}

DeviceProperties LightDevice::GetProperties() {
    auto result = native_->get_properties();
    if (!result) {
        throw gcnew Exception("Failed to get device properties");
    }
    return MarshalDeviceProperties(*result);
}

DeviceType LightDevice::GetDeviceType() {
    return MarshalDeviceType(native_->get_type());
}

String^ LightDevice::GetArchitecture() {
    return gcnew String(native_->get_architecture().data());
}

UInt64 LightDevice::AllocateMemory(UInt64 sizeBytes) {
    auto result = native_->allocate(sizeBytes, lightos::inference::MemoryType::DEVICE_GLOBAL);
    if (!result) {
        throw gcnew Exception("Failed to allocate device memory");
    }
    return *result;
}

void LightDevice::DeallocateMemory(UInt64 handle) {
    auto result = native_->deallocate(handle);
    if (!result) {
        throw gcnew Exception("Failed to deallocate device memory");
    }
}

void LightDevice::CopyHostToDevice(UInt64 deviceHandle, array<Byte>^ hostData) {
    pin_ptr<Byte> pinnedData = &hostData[0];
    auto result = native_->copy_h2d(deviceHandle, pinnedData, hostData->Length);
    if (!result) {
        throw gcnew Exception("Failed to copy data to device");
    }
}

array<Byte>^ LightDevice::CopyDeviceToHost(UInt64 deviceHandle, UInt64 sizeBytes) {
    array<Byte>^ hostData = gcnew array<Byte>(sizeBytes);
    pin_ptr<Byte> pinnedData = &hostData[0];
    auto result = native_->copy_d2h(pinnedData, deviceHandle, sizeBytes);
    if (!result) {
        throw gcnew Exception("Failed to copy data from device");
    }
    return hostData;
}

float LightDevice::GetTemperature() {
    auto result = native_->get_temperature();
    if (!result) return -1.0f;
    return *result;
}

float LightDevice::GetPowerDraw() {
    auto result = native_->get_power_draw();
    if (!result) return -1.0f;
    return *result;
}

float LightDevice::GetUtilization() {
    auto result = native_->get_utilization();
    if (!result) return -1.0f;
    return *result;
}

void LightDevice::SetPowerLimit(float watts) {
    auto result = native_->set_power_limit(watts);
    if (!result) {
        throw gcnew Exception("Failed to set power limit");
    }
}

void LightDevice::SetClockFrequency(UInt32 mhz) {
    auto result = native_->set_clock_frequency(mhz);
    if (!result) {
        throw gcnew Exception("Failed to set clock frequency");
    }
}

// ============================================================================
// PowerGovernor Implementation
// ============================================================================

PowerGovernor::PowerGovernor() {
    lightos::inference::PowerGovernor::Config config;
    native_ = new lightos::inference::PowerGovernor(config);
}

PowerGovernor::PowerGovernor(SchedulingPolicy policy, float globalPowerBudgetWatts) {
    lightos::inference::PowerGovernor::Config config;

    switch (policy) {
        case SchedulingPolicy::FIFO:
            config.policy = lightos::inference::SchedulingPolicy::FIFO;
            break;
        case SchedulingPolicy::ThermalAware:
            config.policy = lightos::inference::SchedulingPolicy::THERMAL_AWARE;
            break;
        case SchedulingPolicy::PowerEfficient:
            config.policy = lightos::inference::SchedulingPolicy::POWER_EFFICIENT;
            break;
        case SchedulingPolicy::LatencyOptimal:
            config.policy = lightos::inference::SchedulingPolicy::LATENCY_OPTIMAL;
            break;
        case SchedulingPolicy::PredictiveCooling:
            config.policy = lightos::inference::SchedulingPolicy::PREDICTIVE_COOLING;
            break;
    }

    config.global_power_budget_watts = globalPowerBudgetWatts;
    native_ = new lightos::inference::PowerGovernor(config);
}

PowerGovernor::~PowerGovernor() {
    this->!PowerGovernor();
}

PowerGovernor::!PowerGovernor() {
    if (native_) {
        delete native_;
        native_ = nullptr;
    }
}

void PowerGovernor::StartScheduler() {
    native_->start_scheduler();
}

void PowerGovernor::StopScheduler() {
    native_->stop_scheduler();
}

Statistics PowerGovernor::GetStatistics() {
    auto nativeStats = native_->get_statistics();

    Statistics managed;
    managed.TotalJobsCompleted = nativeStats.total_jobs_completed;
    managed.ThermalThrottleEvents = nativeStats.thermal_throttle_events;
    managed.PredictiveCoolingTriggers = nativeStats.predictive_cooling_triggers;
    managed.JobMigrations = nativeStats.job_migrations;
    managed.AvgTemperatureC = nativeStats.avg_temperature_c;
    managed.AvgPowerWatts = nativeStats.avg_power_watts;
    managed.AvgUtilization = nativeStats.avg_utilization;
    managed.AvgQueueTimeMs = nativeStats.avg_queue_time.count();

    return managed;
}

// ============================================================================
// DeviceManager Implementation
// ============================================================================

List<DeviceProperties>^ DeviceManager::EnumerateDevices() {
    auto result = lightos::inference::enumerate_devices();
    if (!result) {
        throw gcnew Exception("Failed to enumerate devices");
    }

    auto list = gcnew List<DeviceProperties>();
    for (const auto& props : *result) {
        list->Add(MarshalDeviceProperties(props));
    }
    return list;
}

UInt32 DeviceManager::GetDeviceCount() {
    auto result = lightos::inference::enumerate_devices();
    if (!result) return 0;
    return result->size();
}

// ============================================================================
// TelemetryMonitor Implementation
// ============================================================================

TelemetryMonitor::TelemetryMonitor(PowerGovernor^ governor)
    : governor_(governor), running_(false), interval_ms_(1000) {
}

TelemetryMonitor::~TelemetryMonitor() {
    Stop();
}

void TelemetryMonitor::Start(UInt32 intervalMs) {
    if (running_) return;

    interval_ms_ = intervalMs;
    running_ = true;

    thread_ = gcnew System::Threading::Thread(
        gcnew System::Threading::ThreadStart(this, &TelemetryMonitor::MonitorThread)
    );
    thread_->IsBackground = true;
    thread_->Start();
}

void TelemetryMonitor::Stop() {
    if (!running_) return;

    running_ = false;
    if (thread_ && thread_->IsAlive) {
        thread_->Join();
    }
}

void TelemetryMonitor::MonitorThread() {
    while (running_) {
        try {
            // Get statistics
            auto stats = governor_->GetStatistics();

            // Fire power event
            OnPowerUpdate(stats.AvgPowerWatts, stats.AvgUtilization);

            // Check thermal conditions
            if (stats.AvgTemperatureC > 85.0f) {
                OnThermalCritical(0, stats.AvgTemperatureC, "Critical");
            } else if (stats.AvgTemperatureC > 75.0f) {
                OnThermalWarning(0, stats.AvgTemperatureC, "Warning");
            }

        } catch (Exception^) {
            // Ignore errors in monitoring thread
        }

        System::Threading::Thread::Sleep(interval_ms_);
    }
}

} // namespace Interop
} // namespace LightOS
