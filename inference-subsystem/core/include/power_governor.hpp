/**
 * LightOS Inference Subsystem - Thermal-Aware Scheduler
 *
 * Module 2: PowerGovernor - Solve the "Unsolvable Trilemma"
 *
 * The Trilemma: Power vs I/O vs Utilization
 * Solution: Treat heat as a first-class scheduling constraint
 *
 * Key Innovations:
 * - Predictive Cooling: Pre-cool zones before heavy workloads
 * - Topology-Aware Migration: Move jobs to cooler islands
 * - Sparsity-Aware Power Capping: Dynamic voltage/frequency scaling
 * - Integration with DCIM Pro for thermal telemetry
 *
 * @file power_governor.hpp
 * @author LightRail AI - Principal Kernel Architect
 * @version 1.0.0
 */

#pragma once

#include "light_accelerator.hpp"
#include <atomic>
#include <chrono>
#include <functional>
#include <queue>
#include <optional>
#include <array>

namespace lightos::inference {

// ============================================================================
// Thermal Telemetry (from DCIM Pro)
// ============================================================================

struct ThermalState {
    float temperature_celsius;
    float thermal_inertia;           // Rate of temperature change (°C/sec)
    float sm_clock_stability;        // Clock jitter metric (0.0 to 1.0)
    float power_draw_watts;
    float power_limit_watts;
    std::chrono::milliseconds timestamp;
};

struct TopologyIsland {
    std::uint32_t island_id;
    std::vector<DeviceHandle> devices;
    float avg_temperature;
    float cooling_capacity_watts;    // Available cooling headroom
    std::size_t queue_depth;         // Pending jobs
};

// ============================================================================
// Workload Characterization
// ============================================================================

enum class WorkloadType : std::uint8_t {
    COMPUTE_BOUND,      // High arithmetic intensity (MatMul, Conv)
    MEMORY_BOUND,       // Low arithmetic intensity (Attention, LayerNorm)
    SPARSE,             // >50% zeros (MoE, Pruned models)
    DENSE,              // <10% zeros
    MIXED
};

struct WorkloadProfile {
    WorkloadType type;
    float sparsity_ratio;            // 0.0 (dense) to 1.0 (all zeros)
    float arithmetic_intensity;      // FLOPs per byte
    std::size_t memory_footprint_bytes;
    std::uint32_t estimated_power_watts;
    std::chrono::milliseconds estimated_duration;

    // Thermal impact prediction
    float predicted_temperature_rise; // Expected ΔT (°C)
};

// ============================================================================
// Scheduling Policies
// ============================================================================

enum class SchedulingPolicy : std::uint8_t {
    FIFO,                   // First-In-First-Out
    THERMAL_AWARE,          // Prioritize cooler devices
    POWER_EFFICIENT,        // Minimize watts/token
    LATENCY_OPTIMAL,        // Minimize time-to-first-token
    PREDICTIVE_COOLING      // Pre-cooling enabled
};

// ============================================================================
// PowerGovernor Class
// ============================================================================

class PowerGovernor {
public:
    struct Config {
        SchedulingPolicy policy = SchedulingPolicy::PREDICTIVE_COOLING;

        // Thermal Limits (aligned with DCIM Pro)
        float temperature_warning_c = 75.0f;
        float temperature_critical_c = 85.0f;
        float temperature_emergency_c = 90.0f;

        // Power Limits
        float global_power_budget_watts = 5000.0f;
        float per_device_power_limit_watts = 700.0f;

        // Predictive Cooling Parameters
        float precool_threshold_c = 70.0f;       // Start pre-cooling
        std::chrono::seconds precool_duration{30};
        float cooling_rate_c_per_sec = 0.5f;

        // Sparsity-Aware Power Capping
        bool enable_dynamic_power_cap = true;
        float sparse_power_multiplier = 0.7f;    // 30% reduction for sparse workloads

        // Telemetry
        std::chrono::milliseconds telemetry_interval{100};
    };

    explicit PowerGovernor(const Config& config = {});
    ~PowerGovernor();

    // Device Registration
    void register_device(std::unique_ptr<LightAccelerator> device);
    void unregister_device(DeviceHandle handle);

