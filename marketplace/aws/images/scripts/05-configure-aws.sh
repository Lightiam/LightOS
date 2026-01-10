#!/bin/bash
# 05-configure-aws.sh
# AWS-specific configuration

set -e

echo "================================================"
echo "Step 5: Configuring AWS-specific settings"
echo "================================================"

# Create AWS configuration directory
sudo mkdir -p /etc/lightos/aws

# Create AWS configuration file
sudo tee /etc/lightos/aws/config.json > /dev/null <<'EOF'
{
  "cloud_provider": "aws",
  "instance_metadata_url": "http://169.254.169.254/latest/meta-data/",
  "features": {
    "auto_scaling": true,
    "gpu_auto_detection": true,
    "cloudwatch_metrics": true,
    "s3_integration": true
  },
  "s3": {
    "models_bucket": "lightos-models-{{account_id}}",
    "datasets_bucket": "lightos-datasets-{{account_id}}",
    "region": "{{region}}"
  },
  "cloudwatch": {
    "namespace": "LightOS",
    "metrics_interval": 60
  }
}
EOF

# Create startup script that gets instance metadata
sudo tee /opt/lightos/aws-init.sh > /dev/null <<'EOF'
#!/bin/bash
# Get AWS instance metadata

# Get instance ID
INSTANCE_ID=$(ec2-metadata --instance-id | cut -d' ' -f2)
INSTANCE_TYPE=$(ec2-metadata --instance-type | cut -d' ' -f2)
REGION=$(ec2-metadata --availability-zone | cut -d' ' -f2 | sed 's/[a-z]$//')
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "unknown")

# Update config with actual values
sudo sed -i "s/{{account_id}}/$ACCOUNT_ID/g" /etc/lightos/aws/config.json
sudo sed -i "s/{{region}}/$REGION/g" /etc/lightos/aws/config.json

# Log instance info
echo "Instance ID: $INSTANCE_ID" | sudo tee -a /var/log/lightos/aws-info.log
echo "Instance Type: $INSTANCE_TYPE" | sudo tee -a /var/log/lightos/aws-info.log
echo "Region: $REGION" | sudo tee -a /var/log/lightos/aws-info.log
echo "Account ID: $ACCOUNT_ID" | sudo tee -a /var/log/lightos/aws-info.log

# Set hostname
sudo hostnamectl set-hostname "lightos-$INSTANCE_ID"

# Check for GPU
if command -v nvidia-smi &> /dev/null; then
    GPU_INFO=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -n1)
    echo "GPU: $GPU_INFO" | sudo tee -a /var/log/lightos/aws-info.log
fi
EOF

sudo chmod +x /opt/lightos/aws-init.sh

# Create S3 sync script
sudo tee /opt/lightos/s3-sync.sh > /dev/null <<'EOF'
#!/bin/bash
# Sync models and datasets with S3

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "unknown")
REGION=$(ec2-metadata --availability-zone | cut -d' ' -f2 | sed 's/[a-z]$//')

# Sync models to S3
if [ "$1" == "upload" ]; then
    aws s3 sync /opt/lightos/models/ s3://lightos-models-${ACCOUNT_ID}/models/ --region $REGION
    echo "Models uploaded to S3"
elif [ "$1" == "download" ]; then
    aws s3 sync s3://lightos-models-${ACCOUNT_ID}/models/ /opt/lightos/models/ --region $REGION
    echo "Models downloaded from S3"
else
    echo "Usage: $0 [upload|download]"
fi
EOF

sudo chmod +x /opt/lightos/s3-sync.sh

echo "✓ AWS configuration completed"
