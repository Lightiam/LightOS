# LightOS Cloud Deployment Guide

## Overview

This guide covers deploying LightOS on cloud GPU/TPU clusters for immediate performance improvements on AI workloads.

## Supported Platforms

- **AWS**: EC2 P4d/P5 instances with NVIDIA A100/H100 GPUs
- **GCP**: Compute Engine with NVIDIA A100/L4 GPUs or Cloud TPU v4/v5
- **Azure**: NDv4/NC series with NVIDIA A100/H100 GPUs

## Prerequisites

- Root/sudo access on target instances
- Linux kernel headers installed
- GCC and make toolchain
- Active GPU/TPU instances

## Quick Deploy

### 1. Build LightOS

```bash
git clone https://github.com/your-org/lightos.git
cd lightos
make all
```

### 2. Install on Single Node

```bash
sudo make install
sudo modprobe lightos_core
sudo lightos-agent &
```

### 3. Verify Installation

```bash
# Check kernel module loaded
lsmod | grep lightos_core

# Check device file created
ls -l /dev/lightos

# Check agent running
ps aux | grep lightos-agent
```

## Multi-Node Cluster Deployment

### Using Kubernetes/Helm (Recommended)

```bash
# Deploy LightOS DaemonSet across cluster
kubectl apply -f packaging/k8s/lightos-daemonset.yaml

# Verify pods running on all GPU nodes
kubectl get pods -n lightos-system -o wide
```

### Using Ansible

```bash
# Deploy to all nodes in inventory
ansible-playbook -i inventory.ini deploy-lightos.yml
```

## Configuration

### Agent Configuration

Edit `/etc/lightos/agent.conf`:

```ini
[fabric-os]
endpoint = fabric-os.your-cluster.internal
port = 50051

[telemetry]
interval_ms = 1000
metrics_enabled = true
```

### Environment Variables

```bash
export LIGHTOS_FABRIC_ENDPOINT="fabric-os.example.com:50051"
export LIGHTOS_TELEMETRY_INTERVAL=1000
```

## Performance Tuning

### GPU Clusters

```bash
# Enable aggressive power management
echo "performance" | sudo tee /sys/class/lightos/power_mode

# Optimize for large batch training
echo "256" | sudo tee /sys/class/lightos/batch_size_hint
```

### TPU Clusters (GCP)

```bash
# Configure for TPU pod slices
lightos-agent --device-type tpu --pod-slice 2x2x1
```

## Monitoring

### View Live Metrics

```bash
# Stream telemetry
lightos-agent --telemetry-stdout

# Check device state via ioctl
lightos-cli device-state --device-id 0
```

### Integration with Prometheus

```yaml
# Add to prometheus.yml
scrape_configs:
  - job_name: 'lightos'
    static_configs:
      - targets: ['localhost:9090']
```

## Troubleshooting

### Module Won't Load

```bash
# Check kernel compatibility
uname -r
ls /lib/modules/$(uname -r)/build

# Rebuild for current kernel
cd kernel/modules/lightos-core
make clean && make
```

### Agent Can't Connect to Fabric OS

```bash
# Check network connectivity
ping fabric-os.your-cluster.internal
telnet fabric-os.your-cluster.internal 50051

# Check firewall rules
sudo iptables -L | grep 50051
```

### Low Performance Gains

```bash
# Verify module is loaded and active
cat /proc/modules | grep lightos

# Check if workload is using collectives library
ldd /path/to/training/binary | grep liblightos-collectives

# Enable debug logging
echo 8 | sudo tee /proc/sys/kernel/printk
dmesg | grep -i lightos
```

## Cloud-Specific Notes

### AWS

- Use placement groups for multi-node training
- Enable EFA (Elastic Fabric Adapter) for best network performance
- LightOS automatically detects and optimizes for EFA

### GCP

- For TPU pods, use internal TCP load balancer for Fabric OS
- Enable VPC peering between regions if needed
- LightOS integrates with Cloud Monitoring for metrics

### Azure

- Use InfiniBand-enabled VM sizes (NDv4)
- Configure accelerated networking
- LightOS works with Azure Monitor integration

## Uninstall

```bash
# Stop agent
sudo pkill lightos-agent

# Unload module
sudo rmmod lightos_core

# Remove files
sudo rm /usr/local/bin/lightos-agent
sudo rm /usr/local/lib/liblightos-collectives.so*
sudo rm -r /etc/lightos/
```

## Support

- GitHub Issues: https://github.com/your-org/lightos/issues
- Documentation: https://docs.lightos.ai
- Community: https://discord.gg/lightos

## Version

This guide is for LightOS v0.1.0
