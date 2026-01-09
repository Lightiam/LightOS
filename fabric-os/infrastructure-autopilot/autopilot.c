/* SPDX-License-Identifier: GPL-2.0 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <unistd.h>
#include "autopilot.h"

/*
 * LightOS Infrastructure Autopilot Implementation
 *
 * Simplified DRL controller for data center HVAC optimization.
 * Production version would integrate with TensorFlow/PyTorch for
 * full neural network implementation.
 */

/* Initialize autopilot */
int autopilot_init(struct autopilot_state *state,
                  struct drl_agent_config *config)
{
    if (!state || !config)
        return -1;

    memset(state, 0, sizeof(*state));
    memcpy(&state->agent_config, config, sizeof(*config));

    /* Initialize mode */
    state->mode = HVAC_MODE_BASELINE;

    /* Safety layer defaults */
    state->safety.enabled = true;
    state->safety.max_temp_c = AUTOPILOT_SAFETY_TEMP_LIMIT_C;
    state->safety.max_humidity_percent = 60.0f;
    state->safety.min_airflow_cfm = 1000.0f;

    /* Control loop settings */
    state->control_interval_ms = 60000;  /* 1 minute */
    state->running = false;

    pthread_mutex_init(&state->state_lock, NULL);

    printf("Infrastructure Autopilot initialized\n");
    printf("  Safety layer: %s\n", state->safety.enabled ? "ENABLED" : "DISABLED");
    printf("  Max temperature: %.1f°C\n", state->safety.max_temp_c);
    printf("  Control interval: %dms\n", state->control_interval_ms);

    return 0;
}

/* Cleanup autopilot */
void autopilot_cleanup(struct autopilot_state *state)
{
    if (!state)
        return;

    if (state->running) {
        autopilot_stop(state);
    }

    pthread_mutex_destroy(&state->state_lock);

    printf("Infrastructure Autopilot cleanup complete\n");
    printf("  Total energy saved: %.1f%%\n", state->metrics.energy_saved_percent);
    printf("  Cost savings: $%.2f\n", state->metrics.cumulative_savings_usd);
}

/* Register CRAC unit */
int autopilot_register_crac(struct autopilot_state *state,
                           struct crac_unit *unit)
{
    if (!state || !unit || state->num_crac_units >= AUTOPILOT_MAX_CRAC_UNITS)
        return -1;

    pthread_mutex_lock(&state->state_lock);

    memcpy(&state->crac_units[state->num_crac_units], unit, sizeof(*unit));
    state->crac_units[state->num_crac_units].unit_id = state->num_crac_units;

    state->num_crac_units++;

    pthread_mutex_unlock(&state->state_lock);

    printf("Registered CRAC unit %d: %s\n", unit->unit_id, unit->location);

    return 0;
}

/* Register IT rack */
int autopilot_register_rack(struct autopilot_state *state,
                           struct rack_thermal_state *rack)
{
    if (!state || !rack || state->num_racks >= AUTOPILOT_MAX_RACKS)
        return -1;

    pthread_mutex_lock(&state->state_lock);

    memcpy(&state->racks[state->num_racks], rack, sizeof(*rack));
    state->racks[state->num_racks].rack_id = state->num_racks;

    state->num_racks++;

    pthread_mutex_unlock(&state->state_lock);

    return 0;
}

/* Observe current state for DRL */
int drl_observe_state(struct autopilot_state *state,
                     struct drl_observation *obs)
{
    uint32_t i;
    float temp_sum = 0.0f, load_sum = 0.0f, power_sum = 0.0f;
    time_t now;
    struct tm *tm_info;

    if (!state || !obs)
        return -1;

    memset(obs, 0, sizeof(*obs));

    pthread_mutex_lock(&state->state_lock);

    /* Calculate IT rack statistics */
    obs->max_inlet_temp = 0.0f;
    for (i = 0; i < state->num_racks; i++) {
        struct rack_thermal_state *rack = &state->racks[i];

        temp_sum += rack->inlet_temp_c;
        load_sum += rack->it_load_percent;
        power_sum += rack->power_kw;

        if (rack->inlet_temp_c > obs->max_inlet_temp) {
            obs->max_inlet_temp = rack->inlet_temp_c;
        }
    }

    if (state->num_racks > 0) {
        obs->avg_inlet_temp = temp_sum / state->num_racks;
        obs->avg_it_load = load_sum / state->num_racks;
    }

