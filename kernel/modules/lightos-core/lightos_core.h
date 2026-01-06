/* SPDX-License-Identifier: GPL-2.0 */
#ifndef _LIGHTOS_CORE_H
#define _LIGHTOS_CORE_H

#include <linux/ioctl.h>
#include <linux/types.h>

#define LIGHTOS_DEVICE_NAME "lightos"
#define LIGHTOS_MAX_DEVICES 256
#define LIGHTOS_MAX_LINKS 1024

enum lightos_device_type {
    LIGHTOS_DEVICE_GPU = 0,
    LIGHTOS_DEVICE_TPU = 1,
    LIGHTOS_DEVICE_NPU = 2,
    LIGHTOS_DEVICE_PHOTONIC = 3,  /* Photonic NPU */
};

struct lightos_device_state {
    __u32 device_id;
    __u32 device_type;
    __u32 utilization_percent;
    __u32 power_watts;
    __u64 memory_used_bytes;
    __u64 memory_total_bytes;
};

/* Spiking engine structures (user-space interface) */
struct lightos_spiking_config {
    __u32 encoding;                /* spike_encoding enum */
    __u32 enabled;                 /* Boolean: enable/disable */
    __u32 max_events_per_cycle;
    __u32 processing_interval_us;
    __u32 target_sparsity_percent;
    __u32 current_sparsity_percent;
    __u64 total_events_processed;
    __u64 events_dropped;
};

struct lightos_spike_event {
    __u32 neuron_id;
    __u64 timestamp_ns;
    __s32 amplitude_mv;
    __u32 synapse_count;
};

struct lightos_neuron_state {
    __u32 neuron_id;
    __u32 state;                   /* neuron_state enum */
    __s32 membrane_potential_mv;
    __u64 total_spikes;
    __u32 current_rate_hz;
};

#define LIGHTOS_IOC_MAGIC 'L'
#define LIGHTOS_IOC_GET_DEVICE_STATE _IOWR(LIGHTOS_IOC_MAGIC, 1, struct lightos_device_state)
#define LIGHTOS_IOC_SPIKING_CONFIG _IOWR(LIGHTOS_IOC_MAGIC, 2, struct lightos_spiking_config)
#define LIGHTOS_IOC_SPIKING_START _IO(LIGHTOS_IOC_MAGIC, 3)
#define LIGHTOS_IOC_SPIKING_STOP _IO(LIGHTOS_IOC_MAGIC, 4)
#define LIGHTOS_IOC_SPIKING_SUBMIT_EVENT _IOW(LIGHTOS_IOC_MAGIC, 5, struct lightos_spike_event)
#define LIGHTOS_IOC_SPIKING_GET_STATS _IOR(LIGHTOS_IOC_MAGIC, 6, struct lightos_spiking_config)
#define LIGHTOS_IOC_GET_NEURON_STATE _IOWR(LIGHTOS_IOC_MAGIC, 7, struct lightos_neuron_state)

#endif /* _LIGHTOS_CORE_H */
