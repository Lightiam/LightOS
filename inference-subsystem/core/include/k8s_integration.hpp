/**
 * LightOS Inference Subsystem - Kubernetes Integration
 *
 * Module 4: Kubernetes & Deployment Integration
 *
 * Components:
 * - lightos-agent: DaemonSet for node-level management
 * - gRPC Control Plane: Communication with Fabric OS
 * - eBPF Interception: Redirect PyTorch/JAX calls to LightAccelerator
 *
 * Deployment Model:
 * - Each K8s node runs one lightos-agent pod
 * - Agent manages all GPUs/NPUs on that node
 * - Exposes gRPC for centralized orchestration
 * - eBPF hooks intercept CUDA calls transparently
 *
 * @file k8s_integration.hpp
 * @author LightRail AI - Principal Kernel Architect
 * @version 1.0.0
 */

#pragma once

#include "light_accelerator.hpp"
#include "power_governor.hpp"
#include "tile_engine.hpp"
#include <grpcpp/grpcpp.h>
#include <memory>
#include <thread>

namespace lightos::inference {

// ============================================================================
// gRPC Service Definition (Control Plane Interface)
// ============================================================================

namespace proto {

// Simplified proto definitions (actual .proto file required)
struct DeviceInfo {
    std::string device_id;
    std::string type;
    std::string name;
    std::uint64_t memory_total;
    std::uint64_t memory_available;
    float temperature;
    float power_draw;
    float utilization;
};

struct JobRequest {
    std::string job_id;
    std::string model_name;
    std::uint32_t batch_size;
    std::uint32_t sequence_length;
    std::string precision;
    std::vector<std::uint8_t> input_data;
};

struct JobResponse {
    std::string job_id;
    std::string status;
    std::vector<std::uint8_t> output_data;
    float latency_ms;
    std::string error_message;
};

struct TelemetryReport {
    std::string node_id;
    std::vector<DeviceInfo> devices;
    float total_power_watts;
    float avg_temperature;
    std::uint64_t total_jobs_completed;
    std::chrono::system_clock::time_point timestamp;
};

struct PowerControlRequest {
    std::string device_id;
    float power_limit_watts;
    std::uint32_t clock_frequency_mhz;
};

} // namespace proto

// ============================================================================
// LightOS Agent gRPC Service
// ============================================================================

class LightOSAgentService {
public:
    LightOSAgentService(PowerGovernor& governor);

    // Device Management
    grpc::Status ListDevices(
        grpc::ServerContext* context,
        const google::protobuf::Empty* request,
        proto::DeviceListResponse* response
    );

    grpc::Status GetDeviceInfo(
        grpc::ServerContext* context,
        const proto::DeviceInfoRequest* request,
        proto::DeviceInfo* response
    );

    // Job Submission
    grpc::Status SubmitJob(
        grpc::ServerContext* context,
        const proto::JobRequest* request,
        proto::JobResponse* response
    );

    grpc::Status GetJobStatus(
        grpc::ServerContext* context,
        const proto::JobStatusRequest* request,
        proto::JobResponse* response
    );

    // Telemetry Streaming
    grpc::Status StreamTelemetry(
        grpc::ServerContext* context,
        const google::protobuf::Empty* request,
        grpc::ServerWriter<proto::TelemetryReport>* writer
    );

    // Power Control
    grpc::Status SetPowerLimit(
        grpc::ServerContext* context,
        const proto::PowerControlRequest* request,
        google::protobuf::Empty* response
    );

    grpc::Status SetClockFrequency(
        grpc::ServerContext* context,
        const proto::PowerControlRequest* request,
        google::protobuf::Empty* response
    );

    // Health Check
    grpc::Status HealthCheck(
        grpc::ServerContext* context,
        const google::protobuf::Empty* request,
        proto::HealthResponse* response
    );

private:
    PowerGovernor& governor_;
    std::string node_id_;
};

// ============================================================================
// LightOS Agent Daemon
// ============================================================================

class LightOSAgent {
public:
    struct Config {
        std::string grpc_address = "0.0.0.0:50051";
        std::string fabric_os_endpoint = "fabric-os-service:50052";
        std::string node_id;
        std::chrono::seconds telemetry_interval{5};
        std::chrono::seconds heartbeat_interval{10};

        // eBPF configuration
        bool enable_ebpf_interception = true;
        std::vector<std::string> intercept_libraries = {
            "libcuda.so",
            "libcudart.so",
            "libtorch_cuda.so",
            "libjax.so"
        };

        // Device discovery
        bool auto_discover_devices = true;
        std::vector<DeviceType> supported_device_types = {
            DeviceType::NVIDIA_GPU,
            DeviceType::AMD_GPU,
            DeviceType::PHOTONIC_NPU
        };
    };

    explicit LightOSAgent(const Config& config);
    ~LightOSAgent();

