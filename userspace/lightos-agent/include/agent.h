#ifndef LIGHTOS_AGENT_H
#define LIGHTOS_AGENT_H

#include <stdint.h>

struct agent_config {
    char fabric_os_endpoint[256];
    uint16_t fabric_os_port;
    uint32_t telemetry_interval_ms;
};

int agent_init(const struct agent_config *config);
void agent_run(void);
void agent_cleanup(void);

#endif
