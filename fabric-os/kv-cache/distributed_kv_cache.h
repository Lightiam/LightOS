/* SPDX-License-Identifier: GPL-2.0 */
#ifndef _DISTRIBUTED_KV_CACHE_H
#define _DISTRIBUTED_KV_CACHE_H

#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>

/*
 * Distributed KV Cache for LLM Inference
 *
 * Implements PagedAttention-style memory management with
 * cache-aware routing for maximum resource utilization.
 */

#define KV_CACHE_MAX_NODES 64
#define KV_CACHE_PAGE_SIZE 4096        /* Bytes */
#define KV_CACHE_MAX_SEQUENCES 10000
#define KV_CACHE_MAX_BLOCKS_PER_SEQ 2048

/* Cache eviction policies */
enum kv_eviction_policy {
    KV_EVICT_LRU = 0,              /* Least Recently Used */
    KV_EVICT_LFU = 1,              /* Least Frequently Used */
    KV_EVICT_COST_AWARE = 2,       /* Consider recomputation cost */
    KV_EVICT_FIFO = 3,             /* First In First Out */
};

/* Cache coherency protocol */
enum kv_coherency_protocol {
    KV_COHERENCY_NONE = 0,         /* No coherency (eventual consistency) */
    KV_COHERENCY_MESI = 1,         /* Modified-Exclusive-Shared-Invalid */
    KV_COHERENCY_STRONG = 2,       /* Strong consistency */
};

/* Block state (MESI-like) */
enum kv_block_state {
    KV_BLOCK_INVALID = 0,
    KV_BLOCK_SHARED = 1,
    KV_BLOCK_EXCLUSIVE = 2,
    KV_BLOCK_MODIFIED = 3,
};

/* KV cache block */
struct kv_cache_block {
    uint64_t block_id;
    uint64_t sequence_id;
    uint32_t position;             /* Position in sequence */
    enum kv_block_state state;
    uint64_t last_access_time_ns;
    uint64_t access_count;
    uint32_t ref_count;            /* Reference count */
    uint32_t node_id;              /* Node storing this block */

    /* Data */
    void *key_data;                /* Key tensor */
    void *value_data;              /* Value tensor */
    uint32_t key_size_bytes;
    uint32_t value_size_bytes;

    /* Metadata */
    float recompute_cost_ms;       /* Cost to recompute if evicted */
    bool dirty;                    /* Modified since last sync */
    bool locked;                   /* Locked for computation */
};

/* Sequence metadata */
struct kv_sequence {
    uint64_t sequence_id;
    uint32_t num_blocks;
    uint64_t block_ids[KV_CACHE_MAX_BLOCKS_PER_SEQ];
    uint32_t sequence_length;
    uint64_t created_time_ns;
    uint64_t last_access_time_ns;

    /* Prefix caching */
    uint64_t prefix_hash;          /* Hash of shared prefix */
    uint32_t prefix_length;        /* Length of shared prefix */
    bool prefix_cached;

    /* Routing hints */
    uint32_t preferred_node_id;    /* Node with most cached blocks */
    float cache_hit_rate;          /* Historical hit rate */
};

/* Cache node information */
struct kv_cache_node {
    uint32_t node_id;
    char hostname[256];
    uint32_t port;

    /* Capacity */
    uint64_t total_capacity_bytes;
    uint64_t used_capacity_bytes;
    uint32_t num_blocks;
    uint32_t num_free_blocks;

    /* Statistics */
    uint64_t cache_hits;
    uint64_t cache_misses;
    uint64_t evictions;
    uint64_t network_transfers_bytes;

    /* Load metrics */
    float utilization_percent;
    uint32_t current_requests;
    uint32_t max_concurrent_requests;

    /* State */
    bool online;
    uint64_t last_heartbeat_ns;
};

/* KV cache configuration */
struct kv_cache_config {
    enum kv_eviction_policy eviction_policy;
    enum kv_coherency_protocol coherency_protocol;

    uint64_t total_capacity_bytes;
    uint32_t page_size_bytes;
    uint32_t block_size_tokens;    /* Tokens per block */

    /* Replication */
    uint32_t replication_factor;   /* Number of replicas */
    bool enable_replication;

    /* Prefetching */
    bool enable_prefetch;
    uint32_t prefetch_distance;    /* Blocks to prefetch ahead */

    /* Statistics */
    uint64_t total_requests;
    uint64_t cache_hits;
    uint64_t cache_misses;
    float hit_rate_percent;
    uint64_t total_evictions;
};

/* Global cache coordinator */
struct kv_cache_coordinator {
    struct kv_cache_config config;