    // Workload Submission
    struct Job {
        std::uint64_t job_id;
        WorkloadProfile profile;
        std::function<void(LightAccelerator&)> execute;
        std::chrono::time_point<std::chrono::steady_clock> submit_time;
        std::optional<DeviceHandle> preferred_device;
    };

    std::uint64_t submit_job(const WorkloadProfile& profile, std::function<void(LightAccelerator&)> execute);

    // Scheduling
    void start_scheduler();
    void stop_scheduler();

    // Thermal Management
    Result<void> apply_thermal_throttling(DeviceHandle device, float target_temp);
    Result<void> trigger_predictive_cooling(DeviceHandle device, const WorkloadProfile& upcoming_workload);
    Result<void> migrate_job(std::uint64_t job_id, DeviceHandle target_device);

    // Sparsity-Aware Power Control
    Result<void> adjust_power_for_sparsity(DeviceHandle device, float sparsity_ratio);

    // Telemetry & Monitoring
    Result<ThermalState> get_thermal_state(DeviceHandle device) const;
    Result<std::vector<TopologyIsland>> get_topology_islands() const;
    Result<float> get_global_power_draw() const;
    Result<std::size_t> get_pending_jobs() const;

    // Statistics
    struct Statistics {
        std::uint64_t total_jobs_completed;
        std::uint64_t thermal_throttle_events;
        std::uint64_t predictive_cooling_triggers;
        std::uint64_t job_migrations;
        float avg_temperature_c;
        float avg_power_watts;
        float avg_utilization;
        std::chrono::milliseconds avg_queue_time;
    };

    Statistics get_statistics() const;

private:
    // Internal scheduler logic
    void scheduler_thread();
    std::optional<DeviceHandle> select_device_for_job(const Job& job);
    bool should_precool(DeviceHandle device, const WorkloadProfile& profile);
    void update_thermal_state(DeviceHandle device);
    void enforce_power_limits();

    // Predictive models (from DCIM Pro integration)
    float predict_temperature_rise(DeviceHandle device, const WorkloadProfile& profile);
    std::chrono::milliseconds predict_cooling_time(DeviceHandle device, float target_temp);

    Config config_;
    std::atomic<bool> running_{false};

    // Device Pool
    std::vector<std::unique_ptr<LightAccelerator>> devices_;
    std::unordered_map<DeviceHandle, ThermalState> thermal_states_;
    std::unordered_map<DeviceHandle, std::atomic<bool>> device_busy_;

    // Job Queue
    std::queue<Job> job_queue_;
    std::mutex queue_mutex_;
    std::condition_variable queue_cv_;
    std::atomic<std::uint64_t> next_job_id_{1};

    // Topology Islands (for migration)
    std::vector<TopologyIsland> islands_;

    // Statistics
    mutable std::mutex stats_mutex_;
    Statistics stats_{};

    // Scheduler thread
    std::thread scheduler_thread_;
};

// ============================================================================
// Advanced Thermal Control Algorithms
// ============================================================================

class ThermalController {
public:
    // Predictive Cooling: Pre-cool zone before heavy workload
    // Uses thermal inertia and heat capacity models
    static Result<void> predictive_cool(
        LightAccelerator& device,
        float target_temperature,
        std::chrono::seconds duration
    );

    // Dynamic Power Capping: Adjust voltage/frequency based on sparsity
    // Sparse workloads don't saturate hardware, can save power
    static Result<void> dynamic_power_cap(
        LightAccelerator& device,
        float sparsity_ratio,
        float base_power_watts
    );

    // Topology-Aware Migration: Move job to cooler island
    static Result<void> migrate_to_cooler_island(
        PowerGovernor& governor,
        std::uint64_t job_id,
        const std::vector<TopologyIsland>& islands
    );

