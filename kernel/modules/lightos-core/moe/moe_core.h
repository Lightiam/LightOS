/* SPDX-License-Identifier: GPL-2.0 */
#ifndef _LIGHTOS_MOE_CORE_H
#define _LIGHTOS_MOE_CORE_H

#include <linux/types.h>
#include <linux/spinlock.h>

/*
 * LightOS Mixture of Experts (MoE) Module
 *
 * Implements conditional computation for micro-level sparsity.
 * Target: >69% activation sparsity through expert routing.
 */

#define MOE_MAX_EXPERTS 64
#define MOE_DEFAULT_TOP_K 2
#define MOE_MAX_TOKENS 4096
#define MOE_SPARSITY_TARGET 69  /* 69% nice */

/* Expert routing strategy */
enum moe_routing_strategy {
    MOE_ROUTING_TOP_K = 0,        /* Activate top-K experts */
    MOE_ROUTING_THRESHOLD = 1,    /* Activate experts above threshold */
    MOE_ROUTING_LEARNED = 2,      /* Learned routing (future) */
    MOE_ROUTING_HASH = 3,         /* Hash-based routing for determinism */
};

/* Expert state */
enum expert_state {
    EXPERT_STATE_IDLE = 0,
    EXPERT_STATE_ACTIVE = 1,
    EXPERT_STATE_BUSY = 2,
    EXPERT_STATE_OVERLOADED = 3,
};

/* Expert load balancing */
struct expert_info {
    __u32 expert_id;
    enum expert_state state;
    __u32 current_load;           /* Number of active tokens */
    __u32 capacity;               /* Maximum tokens */
    __u64 total_activations;      /* Total times activated */
    __u64 total_tokens_processed; /* Total tokens processed */
    float utilization_percent;    /* Current utilization */
    float average_score;          /* Average routing score */
};

/* Routing decision for a token */
struct routing_decision {
    __u32 token_id;               /* Input token identifier */
    __u32 num_experts;            /* Number of experts to activate */
    __u32 expert_ids[MOE_DEFAULT_TOP_K * 2];  /* Selected experts */
    float expert_weights[MOE_DEFAULT_TOP_K * 2]; /* Routing weights */
    bool dropped;                 /* Token dropped (sparsity) */
};

/* MoE configuration */
struct moe_config {
    enum moe_routing_strategy strategy;
    __u32 num_experts;            /* Total number of experts */
    __u32 top_k;                  /* Number of experts per token */
    __u32 expert_capacity;        /* Tokens per expert */
    float routing_threshold;      /* Threshold for activation */
    __u32 target_sparsity_percent; /* Target sparsity (69) */

    /* Load balancing */
    bool load_balancing_enabled;
    float load_balancing_alpha;   /* Balance importance (0-1) */

    /* Token dropping for sparsity */
    bool token_dropping_enabled;
    float token_drop_threshold;   /* Drop tokens below this score */

    /* Layer skipping */
    bool layer_skipping_enabled;
    __u32 skip_layers_mask;       /* Bitmask of layers to skip */

    /* Statistics */
    __u64 total_tokens_processed;
    __u64 total_tokens_dropped;
    __u64 total_expert_activations;
    __u32 current_sparsity_percent;
    float average_experts_per_token;
};

/* MoE engine state */
struct moe_engine {
    struct moe_config config;

    /* Expert pool */
    struct expert_info experts[MOE_MAX_EXPERTS];
    spinlock_t expert_lock;

    /* Routing decisions cache */
    struct routing_decision *routing_cache;
    __u32 cache_size;
    spinlock_t cache_lock;

    /* Load balancing */
    float expert_loads[MOE_MAX_EXPERTS];  /* Normalized loads */
    __u64 routing_iterations;

    /* Performance metrics */
    __u64 total_routing_decisions;
    __u64 cache_hits;
    __u64 cache_misses;
};

/* Gating network output (mock for now, will be ML-based later) */
struct gating_output {
    __u32 num_scores;
    float scores[MOE_MAX_EXPERTS]; /* Expert affinity scores */
};

/* Function prototypes */

/* Initialize/cleanup */
int moe_engine_init(struct moe_engine *engine, struct moe_config *config);
void moe_engine_cleanup(struct moe_engine *engine);

/* Expert management */
int moe_expert_register(struct moe_engine *engine, __u32 expert_id,
                       __u32 capacity);
void moe_expert_unregister(struct moe_engine *engine, __u32 expert_id);
int moe_expert_get_info(struct moe_engine *engine, __u32 expert_id,
                       struct expert_info *info);

/* Routing */
int moe_route_token(struct moe_engine *engine, __u32 token_id,
                   struct gating_output *gating,
                   struct routing_decision *decision);
int moe_route_batch(struct moe_engine *engine, __u32 *token_ids,
                   struct gating_output *gating_outputs,
                   struct routing_decision *decisions, __u32 batch_size);

/* Gating network (placeholder) */
int moe_compute_gating(struct moe_engine *engine, const float *token_features,
                      __u32 feature_dim, struct gating_output *output);

/* Load balancing */
void moe_update_expert_loads(struct moe_engine *engine);
int moe_balance_load(struct moe_engine *engine, struct routing_decision *decision);

/* Sparsity optimization */
int moe_apply_token_dropping(struct moe_engine *engine,
                            struct routing_decision *decision);
bool moe_should_skip_layer(struct moe_engine *engine, __u32 layer_id);
__u32 moe_calculate_sparsity(struct moe_engine *engine);

/* Statistics */
void moe_get_statistics(struct moe_engine *engine, struct moe_config *stats);
void moe_reset_statistics(struct moe_engine *engine);

/* Utility functions */
static inline bool moe_expert_is_available(struct expert_info *expert)
{
    return expert->state != EXPERT_STATE_OVERLOADED &&
           expert->current_load < expert->capacity;
}

static inline float moe_compute_load_balance_loss(struct moe_engine *engine)
{
    /* Compute coefficient of variation for expert loads */
    float mean = 0.0f, variance = 0.0f;
    __u32 i;

    for (i = 0; i < engine->config.num_experts; i++) {
        mean += engine->expert_loads[i];
    }
    mean /= engine->config.num_experts;

    for (i = 0; i < engine->config.num_experts; i++) {
        float diff = engine->expert_loads[i] - mean;
        variance += diff * diff;
    }
    variance /= engine->config.num_experts;

    return variance / (mean + 1e-10f);  /* CV^2 */
}

#endif /* _LIGHTOS_MOE_CORE_H */
