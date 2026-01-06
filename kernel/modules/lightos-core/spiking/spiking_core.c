/* SPDX-License-Identifier: GPL-2.0 */
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/slab.h>
#include <linux/math64.h>
#include <linux/ktime.h>
#include "spiking_core.h"

/*
 * LightOS Spiking Neural Network Engine Implementation
 *
 * This module implements an event-driven spiking neural network engine
 * using the Leaky Integrate-and-Fire (LIF) neuron model.
 */

/* Constants for LIF neuron dynamics */
#define LIF_DEFAULT_MEMBRANE_TAU_US 10000    /* 10ms membrane time constant */
#define LIF_DEFAULT_REFRACTORY_US 2000       /* 2ms refractory period */
#define LIF_RESTING_POTENTIAL_MV -70         /* -70mV resting potential */
#define LIF_RESET_POTENTIAL_MV -80           /* -80mV reset potential */

/* Initialize the spiking engine */
int spiking_engine_init(struct spiking_engine *engine, struct spiking_config *config)
{
    if (!engine || !config)
        return -EINVAL;

    memset(engine, 0, sizeof(*engine));
    memcpy(&engine->config, config, sizeof(*config));

    /* Initialize event queue */
    INIT_LIST_HEAD(&engine->event_queue);
    spin_lock_init(&engine->queue_lock);
    engine->pending_events = 0;

    /* Allocate neuron pool */
    engine->neuron_count = SPIKING_MAX_NEURONS;
    engine->neurons = kzalloc(engine->neuron_count * sizeof(struct lif_neuron),
                             GFP_KERNEL);
    if (!engine->neurons) {
        pr_err("Failed to allocate neuron pool\n");
        return -ENOMEM;
    }

    spin_lock_init(&engine->neuron_lock);

    /* Initialize neurons to resting state */
    for (int i = 0; i < engine->neuron_count; i++) {
        struct lif_neuron *neuron = &engine->neurons[i];
        neuron->id = i;
        neuron->state = NEURON_STATE_RESTING;
        neuron->membrane_potential_mv = LIF_RESTING_POTENTIAL_MV;
        neuron->threshold_mv = SPIKING_DEFAULT_THRESHOLD;
        neuron->resting_potential_mv = LIF_RESTING_POTENTIAL_MV;
        neuron->reset_potential_mv = LIF_RESET_POTENTIAL_MV;
        neuron->tau_membrane_us = LIF_DEFAULT_MEMBRANE_TAU_US;
        neuron->tau_refractory_us = LIF_DEFAULT_REFRACTORY_US;
    }

    /* Create workqueue for asynchronous event processing */
    engine->workqueue = alloc_workqueue("spiking_wq", WQ_HIGHPRI | WQ_UNBOUND, 0);
    if (!engine->workqueue) {
        pr_err("Failed to create workqueue\n");
        kfree(engine->neurons);
        return -ENOMEM;
    }

    INIT_DELAYED_WORK(&engine->process_work, spiking_engine_process_cycle);

    pr_info("Spiking engine initialized: encoding=%d, neurons=%d\n",
            config->encoding, engine->neuron_count);

    return 0;
}

/* Cleanup the spiking engine */
void spiking_engine_cleanup(struct spiking_engine *engine)
{
    struct spike_event *event, *tmp;

    if (!engine)
        return;

    /* Stop processing */
    spiking_engine_stop(engine);

    /* Destroy workqueue */
    if (engine->workqueue) {
        destroy_workqueue(engine->workqueue);
        engine->workqueue = NULL;
    }

    /* Free event queue */
    spin_lock(&engine->queue_lock);
    list_for_each_entry_safe(event, tmp, &engine->event_queue, list) {
        list_del(&event->list);
        kfree(event);
    }
    spin_unlock(&engine->queue_lock);

    /* Free neuron pool */
    kfree(engine->neurons);

    pr_info("Spiking engine cleanup complete: %llu spikes processed\n",
            engine->total_spikes_emitted);
}

/* Create a neuron with custom configuration */
int spiking_neuron_create(struct spiking_engine *engine, __u32 neuron_id,
                          struct lif_neuron *config)
{
    struct lif_neuron *neuron;
    unsigned long flags;

    if (!engine || neuron_id >= engine->neuron_count)
        return -EINVAL;

    spin_lock_irqsave(&engine->neuron_lock, flags);
    neuron = &engine->neurons[neuron_id];

    if (config) {
        memcpy(neuron, config, sizeof(*neuron));
        neuron->id = neuron_id;
    }

    spin_unlock_irqrestore(&engine->neuron_lock, flags);
    return 0;
}

/* Get neuron state */
int spiking_neuron_get_state(struct spiking_engine *engine, __u32 neuron_id,
                             struct lif_neuron *state)
{
    struct lif_neuron *neuron;
    unsigned long flags;

    if (!engine || !state || neuron_id >= engine->neuron_count)
        return -EINVAL;

