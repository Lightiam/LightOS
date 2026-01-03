#include "../include/lightos_collectives.h"
#include <stdio.h>
#include <string.h>

int lightos_allreduce(const void *sendbuf, void *recvbuf, size_t count,
                      lightos_dtype_t dtype, lightos_op_t op, void *comm)
{
    printf("LightOS Allreduce: count=%zu\n", count);
    if (sendbuf != recvbuf) {
        size_t size = count * sizeof(float);
        memcpy(recvbuf, sendbuf, size);
    }
    return 0;
}