    // Thermal-Aware Frequency Scaling
    // NVIDIA: nvidia-smi -lgc (lock GPU clock)
    // AMD: rocm-smi --setperflevel
    static Result<void> thermal_frequency_scaling(
        LightAccelerator& device,
        float current_temp,
        float target_temp
    );
};

// ============================================================================
// Sparsity Detection (for Power Optimization)
// ============================================================================

class SparsityDetector {
public:
    // Analyze tensor sparsity on-the-fly
    template<typename T>
    static float detect_sparsity(const T* data, std::size_t size, T epsilon = T(1e-6)) {
        std::size_t zero_count = 0;
        for (std::size_t i = 0; i < size; ++i) {
            if (std::abs(data[i]) < epsilon) {
                ++zero_count;
            }
        }
        return static_cast<float>(zero_count) / size;
    }

    // Hardware-accelerated sparsity detection (GPU kernel)
    static Result<float> detect_sparsity_gpu(
        LightAccelerator& device,
        MemoryHandle data,
        std::size_t size,
        StreamHandle stream = 0
    );

    // Predict sparsity from model architecture (MoE, Pruned)
    static float predict_sparsity(const std::string& model_name);
};

// ============================================================================
// DCIM Pro Integration
// ============================================================================

class DCIMProConnector {
public:
    DCIMProConnector(std::string_view endpoint);

    // Fetch enhanced telemetry from DCIM Pro
    Result<ThermalState> fetch_thermal_state(DeviceHandle device);
    Result<float> fetch_sm_clock_stability(DeviceHandle device);
    Result<float> fetch_thermal_inertia(DeviceHandle device);

    // Trigger predictive cooling via DCIM Pro
    Result<void> trigger_hvac_precool(std::uint32_t rack_id, float target_temp);

    // Report power metrics
    Result<void> report_power_savings(float watts_saved);

private:
    std::string endpoint_;
};

// ============================================================================
// Concrete Implementation: Thermal-Aware Scheduler Logic
// ============================================================================

// Example: Select best device for a job
inline std::optional<DeviceHandle> PowerGovernor::select_device_for_job(const Job& job) {
    std::optional<DeviceHandle> best_device;
    float best_score = std::numeric_limits<float>::max();

    for (const auto& device : devices_) {
        auto handle = reinterpret_cast<DeviceHandle>(device.get());

        // Skip if device is busy
        if (device_busy_[handle].load()) continue;

        // Get thermal state
        auto thermal = get_thermal_state(handle);
        if (!thermal) continue;

        float score = 0.0f;

        switch (config_.policy) {
            case SchedulingPolicy::THERMAL_AWARE:
                // Prefer cooler devices
                score = thermal->temperature_celsius;
                break;

            case SchedulingPolicy::POWER_EFFICIENT:
                // Prefer devices with lower power draw
                score = thermal->power_draw_watts / thermal->power_limit_watts;
                break;

            case SchedulingPolicy::PREDICTIVE_COOLING:
                // Factor in predicted temperature rise
                score = thermal->temperature_celsius +
                        predict_temperature_rise(handle, job.profile);
                break;

            default:
                score = thermal->temperature_celsius;
        }

        // Check if device would exceed thermal limits
        if (thermal->temperature_celsius > config_.temperature_warning_c) {
            score += 100.0f;  // Penalize hot devices
        }

        if (score < best_score) {
            best_score = score;
            best_device = handle;
        }
    }

    // If best device is too hot, trigger predictive cooling
    if (best_device) {
        auto thermal = get_thermal_state(*best_device);
        if (thermal && should_precool(*best_device, job.profile)) {
            trigger_predictive_cooling(*best_device, job.profile);
        }
    }

    return best_device;
}

// Example: Sparsity-aware power adjustment
inline Result<void> PowerGovernor::adjust_power_for_sparsity(DeviceHandle device, float sparsity_ratio) {
    if (!config_.enable_dynamic_power_cap) {
        return {};
    }

    // Sparse workloads don't saturate hardware
    // Safe to reduce power limit without losing throughput
    float power_multiplier = 1.0f - (sparsity_ratio * (1.0f - config_.sparse_power_multiplier));

    float new_limit = config_.per_device_power_limit_watts * power_multiplier;

    // Find device
    for (auto& dev : devices_) {
        if (reinterpret_cast<DeviceHandle>(dev.get()) == device) {
            return dev->set_power_limit(new_limit);
        }
    }

    return std::unexpected(AcceleratorError::INVALID_DEVICE);
}

} // namespace lightos::inference
