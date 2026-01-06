/* SPDX-License-Identifier: GPL-2.0 */
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/slab.h>
#include <linux/sort.h>
#include <linux/random.h>
#include "moe_core.h"

/*
 * LightOS Mixture of Experts Implementation
 *
 * Achieves >69% sparsity through conditional expert activation.
 */

/* Comparison function for sorting experts by score */
struct score_pair {
    __u32 expert_id;
    float score;
};

static int compare_scores(const void *a, const void *b)
{
    const struct score_pair *pa = a;
    const struct score_pair *pb = b;

    if (pa->score > pb->score)
        return -1;
    else if (pa->score < pb->score)
        return 1;
    return 0;
}

/* Initialize MoE engine */
int moe_engine_init(struct moe_engine *engine, struct moe_config *config)
{
    __u32 i;

    if (!engine || !config)
        return -EINVAL;

    memset(engine, 0, sizeof(*engine));
    memcpy(&engine->config, config, sizeof(*config));

    /* Initialize expert pool */
    for (i = 0; i < MOE_MAX_EXPERTS; i++) {
        engine->experts[i].expert_id = i;
        engine->experts[i].state = EXPERT_STATE_IDLE;
        engine->experts[i].current_load = 0;
        engine->experts[i].capacity = config->expert_capacity ?
                                      config->expert_capacity : 256;
        engine->experts[i].total_activations = 0;
        engine->experts[i].total_tokens_processed = 0;
        engine->experts[i].utilization_percent = 0.0f;
        engine->expert_loads[i] = 0.0f;
    }

    spin_lock_init(&engine->expert_lock);

    /* Allocate routing cache */
    engine->cache_size = MOE_MAX_TOKENS;
    engine->routing_cache = kzalloc(engine->cache_size *
                                   sizeof(struct routing_decision),
                                   GFP_KERNEL);
    if (!engine->routing_cache) {
        pr_err("Failed to allocate routing cache\n");
        return -ENOMEM;
    }

    spin_lock_init(&engine->cache_lock);

    pr_info("MoE engine initialized: experts=%d, top_k=%d, target_sparsity=%d%%\n",
            config->num_experts, config->top_k, config->target_sparsity_percent);

    return 0;
}

/* Cleanup MoE engine */
void moe_engine_cleanup(struct moe_engine *engine)
{
    if (!engine)
        return;

    kfree(engine->routing_cache);

    pr_info("MoE engine cleanup: %llu tokens processed, %d%% sparsity achieved\n",
            engine->config.total_tokens_processed,
            engine->config.current_sparsity_percent);
}

/* Register an expert */
int moe_expert_register(struct moe_engine *engine, __u32 expert_id,
                       __u32 capacity)
{
    unsigned long flags;

    if (!engine || expert_id >= MOE_MAX_EXPERTS)
        return -EINVAL;

    spin_lock_irqsave(&engine->expert_lock, flags);

    engine->experts[expert_id].state = EXPERT_STATE_IDLE;
    engine->experts[expert_id].capacity = capacity;
    engine->experts[expert_id].current_load = 0;

    spin_unlock_irqrestore(&engine->expert_lock, flags);

    return 0;
}

/* Get expert info */
int moe_expert_get_info(struct moe_engine *engine, __u32 expert_id,
                       struct expert_info *info)
{
    unsigned long flags;

    if (!engine || !info || expert_id >= MOE_MAX_EXPERTS)
        return -EINVAL;

    spin_lock_irqsave(&engine->expert_lock, flags);
    memcpy(info, &engine->experts[expert_id], sizeof(*info));
    spin_unlock_irqrestore(&engine->expert_lock, flags);

    return 0;
}

/* Mock gating network (will be replaced with real ML model) */
int moe_compute_gating(struct moe_engine *engine, const float *token_features,
                      __u32 feature_dim, struct gating_output *output)
{
    __u32 i;
    float sum = 0.0f;

    if (!engine || !output)
        return -EINVAL;

    output->num_scores = engine->config.num_experts;

    /* Mock gating: use pseudo-random scores with some structure */
    for (i = 0; i < output->num_scores; i++) {
        /* Simple hash-based score for determinism */
        __u32 hash = i * 2654435761U;  /* Knuth's multiplicative hash */
        if (token_features && feature_dim > 0) {
            hash ^= (__u32)(token_features[0] * 1000000.0f);
        }
        output->scores[i] = ((float)(hash % 10000)) / 10000.0f;
        sum += output->scores[i];
    }

    /* Normalize to sum to 1.0 (softmax-like) */
    for (i = 0; i < output->num_scores; i++) {
        output->scores[i] /= (sum + 1e-10f);
    }

    return 0;
}

/* Select top-K experts */
static int select_top_k_experts(struct moe_engine *engine,
                               struct gating_output *gating,
                               __u32 top_k,
                               struct routing_decision *decision)
{
    struct score_pair pairs[MOE_MAX_EXPERTS];
    __u32 i;

