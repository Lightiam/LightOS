#include "../include/benchmark.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct benchmark_record* benchmark_create(void)
{
    struct benchmark_record *rec = calloc(1, sizeof(*rec));
    if (rec == NULL) {
        fprintf(stderr, "Failed to allocate memory for benchmark record\n");
    }
    return rec;
}

void benchmark_free(struct benchmark_record *rec)
{
    free(rec);
}

char* benchmark_to_json(const struct benchmark_record *rec)
{
    /* Calculate required buffer size:
     * - Fixed JSON structure: ~150 bytes
     * - id field: up to 256 bytes
     * - provider field: up to 64 bytes
     * - model field: up to 128 bytes
     * - Float values: ~40 bytes total
     * Total with safety margin: 650 bytes
     */
    const size_t buffer_size = 650;
    char *json;
    int written;

    if (rec == NULL) {
        return NULL;
    }

    json = malloc(buffer_size);
    if (json == NULL) {
        fprintf(stderr, "Failed to allocate memory for JSON output\n");
        return NULL;
    }

    written = snprintf(json, buffer_size,
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

    /* Check if output was truncated */
    if (written < 0 || (size_t)written >= buffer_size) {
        fprintf(stderr, "Warning: JSON output may have been truncated\n");
    }

    return json;
}
