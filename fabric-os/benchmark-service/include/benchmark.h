#ifndef LIGHTOS_BENCHMARK_H
#define LIGHTOS_BENCHMARK_H

struct benchmark_record {
    char id[256];
    char provider[64];
    char model[128];
    float throughput_tokens_per_s;
    float latency_ms;
};

/**
 * benchmark_create - Allocate a new benchmark record
 *
 * Returns: Pointer to allocated record, or NULL on failure
 * Caller must free with benchmark_free()
 */
struct benchmark_record* benchmark_create(void);

/**
 * benchmark_free - Free a benchmark record
 * @rec: Record to free
 */
void benchmark_free(struct benchmark_record *rec);

/**
 * benchmark_to_json - Convert record to JSON string
 * @rec: Record to convert
 *
 * Returns: Dynamically allocated JSON string, or NULL on failure
 * Caller must free() the returned string
 */
char* benchmark_to_json(const struct benchmark_record *rec);

#endif
