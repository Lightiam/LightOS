#include "../include/benchmark.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct benchmark_record* benchmark_create(void)
{
    struct benchmark_record *rec = calloc(1, sizeof(*rec));
    return rec;
}

void benchmark_free(struct benchmark_record *rec)
{
    free(rec);
}

char* benchmark_to_json(const struct benchmark_record *rec)
{
    char *json = malloc(1024);
    snprintf(json, 1024,
        "{\n"
        "  \"id\": \"%s\",\n"
        "  \"provider\": \"%s\",\n"
        "  \"model\": \"%s\",\n"
        "  \"metrics\": {\n"
        "    \"throughput_tokens_per_s\": %.2f,\n"
        "    \"latency_ms\": %.2f\n"
        "  }\n"
        "}",
        rec->id, rec->provider, rec->model,
        rec->throughput_tokens_per_s, rec->latency_ms);
    return json;
}
