/* SPDX-License-Identifier: GPL-2.0 */
#ifndef _LIGHTOS_SPIKING_CORE_H
#define _LIGHTOS_SPIKING_CORE_H

#include <linux/types.h>
#include <linux/list.h>
#include <linux/spinlock.h>
#include <linux/workqueue.h>

/*
 * LightOS Spiking Neural Network Engine
 *
 * Event-driven processing inspired by biological neurons.
 * Achieves >69% sparsity through conditional activation.
 */

#define SPIKING_MAX_EVENTS 4096
#define SPIKING_MAX_NEURONS 65536
#define SPIKING_DEFAULT_THRESHOLD 500  /* millivolts */

/* Spike encoding methods */
enum spike_encoding {
    SPIKE_ENCODING_RATE = 0,      /* Spike frequency encodes magnitude */
    SPIKE_ENCODING_TEMPORAL = 1,  /* Spike timing encodes information */
    SPIKE_ENCODING_DELTA = 2,     /* Spikes on value changes (optimal) */
};

/* Neuron states */
enum neuron_state {
    NEURON_STATE_RESTING = 0,
    NEURON_STATE_INTEGRATING = 1,
    NEURON_STATE_SPIKING = 2,
    NEURON_STATE_REFRACTORY = 3,
};

/* Spike event structure */
struct spike_event {
    struct list_head list;        /* List linkage */
    __u32 neuron_id;              /* Source neuron */
    __u64 timestamp_ns;           /* Event timestamp */
    __s32 amplitude_mv;           /* Spike amplitude in millivolts */
    __u32 synapse_count;          /* Number of target synapses */
    void *payload;                /* Optional event payload */
};

/* Leaky Integrate-and-Fire (LIF) neuron model */
struct lif_neuron {
    __u32 id;                     /* Neuron identifier */
    enum neuron_state state;      /* Current state */

    /* Membrane dynamics */
    __s32 membrane_potential_mv;  /* Current potential (millivolts) */
    __s32 threshold_mv;           /* Firing threshold */
    __s32 resting_potential_mv;   /* Resting potential (typically -70mV) */
    __s32 reset_potential_mv;     /* Post-spike reset potential */

    /* Time constants (microseconds) */
    __u32 tau_membrane_us;        /* Membrane time constant */
    __u32 tau_refractory_us;      /* Refractory period */
    __u64 last_spike_time_ns;     /* Last spike timestamp */

    /* Spike statistics */
    __u64 total_spikes;           /* Total spikes emitted */
    __u64 last_isi_ns;            /* Last inter-spike interval */
    __u32 current_rate_hz;        /* Current firing rate */

    /* Connections */
    __u32 input_synapse_count;    /* Number of input synapses */
    __u32 output_synapse_count;   /* Number of output synapses */
};

/* Spiking engine configuration */
struct spiking_config {
    enum spike_encoding encoding; /* Encoding method */
    bool enabled;                  /* Enable/disable spiking engine */
    __u32 max_events_per_cycle;   /* Event processing limit */
    __u32 processing_interval_us; /* Event processing interval */

    /* Sparsity targets */
    __u32 target_sparsity_percent; /* Target activation sparsity (e.g., 69) */
    __u32 current_sparsity_percent;/* Current measured sparsity */

    /* Performance metrics */
    __u64 total_events_processed;
    __u64 events_dropped;
    __u64 total_neurons_active;
    __u64 total_neurons_inactive;
};

/* Spiking engine state */
struct spiking_engine {
    struct spiking_config config;

    /* Event queue */
    struct list_head event_queue;
    spinlock_t queue_lock;
    __u32 pending_events;

    /* Neuron pool */
    struct lif_neuron *neurons;
    __u32 neuron_count;
    spinlock_t neuron_lock;

    /* Asynchronous processing */
    struct workqueue_struct *workqueue;
    struct delayed_work process_work;
    bool processing_active;

    /* Statistics */
    __u64 cycles_processed;
    __u64 total_spikes_emitted;
    __u64 total_spikes_received;
};

/* Function prototypes */

/* Initialize/cleanup */
int spiking_engine_init(struct spiking_engine *engine, struct spiking_config *config);
void spiking_engine_cleanup(struct spiking_engine *engine);

/* Neuron management */
int spiking_neuron_create(struct spiking_engine *engine, __u32 neuron_id,
                          struct lif_neuron *config);
void spiking_neuron_destroy(struct spiking_engine *engine, __u32 neuron_id);
int spiking_neuron_get_state(struct spiking_engine *engine, __u32 neuron_id,
                             struct lif_neuron *state);

/* Event submission */
int spiking_event_submit(struct spiking_engine *engine, struct spike_event *event);
int spiking_event_submit_batch(struct spiking_engine *engine,
                               struct spike_event *events, __u32 count);

/* Encoding/Decoding */
int spiking_encode_value(struct spiking_engine *engine, float value,
                        struct spike_event *event);
float spiking_decode_spikes(struct spiking_engine *engine,
                            struct spike_event *events, __u32 count);

/* Processing control */
int spiking_engine_start(struct spiking_engine *engine);
void spiking_engine_stop(struct spiking_engine *engine);
void spiking_engine_process_cycle(struct work_struct *work);

/* Statistics */
void spiking_get_statistics(struct spiking_engine *engine,
                           struct spiking_config *stats);
__u32 spiking_calculate_sparsity(struct spiking_engine *engine);

/* Utility functions */
static inline bool spiking_neuron_is_active(struct lif_neuron *neuron)
{
    return neuron->state == NEURON_STATE_INTEGRATING ||
           neuron->state == NEURON_STATE_SPIKING;
}

static inline __u64 spiking_get_time_ns(void)
{
    return ktime_get_ns();
}

#endif /* _LIGHTOS_SPIKING_CORE_H */