    // Start the agent
    void start();

    // Stop the agent
    void stop();

    // Wait for shutdown signal
    void wait_for_shutdown();

private:
    void discover_devices();
    void start_grpc_server();
    void start_telemetry_reporter();
    void start_heartbeat();
    void setup_ebpf_hooks();

    Config config_;
    std::unique_ptr<PowerGovernor> governor_;
    std::unique_ptr<grpc::Server> grpc_server_;
    std::unique_ptr<LightOSAgentService> service_;

    std::atomic<bool> running_{false};
    std::vector<std::thread> threads_;
};

// ============================================================================
// eBPF Interception Layer
// ============================================================================

class eBPFInterceptor {
public:
    eBPFInterceptor(PowerGovernor& governor);
    ~eBPFInterceptor();

    // Load eBPF programs
    Result<void> load();

    // Attach eBPF hooks to target libraries
    Result<void> attach(const std::vector<std::string>& libraries);

    // Detach all hooks
    void detach();

    // Intercept CUDA Runtime API calls
    // Examples:
    // - cudaMalloc()        → LightAccelerator::allocate()
    // - cudaMemcpy()        → LightAccelerator::copy_h2d()
    // - cudaLaunchKernel()  → LightAccelerator::launch_kernel()

    struct InterceptStats {
        std::uint64_t total_intercepts;
        std::uint64_t malloc_calls;
        std::uint64_t memcpy_calls;
        std::uint64_t kernel_launches;
        std::uint64_t redirected_to_lightos;
    };

    InterceptStats get_stats() const;

private:
    PowerGovernor& governor_;
    int ebpf_fd_ = -1;
    std::vector<int> attached_hooks_;
    InterceptStats stats_{};
};

// ============================================================================
// Kubernetes DaemonSet Deployment Manifest
// ============================================================================

constexpr std::string_view DAEMONSET_YAML = R"yaml(
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: lightos-agent
  namespace: lightos-system
  labels:
    app: lightos-agent
spec:
  selector:
    matchLabels:
      app: lightos-agent
  template:
    metadata:
      labels:
        app: lightos-agent
    spec:
      hostNetwork: true
      hostPID: true
      containers:
      - name: lightos-agent
        image: lightrail/lightos-agent:v1.0.0
        imagePullPolicy: Always
        securityContext:
          privileged: true  # Required for eBPF and GPU access
          capabilities:
            add:
            - SYS_ADMIN   # eBPF loading
            - SYS_PTRACE  # Process tracing
            - NET_ADMIN   # Network hooks
        env:
        - name: NODE_NAME
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
        - name: GRPC_ADDRESS
          value: "0.0.0.0:50051"
        - name: FABRIC_OS_ENDPOINT
          value: "fabric-os-service.lightos-system.svc.cluster.local:50052"
        - name: ENABLE_EBPF
          value: "true"
        volumeMounts:
        - name: dev
          mountPath: /dev
        - name: sys
          mountPath: /sys
        - name: modules
          mountPath: /lib/modules
          readOnly: true
        - name: bpf
          mountPath: /sys/fs/bpf
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
            nvidia.com/gpu: "8"  # Manage up to 8 GPUs per node
      volumes:
      - name: dev
        hostPath:
          path: /dev
      - name: sys
        hostPath:
          path: /sys
      - name: modules
        hostPath:
          path: /lib/modules
      - name: bpf
        hostPath:
          path: /sys/fs/bpf
          type: DirectoryOrCreate
      tolerations:
      - key: nvidia.com/gpu
        operator: Exists
        effect: NoSchedule
)yaml";

// ============================================================================
// Fabric OS Integration (Centralized Control Plane)
// ============================================================================

class FabricOSClient {
public:
    FabricOSClient(std::string_view endpoint);

    // Register node with Fabric OS
    Result<void> register_node(
        const std::string& node_id,
        const std::vector<DeviceProperties>& devices
    );

    // Send periodic heartbeat
    Result<void> send_heartbeat(
        const std::string& node_id,
        const proto::TelemetryReport& telemetry
    );

    // Receive job assignments
    Result<proto::JobRequest> receive_job();

    // Report job completion
    Result<void> report_job_completion(
        const std::string& job_id,
        const proto::JobResponse& response
    );

    // Receive power control commands
    Result<proto::PowerControlRequest> receive_power_control();

private:
    std::unique_ptr<grpc::Channel> channel_;
    std::unique_ptr<grpc::ClientContext> context_;
};

// ============================================================================
// Container Image Build (Dockerfile)
// ============================================================================

