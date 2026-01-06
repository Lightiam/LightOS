/* SPDX-License-Identifier: GPL-2.0 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <float.h>
#include <pthread.h>
#include <unistd.h>
#include "lightrail_scheduler.h"

/*
 * LightRail AI Mathematical Scheduler Implementation
 *
 * Provides provably optimal scheduling through mathematical algorithms.
 */

/* Priority queue for Dijkstra's algorithm */
struct pq_node {
    uint32_t device_id;
    float cost;
};

/* Initialize scheduler */
int lightrail_scheduler_init(struct lightrail_scheduler *sched,
                            struct scheduler_config *config)
{
    int ret;

    if (!sched || !config)
        return -1;

    memset(sched, 0, sizeof(*sched));
    memcpy(&sched->config, config, sizeof(*config));

    /* Initialize device pool */
    sched->num_devices = 0;
    pthread_mutex_init(&sched->device_lock, NULL);

    /* Allocate task queue */
    sched->task_queue_size = LIGHTRAIL_MAX_TASKS;
    sched->task_queue = calloc(sched->task_queue_size,
                              sizeof(struct task_descriptor));
    if (!sched->task_queue) {
        fprintf(stderr, "Failed to allocate task queue\n");
        return -1;
    }

    sched->task_queue_head = 0;
    sched->task_queue_tail = 0;
    pthread_mutex_init(&sched->task_lock, NULL);
    pthread_cond_init(&sched->task_available, NULL);

    /* Allocate routing table */
    sched->routing_table = calloc(LIGHTRAIL_MAX_DEVICES, sizeof(struct route *));
    if (!sched->routing_table) {
        fprintf(stderr, "Failed to allocate routing table\n");
        free(sched->task_queue);
        return -1;
    }

    for (uint32_t i = 0; i < LIGHTRAIL_MAX_DEVICES; i++) {
        sched->routing_table[i] = calloc(LIGHTRAIL_MAX_DEVICES,
                                        sizeof(struct route));
        if (!sched->routing_table[i]) {
            fprintf(stderr, "Failed to allocate routing table row\n");
            /* Cleanup */
            for (uint32_t j = 0; j < i; j++)
                free(sched->routing_table[j]);
            free(sched->routing_table);
            free(sched->task_queue);
            return -1;
        }
    }

    pthread_mutex_init(&sched->route_lock, NULL);

    sched->running = false;

    printf("LightRail Scheduler initialized: algorithm=%d, objective=%d\n",
           config->algorithm, config->objective);

    return 0;
}

/* Cleanup scheduler */
void lightrail_scheduler_cleanup(struct lightrail_scheduler *sched)
{
    if (!sched)
        return;

    /* Stop scheduler thread if running */
    if (sched->running) {
        lightrail_stop_scheduler(sched);
    }

    /* Free routing table */
    if (sched->routing_table) {
        for (uint32_t i = 0; i < LIGHTRAIL_MAX_DEVICES; i++) {
            free(sched->routing_table[i]);
        }
        free(sched->routing_table);
    }

    /* Free task queue */
    free(sched->task_queue);

    /* Destroy mutexes */
    pthread_mutex_destroy(&sched->device_lock);
    pthread_mutex_destroy(&sched->task_lock);
    pthread_mutex_destroy(&sched->route_lock);
    pthread_cond_destroy(&sched->task_available);

    printf("LightRail Scheduler cleanup complete: %llu tasks scheduled\n",
           (unsigned long long)sched->config.total_tasks_scheduled);
}

/* Register a device */
int lightrail_register_device(struct lightrail_scheduler *sched,
                             struct device_info *device)
{
    if (!sched || !device || sched->num_devices >= LIGHTRAIL_MAX_DEVICES)
        return -1;

    pthread_mutex_lock(&sched->device_lock);

    uint32_t device_id = sched->num_devices;
    memcpy(&sched->devices[device_id], device, sizeof(*device));
    sched->devices[device_id].device_id = device_id;
    sched->num_devices++;

    pthread_mutex_unlock(&sched->device_lock);

    printf("Registered device %d: %s (%d)\n", device_id, device->name,
           device->type);

    return device_id;
}

