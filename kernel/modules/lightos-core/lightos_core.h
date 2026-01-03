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
};

struct lightos_device_state {
    __u32 device_id;
    __u32 device_type;
    __u32 utilization_percent;
    __u32 power_watts;
    __u64 memory_used_bytes;
    __u64 memory_total_bytes;
};

#define LIGHTOS_IOC_MAGIC 'L'
#define LIGHTOS_IOC_GET_DEVICE_STATE _IOWR(LIGHTOS_IOC_MAGIC, 1, struct lightos_device_state)

#endif /* _LIGHTOS_CORE_H */
