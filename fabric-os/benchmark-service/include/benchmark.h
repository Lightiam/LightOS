#ifndef LIGHTOS_BENCHMARK_H
#define LIGHTOS_BENCHMARK_H

struct benchmark_record {
    char id[256];
    char provider[64];
    char model[128];
    float throughput_tokens_per_s;
    float latency_ms;
};

struct benchmark_record* benchmark_create(void);
void benchmark_free(struct benchmark_record *rec);
char* benchmark_to_json(const struct benchmark_record *rec);

#endif