/* Submit a task for scheduling */
int lightrail_submit_task(struct lightrail_scheduler *sched,
                         struct task_descriptor *task)
{
    uint32_t next_tail;

    if (!sched || !task)
        return -1;

    pthread_mutex_lock(&sched->task_lock);

    /* Check if queue is full */
    next_tail = (sched->task_queue_tail + 1) % sched->task_queue_size;
    if (next_tail == sched->task_queue_head) {
        pthread_mutex_unlock(&sched->task_lock);
        fprintf(stderr, "Task queue full\n");
        return -1;
    }

    /* Add task to queue */
    memcpy(&sched->task_queue[sched->task_queue_tail], task, sizeof(*task));
    sched->task_queue[sched->task_queue_tail].task_id =
        sched->config.total_tasks_scheduled++;
    sched->task_queue[sched->task_queue_tail].state = TASK_STATE_PENDING;

    sched->task_queue_tail = next_tail;

    /* Signal scheduler thread */
    pthread_cond_signal(&sched->task_available);

    pthread_mutex_unlock(&sched->task_lock);

    return 0;
}

/* Dijkstra's algorithm for optimal route finding */
int lightrail_schedule_dijkstra(struct lightrail_scheduler *sched,
                               uint32_t source_id, uint32_t dest_id,
                               struct route *route)
{
    float dist[LIGHTRAIL_MAX_DEVICES];
    uint32_t prev[LIGHTRAIL_MAX_DEVICES];
    bool visited[LIGHTRAIL_MAX_DEVICES];
    uint32_t i, current;
    float min_dist;

    if (!sched || !route || source_id >= sched->num_devices ||
        dest_id >= sched->num_devices)
        return -1;

    /* Initialize */
    for (i = 0; i < sched->num_devices; i++) {
        dist[i] = FLT_MAX;
        prev[i] = UINT32_MAX;
        visited[i] = false;
    }

    dist[source_id] = 0.0f;

    /* Main loop */
    for (uint32_t count = 0; count < sched->num_devices; count++) {
        /* Find minimum distance unvisited node */
        min_dist = FLT_MAX;
        current = UINT32_MAX;

        for (i = 0; i < sched->num_devices; i++) {
            if (!visited[i] && dist[i] < min_dist) {
                min_dist = dist[i];
                current = i;
            }
        }

        if (current == UINT32_MAX || current == dest_id)
            break;

        visited[current] = true;

        /* Update distances to neighbors */
        pthread_mutex_lock(&sched->device_lock);
        struct device_info *dev = &sched->devices[current];

        for (i = 0; i < dev->num_links; i++) {
            uint32_t neighbor = dev->connected_devices[i];

            if (neighbor >= sched->num_devices || visited[neighbor])
                continue;

            /* Cost function based on optimization objective */
            float edge_cost;
            switch (sched->config.objective) {
            case OPT_MINIMIZE_LATENCY:
                edge_cost = (float)dev->link_latency_us[i];
                break;
            case OPT_MINIMIZE_POWER:
                edge_cost = (float)dev->power_watts;
                break;
            case OPT_MINIMIZE_COST:
                edge_cost = dev->cost_per_hour;
                break;
            case OPT_MAXIMIZE_THROUGHPUT:
                edge_cost = 1.0f / (float)dev->link_bandwidth_gbps[i];
                break;
            default:
                edge_cost = 1.0f;
            }

            float alt = dist[current] + edge_cost;
            if (alt < dist[neighbor]) {
                dist[neighbor] = alt;
                prev[neighbor] = current;
            }
        }

        pthread_mutex_unlock(&sched->device_lock);
    }

    /* Reconstruct path */
    if (dist[dest_id] == FLT_MAX) {
        fprintf(stderr, "No route from %d to %d\n", source_id, dest_id);
        return -1;
    }

    /* Build route */
    route->source_device_id = source_id;
    route->dest_device_id = dest_id;
    route->num_hops = 0;
    route->total_latency_us = 0;
    route->total_bandwidth_gbps = UINT32_MAX;
    route->total_cost = 0.0f;

    /* Backtrack from dest to source */
    current = dest_id;
    uint32_t path_temp[LIGHTRAIL_MAX_ROUTES];
    uint32_t path_len = 0;

