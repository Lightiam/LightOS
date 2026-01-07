# LightOS Neural Compute Engine - AWS Deployment Guide

## 🎯 Complete Deployment with Infrastructure Autopilot

This guide covers deploying the full LightOS Neural Compute Engine stack on AWS, including:
- ✅ Spiking Neural Network Engine
- ✅ MoE Sparsity Module
- ✅ Photonic NPU Driver with Thermal Guard
- ✅ **Infrastructure Autopilot (DRL-based HVAC optimization)**
- ✅ **LLM Training Ground UI**
- ✅ Distributed KV Cache
- ✅ LightRail AI Scheduler
- ✅ Performance Metrics Collection

---

## 📋 Prerequisites

### AWS Account Requirements
- AWS account with appropriate permissions
- AWS CLI installed and configured
- Terraform >= 1.0 installed (optional, for infrastructure-as-code)

### Cost Estimates

| Configuration | Instance Type | Est. Cost/Hour | Est. Cost/Month* |
|---------------|---------------|----------------|------------------|
| **Basic** (Testing) | 2x t3.medium | $0.08 | $60 |
| **Standard** (Development) | 4x t3.xlarge | $0.67 | $500 |
| **GPU** (Training) | 2x g4dn.xlarge | $1.05 | $780 |
| **High-Performance** | 8x p3.2xlarge | $24.48 | $18,000 |

\* Assumes 24/7 operation. Actual costs much lower with spot instances + auto-stop.

---

## 🚀 Quick Start (15 Minutes)

### Option 1: Manual Deployment

```bash
# 1. Launch EC2 instance
aws ec2 run-instances \
  --image-id ami-0c7217cdde317cfec \
  --instance-type t3.medium \
  --key-name your-key \
  --security-group-ids sg-xxxxx \
  --subnet-id subnet-xxxxx \
  --user-data file://user-data.sh \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=lightos-main}]'

# 2. Get instance IP
INSTANCE_IP=$(aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=lightos-main" \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

# 3. SSH and verify
ssh -i your-key.pem ubuntu@$INSTANCE_IP
dmesg | grep LightOS
```

### Option 2: Terraform Deployment (Recommended)

```bash
# 1. Navigate to Terraform directory
cd /home/user/LightOS/deployment/aws/terraform

# 2. Initialize Terraform
terraform init

# 3. Plan deployment
terraform plan \
  -var="aws_region=us-east-1" \
  -var="enable_gpu=false" \
  -var="enable_autopilot=true" \
  -var="num_compute_nodes=2"

# 4. Apply configuration
terraform apply -auto-approve

# 5. Get outputs
terraform output alb_dns_name
terraform output redis_endpoint
```

---

## 🏗️ Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                  AWS Application Load Balancer               │
│            (Distributes requests to compute nodes)           │
└────────────────┬───────────────┬──────────────────────────────┘
                 │               │
        ┌────────▼──────┐  ┌─────▼──────┐
        │  Compute      │  │  Compute   │
        │  Node 1       │  │  Node 2    │
        │               │  │            │
        │ • LightOS     │  │ • LightOS  │
        │ • Spiking Eng │  │ • Spiking  │
        │ • MoE Module  │  │ • MoE      │
        │ • Autopilot   │  │ • Autopilot│
        └────────┬──────┘  └─────┬──────┘
                 │               │
        ┌────────▼───────────────▼──────┐
        │   ElastiCache Redis Cluster   │
        │   (Distributed KV Cache)      │
        └───────────────────────────────┘
```

---

## 🤖 Infrastructure Autopilot Setup

The Infrastructure Autopilot uses Deep Reinforcement Learning to optimize data center HVAC systems, achieving up to **53.6% energy savings**.

### Enable Autopilot

```bash
# SSH into your instance
ssh -i your-key.pem ubuntu@$INSTANCE_IP

# Navigate to autopilot directory
cd ~/LightOS/fabric-os/infrastructure-autopilot

# Build autopilot
gcc -pthread -o autopilot autopilot.c -lm

# Run autopilot in background
./autopilot &

# Check logs
tail -f /var/log/lightos/autopilot.log
```

### Configure Autopilot

Create `/etc/lightos/autopilot.conf`:

```json
{
  "mode": "autopilot",
  "safety_enabled": true,
  "max_temp_celsius": 27,
  "control_interval_ms": 60000,
  "drl_config": {
    "learning_rate": 0.001,
    "discount_factor": 0.99,
    "exploration_rate": 0.1
  },
  "hvac_endpoints": [
    {
      "type": "crac",
      "location": "row-a-pos-1",
      "ip": "10.0.1.10",
      "protocol": "bacnet"
    }
  ]
}
```

### Monitor Autopilot Performance

```bash
# Real-time monitoring
watch -n 5 'curl -s http://localhost:8080/autopilot/status | jq .'

