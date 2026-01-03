/* SPDX-License-Identifier: GPL-2.0 */
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/device.h>
#include <linux/uaccess.h>
#include <linux/string.h>
#include "lightos_core.h"

MODULE_LICENSE("GPL");
MODULE_AUTHOR("LightRail AI");
MODULE_DESCRIPTION("LightOS Core Kernel Module");
MODULE_VERSION("0.1.0");

static dev_t lightos_dev;
static struct cdev lightos_cdev;
static struct class *lightos_class;

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
    int ret;

    switch (cmd) {
    case LIGHTOS_IOC_GET_DEVICE_STATE:
        /* Populate with mock data for v0.1 */
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
    
    pr_info("LightOS v0.1.0 loaded\n");
    return 0;
}

static void __exit lightos_exit(void)
{
    device_destroy(lightos_class, lightos_dev);
    class_destroy(lightos_class);
    cdev_del(&lightos_cdev);
    unregister_chrdev_region(lightos_dev, 1);
    pr_info("LightOS unloaded\n");
}

module_init(lightos_init);
module_exit(lightos_exit);