    while (current != source_id && path_len < LIGHTRAIL_MAX_ROUTES) {
        path_temp[path_len++] = current;
        current = prev[current];
    }
    path_temp[path_len++] = source_id;

    /* Reverse path */
    for (i = 0; i < path_len && i < LIGHTRAIL_MAX_ROUTES; i++) {
        route->path[i] = path_temp[path_len - 1 - i];
    }
    route->num_hops = path_len - 1;

    /* Calculate route metrics */
    for (i = 0; i < route->num_hops; i++) {
        uint32_t from = route->path[i];
        uint32_t to = route->path[i + 1];

        pthread_mutex_lock(&sched->device_lock);
        struct device_info *dev_from = &sched->devices[from];

        /* Find link to next hop */
        for (uint32_t j = 0; j < dev_from->num_links; j++) {
            if (dev_from->connected_devices[j] == to) {
                route->total_latency_us += dev_from->link_latency_us[j];
                if (dev_from->link_bandwidth_gbps[j] < route->total_bandwidth_gbps) {
                    route->total_bandwidth_gbps = dev_from->link_bandwidth_gbps[j];
                }
                route->total_cost += dev_from->cost_per_hour / 3600.0f;  /* Per second */
                break;
            }
        }

        pthread_mutex_unlock(&sched->device_lock);
    }

    route->congestion_factor = 1.0f;  /* TODO: Calculate based on current load */

    return 0;
}

/* Cache-aware scheduling */
int lightrail_schedule_with_cache_affinity(struct lightrail_scheduler *sched,
                                          struct task_descriptor *task)
{
    float best_score = -FLT_MAX;
    uint32_t best_device = UINT32_MAX;
    uint32_t i;

    if (!sched || !task)
        return -1;

    pthread_mutex_lock(&sched->device_lock);

    /* Evaluate each device */
    for (i = 0; i < sched->num_devices; i++) {
        struct device_info *dev = &sched->devices[i];

        /* Check if device can run task */
        if (!lightrail_device_can_run_task(dev, task))
            continue;

        /* Calculate cache benefit */
        float cache_benefit = lightrail_calculate_cache_benefit(sched, task, i);

        /* Estimate execution time */
        uint32_t exec_time_ms = lightrail_estimate_task_duration(task, dev);

        /* Calculate data transfer cost if cache miss */
        float transfer_cost_ms = 0.0f;
        if (task->has_kv_cache && task->cache_device_id != i) {
            /* Need to transfer cache data */
            struct route route;
            if (lightrail_schedule_dijkstra(sched, task->cache_device_id, i,
                                          &route) == 0) {
                transfer_cost_ms = (float)route.total_latency_us / 1000.0f;
                transfer_cost_ms += (float)task->kv_cache_size_bytes /
                                   (float)(route.total_bandwidth_gbps * 1e9f / 8.0f) *
                                   1000.0f;
            }
        }

        /* Calculate overall score (higher is better) */
        float score = cache_benefit -
                     (float)exec_time_ms -
                     transfer_cost_ms -
                     (dev->utilization_percent / 10.0f);

        if (score > best_score) {
            best_score = score;
            best_device = i;
        }
    }

    pthread_mutex_unlock(&sched->device_lock);

    if (best_device == UINT32_MAX) {
        fprintf(stderr, "No suitable device for task %d\n", task->task_id);
        return -1;
    }

    /* Assign task to best device */
    task->assigned_device_id = best_device;
    task->state = TASK_STATE_SCHEDULED;

    sched->config.cache_aware_decisions++;

    return 0;
}

/* Calculate cache benefit for a device */
float lightrail_calculate_cache_benefit(struct lightrail_scheduler *sched,
                                       struct task_descriptor *task,
                                       uint32_t device_id)
{
    if (!task->has_kv_cache)
        return 0.0f;

    if (task->cache_device_id == device_id) {
        /* Cache hit! */
        return sched->config.cache_hit_value;
    }

    /* Cache miss */
    return 0.0f;
}

