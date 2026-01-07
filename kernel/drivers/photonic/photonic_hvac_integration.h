/* SPDX-License-Identifier: GPL-2.0 */
#ifndef _PHOTONIC_HVAC_INTEGRATION_H
#define _PHOTONIC_HVAC_INTEGRATION_H

#include <linux/types.h>
#include "photonic_driver.h"

/*
 * Photonic Driver <-> Infrastructure Autopilot Integration
 *
 * Allows chip-level thermal management to communicate with
 * data center HVAC systems for coordinated cooling.
 */

/* HVAC callback for chip thermal events */
struct hvac_callbacks {
    /* Called when chip temperature changes significantly */
    void (*on_temp_change)(void *autopilot_ctx, __u32 device_id,
                          __u32 temp_mc, __u32 power_w);

    /* Called when thermal throttling starts/stops */
    void (*on_throttle_change)(void *autopilot_ctx, __u32 device_id,
                              bool throttling, __u32 throttle_percent);

    /* Called to request additional cooling */
    int (*request_cooling)(void *autopilot_ctx, __u32 device_id,
                          __u32 additional_airflow_cfm);

    /* Called during emergency shutdown */
    void (*on_emergency_shutdown)(void *autopilot_ctx, __u32 device_id,
                                 __u32 temp_mc);
};

/* HVAC integration state */
struct hvac_integration {
    bool enabled;
    void *autopilot_ctx;            /* Opaque pointer to autopilot state */
    struct hvac_callbacks callbacks;

    /* Metrics for feedback */
    __u32 rack_inlet_temp_mc;       /* Cold aisle temp */
    __u32 rack_airflow_cfm;         /* Airflow at rack */
    __u32 ambient_temp_mc;          /* Room ambient */

    /* Communication stats */
    __u64 callbacks_invoked;
    __u64 cooling_requests_sent;
    __u64 cooling_requests_granted;
};

/* Function prototypes */

/* Initialize HVAC integration */
int photonic_hvac_init(struct photonic_device *pdev,
                      void *autopilot_ctx,
                      struct hvac_callbacks *callbacks);

/* Notify HVAC of temperature change */
void photonic_hvac_notify_temp(struct photonic_device *pdev);

/* Request additional cooling from HVAC */
int photonic_hvac_request_cooling(struct photonic_device *pdev,
                                 __u32 cfm_needed);

/* Update ambient conditions from HVAC */
void photonic_hvac_update_ambient(struct photonic_device *pdev,
                                 __u32 inlet_temp_mc,
                                 __u32 airflow_cfm);

/* Coordinated thermal management */
void photonic_hvac_coordinated_thermal_control(struct photonic_device *pdev);

#endif /* _PHOTONIC_HVAC_INTEGRATION_H */
