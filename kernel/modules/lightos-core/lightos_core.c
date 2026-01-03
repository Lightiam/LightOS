/* SPDX-License-Identifier: GPL-2.0 */
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/device.h>
#include "lightos_core.h"

MODULE_LICENSE("GPL");
MODULE_AUTHOR("LightRail AI");
MODULE_DESCRIPTION("LightOS Core Kernel Module");
MODULE_VERSION("0.1.0");

static dev_t lightos_dev;
static struct cdev lightos_cdev;
static struct class *lightos_class;

static long lightos_ioctl(struct file *file, unsigned int cmd, unsigned long arg)
{
    return 0;
}

static struct file_operations lightos_fops = {
    .owner = THIS_MODULE,
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