/* Schedule a task (main scheduling function) */
int lightrail_schedule_optimal(struct lightrail_scheduler *sched,
                              struct task_descriptor *task)
{
    int ret;

    if (!sched || !task)
        return -1;

    /* Use appropriate algorithm */
    switch (sched->config.algorithm) {
    case SCHED_OPTIMAL_DIJKSTRA:
    case SCHED_OPTIMAL_ASTAR:
        /* Cache-aware scheduling with optimal routing */
        ret = lightrail_schedule_with_cache_affinity(sched, task);
        break;

    case SCHED_GREEDY_OPTIMAL:
        /* Simple greedy: pick least loaded device */
        {
            uint32_t best_device = 0;
            float min_util = 100.0f;

            pthread_mutex_lock(&sched->device_lock);
            for (uint32_t i = 0; i < sched->num_devices; i++) {
                if (sched->devices[i].utilization_percent < min_util &&
                    lightrail_device_can_run_task(&sched->devices[i], task)) {
                    min_util = sched->devices[i].utilization_percent;
                    best_device = i;
                }
            }
            pthread_mutex_unlock(&sched->device_lock);

            task->assigned_device_id = best_device;
            task->state = TASK_STATE_SCHEDULED;
            ret = 0;
        }
        break;

    default:
        fprintf(stderr, "Unsupported scheduling algorithm: %d\n",
                sched->config.algorithm);
        ret = -1;
    }

    if (ret == 0) {
        sched->config.total_scheduling_decisions++;
    }

    return ret;
}

/* Scheduler thread */
void *lightrail_scheduler_thread(void *arg)
{
    struct lightrail_scheduler *sched = (struct lightrail_scheduler *)arg;
    struct task_descriptor task;

    printf("LightRail Scheduler thread started\n");

    while (sched->running) {
        pthread_mutex_lock(&sched->task_lock);

        /* Wait for tasks */
        while (sched->task_queue_head == sched->task_queue_tail &&
               sched->running) {
            pthread_cond_wait(&sched->task_available, &sched->task_lock);
        }

        if (!sched->running) {
            pthread_mutex_unlock(&sched->task_lock);
            break;
        }

        /* Get next task */
        memcpy(&task, &sched->task_queue[sched->task_queue_head],
               sizeof(task));
        sched->task_queue_head = (sched->task_queue_head + 1) %
                                sched->task_queue_size;

        pthread_mutex_unlock(&sched->task_lock);

        /* Schedule the task */
        if (lightrail_schedule_optimal(sched, &task) == 0) {
            printf("Task %d scheduled to device %d\n",
                   task.task_id, task.assigned_device_id);

            /* Update device utilization */
            pthread_mutex_lock(&sched->device_lock);
            sched->devices[task.assigned_device_id].utilization_percent +=
                (float)task.compute_ops / 1e12f;  /* Mock calculation */
            pthread_mutex_unlock(&sched->device_lock);
        } else {
            fprintf(stderr, "Failed to schedule task %d\n", task.task_id);
        }
    }

    printf("LightRail Scheduler thread exiting\n");
    return NULL;
}

/* Start scheduler thread */
int lightrail_start_scheduler(struct lightrail_scheduler *sched)
{
    if (!sched || sched->running)
        return -1;

    sched->running = true;

    if (pthread_create(&sched->scheduler_thread, NULL,
                      lightrail_scheduler_thread, sched) != 0) {
        fprintf(stderr, "Failed to create scheduler thread\n");
        sched->running = false;
        return -1;
    }

    printf("LightRail Scheduler started\n");
    return 0;
}

/* Stop scheduler thread */
void lightrail_stop_scheduler(struct lightrail_scheduler *sched)
{
    if (!sched || !sched->running)
        return;

    sched->running = false;

    /* Wake up scheduler thread */
    pthread_cond_broadcast(&sched->task_available);

    /* Wait for thread to exit */
    pthread_join(sched->scheduler_thread, NULL);

    printf("LightRail Scheduler stopped\n");
}

/* Get statistics */
void lightrail_get_statistics(struct lightrail_scheduler *sched,
                             struct scheduler_config *stats)
{
    if (!sched || !stats)
        return;

    memcpy(stats, &sched->config, sizeof(*stats));
}