    obs->total_power_kw = power_sum;

    /* CRAC states */
    for (i = 0; i < state->num_crac_units && i < AUTOPILOT_MAX_CRAC_UNITS; i++) {
        obs->crac_supply_temps[i] = state->crac_units[i].supply_temp_c;
        obs->crac_airflows[i] = state->crac_units[i].airflow_cfm;
    }

    /* Time features */
    now = time(NULL);
    tm_info = localtime(&now);
    obs->hour_of_day = tm_info->tm_hour;
    obs->day_of_week = tm_info->tm_wday;

    /* Mock weather data (would come from API in production) */
    obs->outside_temp_c = 25.0f;
    obs->outside_humidity_percent = 50.0f;

    pthread_mutex_unlock(&state->state_lock);

    return 0;
}

/* Compute action using simplified DRL policy */
int drl_compute_action(struct autopilot_state *state,
                      struct drl_observation *obs,
                      struct drl_action *action)
{
    uint32_t i;
    float temp_error, load_factor;

    if (!state || !obs || !action)
        return -1;

    memset(action, 0, sizeof(*action));

    /* Simplified policy (production would use neural network):
     *
     * Policy logic:
     * 1. If temperature too high → increase cooling
     * 2. If temperature OK and low load → reduce cooling (save energy)
     * 3. If high load predicted → pre-cool proactively
     */

    /* Calculate temperature error */
    temp_error = obs->avg_inlet_temp - TEMP_OPTIMAL_C;

    /* Load factor affects aggressiveness */
    load_factor = obs->avg_it_load / 100.0f;

    /* Global temperature adjustment */
    if (temp_error > 2.0f) {
        /* Too hot: lower supply temp */
        action->global_temp_offset = -1.5f * (temp_error / 2.0f);
    } else if (temp_error < -2.0f && load_factor < 0.5f) {
        /* Too cold and low load: raise supply temp (save energy) */
        action->global_temp_offset = 1.0f * (-temp_error / 2.0f);
    } else {
        /* In optimal range: minor adjustments */
        action->global_temp_offset = -0.2f * temp_error;
    }

    /* Clamp to ±2°C per control cycle */
    if (action->global_temp_offset > 2.0f)
        action->global_temp_offset = 2.0f;
    if (action->global_temp_offset < -2.0f)
        action->global_temp_offset = -2.0f;

    /* Per-CRAC adjustments (simple proportional control) */
    for (i = 0; i < state->num_crac_units && i < AUTOPILOT_MAX_CRAC_UNITS; i++) {
        action->crac_temp_deltas[i] = action->global_temp_offset;

        /* Airflow adjustment based on load */
        if (load_factor > 0.8f) {
            action->crac_airflow_deltas[i] = 100.0f;  /* +100 CFM */
        } else if (load_factor < 0.3f) {
            action->crac_airflow_deltas[i] = -100.0f; /* -100 CFM */
        }
    }

    /* Global airflow multiplier */
    action->global_airflow_multiplier = 1.0f + (load_factor - 0.5f) * 0.2f;

    return 0;
}

/* Compute reward signal */
float drl_compute_reward(struct autopilot_state *state,
                        struct drl_observation *obs,
                        struct drl_action *action)
{
    struct drl_reward reward;
    float temp_violation_penalty = 0.0f;
    float energy_reward = 0.0f;
    uint32_t i;

    if (!state || !obs || !action)
        return -1000.0f;

    /* Energy component: penalize high power */
    /* Baseline cooling power: ~30% of IT power */
    float baseline_hvac_power = state->metrics.total_it_power_kw * 0.30f;
    float actual_hvac_power = state->metrics.total_hvac_power_kw;
    energy_reward = -(actual_hvac_power / baseline_hvac_power);

    /* Comfort component: reward for staying in optimal range */
    float comfort_reward = 0.0f;
    if (obs->avg_inlet_temp >= 18.0f && obs->avg_inlet_temp <= 22.0f) {
        comfort_reward = 10.0f;  /* In optimal range */
    } else if (obs->avg_inlet_temp > 22.0f && obs->avg_inlet_temp <= 24.0f) {
        comfort_reward = 5.0f;   /* Acceptable */
    } else {
        comfort_reward = -5.0f;  /* Outside desired range */
    }

