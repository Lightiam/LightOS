#!/bin/bash
# 08-install-cloudwatch.sh
# Install and configure CloudWatch agent

set -e

echo "================================================"
echo "Step 8: Installing CloudWatch agent"
echo "================================================"

# Download CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb -O /tmp/amazon-cloudwatch-agent.deb

# Install CloudWatch agent
sudo dpkg -i /tmp/amazon-cloudwatch-agent.deb
rm /tmp/amazon-cloudwatch-agent.deb

# Create CloudWatch configuration
sudo tee /opt/aws/amazon-cloudwatch-agent/etc/config.json > /dev/null <<'EOF'
{
  "agent": {
    "metrics_collection_interval": 60,
    "run_as_user": "cwagent"
  },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/lightos/*.log",
            "log_group_name": "/aws/ec2/lightos",
            "log_stream_name": "{instance_id}/lightos",
            "retention_in_days": 7
          },
          {
            "file_path": "/var/log/syslog",
            "log_group_name": "/aws/ec2/lightos",
            "log_stream_name": "{instance_id}/syslog",
            "retention_in_days": 3
          }
        ]
      }
    }
  },
  "metrics": {
    "namespace": "LightOS",
    "metrics_collected": {
      "cpu": {
        "measurement": [
          {
            "name": "cpu_usage_idle",
            "rename": "CPU_IDLE",
            "unit": "Percent"
          },
          {
            "name": "cpu_usage_iowait",
            "rename": "CPU_IOWAIT",
            "unit": "Percent"
          }
        ],
        "metrics_collection_interval": 60,
        "totalcpu": false
      },
      "disk": {
        "measurement": [
          {
            "name": "used_percent",
            "rename": "DISK_USED",
            "unit": "Percent"
          }
        ],
        "metrics_collection_interval": 60,
        "resources": [
          "*"
        ]
      },
      "mem": {
        "measurement": [
          {
            "name": "mem_used_percent",
            "rename": "MEM_USED",
            "unit": "Percent"
          }
        ],
        "metrics_collection_interval": 60
      },
      "nvidia_gpu": {
        "measurement": [
          {
            "name": "utilization_gpu",
            "rename": "GPU_UTILIZATION",
            "unit": "Percent"
          },
          {
            "name": "utilization_memory",
            "rename": "GPU_MEMORY",
            "unit": "Percent"
          },
          {
            "name": "temperature_gpu",
            "rename": "GPU_TEMPERATURE",
            "unit": "None"
          }
        ],
        "metrics_collection_interval": 60
      }
    }
  }
}
EOF

# Note: CloudWatch agent will be started on first boot via user data
# We don't start it here because instance doesn't have IAM role yet

echo "✓ CloudWatch agent installed"
