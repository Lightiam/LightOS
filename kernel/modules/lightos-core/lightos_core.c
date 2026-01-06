/* SPDX-License-Identifier: GPL-2.0 */
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/device.h>
#include <linux/uaccess.h>
#include <linux/string.h>
#include <linux/mutex.h>
#include "lightos_core.h"
#include "spiking/spiking_core.h"

MODULE_LICENSE("GPL");
MODULE_AUTHOR("LightRail AI");
MODULE_DESCRIPTION("LightOS Neural Compute Engine - Core Kernel Module");
MODULE_VERSION("0.2.0");

static dev_t lightos_dev;
static struct cdev lightos_cdev;
static struct class *lightos_class;

/* Global spiking engine instance */
static struct spiking_engine global_spiking_engine;
static struct mutex spiking_mutex;

static int lightos_open(struct inode *inode, struct file *file)
{
    pr_debug("LightOS device opened\n");
    return 0;
}

static int lightos_release(struct inode *inode, struct file *file)
{
    pr_debug("LightOS device released\n");
    return 0;
}

static long lightos_ioctl(struct file *file, unsigned int cmd, unsigned long arg)
{
    struct lightos_device_state state;
    struct lightos_spiking_config spiking_cfg;
    struct lightos_spike_event spike_evt;
    struct lightos_neuron_state neuron_st;
    struct spiking_config kernel_cfg;
    struct spike_event kernel_evt;
    struct lif_neuron kernel_neuron;
    int ret;

    switch (cmd) {
    case LIGHTOS_IOC_GET_DEVICE_STATE:
        /* Populate with enhanced data for v0.2 */
        memset(&state, 0, sizeof(state));
        state.device_id = 0;
        state.device_type = LIGHTOS_DEVICE_GPU;
        state.utilization_percent = 75;
        state.power_watts = 250;
        state.memory_used_bytes = 8ULL * 1024 * 1024 * 1024; /* 8GB */
        state.memory_total_bytes = 16ULL * 1024 * 1024 * 1024; /* 16GB */

        ret = copy_to_user((void __user *)arg, &state, sizeof(state));
        if (ret != 0)
            return -EFAULT;

        return 0;

    case LIGHTOS_IOC_SPIKING_CONFIG:
        /* Configure spiking engine */
        ret = copy_from_user(&spiking_cfg, (void __user *)arg, sizeof(spiking_cfg));
        if (ret != 0)
            return -EFAULT;

        mutex_lock(&spiking_mutex);

        /* Convert user config to kernel config */
        kernel_cfg.encoding = spiking_cfg.encoding;
        kernel_cfg.enabled = spiking_cfg.enabled;
        kernel_cfg.max_events_per_cycle = spiking_cfg.max_events_per_cycle ?
                                          spiking_cfg.max_events_per_cycle : 1000;
        kernel_cfg.processing_interval_us = spiking_cfg.processing_interval_us ?
                                            spiking_cfg.processing_interval_us : 1000;
        kernel_cfg.target_sparsity_percent = spiking_cfg.target_sparsity_percent ?
                                             spiking_cfg.target_sparsity_percent : 69;

        /* Initialize or reconfigure spiking engine */
        if (global_spiking_engine.neurons == NULL) {
            ret = spiking_engine_init(&global_spiking_engine, &kernel_cfg);
        } else {
            memcpy(&global_spiking_engine.config, &kernel_cfg, sizeof(kernel_cfg));
            ret = 0;
        }

        mutex_unlock(&spiking_mutex);
        return ret;

    case LIGHTOS_IOC_SPIKING_START:
        /* Start spiking engine */
        mutex_lock(&spiking_mutex);
        ret = spiking_engine_start(&global_spiking_engine);
        mutex_unlock(&spiking_mutex);
        return ret;

    case LIGHTOS_IOC_SPIKING_STOP:
        /* Stop spiking engine */
        mutex_lock(&spiking_mutex);
        spiking_engine_stop(&global_spiking_engine);
        mutex_unlock(&spiking_mutex);
        return 0;

    case LIGHTOS_IOC_SPIKING_SUBMIT_EVENT:
        /* Submit spike event */
        ret = copy_from_user(&spike_evt, (void __user *)arg, sizeof(spike_evt));
        if (ret != 0)
            return -EFAULT;

        /* Convert to kernel event */
        memset(&kernel_evt, 0, sizeof(kernel_evt));
        kernel_evt.neuron_id = spike_evt.neuron_id;
        kernel_evt.timestamp_ns = spike_evt.timestamp_ns;
        kernel_evt.amplitude_mv = spike_evt.amplitude_mv;
        kernel_evt.synapse_count = spike_evt.synapse_count;

        mutex_lock(&spiking_mutex);
        ret = spiking_event_submit(&global_spiking_engine, &kernel_evt);
        mutex_unlock(&spiking_mutex);
        return ret;

    case LIGHTOS_IOC_SPIKING_GET_STATS:
        /* Get spiking statistics */
        mutex_lock(&spiking_mutex);
        spiking_get_statistics(&global_spiking_engine, &kernel_cfg);
        mutex_unlock(&spiking_mutex);

        /* Convert to user format */
        spiking_cfg.encoding = kernel_cfg.encoding;
        spiking_cfg.enabled = kernel_cfg.enabled;
        spiking_cfg.max_events_per_cycle = kernel_cfg.max_events_per_cycle;
        spiking_cfg.processing_interval_us = kernel_cfg.processing_interval_us;
        spiking_cfg.target_sparsity_percent = kernel_cfg.target_sparsity_percent;
        spiking_cfg.current_sparsity_percent = kernel_cfg.current_sparsity_percent;
        spiking_cfg.total_events_processed = kernel_cfg.total_events_processed;
        spiking_cfg.events_dropped = kernel_cfg.events_dropped;

        ret = copy_to_user((void __user *)arg, &spiking_cfg, sizeof(spiking_cfg));
        if (ret != 0)
            return -EFAULT;

        return 0;

    case LIGHTOS_IOC_GET_NEURON_STATE:
        /* Get neuron state */
        ret = copy_from_user(&neuron_st, (void __user *)arg, sizeof(neuron_st));
        if (ret != 0)
            return -EFAULT;

        mutex_lock(&spiking_mutex);
        ret = spiking_neuron_get_state(&global_spiking_engine, neuron_st.neuron_id,
                                       &kernel_neuron);
        mutex_unlock(&spiking_mutex);

        if (ret != 0)
            return ret;

        /* Convert to user format */
        neuron_st.state = kernel_neuron.state;
        neuron_st.membrane_potential_mv = kernel_neuron.membrane_potential_mv;
        neuron_st.total_spikes = kernel_neuron.total_spikes;
        neuron_st.current_rate_hz = kernel_neuron.current_rate_hz;

        ret = copy_to_user((void __user *)arg, &neuron_st, sizeof(neuron_st));
        if (ret != 0)
            return -EFAULT;

        return 0;

    default:
        return -ENOTTY;
    }
}