    /* Safety component: large penalty for violations */
    float safety_penalty = 0.0f;
    if (obs->max_inlet_temp > state->safety.max_temp_c) {
        temp_violation_penalty = -100.0f * (obs->max_inlet_temp - state->safety.max_temp_c);
        safety_penalty += temp_violation_penalty;
        state->safety.safety_violations++;
    }

    /* Combine components */
    reward.energy_component = energy_reward * state->agent_config.reward_energy_weight;
    reward.comfort_component = comfort_reward * state->agent_config.reward_temp_weight;
    reward.safety_component = safety_penalty * state->agent_config.reward_safety_weight;

    reward.total_reward = reward.energy_component +
                         reward.comfort_component +
                         reward.safety_component;

    return reward.total_reward;
}

/* Safety check before executing action */
bool safety_check_action(struct autopilot_state *state,
                        struct drl_action *action)
{
    uint32_t i;
    float predicted_temp;

    if (!state || !action || !state->safety.enabled)
        return true;  /* Safety disabled or no data */

    /* Check if proposed action would violate temperature limits */
    for (i = 0; i < state->num_crac_units; i++) {
        struct crac_unit *crac = &state->crac_units[i];
        float new_supply_temp = crac->target_supply_temp_c + action->crac_temp_deltas[i];

        /* Don't allow supply temp outside operational range */
        if (new_supply_temp < crac->min_supply_temp_c ||
            new_supply_temp > crac->max_supply_temp_c) {
            printf("Safety check failed: CRAC %d temp %.1f°C outside range [%.1f, %.1f]\n",
                   i, new_supply_temp, crac->min_supply_temp_c, crac->max_supply_temp_c);
            return false;
        }
    }

    /* Predict resulting inlet temperature (simplified) */
    predicted_temp = state->metrics.avg_inlet_temp - action->global_temp_offset;

    if (predicted_temp > state->safety.max_temp_c) {
        printf("Safety check failed: Predicted inlet temp %.1f°C > limit %.1f°C\n",
               predicted_temp, state->safety.max_temp_c);
        return false;
    }

    return true;
}

/* Execute control action */
int autopilot_execute_action(struct autopilot_state *state,
                            struct drl_action *action)
{
    uint32_t i;

    if (!state || !action)
        return -1;

    /* Safety check first */
    if (!safety_check_action(state, action)) {
        printf("Action rejected by safety layer\n");
        state->safety.safety_overrides++;
        return -1;
    }

    pthread_mutex_lock(&state->state_lock);

    /* Apply action to CRAC units */
    for (i = 0; i < state->num_crac_units; i++) {
        struct crac_unit *crac = &state->crac_units[i];

        /* Update temperature setpoint */
        crac->target_supply_temp_c += action->crac_temp_deltas[i];

        /* Clamp to operational limits */
        if (crac->target_supply_temp_c < crac->min_supply_temp_c)
            crac->target_supply_temp_c = crac->min_supply_temp_c;
        if (crac->target_supply_temp_c > crac->max_supply_temp_c)
            crac->target_supply_temp_c = crac->max_supply_temp_c;

        /* Update airflow setpoint */
        crac->target_airflow_cfm += action->crac_airflow_deltas[i];
        crac->target_airflow_cfm *= action->global_airflow_multiplier;

        /* Clamp airflow */
        if (crac->target_airflow_cfm > crac->max_airflow_cfm)
            crac->target_airflow_cfm = crac->max_airflow_cfm;
        if (crac->target_airflow_cfm < state->safety.min_airflow_cfm)
            crac->target_airflow_cfm = state->safety.min_airflow_cfm;

        /* In production, would send commands to actual CRAC controllers here via:
         * - BACnet protocol
         * - Modbus TCP
         * - Proprietary APIs (Schneider, Vertiv, etc.)
         */

        printf("CRAC %d: Temp %.1f°C → %.1f°C, Airflow %.0f CFM → %.0f CFM\n",
               i, crac->supply_temp_c, crac->target_supply_temp_c,
               crac->airflow_cfm, crac->target_airflow_cfm);
    }

    pthread_mutex_unlock(&state->state_lock);

    return 0;
}

