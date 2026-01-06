/* SPDX-License-Identifier: GPL-2.0 */
#ifndef _LIGHTRAIL_SCHEDULER_H
#define _LIGHTRAIL_SCHEDULER_H

#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>

/*
 * LightRail AI Mathematical Scheduler
 *
 * Provably optimal routing and scheduling algorithms for AI workloads.
 * Replaces heuristic-based scheduling with mathematical guarantees.
 */

#define LIGHTRAIL_MAX_DEVICES 256
#define LIGHTRAIL_MAX_TASKS 4096
#define LIGHTRAIL_MAX_ROUTES 16

/* Optimization objectives */
enum optimization_objective {
    OPT_MINIMIZE_LATENCY = 0,       /* Minimize end-to-end latency */
    OPT_MINIMIZE_POWER = 1,         /* Minimize energy consumption */
    OPT_MINIMIZE_COST = 2,          /* Minimize monetary cost */
    OPT_MAXIMIZE_THROUGHPUT = 3,    /* Maximize tokens/second */
    OPT_BALANCED = 4,               /* Multi-objective balance */
};

/* Scheduling algorithm */
enum scheduling_algorithm {
    SCHED_OPTIMAL_DIJKSTRA = 0,     /* Dijkstra for shortest path */
    SCHED_OPTIMAL_ASTAR = 1,        /* A* with heuristics */
    SCHED_BELLMAN_FORD = 2,         /* Bellman-Ford for constraints */
    SCHED_LINEAR_PROGRAMMING = 3,   /* Simplex method */
    SCHED_DYNAMIC_PROGRAMMING = 4,  /* DP for multi-stage */
    SCHED_GREEDY_OPTIMAL = 5,       /* Greedy with optimality proof */
};

/* Device types */
enum device_type {
    DEVICE_TYPE_CPU = 0,
    DEVICE_TYPE_GPU = 1,
    DEVICE_TYPE_TPU = 2,
    DEVICE_TYPE_NPU = 3,
    DEVICE_TYPE_PHOTONIC = 4,
};

/* Task states */
enum task_state {
    TASK_STATE_PENDING = 0,
    TASK_STATE_SCHEDULED = 1,
    TASK_STATE_RUNNING = 2,
    TASK_STATE_COMPLETED = 3,
    TASK_STATE_FAILED = 4,
    TASK_STATE_PREEMPTED = 5,
};

/* Device information */
struct device_info {
    uint32_t device_id;
    enum device_type type;
    char name[64];

    /* Capabilities */
    uint64_t compute_capacity_gflops;
    uint64_t memory_capacity_bytes;
    uint64_t memory_bandwidth_gbps;
    uint32_t num_cores;

    /* Current state */
    float utilization_percent;
    uint64_t memory_used_bytes;
    uint32_t power_watts;
    uint32_t temperature_mc;

    /* Performance characteristics */
    float peak_performance_tflops;
    float energy_efficiency_gflops_per_w;
    uint32_t latency_us;            /* Average operation latency */

    /* Cost (for multi-cloud scenarios) */
    float cost_per_hour;
    float cost_per_inference;

    /* Connectivity */
    uint32_t num_links;
    uint32_t link_bandwidth_gbps[LIGHTRAIL_MAX_ROUTES];
    uint32_t link_latency_us[LIGHTRAIL_MAX_ROUTES];
    uint32_t connected_devices[LIGHTRAIL_MAX_ROUTES];
};

/* Task descriptor */
struct task_descriptor {
    uint32_t task_id;
    enum task_state state;

    /* Workload characteristics */
    uint64_t compute_ops;           /* FLOPs required */
    uint64_t memory_required_bytes;
    uint64_t memory_bandwidth_required_gbps;
    uint32_t batch_size;

    /* Constraints */
    uint32_t deadline_ms;           /* SLA deadline */
    enum device_type preferred_device_type;
    uint32_t min_memory_bytes;
    uint32_t max_power_watts;
    bool requires_high_precision;   /* FP32 vs FP16 */

    /* Scheduling decisions */
    uint32_t assigned_device_id;
    uint32_t scheduled_time_ms;
    uint32_t estimated_duration_ms;
    uint32_t estimated_power_mw;
    float estimated_cost;

    /* KV cache affinity */
    bool has_kv_cache;
    uint64_t kv_cache_size_bytes;
    uint32_t cache_device_id;       /* Device with cached data */

    /* Dependencies */
    uint32_t num_dependencies;
    uint32_t dependency_ids[16];

    /* Priority */
    uint32_t priority;              /* Higher = more important */
};

/* Route between devices */
struct route {
    uint32_t source_device_id;
    uint32_t dest_device_id;
    uint32_t num_hops;
    uint32_t path[LIGHTRAIL_MAX_ROUTES];  /* Device IDs in path */
    uint32_t total_latency_us;
    uint32_t total_bandwidth_gbps;
    float total_cost;
    float congestion_factor;        /* 1.0 = no congestion */
};

/* Scheduler configuration */
struct scheduler_config {
    enum optimization_objective objective;
    enum scheduling_algorithm algorithm;

    /* Multi-objective weights (sum to 1.0) */
    float weight_latency;           /* α */
    float weight_power;             /* β */
    float weight_cost;              /* γ */

    /* Constraints */
    uint32_t max_latency_ms;
    uint32_t max_power_watts;
    float max_cost_per_task;

    /* Cache awareness */
    bool cache_aware_scheduling;
    float cache_hit_value;          /* Value of cache hits vs misses */

    /* Load balancing */
    bool load_balancing_enabled;
    float load_balance_threshold;   /* Max deviation from average */

