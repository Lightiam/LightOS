/* LightOS Unified Runtime - Platform-agnostic API */
#ifndef LIGHTOS_RUNTIME_H
#define LIGHTOS_RUNTIME_H

typedef enum {
    LIGHTOS_DEVICE_ANY = 0,
    LIGHTOS_DEVICE_CUDA = 1,
    LIGHTOS_DEVICE_ROCM = 2,
    LIGHTOS_DEVICE_OPENCL = 3,
} lightos_device_type_t;

typedef struct lightos_context_impl* lightos_context_t;

lightos_context_t lightos_create_context(lightos_device_type_t type);
void lightos_destroy_context(lightos_context_t ctx);

#endif