/* Control loop (runs in separate thread) */
void autopilot_control_loop(void *arg)
{
    struct autopilot_state *state = (struct autopilot_state *)arg;
    struct drl_observation obs;
    struct drl_action action;
    float reward;

    printf("Infrastructure Autopilot control loop started\n");
    printf("  Mode: %s\n", state->mode == HVAC_MODE_AUTOPILOT ? "AUTOPILOT" : "BASELINE");
    printf("  Control interval: %dms\n", state->control_interval_ms);

    while (state->running) {
        /* 1. Observe current state */
        drl_observe_state(state, &obs);

        /* 2. Compute action based on policy */
        if (state->mode == HVAC_MODE_AUTOPILOT) {
            drl_compute_action(state, &obs, &action);
        } else {
            /* Baseline mode: no action */
            memset(&action, 0, sizeof(action));
        }

        /* 3. Execute action */
        if (state->mode == HVAC_MODE_AUTOPILOT) {
            autopilot_execute_action(state, &action);
        }

        /* 4. Compute reward (for learning) */
        reward = drl_compute_reward(state, &obs, &action);

        /* 5. Update metrics */
        autopilot_update_metrics(state);

        /* 6. Log status */
        printf("[Autopilot] Temp: %.1f°C, Load: %.0f%%, Power: %.1fkW, Reward: %.1f, Savings: %.1f%%\n",
               obs.avg_inlet_temp, obs.avg_it_load, obs.total_power_kw,
               reward, state->metrics.energy_saved_percent);

        /* 7. Sleep until next control cycle */
        usleep(state->control_interval_ms * 1000);
    }

    printf("Infrastructure Autopilot control loop stopped\n");
}

/* Start autopilot */
int autopilot_start(struct autopilot_state *state)
{
    if (!state || state->running)
        return -1;

    state->running = true;

    if (pthread_create(&state->control_thread, NULL,
                      (void *(*)(void *))autopilot_control_loop, state) != 0) {
        fprintf(stderr, "Failed to create control thread\n");
        state->running = false;
        return -1;
    }

    printf("Infrastructure Autopilot started\n");
    return 0;
}

/* Stop autopilot */
void autopilot_stop(struct autopilot_state *state)
{
    if (!state || !state->running)
        return;

    state->running = false;
    pthread_join(state->control_thread, NULL);

    printf("Infrastructure Autopilot stopped\n");
}

/* Update performance metrics */
void autopilot_update_metrics(struct autopilot_state *state)
{
    uint32_t i;
    float it_power = 0.0f, hvac_power = 0.0f;
    float temp_sum = 0.0f;

    if (!state)
        return;

    pthread_mutex_lock(&state->state_lock);

    /* Calculate IT power */
    for (i = 0; i < state->num_racks; i++) {
        it_power += state->racks[i].power_kw;
    }

    /* Calculate HVAC power */
    for (i = 0; i < state->num_crac_units; i++) {
        hvac_power += state->crac_units[i].power_kw;
    }

    state->metrics.total_it_power_kw = it_power;
    state->metrics.total_hvac_power_kw = hvac_power;

    /* Calculate PUE */
    state->metrics.pue = calculate_pue(it_power + hvac_power, it_power);

    /* Calculate energy savings vs baseline (30% HVAC overhead) */
    float baseline_hvac = it_power * 0.30f;
    if (baseline_hvac > 0.0f) {
        state->metrics.energy_saved_percent =
            (baseline_hvac - hvac_power) / baseline_hvac * 100.0f;
    }

    /* Temperature statistics */
    for (i = 0; i < state->num_racks; i++) {
        temp_sum += state->racks[i].inlet_temp_c;
        if (state->racks[i].inlet_temp_c > state->metrics.max_inlet_temp_c) {
            state->metrics.max_inlet_temp_c = state->racks[i].inlet_temp_c;
        }
    }

    if (state->num_racks > 0) {
        state->metrics.avg_inlet_temp_c = temp_sum / state->num_racks;
    }

    /* Cost savings (assume $0.10/kWh) */
    float baseline_cost = baseline_hvac * 0.10f;
    float actual_cost = hvac_power * 0.10f;
    state->metrics.hvac_cost_per_hour = actual_cost;
    state->metrics.cumulative_savings_usd += (baseline_cost - actual_cost);

    pthread_mutex_unlock(&state->state_lock);
}

/* Calculate PUE */
float autopilot_calculate_pue(struct autopilot_state *state)
{
    if (!state)
        return 1.0f;

    autopilot_update_metrics(state);
    return state->metrics.pue;
}