    /* Preemption */
    bool preemption_enabled;
    uint32_t preemption_overhead_us;

    /* Predictive features */
    bool enable_prefetching;
    bool enable_workload_prediction;

    /* Statistics */
    uint64_t total_tasks_scheduled;
    uint64_t total_tasks_completed;
    uint64_t total_scheduling_decisions;
    uint64_t cache_aware_decisions;
    float average_scheduling_time_us;
    float optimization_quality;     /* 0-1, how close to optimal */
};

/* Scheduler state */
struct lightrail_scheduler {
    struct scheduler_config config;

    /* Device pool */
    struct device_info devices[LIGHTRAIL_MAX_DEVICES];
    uint32_t num_devices;
    pthread_mutex_t device_lock;

    /* Task queue */
    struct task_descriptor *task_queue;
    uint32_t task_queue_size;
    uint32_t task_queue_head;
    uint32_t task_queue_tail;
    pthread_mutex_t task_lock;
    pthread_cond_t task_available;

    /* Routing table (cached routes) */
    struct route **routing_table;   /* [source][dest] */
    pthread_mutex_t route_lock;

    /* Scheduling thread */
    pthread_t scheduler_thread;
    bool running;

    /* Performance metrics */
    uint64_t total_execution_time_us;
    uint64_t total_data_movement_bytes;
    uint64_t total_energy_consumed_joules;
    float total_cost;
};

/* Function prototypes */

/* Initialization */
int lightrail_scheduler_init(struct lightrail_scheduler *sched,
                            struct scheduler_config *config);
void lightrail_scheduler_cleanup(struct lightrail_scheduler *sched);

/* Device management */
int lightrail_register_device(struct lightrail_scheduler *sched,
                             struct device_info *device);
int lightrail_unregister_device(struct lightrail_scheduler *sched,
                               uint32_t device_id);
int lightrail_update_device_state(struct lightrail_scheduler *sched,
                                 uint32_t device_id,
                                 struct device_info *state);

/* Task submission */
int lightrail_submit_task(struct lightrail_scheduler *sched,
                         struct task_descriptor *task);
int lightrail_submit_batch(struct lightrail_scheduler *sched,
                          struct task_descriptor *tasks,
                          uint32_t count);

/* Scheduling algorithms */
int lightrail_schedule_optimal(struct lightrail_scheduler *sched,
                              struct task_descriptor *task);
int lightrail_schedule_dijkstra(struct lightrail_scheduler *sched,
                               uint32_t source_id, uint32_t dest_id,
                               struct route *route);
int lightrail_schedule_astar(struct lightrail_scheduler *sched,
                            struct task_descriptor *task);
int lightrail_schedule_linear_programming(struct lightrail_scheduler *sched);

/* Route computation */
int lightrail_compute_route(struct lightrail_scheduler *sched,
                           uint32_t source_id, uint32_t dest_id,
                           struct route *route);
int lightrail_compute_all_routes(struct lightrail_scheduler *sched);
float lightrail_route_cost(struct lightrail_scheduler *sched,
                          struct route *route,
                          struct task_descriptor *task);

/* Cache-aware scheduling */
int lightrail_schedule_with_cache_affinity(struct lightrail_scheduler *sched,
                                          struct task_descriptor *task);
float lightrail_calculate_cache_benefit(struct lightrail_scheduler *sched,
                                       struct task_descriptor *task,
                                       uint32_t device_id);

/* Load balancing */
int lightrail_balance_load(struct lightrail_scheduler *sched);
float lightrail_calculate_load_imbalance(struct lightrail_scheduler *sched);

/* Predictive scheduling */
int lightrail_predict_workload(struct lightrail_scheduler *sched,
                              struct task_descriptor *predicted_tasks,
                              uint32_t *num_tasks);
int lightrail_prefetch_data(struct lightrail_scheduler *sched,
                           struct task_descriptor *task);

/* Scheduler thread */
void *lightrail_scheduler_thread(void *arg);
int lightrail_start_scheduler(struct lightrail_scheduler *sched);
void lightrail_stop_scheduler(struct lightrail_scheduler *sched);

/* Statistics */
void lightrail_get_statistics(struct lightrail_scheduler *sched,
                             struct scheduler_config *stats);
void lightrail_reset_statistics(struct lightrail_scheduler *sched);

/* Utility functions */
static inline float lightrail_compute_objective(struct lightrail_scheduler *sched,
                                               uint32_t latency_ms,
                                               uint32_t power_mw,
                                               float cost)
{
    /* Multi-objective function: α·latency + β·power + γ·cost */
    return (sched->config.weight_latency * (float)latency_ms) +
           (sched->config.weight_power * (float)power_mw / 1000.0f) +
           (sched->config.weight_cost * cost);
}

static inline bool lightrail_device_can_run_task(struct device_info *device,
                                                 struct task_descriptor *task)
{
    return (device->memory_capacity_bytes >= task->memory_required_bytes) &&
           (device->power_watts <= task->max_power_watts) &&
           (device->utilization_percent < 95.0f);
}

static inline uint32_t lightrail_estimate_task_duration(struct task_descriptor *task,
                                                        struct device_info *device)
{
    if (device->peak_performance_tflops == 0.0f)
        return UINT32_MAX;

    /* Duration = ops / (performance * utilization) */
    float performance_tflops = device->peak_performance_tflops *
                              (1.0f - device->utilization_percent / 100.0f);
    float duration_s = (float)task->compute_ops / (performance_tflops * 1e12f);

    return (uint32_t)(duration_s * 1000.0f);  /* Convert to ms */
}

#endif /* _LIGHTRAIL_SCHEDULER_H */
