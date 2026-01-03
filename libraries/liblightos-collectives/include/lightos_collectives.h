#ifndef LIGHTOS_COLLECTIVES_H
#define LIGHTOS_COLLECTIVES_H

#include <stddef.h>

typedef enum {
    LIGHTOS_DTYPE_FLOAT32 = 0,
    LIGHTOS_DTYPE_FLOAT64 = 1,
    LIGHTOS_DTYPE_INT32 = 2,
} lightos_dtype_t;

typedef enum {
    LIGHTOS_OP_SUM = 0,
    LIGHTOS_OP_MAX = 1,
    LIGHTOS_OP_MIN = 2,
} lightos_op_t;

int lightos_allreduce(const void *sendbuf, void *recvbuf, size_t count,
                      lightos_dtype_t dtype, lightos_op_t op, void *comm);

#endif
