/* LightOS Unified Runtime (LOUR)
 * Platform-agnostic API for AI accelerators
 * Works with CUDA, ROCm, OpenCL, oneAPI, Metal
 */

#ifndef LIGHTOS_RUNTIME_H
#define LIGHTOS_RUNTIME_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Device Types */
typedef enum {
    LIGHTOS_DEVICE_ANY = 0,      /* Auto-select best device */
    LIGHTOS_DEVICE_CUDA = 1,     /* NVIDIA GPU via CUDA */
    LIGHTOS_DEVICE_ROCM = 2,     /* AMD GPU via ROCm */
    LIGHTOS_DEVICE_OPENCL = 3,   /* Generic via OpenCL */
    LIGHTOS_DEVICE_ONEAPI = 4,   /* Intel XPU via oneAPI */
    LIGHTOS_DEVICE_METAL = 5,    /* Apple Silicon via Metal */
    LIGHTOS_DEVICE_PHOTONIC = 6, /* Future photonic NPU */
} lightos_device_type_t;

/* Data Types */
typedef enum {
    LIGHTOS_DTYPE_FLOAT16 = 0,
    LIGHTOS_DTYPE_FLOAT32 = 1,
    LIGHTOS_DTYPE_FLOAT64 = 2,
    LIGHTOS_DTYPE_INT8 = 3,
    LIGHTOS_DTYPE_INT32 = 4,
} lightos_dtype_t;

/* Collective Operations */
typedef enum {
    LIGHTOS_OP_SUM = 0,
    LIGHTOS_OP_MAX = 1,
    LIGHTOS_OP_MIN = 2,
} lightos_op_t;

/* Opaque Handles */
typedef struct lightos_context_impl* lightos_context_t;
typedef struct lightos_buffer_impl* lightos_buffer_t;
typedef struct lightos_kernel_impl* lightos_kernel_t;

/* Context Management */
lightos_context_t lightos_create_context(lightos_device_type_t type);
void lightos_destroy_context(lightos_context_t ctx);

/* Memory Management */
lightos_buffer_t lightos_alloc(lightos_context_t ctx, size_t size);
void lightos_free(lightos_buffer_t buf);

/* Kernel Execution */
lightos_kernel_t lightos_create_kernel(lightos_context_t ctx, 
                                       const char *source,
                                       const char *name);
int lightos_execute(lightos_kernel_t kernel,
                    size_t global_size[3],
                    size_t local_size[3]);

/* Collective Operations */
int lightos_allreduce(const void *sendbuf, void *recvbuf,
                      size_t count, lightos_dtype_t dtype,
                      lightos_op_t op, void *comm);

#ifdef __cplusplus
}
#endif

#endif /* LIGHTOS_RUNTIME_H */