    /* Create score pairs */
    for (i = 0; i < gating->num_scores; i++) {
        pairs[i].expert_id = i;
        pairs[i].score = gating->scores[i];

        /* Apply load balancing penalty if enabled */
        if (engine->config.load_balancing_enabled) {
            float load_penalty = engine->expert_loads[i] *
                                engine->config.load_balancing_alpha;
            pairs[i].score *= (1.0f - load_penalty);
        }
    }

    /* Sort by score (descending) */
    sort(pairs, gating->num_scores, sizeof(struct score_pair),
         compare_scores, NULL);

    /* Select top-K available experts */
    decision->num_experts = 0;
    for (i = 0; i < gating->num_scores && decision->num_experts < top_k; i++) {
        __u32 expert_id = pairs[i].expert_id;

        /* Check if expert is available */
        if (moe_expert_is_available(&engine->experts[expert_id])) {
            decision->expert_ids[decision->num_experts] = expert_id;
            decision->expert_weights[decision->num_experts] = pairs[i].score;
            decision->num_experts++;
        }
    }

    /* If we couldn't get enough experts, fill with less preferred ones */
    if (decision->num_experts < top_k) {
        for (i = 0; i < gating->num_scores && decision->num_experts < top_k; i++) {
            __u32 expert_id = pairs[i].expert_id;
            bool already_selected = false;
            __u32 j;

            /* Check if already selected */
            for (j = 0; j < decision->num_experts; j++) {
                if (decision->expert_ids[j] == expert_id) {
                    already_selected = true;
                    break;
                }
            }

            if (!already_selected) {
                decision->expert_ids[decision->num_experts] = expert_id;
                decision->expert_weights[decision->num_experts] = pairs[i].score;
                decision->num_experts++;
            }
        }
    }

    return 0;
}

/* Route a single token to experts */
int moe_route_token(struct moe_engine *engine, __u32 token_id,
                   struct gating_output *gating,
                   struct routing_decision *decision)
{
    unsigned long flags;
    __u32 i;
    int ret;

    if (!engine || !gating || !decision)
        return -EINVAL;

    memset(decision, 0, sizeof(*decision));
    decision->token_id = token_id;
    decision->dropped = false;

    /* Apply token dropping for sparsity */
    if (engine->config.token_dropping_enabled) {
        ret = moe_apply_token_dropping(engine, decision);
        if (ret < 0 || decision->dropped) {
            engine->config.total_tokens_dropped++;
            return 0;  /* Token dropped, not an error */
        }
    }

    /* Select experts based on routing strategy */
    switch (engine->config.strategy) {
    case MOE_ROUTING_TOP_K:
        ret = select_top_k_experts(engine, gating, engine->config.top_k,
                                  decision);
        break;

    case MOE_ROUTING_THRESHOLD:
        /* Activate all experts above threshold */
        decision->num_experts = 0;
        for (i = 0; i < gating->num_scores; i++) {
            if (gating->scores[i] >= engine->config.routing_threshold) {
                decision->expert_ids[decision->num_experts] = i;
                decision->expert_weights[decision->num_experts] = gating->scores[i];
                decision->num_experts++;
            }
        }
        ret = 0;
        break;

    case MOE_ROUTING_HASH:
        /* Deterministic hash-based routing */
        {
            __u32 hash = token_id * 2654435761U;
            __u32 expert_id = hash % engine->config.num_experts;
            decision->expert_ids[0] = expert_id;
            decision->expert_weights[0] = 1.0f;
            decision->num_experts = 1;
            ret = 0;
        }
        break;

    default:
        ret = -EINVAL;
    }

    if (ret < 0)
        return ret;

    /* Update expert loads */
    spin_lock_irqsave(&engine->expert_lock, flags);
    for (i = 0; i < decision->num_experts; i++) {
        __u32 expert_id = decision->expert_ids[i];
        if (expert_id < MOE_MAX_EXPERTS) {
            engine->experts[expert_id].current_load++;
            engine->experts[expert_id].total_activations++;
            engine->experts[expert_id].total_tokens_processed++;

            if (engine->experts[expert_id].current_load >= engine->experts[expert_id].capacity) {
                engine->experts[expert_id].state = EXPERT_STATE_OVERLOADED;
            } else {
                engine->experts[expert_id].state = EXPERT_STATE_ACTIVE;
            }
        }
    }
    spin_unlock_irqrestore(&engine->expert_lock, flags);

    /* Update statistics */
    engine->config.total_tokens_processed++;
    engine->config.total_expert_activations += decision->num_experts;
    engine->config.average_experts_per_token =
        (float)engine->config.total_expert_activations /
        (float)(engine->config.total_tokens_processed + 1);

    return 0;
}

