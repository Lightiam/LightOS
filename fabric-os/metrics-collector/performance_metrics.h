/* SPDX-License-Identifier: GPL-2.0 */
#ifndef _PERFORMANCE_METRICS_H
#define _PERFORMANCE_METRICS_H

#include <stdint.h>
#include <stdbool.h>
#include <time.h>

/*
 * Performance Metrics Collection
 *
 * Tracks Time-to-First-Token (TTFT), energy efficiency,
 * and other critical performance indicators.
 */

#define METRICS_MAX_SAMPLES 10000
#define METRICS_PERCENTILES 5

/* Metric types */
enum metric_type {
    METRIC_LATENCY = 0,
    METRIC_THROUGHPUT = 1,
    METRIC_ENERGY = 2,
    METRIC_COST = 3,
    METRIC_UTILIZATION = 4,
    METRIC_SPARSITY = 5,
    METRIC_THERMAL = 6,
};

/* Latency metrics */
struct latency_metrics {
    /* Time to First Token (TTFT) */
    uint64_t ttft_ns;              /* Last TTFT measurement */
    uint64_t ttft_sum_ns;          /* Sum for average */
    uint64_t ttft_min_ns;          /* Minimum TTFT */
    uint64_t ttft_max_ns;          /* Maximum TTFT */
    uint32_t ttft_samples;         /* Number of samples */
    float ttft_avg_ms;             /* Average TTFT in ms */
    float ttft_p50_ms;             /* 50th percentile */
    float ttft_p95_ms;             /* 95th percentile */
    float ttft_p99_ms;             /* 99th percentile */

    /* Per-token decode latency */
    uint64_t decode_latency_ns;
    uint64_t decode_sum_ns;
    uint32_t decode_samples;
    float decode_avg_ms;

    /* Prefill (prompt processing) latency */
    uint64_t prefill_latency_ns;
    uint64_t prefill_sum_ns;
    uint32_t prefill_samples;
    float prefill_avg_ms;

    /* End-to-end request latency */
    uint64_t e2e_latency_ns;
    uint64_t e2e_sum_ns;
    uint32_t e2e_samples;
    float e2e_avg_ms;
    float e2e_p99_ms;
};

/* Throughput metrics */
struct throughput_metrics {
    /* Tokens per second */
    float tokens_per_second;
    float tokens_per_second_per_user;
    uint64_t total_tokens_generated;

    /* Requests per second */
    float requests_per_second;
    uint64_t total_requests_processed;

    /* Batch efficiency */
    float average_batch_size;
    uint32_t max_batch_size;
    uint64_t total_batches;

    /* Continuous batching metrics */
    uint32_t active_sequences;
    uint32_t queued_sequences;
    float sequence_completion_rate;
};

/* Energy efficiency metrics */
struct energy_metrics {
    /* Energy consumption */
    uint64_t energy_consumed_joules;
    uint32_t power_watts;          /* Current power draw */
    uint32_t power_avg_watts;      /* Average power */
    uint32_t power_peak_watts;     /* Peak power */

    /* Energy efficiency */
    float energy_per_token_joules;
    float energy_per_request_joules;
    float tops_per_watt;           /* Tera-ops per Watt */

    /* Power breakdown */
    uint32_t compute_power_watts;
    uint32_t memory_power_watts;
    uint32_t io_power_watts;
    uint32_t cooling_power_watts;

    /* Thermal */
    uint32_t temperature_mc;
    bool thermal_throttling_active;
    uint64_t thermal_throttling_time_ns;
};

/* Resource utilization metrics */
struct utilization_metrics {
    /* GPU/NPU utilization */
    float gpu_utilization_percent;
    float gpu_memory_utilization_percent;
    float gpu_sm_utilization_percent;  /* Streaming multiprocessor */

    /* CPU utilization */
    float cpu_utilization_percent;
    float cpu_user_percent;
    float cpu_system_percent;

    /* Memory utilization */
    uint64_t memory_used_bytes;
    uint64_t memory_total_bytes;
    float memory_utilization_percent;