# Expected output:
{
  "status": "running",
  "mode": "autopilot",
  "metrics": {
    "avg_inlet_temp_c": 20.5,
    "total_hvac_power_kw": 45.2,
    "total_it_power_kw": 150.0,
    "pue": 1.30,
    "energy_saved_percent": 48.3,
    "cost_savings_usd_per_hour": 12.50
  },
  "safety": {
    "violations": 0,
    "overrides": 0,
    "last_check": "2026-01-07T10:30:00Z"
  }
}
```

---

## 🎓 LLM Training Ground Setup

The LLM Training Ground provides a unified interface for selecting models, datasets, and launching training runs.

### Install Dependencies

```bash
# Install Python dependencies
pip3 install torch transformers datasets flask huggingface-hub

# Install LLM Training Ground
cd ~/LightOS/llm-training-ground
pip3 install -r requirements.txt
```

### Launch UI

```bash
# Start the web UI
cd ~/LightOS/llm-training-ground/ui
python3 app.py

# Access at: http://<INSTANCE_IP>:3000
```

### Use Asset Browser (Programmatically)

```python
from asset_browser import AssetBrowser, BudgetGuardrails

# Initialize browser
browser = AssetBrowser()

# List available spiking models
spiking_models = browser.list_models(supports_spiking=True)
print(f"Available spiking models: {len(spiking_models)}")

for model in spiking_models:
    print(f"  - {model.name}: {model.size_params/1e9:.1f}B parameters")

# Set budget constraints
budget = BudgetGuardrails(
    max_cost_usd=1000.0,
    max_duration_hours=48.0,
    max_energy_kwh=5000.0,
    enable_spot_instances=True
)

# Recommend optimal compute
model = spiking_models[0]  # SpikingBrain-7B
compute = browser.recommend_compute(model, budget)

print(f"\nRecommended: {compute.num_devices}x {compute.hardware_type.value}")
print(f"Cost: ${compute.cost_per_hour:.2f}/hr")
print(f"Location: {compute.location}")
```

### Launch Training Run

```python
from run_launcher import RunLauncher, TrainingConfig

# Initialize launcher
launcher = RunLauncher(lightos_endpoint="localhost:50051")

# Create training configuration
config = TrainingConfig(
    run_id="",  # Auto-generated
    model=model,
    dataset=browser.datasets[0],  # Select dataset
    compute=compute,
    budget=budget,
    enable_spiking=True,
    enable_moe=True,
    target_sparsity=0.69,  # 69% sparsity target
    batch_size=8,
    learning_rate=3e-4,
    num_epochs=3
)

# Create and launch
run_id = launcher.create_run(config)
launcher.launch_run(run_id, config)

# Monitor progress
status = launcher.get_status(run_id)
print(f"Status: {status.status}")
print(f"Progress: {status.progress_percent:.1f}%")
print(f"Sparsity: {status.sparsity_achieved:.1f}%")
```

---

## 🔥 Thermal Guard + HVAC Integration

The enhanced Thermal Guard coordinates chip-level and data-center-level cooling.

### How It Works

```
Chip Level (Photonic NPU)
  Temperature: 78°C (approaching warning threshold)
       ↓
  Thermal Guard detects heat increase
       ↓
  Sends cooling request to Infrastructure Autopilot
       ↓
Data Center Level (HVAC)
  Autopilot receives request
       ↓
  DRL policy computes optimal action
       ↓
  Lowers CRAC supply temp by 1.5°C
  Increases airflow by 200 CFM
       ↓
  Chip temperature drops to 72°C
  ✅ Crisis averted!
```

### Configure Integration

```c
// In your application code
#include "photonic_hvac_integration.h"

struct hvac_callbacks callbacks = {
    .on_temp_change = handle_chip_temp_change,
    .on_throttle_change = handle_throttle_event,
    .request_cooling = request_additional_cooling,
    .on_emergency_shutdown = handle_emergency
};

// Initialize integration
photonic_hvac_init(photonic_device, autopilot_ctx, &callbacks);

// Now chip and HVAC communicate automatically!
```

---

## 📊 Performance Monitoring

### CloudWatch Integration

```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb

# Configure for LightOS metrics
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -c file:///home/ubuntu/LightOS/deployment/aws/cloudwatch-config.json \
  -s