constexpr std::string_view DOCKERFILE = R"dockerfile(
FROM nvidia/cuda:12.3.0-devel-ubuntu22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    libbpf-dev \
    clang \
    llvm \
    libelf-dev \
    linux-headers-$(uname -r) \
    libprotobuf-dev \
    protobuf-compiler \
    libgrpc++-dev \
    && rm -rf /var/lib/apt/lists/*

# Build LightOS Agent
WORKDIR /app
COPY . .
RUN mkdir build && cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release .. && \
    make -j$(nproc) && \
    make install

# eBPF programs
COPY ebpf/*.o /opt/lightos/ebpf/

# Configuration
COPY config/agent.yaml /etc/lightos/agent.yaml

EXPOSE 50051

ENTRYPOINT ["/usr/local/bin/lightos-agent"]
CMD ["--config", "/etc/lightos/agent.yaml"]
)dockerfile";

// ============================================================================
// Helm Chart (values.yaml)
// ============================================================================

constexpr std::string_view HELM_VALUES = R"yaml(
image:
  repository: lightrail/lightos-agent
  tag: v1.0.0
  pullPolicy: Always

resources:
  requests:
    memory: 512Mi
    cpu: 500m
  limits:
    memory: 2Gi
    cpu: 2

grpc:
  port: 50051

fabricOS:
  endpoint: fabric-os-service.lightos-system.svc.cluster.local:50052

telemetry:
  interval: 5s
  enablePrometheus: true
  prometheusPort: 9090

ebpf:
  enabled: true
  interceptLibraries:
    - libcuda.so
    - libcudart.so
    - libtorch_cuda.so

powerManagement:
  enabled: true
  defaultPowerLimit: 700  # watts
  thermalThreshold: 85    # celsius

tolerations:
  - key: nvidia.com/gpu
    operator: Exists
    effect: NoSchedule

nodeSelector:
  accelerator: nvidia-gpu
)yaml";

// ============================================================================
// Installation Script
// ============================================================================

constexpr std::string_view INSTALL_SCRIPT = R"bash(
#!/bin/bash
set -e

echo "Installing LightOS Agent on Kubernetes cluster..."

# Create namespace
kubectl create namespace lightos-system --dry-run=client -o yaml | kubectl apply -f -

# Install dependencies
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/main/nvidia-device-plugin.yml

# Deploy LightOS Agent DaemonSet
kubectl apply -f - <<EOF
$(cat daemonset.yaml)
EOF

# Deploy Fabric OS Control Plane
kubectl apply -f fabric-os-deployment.yaml

# Deploy Monitoring Stack (Prometheus + Grafana)
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace lightos-system \
  --set grafana.enabled=true

# Wait for rollout
kubectl rollout status daemonset/lightos-agent -n lightos-system --timeout=300s

echo "✅ LightOS Agent installed successfully!"
echo ""
echo "Check status:"
echo "  kubectl get pods -n lightos-system -l app=lightos-agent"
echo ""
echo "View logs:"
echo "  kubectl logs -n lightos-system -l app=lightos-agent --tail=100 -f"
echo ""
echo "Access Grafana:"
echo "  kubectl port-forward -n lightos-system svc/prometheus-grafana 3000:80"
)bash";

// ============================================================================
// Example: Agent Implementation
// ============================================================================

inline LightOSAgent::LightOSAgent(const Config& config)
    : config_(config) {

    // Initialize PowerGovernor
    PowerGovernor::Config gov_config;
    gov_config.policy = SchedulingPolicy::PREDICTIVE_COOLING;
    governor_ = std::make_unique<PowerGovernor>(gov_config);

    // Set node ID from environment or config
    if (config_.node_id.empty()) {
        const char* node_name = std::getenv("NODE_NAME");
        config_.node_id = node_name ? node_name : "unknown";
    }
}

inline void LightOSAgent::start() {
    running_.store(true);

    // 1. Discover devices
    discover_devices();

    // 2. Setup eBPF hooks (if enabled)
    if (config_.enable_ebpf_interception) {
        setup_ebpf_hooks();
    }

    // 3. Start gRPC server
    start_grpc_server();

    // 4. Start telemetry reporter
    start_telemetry_reporter();

    // 5. Start heartbeat to Fabric OS
    start_heartbeat();

    // 6. Start PowerGovernor scheduler
    governor_->start_scheduler();
}

inline void LightOSAgent::discover_devices() {
    auto devices_result = enumerate_devices();
    if (!devices_result) {
        throw std::runtime_error("Failed to enumerate devices");
    }

    for (const auto& props : *devices_result) {
        // Create device instance
        auto device = LightAccelerator::create(props.type, 0);
        if (device) {
            governor_->register_device(std::move(*device));
        }
    }
}

inline void LightOSAgent::start_grpc_server() {
    grpc::ServerBuilder builder;
    builder.AddListeningPort(config_.grpc_address, grpc::InsecureServerCredentials());

    service_ = std::make_unique<LightOSAgentService>(*governor_);
    builder.RegisterService(service_.get());

    grpc_server_ = builder.BuildAndStart();
}

} // namespace lightos::inference