    spin_lock_irqsave(&engine->neuron_lock, flags);
    neuron = &engine->neurons[neuron_id];
    memcpy(state, neuron, sizeof(*state));
    spin_unlock_irqrestore(&engine->neuron_lock, flags);

    return 0;
}

/* Submit a spike event to the queue */
int spiking_event_submit(struct spiking_engine *engine, struct spike_event *event)
{
    struct spike_event *new_event;
    unsigned long flags;

    if (!engine || !event)
        return -EINVAL;

    /* Check if queue is full */
    if (engine->pending_events >= SPIKING_MAX_EVENTS) {
        engine->config.events_dropped++;
        return -ENOSPC;
    }

    /* Allocate and copy event */
    new_event = kmalloc(sizeof(*new_event), GFP_ATOMIC);
    if (!new_event) {
        engine->config.events_dropped++;
        return -ENOMEM;
    }

    memcpy(new_event, event, sizeof(*event));
    new_event->timestamp_ns = spiking_get_time_ns();

    /* Add to queue */
    spin_lock_irqsave(&engine->queue_lock, flags);
    list_add_tail(&new_event->list, &engine->event_queue);
    engine->pending_events++;
    spin_unlock_irqrestore(&engine->queue_lock, flags);

    return 0;
}

/* Submit a batch of spike events */
int spiking_event_submit_batch(struct spiking_engine *engine,
                               struct spike_event *events, __u32 count)
{
    int ret;
    __u32 i;

    if (!engine || !events)
        return -EINVAL;

    for (i = 0; i < count; i++) {
        ret = spiking_event_submit(engine, &events[i]);
        if (ret < 0)
            pr_debug("Failed to submit event %d: %d\n", i, ret);
    }

    return 0;
}

/* Encode a floating-point value as spikes */
int spiking_encode_value(struct spiking_engine *engine, float value,
                        struct spike_event *event)
{
    if (!engine || !event)
        return -EINVAL;

    memset(event, 0, sizeof(*event));

    switch (engine->config.encoding) {
    case SPIKE_ENCODING_RATE:
        /* Rate coding: spike frequency proportional to value */
        event->amplitude_mv = SPIKING_DEFAULT_THRESHOLD + 100;
        /* Higher values generate more spikes */
        break;

    case SPIKE_ENCODING_TEMPORAL:
        /* Temporal coding: spike timing encodes value */
        /* Earlier spikes = higher values */
        event->amplitude_mv = SPIKING_DEFAULT_THRESHOLD + (int)(value * 1000);
        break;

    case SPIKE_ENCODING_DELTA:
        /* Delta coding: only spike on significant changes */
        /* Most efficient for sparse data */
        if (abs(value) > 0.01f) {  /* Threshold for generating spike */
            event->amplitude_mv = SPIKING_DEFAULT_THRESHOLD + (int)(value * 1000);
        } else {
            return -EAGAIN;  /* No spike needed */
        }
        break;

    default:
        return -EINVAL;
    }

    return 0;
}

/* Decode spikes back to a floating-point value */
float spiking_decode_spikes(struct spiking_engine *engine,
                            struct spike_event *events, __u32 count)
{
    float value = 0.0f;
    __u32 i;

    if (!engine || !events || count == 0)
        return 0.0f;

    switch (engine->config.encoding) {
    case SPIKE_ENCODING_RATE:
        /* Rate coding: count spikes in time window */
        value = (float)count / engine->config.max_events_per_cycle;
        break;

    case SPIKE_ENCODING_TEMPORAL:
        /* Temporal coding: use spike timing */
        if (count > 0) {
            value = (float)(events[0].amplitude_mv - SPIKING_DEFAULT_THRESHOLD) / 1000.0f;
        }
        break;

    case SPIKE_ENCODING_DELTA:
        /* Delta coding: accumulate changes */
        for (i = 0; i < count; i++) {
            value += (float)(events[i].amplitude_mv - SPIKING_DEFAULT_THRESHOLD) / 1000.0f;
        }
        break;
    }

    return value;
}

/* Update neuron membrane potential (LIF dynamics) */
static void update_neuron_potential(struct lif_neuron *neuron, __s32 input_current_mv,
                                   __u64 dt_ns)
{
    __s64 decay_factor;
    __s64 delta_v;
    __u64 dt_us = dt_ns / 1000;  /* Convert to microseconds */

    /* Check if in refractory period */
    if (neuron->state == NEURON_STATE_REFRACTORY) {
        __u64 time_since_spike_us = (spiking_get_time_ns() - neuron->last_spike_time_ns) / 1000;
        if (time_since_spike_us >= neuron->tau_refractory_us) {
            neuron->state = NEURON_STATE_RESTING;
            neuron->membrane_potential_mv = neuron->resting_potential_mv;
        }
        return;
    }

    /* Leaky integration: V(t) = V(t-1) + dt/tau * (V_rest - V(t-1)) + I(t) */
    decay_factor = ((__s64)dt_us * 1000) / neuron->tau_membrane_us;
    delta_v = (decay_factor * (neuron->resting_potential_mv - neuron->membrane_potential_mv)) / 1000;
    delta_v += input_current_mv;

    neuron->membrane_potential_mv += delta_v;

    /* Check for spike threshold crossing */
    if (neuron->membrane_potential_mv >= neuron->threshold_mv) {
        neuron->state = NEURON_STATE_SPIKING;
        neuron->last_spike_time_ns = spiking_get_time_ns();
        neuron->total_spikes++;

        /* Reset to reset potential */
        neuron->membrane_potential_mv = neuron->reset_potential_mv;

        /* Enter refractory period */
        neuron->state = NEURON_STATE_REFRACTORY;
    } else {
        neuron->state = NEURON_STATE_INTEGRATING;
    }
}