    /* Node pool */
    struct kv_cache_node nodes[KV_CACHE_MAX_NODES];
    uint32_t num_nodes;
    pthread_mutex_t node_lock;

    /* Block table (global view) */
    struct kv_cache_block *blocks;
    uint64_t num_blocks;
    pthread_mutex_t block_lock;

    /* Sequence table */
    struct kv_sequence *sequences;
    uint32_t num_sequences;
    pthread_mutex_t sequence_lock;

    /* Eviction queue (LRU) */
    struct kv_cache_block **eviction_queue;
    uint32_t eviction_queue_size;
    pthread_mutex_t eviction_lock;

    /* Routing table */
    uint32_t *sequence_to_node_map; /* Sequence ID -> preferred node */
    pthread_mutex_t routing_lock;

    /* Coordinator state */
    bool running;
    pthread_t coordinator_thread;
};

/* Function prototypes */

/* Initialization */
int kv_cache_init(struct kv_cache_coordinator *coord,
                 struct kv_cache_config *config);
void kv_cache_cleanup(struct kv_cache_coordinator *coord);

/* Node management */
int kv_cache_register_node(struct kv_cache_coordinator *coord,
                          struct kv_cache_node *node);
int kv_cache_unregister_node(struct kv_cache_coordinator *coord,
                            uint32_t node_id);
int kv_cache_node_heartbeat(struct kv_cache_coordinator *coord,
                           uint32_t node_id);

/* Cache operations */
int kv_cache_allocate_block(struct kv_cache_coordinator *coord,
                           uint64_t sequence_id,
                           struct kv_cache_block **block);
int kv_cache_get_block(struct kv_cache_coordinator *coord,
                      uint64_t block_id,
                      struct kv_cache_block **block);
int kv_cache_free_block(struct kv_cache_coordinator *coord,
                       uint64_t block_id);

/* Sequence management */
int kv_cache_create_sequence(struct kv_cache_coordinator *coord,
                            uint64_t sequence_id,
                            uint32_t estimated_length);
int kv_cache_append_tokens(struct kv_cache_coordinator *coord,
                          uint64_t sequence_id,
                          uint32_t num_tokens);
int kv_cache_free_sequence(struct kv_cache_coordinator *coord,
                          uint64_t sequence_id);

/* Prefix caching */
int kv_cache_find_prefix(struct kv_cache_coordinator *coord,
                        const uint32_t *tokens,
                        uint32_t num_tokens,
                        struct kv_sequence **matching_seq);
int kv_cache_share_prefix(struct kv_cache_coordinator *coord,
                         uint64_t seq_id_1,
                         uint64_t seq_id_2);

/* Eviction */
int kv_cache_evict_lru(struct kv_cache_coordinator *coord,
                      uint64_t num_bytes_needed);
int kv_cache_evict_cost_aware(struct kv_cache_coordinator *coord,
                             uint64_t num_bytes_needed);
struct kv_cache_block *kv_cache_select_victim(struct kv_cache_coordinator *coord);

/* Routing */
uint32_t kv_cache_route_sequence(struct kv_cache_coordinator *coord,
                                uint64_t sequence_id);
int kv_cache_migrate_sequence(struct kv_cache_coordinator *coord,
                             uint64_t sequence_id,
                             uint32_t target_node_id);

/* Replication */
int kv_cache_replicate_block(struct kv_cache_coordinator *coord,
                            uint64_t block_id,
                            uint32_t target_node_id);
int kv_cache_sync_replicas(struct kv_cache_coordinator *coord,
                          uint64_t block_id);

/* Statistics */
void kv_cache_get_statistics(struct kv_cache_coordinator *coord,
                            struct kv_cache_config *stats);
float kv_cache_calculate_hit_rate(struct kv_cache_coordinator *coord);
uint64_t kv_cache_get_total_usage(struct kv_cache_coordinator *coord);

/* Utility functions */
static inline bool kv_cache_block_is_cached(struct kv_cache_block *block)
{
    return block && block->state != KV_BLOCK_INVALID;
}

static inline float kv_cache_node_utilization(struct kv_cache_node *node)
{
    if (node->total_capacity_bytes == 0)
        return 0.0f;
    return (float)node->used_capacity_bytes /
           (float)node->total_capacity_bytes * 100.0f;
}

static inline bool kv_cache_node_has_capacity(struct kv_cache_node *node,
                                             uint64_t required_bytes)
{
    return (node->total_capacity_bytes - node->used_capacity_bytes) >=
           required_bytes;
}

#endif /* _DISTRIBUTED_KV_CACHE_H */
