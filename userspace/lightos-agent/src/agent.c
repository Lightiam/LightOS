#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <string.h>
#include <errno.h>
#include <time.h>
#include "../include/agent.h"

#define LIGHTOS_DEVICE "/dev/lightos"
#define LIGHTOS_IOC_MAGIC 'L'

struct lightos_device_state {
    uint32_t device_id;
    uint32_t device_type;
    uint32_t utilization_percent;
    uint32_t power_watts;
    uint64_t memory_used_bytes;
    uint64_t memory_total_bytes;
};

#define LIGHTOS_IOC_GET_DEVICE_STATE _IOWR(LIGHTOS_IOC_MAGIC, 1, struct lightos_device_state)

static volatile int running = 1;
static int lightos_fd = -1;

static void signal_handler(int sig)
{
    (void)sig; /* Unused parameter */
    running = 0;
}

static int collect_telemetry(void)
{
    struct lightos_device_state state;
    int ret;

    if (lightos_fd < 0) {
        fprintf(stderr, "Device not opened\n");
        return -1;
    }

    ret = ioctl(lightos_fd, LIGHTOS_IOC_GET_DEVICE_STATE, &state);
    if (ret < 0) {
        fprintf(stderr, "Failed to get device state: %s\n", strerror(errno));
        return -1;
    }

    /* Log telemetry data */
    time_t now = time(NULL);
    printf("[%s] Device %u: Type=%u, Util=%u%%, Power=%uW, Mem=%lu/%lu MB\n",
           ctime(&now),
           state.device_id,
           state.device_type,
           state.utilization_percent,
           state.power_watts,
           state.memory_used_bytes / (1024 * 1024),
           state.memory_total_bytes / (1024 * 1024));

    return 0;
}

int agent_init(const struct agent_config *config)
{
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);

    printf("LightOS Agent v0.1.0 initialized\n");
    printf("Fabric OS: %s:%d\n", config->fabric_os_endpoint, config->fabric_os_port);
    printf("Telemetry interval: %u ms\n", config->telemetry_interval_ms);

    /* Open LightOS device */
    lightos_fd = open(LIGHTOS_DEVICE, O_RDWR);
    if (lightos_fd < 0) {
        fprintf(stderr, "Warning: Failed to open %s: %s\n",
                LIGHTOS_DEVICE, strerror(errno));
        fprintf(stderr, "Continuing without device telemetry...\n");
    } else {
        printf("Connected to %s\n", LIGHTOS_DEVICE);
    }

    return 0;
}

void agent_run(void)
{
    printf("Agent running... Press Ctrl+C to stop\n");

    while (running) {
        /* Collect and report telemetry */
        if (lightos_fd >= 0) {
            collect_telemetry();
        }

        sleep(1);
    }
}

void agent_cleanup(void)
{
    printf("Agent shutting down\n");

    if (lightos_fd >= 0) {
        close(lightos_fd);
        lightos_fd = -1;
    }
}

static void print_usage(const char *progname)
{
    printf("Usage: %s [OPTIONS]\n", progname);
    printf("\nOptions:\n");
    printf("  -e, --endpoint <host>    Fabric OS endpoint (default: localhost)\n");
    printf("  -p, --port <port>        Fabric OS port (default: 50051)\n");
    printf("  -i, --interval <ms>      Telemetry interval in ms (default: 1000)\n");
    printf("  -h, --help               Show this help message\n");
    printf("\nExample:\n");
    printf("  %s -e fabric-os.example.com -p 50051 -i 500\n", progname);
}

int main(int argc, char *argv[])
{
    struct agent_config config = {
        .fabric_os_endpoint = "localhost",
        .fabric_os_port = 50051,
        .telemetry_interval_ms = 1000,
    };

    /* Parse command-line arguments */
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-h") == 0 || strcmp(argv[i], "--help") == 0) {
            print_usage(argv[0]);
            return 0;
        } else if (strcmp(argv[i], "-e") == 0 || strcmp(argv[i], "--endpoint") == 0) {
            if (i + 1 >= argc) {
                fprintf(stderr, "Error: %s requires an argument\n", argv[i]);
                print_usage(argv[0]);
                return 1;
            }
            strncpy(config.fabric_os_endpoint, argv[++i],
                    sizeof(config.fabric_os_endpoint) - 1);
            config.fabric_os_endpoint[sizeof(config.fabric_os_endpoint) - 1] = '\0';
        } else if (strcmp(argv[i], "-p") == 0 || strcmp(argv[i], "--port") == 0) {
            if (i + 1 >= argc) {
                fprintf(stderr, "Error: %s requires an argument\n", argv[i]);
                print_usage(argv[0]);
                return 1;
            }
            config.fabric_os_port = (uint16_t)atoi(argv[++i]);
        } else if (strcmp(argv[i], "-i") == 0 || strcmp(argv[i], "--interval") == 0) {
            if (i + 1 >= argc) {
                fprintf(stderr, "Error: %s requires an argument\n", argv[i]);
                print_usage(argv[0]);
                return 1;
            }
            config.telemetry_interval_ms = (uint32_t)atoi(argv[++i]);
        } else {
            fprintf(stderr, "Error: Unknown option '%s'\n", argv[i]);
            print_usage(argv[0]);
            return 1;
        }
    }

    agent_init(&config);
    agent_run();
    agent_cleanup();

    return 0;
}