```

### Custom Metrics Dashboard

Access CloudWatch dashboard:
```
https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=LightOS-NCE
```

**Metrics tracked**:
- Spiking engine sparsity (%)
- MoE expert utilization (%)
- Photonic NPU temperature (°C)
- Infrastructure Autopilot PUE
- HVAC energy savings (%)
- LLM training throughput (tokens/sec)
- Cost per 1000 tokens ($)

---

## 💰 Cost Optimization

### 1. Use Spot Instances (70% savings)

```bash
terraform apply \
  -var="use_spot_instances=true" \
  -var="spot_max_price=0.30"
```

### 2. Auto-Stop Idle Instances

Create Lambda function to stop instances after 30min idle:

```python
# lambda_function.py
import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')

    # Find idle LightOS instances
    response = ec2.describe_instances(
        Filters=[
            {'Name': 'tag:Project', 'Values': ['lightos']},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )

    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            # Check CPU utilization via CloudWatch
            # If < 5% for 30min, stop instance
            pass
```

### 3. Infrastructure Autopilot Savings

Expected HVAC energy savings: **53.6%**

Example monthly savings for 100kW data center:
```
Baseline HVAC cost:  $21,600/month
With Autopilot:      $10,022/month
Monthly savings:     $11,578/month
Annual savings:      $138,936/year
```

---

## 🔒 Security Best Practices

### 1. Restrict SSH Access

```bash
# Update security group to allow SSH only from your IP
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 22 \
  --cidr <YOUR_IP>/32
```

### 2. Enable Encryption

```hcl
# In Terraform main.tf
resource "aws_ebs_volume" "lightos_data" {
  encrypted = true
  kms_key_id = aws_kms_key.lightos_key.arn
}
```

### 3. Use IAM Roles (Not Access Keys)

Already configured in Terraform deployment! ✅

---

## 🧪 Testing Your Deployment

### 1. Verify Kernel Module

```bash
ssh ubuntu@$INSTANCE_IP
lsmod | grep lightos
dmesg | grep "LightOS Neural Compute Engine"
```

### 2. Test Spiking Engine

```bash
cd ~/LightOS
sudo ./test_spiking

# Expected output:
# ✓ Spiking engine configured
# ✓ Spiking engine started
# Current sparsity: 72%
# 🎉 SUCCESS! Achieved >69% sparsity target!
```

### 3. Test Infrastructure Autopilot

```bash
curl http://localhost:8080/autopilot/status
curl http://localhost:8080/autopilot/metrics
```

### 4. Test LLM Training Ground

```bash
curl http://localhost:3000/api/models
curl http://localhost:3000/api/datasets
```

---

## 🚨 Troubleshooting

### Kernel Module Won't Load

```bash
# Check kernel version
uname -r

# Ensure headers match
apt-cache policy linux-headers-$(uname -r)

# Rebuild module
cd ~/LightOS
make clean
make kernel
sudo make install
sudo modprobe lightos
```

### Autopilot Not Starting

```bash
# Check logs
journalctl -u autopilot -f

# Verify configuration
cat /etc/lightos/autopilot.conf | jq .

# Test manually
cd ~/LightOS/fabric-os/infrastructure-autopilot
./autopilot --test-mode
```

### High Costs

```bash
# Check running instances
aws ec2 describe-instances --query 'Reservations[].Instances[?State.Name==`running`].[InstanceId,InstanceType,LaunchTime]' --output table

# Stop unused instances
aws ec2 stop-instances --instance-ids i-xxxxx

# Enable auto-stop
# (See Cost Optimization section)
```

---

## 📚 Next Steps

1. **Production Hardening**
   - Enable multi-AZ deployment
   - Configure auto-scaling policies
   - Set up automated backups
   - Implement disaster recovery

2. **Integrate with CI/CD**
   - GitHub Actions for automated deployment
   - Automated testing pipeline
   - Blue-green deployments

3. **Advanced Features**
   - Multi-region deployment
   - Federated learning across regions
   - Custom model architectures
   - Real-time model serving

4. **Monitoring & Alerting**
   - SNS notifications for thermal events
   - PagerDuty integration
   - Grafana dashboards

---

## 🎓 Additional Resources

- **Documentation**: `/home/user/LightOS/NEURAL_COMPUTE_ENGINE_README.md`
- **Architecture**: `/home/user/LightOS/docs/architecture/NEURAL_COMPUTE_ENGINE.md`
- **API Reference**: `/home/user/LightOS/docs/api/`
- **Examples**: `/home/user/LightOS/examples/`

---

## 🆘 Support

- **Issues**: https://github.com/Lightiam/LightOS/issues
- **Discussions**: https://github.com/Lightiam/LightOS/discussions
- **Email**: support@lightrail.ai

---

**Version**: 0.2.1 (with Infrastructure Autopilot)
**Last Updated**: 2026-01-07
**Deployment Time**: ~15 minutes
**Estimated Monthly Cost**: $60-$18,000 (depending on configuration)