static struct file_operations lightos_fops = {
    .owner = THIS_MODULE,
    .open = lightos_open,
    .release = lightos_release,
    .unlocked_ioctl = lightos_ioctl,
};

static int __init lightos_init(void)
{
    int ret;

    /* Initialize spiking mutex */
    mutex_init(&spiking_mutex);
    memset(&global_spiking_engine, 0, sizeof(global_spiking_engine));

    ret = alloc_chrdev_region(&lightos_dev, 0, 1, LIGHTOS_DEVICE_NAME);
    if (ret < 0) {
        pr_err("Failed to allocate device number\n");
        return ret;
    }

    cdev_init(&lightos_cdev, &lightos_fops);
    ret = cdev_add(&lightos_cdev, lightos_dev, 1);
    if (ret < 0) {
        unregister_chrdev_region(lightos_dev, 1);
        return ret;
    }

    lightos_class = class_create(THIS_MODULE, LIGHTOS_DEVICE_NAME);
    if (IS_ERR(lightos_class)) {
        cdev_del(&lightos_cdev);
        unregister_chrdev_region(lightos_dev, 1);
        return PTR_ERR(lightos_class);
    }

    device_create(lightos_class, NULL, lightos_dev, NULL, LIGHTOS_DEVICE_NAME);

    pr_info("LightOS Neural Compute Engine v0.2.0 loaded\n");
    pr_info("  - Spiking Neural Network support enabled\n");
    pr_info("  - Platform-agnostic architecture\n");
    return 0;
}

static void __exit lightos_exit(void)
{
    /* Cleanup spiking engine */
    mutex_lock(&spiking_mutex);
    if (global_spiking_engine.neurons != NULL) {
        spiking_engine_cleanup(&global_spiking_engine);
    }
    mutex_unlock(&spiking_mutex);

    device_destroy(lightos_class, lightos_dev);
    class_destroy(lightos_class);
    cdev_del(&lightos_cdev);
    unregister_chrdev_region(lightos_dev, 1);
    pr_info("LightOS Neural Compute Engine unloaded\n");
}

module_init(lightos_init);
module_exit(lightos_exit);
