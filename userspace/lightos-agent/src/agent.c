#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include "../include/agent.h"

static volatile int running = 1;

static void signal_handler(int sig)
{
    running = 0;
}

int agent_init(const struct agent_config *config)
{
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    printf("LightOS Agent v0.1.0 initialized\n");
    printf("Fabric OS: %s:%d\n", config->fabric_os_endpoint, config->fabric_os_port);
    return 0;
}

void agent_run(void)
{
    printf("Agent running... Press Ctrl+C to stop\n");
    while (running) {
        sleep(1);
    }
}

void agent_cleanup(void)
{
    printf("Agent shutting down\n");
}

int main(int argc, char *argv[])
{
    struct agent_config config = {
        .fabric_os_endpoint = "localhost",
        .fabric_os_port = 50051,
        .telemetry_interval_ms = 1000,
    };
    
    agent_init(&config);
    agent_run();
    agent_cleanup();
    
    return 0;
}