    /* Cache utilization */
    uint64_t kv_cache_used_bytes;
    uint64_t kv_cache_total_bytes;
    float kv_cache_hit_rate;
    uint64_t kv_cache_hits;
    uint64_t kv_cache_misses;

    /* Network utilization */
    uint64_t network_bytes_sent;
    uint64_t network_bytes_received;
    float network_bandwidth_utilization_percent;
};

/* Sparsity metrics */
struct sparsity_metrics {
    /* Activation sparsity */
    float activation_sparsity_percent;
    uint64_t total_activations;
    uint64_t zero_activations;

    /* Expert sparsity (MoE) */
    float expert_sparsity_percent;
    uint32_t active_experts;
    uint32_t total_experts;
    float avg_experts_per_token;

    /* Token dropping */
    uint64_t tokens_processed;
    uint64_t tokens_dropped;
    float token_drop_rate;

    /* Layer skipping */
    uint64_t layers_executed;
    uint64_t layers_skipped;
    float layer_skip_rate;

    /* Compute savings */
    uint64_t compute_ops_saved;
    uint64_t compute_ops_total;
    float compute_reduction_percent;
};

/* Aggregate performance metrics */
struct performance_metrics {
    /* Timestamp */
    uint64_t timestamp_ns;
    struct timespec collection_time;

    /* Component metrics */
    struct latency_metrics latency;
    struct throughput_metrics throughput;
    struct energy_metrics energy;
    struct utilization_metrics utilization;
    struct sparsity_metrics sparsity;

    /* Cost metrics */
    float cost_per_1000_tokens;
    float cost_per_hour;
    float total_cost;

    /* Quality metrics */
    float model_accuracy_percent;
    uint32_t errors_detected;
    uint32_t requests_failed;
};

/* Metrics collector */
struct metrics_collector {
    struct performance_metrics current;
    struct performance_metrics *history;
    uint32_t history_size;
    uint32_t history_index;

    /* Percentile tracking */
    uint64_t *ttft_samples;
    uint32_t num_ttft_samples;

    /* Collection state */
    bool collecting;
    uint64_t collection_start_ns;
    pthread_mutex_t lock;
};

/* Function prototypes */

/* Initialization */
int metrics_init(struct metrics_collector *collector,
                uint32_t history_size);
void metrics_cleanup(struct metrics_collector *collector);

/* Collection */
int metrics_start_collection(struct metrics_collector *collector);
void metrics_stop_collection(struct metrics_collector *collector);
void metrics_reset(struct metrics_collector *collector);

/* Recording */
void metrics_record_ttft(struct metrics_collector *collector,
                        uint64_t ttft_ns);
void metrics_record_decode_latency(struct metrics_collector *collector,
                                  uint64_t latency_ns);
void metrics_record_token(struct metrics_collector *collector,
                         uint32_t batch_size);
void metrics_record_energy(struct metrics_collector *collector,
                          uint32_t power_watts,
                          uint64_t duration_ns);
void metrics_record_cache_access(struct metrics_collector *collector,
                                bool hit);
void metrics_record_sparsity(struct metrics_collector *collector,
                            uint64_t active,
                            uint64_t total);

/* Analysis */
void metrics_calculate_percentiles(struct metrics_collector *collector);
float metrics_get_percentile(uint64_t *samples,
                            uint32_t num_samples,
                            float percentile);
void metrics_update_averages(struct metrics_collector *collector);

/* Export */
void metrics_export_json(struct metrics_collector *collector,
                        char *buffer,
                        uint32_t buffer_size);
void metrics_export_prometheus(struct metrics_collector *collector,
                              char *buffer,
                              uint32_t buffer_size);
void metrics_print_summary(struct metrics_collector *collector);

/* Utility functions */
static inline uint64_t metrics_get_time_ns(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

static inline float metrics_calculate_tps(uint64_t tokens,
                                         uint64_t duration_ns)
{
    if (duration_ns == 0)
        return 0.0f;
    return (float)tokens / ((float)duration_ns / 1e9f);
}

static inline float metrics_ns_to_ms(uint64_t ns)
{
    return (float)ns / 1e6f;
}

#endif /* _PERFORMANCE_METRICS_H */