/* Process one cycle of spike events */
void spiking_engine_process_cycle(struct work_struct *work)
{
    struct spiking_engine *engine = container_of(work, struct spiking_engine,
                                                  process_work.work);
    struct spike_event *event, *tmp;
    struct lif_neuron *neuron;
    __u32 events_processed = 0;
    __u32 active_neurons = 0;
    __u64 current_time_ns = spiking_get_time_ns();
    __u64 dt_ns = engine->config.processing_interval_us * 1000;
    unsigned long flags;

    /* Process events from the queue */
    spin_lock_irqsave(&engine->queue_lock, flags);
    list_for_each_entry_safe(event, tmp, &engine->event_queue, list) {
        if (events_processed >= engine->config.max_events_per_cycle)
            break;

        /* Validate neuron ID */
        if (event->neuron_id >= engine->neuron_count) {
            list_del(&event->list);
            kfree(event);
            engine->pending_events--;
            continue;
        }

        /* Get target neuron */
        neuron = &engine->neurons[event->neuron_id];

        /* Update neuron with spike input */
        update_neuron_potential(neuron, event->amplitude_mv, dt_ns);

        /* Track statistics */
        if (neuron->state == NEURON_STATE_SPIKING) {
            engine->total_spikes_emitted++;
        }

        /* Remove processed event */
        list_del(&event->list);
        kfree(event);
        engine->pending_events--;
        events_processed++;
    }
    spin_unlock_irqrestore(&engine->queue_lock, flags);

    /* Update all neurons (decay) */
    spin_lock_irqsave(&engine->neuron_lock, flags);
    for (int i = 0; i < engine->neuron_count; i++) {
        neuron = &engine->neurons[i];

        /* Update neurons that didn't receive input */
        if (neuron->state != NEURON_STATE_RESTING) {
            update_neuron_potential(neuron, 0, dt_ns);
        }

        if (spiking_neuron_is_active(neuron)) {
            active_neurons++;
        }
    }
    spin_unlock_irqrestore(&engine->neuron_lock, flags);

    /* Update statistics */
    engine->cycles_processed++;
    engine->config.total_events_processed += events_processed;
    engine->config.total_neurons_active = active_neurons;
    engine->config.total_neurons_inactive = engine->neuron_count - active_neurons;

    /* Calculate current sparsity */
    engine->config.current_sparsity_percent = spiking_calculate_sparsity(engine);

    /* Schedule next cycle if engine is still active */
    if (engine->processing_active) {
        queue_delayed_work(engine->workqueue, &engine->process_work,
                          usecs_to_jiffies(engine->config.processing_interval_us));
    }
}

/* Start the spiking engine */
int spiking_engine_start(struct spiking_engine *engine)
{
    if (!engine || !engine->config.enabled)
        return -EINVAL;

    if (engine->processing_active)
        return -EALREADY;

    engine->processing_active = true;

    /* Schedule first processing cycle */
    queue_delayed_work(engine->workqueue, &engine->process_work,
                      usecs_to_jiffies(engine->config.processing_interval_us));

    pr_info("Spiking engine started\n");
    return 0;
}

/* Stop the spiking engine */
void spiking_engine_stop(struct spiking_engine *engine)
{
    if (!engine)
        return;

    engine->processing_active = false;
    cancel_delayed_work_sync(&engine->process_work);

    pr_info("Spiking engine stopped\n");
}

/* Get current statistics */
void spiking_get_statistics(struct spiking_engine *engine,
                           struct spiking_config *stats)
{
    if (!engine || !stats)
        return;

    memcpy(stats, &engine->config, sizeof(*stats));
}

/* Calculate current sparsity percentage */
__u32 spiking_calculate_sparsity(struct spiking_engine *engine)
{
    __u64 inactive_neurons;
    __u32 sparsity;

    if (!engine || engine->neuron_count == 0)
        return 0;

    inactive_neurons = engine->config.total_neurons_inactive;
    sparsity = (inactive_neurons * 100) / engine->neuron_count;

    return sparsity;
}

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("LightOS Spiking Neural Network Engine");