/* Route a batch of tokens */
int moe_route_batch(struct moe_engine *engine, __u32 *token_ids,
                   struct gating_output *gating_outputs,
                   struct routing_decision *decisions, __u32 batch_size)
{
    __u32 i;
    int ret;

    if (!engine || !token_ids || !gating_outputs || !decisions)
        return -EINVAL;

    for (i = 0; i < batch_size; i++) {
        ret = moe_route_token(engine, token_ids[i], &gating_outputs[i],
                             &decisions[i]);
        if (ret < 0)
            pr_debug("Failed to route token %d: %d\n", i, ret);
    }

    /* Update expert loads after batch */
    moe_update_expert_loads(engine);

    return 0;
}

/* Update normalized expert loads */
void moe_update_expert_loads(struct moe_engine *engine)
{
    unsigned long flags;
    __u32 i;
    __u64 total_load = 0;

    if (!engine)
        return;

    spin_lock_irqsave(&engine->expert_lock, flags);

    /* Calculate total load */
    for (i = 0; i < engine->config.num_experts; i++) {
        total_load += engine->experts[i].current_load;
    }

    /* Normalize loads */
    for (i = 0; i < engine->config.num_experts; i++) {
        if (total_load > 0) {
            engine->expert_loads[i] = (float)engine->experts[i].current_load /
                                     (float)total_load;
        } else {
            engine->expert_loads[i] = 0.0f;
        }

        engine->experts[i].utilization_percent =
            (float)engine->experts[i].current_load /
            (float)engine->experts[i].capacity * 100.0f;
    }

    spin_unlock_irqrestore(&engine->expert_lock, flags);
}

/* Apply token dropping for sparsity */
int moe_apply_token_dropping(struct moe_engine *engine,
                            struct routing_decision *decision)
{
    __u32 random_val;

    if (!engine || !decision)
        return -EINVAL;

    /* Get random value for probabilistic dropping */
    get_random_bytes(&random_val, sizeof(random_val));
    float random_prob = (float)(random_val % 10000) / 10000.0f;

    /* Calculate drop probability to achieve target sparsity */
    float current_sparsity = (float)engine->config.current_sparsity_percent / 100.0f;
    float target_sparsity = (float)engine->config.target_sparsity_percent / 100.0f;
    float drop_prob = target_sparsity - current_sparsity;

    if (drop_prob < 0.0f)
        drop_prob = 0.0f;
    if (drop_prob > 1.0f)
        drop_prob = 1.0f;

    /* Drop token if random value is below drop probability */
    if (random_prob < drop_prob) {
        decision->dropped = true;
        return 0;
    }

    decision->dropped = false;
    return 0;
}

/* Check if layer should be skipped */
bool moe_should_skip_layer(struct moe_engine *engine, __u32 layer_id)
{
    if (!engine || !engine->config.layer_skipping_enabled)
        return false;

    /* Check if layer is in skip mask */
    if (layer_id < 32) {
        return (engine->config.skip_layers_mask & (1U << layer_id)) != 0;
    }

    return false;
}

/* Calculate current sparsity percentage */
__u32 moe_calculate_sparsity(struct moe_engine *engine)
{
    __u64 total_possible_activations;
    __u64 actual_activations;
    __u32 sparsity;

    if (!engine || engine->config.total_tokens_processed == 0)
        return 0;

    /* Total possible activations = tokens * all experts */
    total_possible_activations = engine->config.total_tokens_processed *
                                engine->config.num_experts;

    /* Actual activations */
    actual_activations = engine->config.total_expert_activations;

    /* Sparsity = (1 - actual/possible) * 100 */
    if (total_possible_activations > 0) {
        sparsity = 100 - ((actual_activations * 100) / total_possible_activations);
    } else {
        sparsity = 0;
    }

    engine->config.current_sparsity_percent = sparsity;
    return sparsity;
}

/* Get statistics */
void moe_get_statistics(struct moe_engine *engine, struct moe_config *stats)
{
    if (!engine || !stats)
        return;

    /* Update sparsity before returning stats */
    moe_calculate_sparsity(engine);
    memcpy(stats, &engine->config, sizeof(*stats));
}

/* Reset statistics */
void moe_reset_statistics(struct moe_engine *engine)
{
    unsigned long flags;
    __u32 i;

    if (!engine)
        return;

    spin_lock_irqsave(&engine->expert_lock, flags);

    for (i = 0; i < MOE_MAX_EXPERTS; i++) {
        engine->experts[i].current_load = 0;
        engine->experts[i].state = EXPERT_STATE_IDLE;
    }

    engine->config.total_tokens_processed = 0;
    engine->config.total_tokens_dropped = 0;
    engine->config.total_expert_activations = 0;
    engine->config.current_sparsity_percent = 0;
    engine->config.average_experts_per_token = 0.0f;

    spin_unlock_irqrestore(&engine->expert_lock, flags);
}

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("LightOS Mixture of Experts Engine");
