# LightOS AWS Marketplace Publishing Guide

Complete guide to publishing LightOS on AWS Marketplace.

---

## Overview

Publish LightOS as an Amazon Machine Image (AMI) available on AWS Marketplace for easy deployment on EC2 instances.

**Product Type:** Machine Learning AMI
**Pricing Model:** BYOL (Bring Your Own License) + Hourly/Annual subscriptions
**Target Instance Types:** GPU instances (g4dn, g5, p3, p4d)

---

## Prerequisites

### Required AWS Resources
- AWS Account with Marketplace seller registration
- S3 bucket for artifacts
- EC2 access for AMI creation
- IAM roles for marketplace operations

### Required Tools
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Install Packer for AMI building
wget https://releases.hashicorp.com/packer/1.9.4/packer_1.9.4_linux_amd64.zip
unzip packer_1.9.4_linux_amd64.zip
sudo mv packer /usr/local/bin/
```

---

## Step 1: Create Base AMI

### Build Script: `marketplace/aws/images/build-ami.sh`

```bash
#!/bin/bash
# Build LightOS AMI for AWS Marketplace

set -e

REGION="${AWS_REGION:-us-east-1}"
INSTANCE_TYPE="g4dn.xlarge"
SOURCE_AMI="ami-0c55b159cbfafe1f0"  # Ubuntu 22.04 LTS

echo "🚀 Building LightOS AMI for AWS Marketplace"

# Create temporary instance
INSTANCE_ID=$(aws ec2 run-instances \
  --image-id $SOURCE_AMI \
  --instance-type $INSTANCE_TYPE \
  --key-name lightos-builder \
  --security-group-ids sg-xxxxxxxx \
  --subnet-id subnet-xxxxxxxx \
  --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":100,"VolumeType":"gp3"}}]' \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=LightOS-Builder}]' \
  --query 'Instances[0].InstanceId' \
  --output text)

echo "✓ Instance created: $INSTANCE_ID"

# Wait for instance to be running
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

echo "✓ Instance running at: $PUBLIC_IP"
sleep 30

# Install LightOS
ssh -o StrictHostKeyChecking=no ubuntu@$PUBLIC_IP << 'EOF'
  # Update system
  sudo apt update && sudo apt upgrade -y

  # Install dependencies
  sudo apt install -y build-essential python3-pip nvidia-driver-535 nvidia-cuda-toolkit

  # Clone and install LightOS
  git clone https://github.com/Lightiam/LightOS.git
  cd LightOS
  sudo ./simple-deploy.sh

  # Configure for AWS
  sudo tee /etc/lightos/aws-config.json << 'AWSCONF'
{
  "cloud_provider": "aws",
  "instance_metadata": "http://169.254.169.254/latest/meta-data/",
  "auto_scaling": true,
  "gpu_auto_detection": true
}
AWSCONF

  # Clean up
  sudo apt clean
  sudo rm -rf /tmp/* /var/tmp/*
  history -c
EOF

echo "✓ LightOS installed"

# Stop instance
aws ec2 stop-instances --instance-ids $INSTANCE_ID
aws ec2 wait instance-stopped --instance-ids $INSTANCE_ID

# Create AMI
AMI_ID=$(aws ec2 create-image \
  --instance-id $INSTANCE_ID \
  --name "LightOS-v0.2.1-$(date +%Y%m%d)" \
  --description "LightOS Neural Compute Engine v0.2.1 - Fast LLM Training & AI Development" \
  --query 'ImageId' \
  --output text)

echo "✓ AMI created: $AMI_ID"

# Tag AMI
aws ec2 create-tags --resources $AMI_ID --tags \
  Key=Name,Value="LightOS v0.2.1" \
  Key=Version,Value="0.2.1" \
  Key=Marketplace,Value="true"

# Wait for AMI to be available
aws ec2 wait image-available --image-ids $AMI_ID

# Terminate builder instance
aws ec2 terminate-instances --instance-ids $INSTANCE_ID

echo "✅ AMI ready: $AMI_ID"
echo "Next: Register this AMI in AWS Marketplace Portal"
```

---

## Step 2: Packer Configuration

### File: `marketplace/aws/images/lightos.pkr.hcl`

```hcl
packer {
  required_plugins {
    amazon = {
      version = ">= 1.0.0"
      source  = "github.com/hashicorp/amazon"
    }
  }
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "lightos_version" {
  type    = string
  default = "0.2.1"
}

source "amazon-ebs" "lightos" {
  ami_name      = "LightOS-${var.lightos_version}-{{timestamp}}"
  instance_type = "g4dn.xlarge"
  region        = var.aws_region

  source_ami_filter {
    filters = {
      name                = "ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"
      root-device-type    = "ebs"
      virtualization-type = "hvm"
    }
    most_recent = true
    owners      = ["099720109477"]  # Canonical
  }

  ssh_username = "ubuntu"

  launch_block_device_mappings {
    device_name = "/dev/sda1"
    volume_size = 100
    volume_type = "gp3"
    iops        = 3000
    throughput  = 125
    delete_on_termination = true
  }

  tags = {
    Name        = "LightOS v${var.lightos_version}"
    Version     = var.lightos_version
    OS          = "Ubuntu 22.04"
    Marketplace = "AWS"
  }
}

build {
  sources = ["source.amazon-ebs.lightos"]

  # Update system
  provisioner "shell" {
    inline = [
      "sudo apt-get update",
      "sudo apt-get upgrade -y",
      "sudo apt-get install -y build-essential python3-pip git"
    ]
  }

  # Install NVIDIA drivers
  provisioner "shell" {
    inline = [
      "sudo apt-get install -y nvidia-driver-535 nvidia-cuda-toolkit",
      "sudo apt-get install -y nvidia-utils-535"
    ]
  }

  # Install LightOS
  provisioner "file" {
    source      = "../../../"
    destination = "/tmp/LightOS"
  }

  provisioner "shell" {
    inline = [
      "cd /tmp/LightOS",
      "sudo ./simple-deploy.sh"
    ]
  }

  # AWS-specific configuration
  provisioner "shell" {
    inline = [
      "sudo mkdir -p /etc/lightos",
      "echo '{\"cloud\":\"aws\",\"auto_scaling\":true}' | sudo tee /etc/lightos/cloud.json"
    ]
  }

  # Clean up
  provisioner "shell" {
    inline = [
      "sudo apt-get clean",
      "sudo rm -rf /tmp/*",
      "sudo rm -rf /var/tmp/*",
      "history -c"
    ]
  }
}
```

**Build:**
```bash
cd marketplace/aws/images
packer build lightos.pkr.hcl
```

---

## Step 3: CloudFormation Template

### File: `marketplace/aws/templates/lightos-stack.yaml`

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'LightOS Neural Compute Engine - Fast LLM Training & AI Development'

Metadata:
  AWS::CloudFormation::Interface:
    ParameterGroups:
      - Label:
          default: "Instance Configuration"
        Parameters:
          - InstanceType
          - KeyName
          - VolumeSize
      - Label:
          default: "Network Configuration"
        Parameters:
          - VPC
          - Subnet
          - AllowedSSHCIDR

Parameters:
  InstanceType:
    Description: EC2 instance type (GPU recommended)
    Type: String
    Default: g4dn.xlarge
    AllowedValues:
      - g4dn.xlarge    # 4 vCPU, 16GB RAM, 1x T4 GPU - $0.526/hr
      - g4dn.2xlarge   # 8 vCPU, 32GB RAM, 1x T4 GPU - $0.752/hr
      - g5.xlarge      # 4 vCPU, 16GB RAM, 1x A10G GPU - $1.006/hr
      - g5.2xlarge     # 8 vCPU, 32GB RAM, 1x A10G GPU - $1.212/hr
      - p3.2xlarge     # 8 vCPU, 61GB RAM, 1x V100 GPU - $3.06/hr
      - p4d.24xlarge   # 96 vCPU, 1152GB RAM, 8x A100 GPU - $32.77/hr
    ConstraintDescription: Must be a valid GPU instance type

  KeyName:
    Description: EC2 Key Pair for SSH access
    Type: AWS::EC2::KeyPair::KeyName
    ConstraintDescription: Must be an existing EC2 KeyPair

  VolumeSize:
    Description: EBS Volume Size (GB)
    Type: Number
    Default: 100
    MinValue: 50
    MaxValue: 1000

  VPC:
    Description: VPC ID
    Type: AWS::EC2::VPC::Id

  Subnet:
    Description: Subnet ID (must have public IP)
    Type: AWS::EC2::Subnet::Id

  AllowedSSHCIDR:
    Description: CIDR block allowed to SSH
    Type: String
    Default: 0.0.0.0/0
    AllowedPattern: '(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})/(\d{1,2})'

Mappings:
  RegionMap:
    us-east-1:
      AMI: ami-xxxxxxxxx  # Replace with actual AMI ID
    us-west-2:
      AMI: ami-xxxxxxxxx
    eu-west-1:
      AMI: ami-xxxxxxxxx
    ap-southeast-1:
      AMI: ami-xxxxxxxxx

Resources:
  SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: LightOS Security Group
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: !Ref AllowedSSHCIDR
          Description: SSH access
        - IpProtocol: tcp
          FromPort: 8080
          ToPort: 8080
          CidrIp: 0.0.0.0/0
          Description: LightOS Web UI
        - IpProtocol: tcp
          FromPort: 8888
          ToPort: 8888
          CidrIp: 0.0.0.0/0
          Description: Jupyter Notebook
      Tags:
        - Key: Name
          Value: LightOS-SecurityGroup

  InstanceRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy
      Policies:
        - PolicyName: LightOSS3Access
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject
                  - s3:PutObject
                  - s3:ListBucket
                Resource:
                  - !Sub 'arn:aws:s3:::lightos-models-${AWS::AccountId}/*'
                  - !Sub 'arn:aws:s3:::lightos-models-${AWS::AccountId}'

  InstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      Roles:
        - !Ref InstanceRole

  LightOSInstance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !FindInMap [RegionMap, !Ref 'AWS::Region', AMI]
      InstanceType: !Ref InstanceType
      KeyName: !Ref KeyName
      IamInstanceProfile: !Ref InstanceProfile
      SecurityGroupIds:
        - !Ref SecurityGroup
      SubnetId: !Ref Subnet
      BlockDeviceMappings:
        - DeviceName: /dev/sda1
          Ebs:
            VolumeSize: !Ref VolumeSize
            VolumeType: gp3
            Iops: 3000
            Throughput: 125
            DeleteOnTermination: true
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          # LightOS startup script

          # Update hostname
          hostnamectl set-hostname lightos-$(ec2-metadata --instance-id | cut -d' ' -f2)

          # Start LightOS services
          systemctl enable lightos
          systemctl start lightos

          # Configure CloudWatch
          wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
          dpkg -i amazon-cloudwatch-agent.deb

          # Send success signal
          /opt/aws/bin/cfn-signal -e $? --stack ${AWS::StackName} --resource LightOSInstance --region ${AWS::Region}
      Tags:
        - Key: Name
          Value: LightOS-Instance
        - Key: Application
          Value: LightOS
    CreationPolicy:
      ResourceSignal:
        Timeout: PT15M

  ModelStorageBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub 'lightos-models-${AWS::AccountId}'
      VersioningConfiguration:
        Status: Enabled
      LifecycleConfiguration:
        Rules:
          - Id: DeleteOldVersions
            Status: Enabled
            NoncurrentVersionExpirationInDays: 30
      Tags:
        - Key: Application
          Value: LightOS

Outputs:
  InstanceId:
    Description: Instance ID
    Value: !Ref LightOSInstance

  PublicIP:
    Description: Public IP address
    Value: !GetAtt LightOSInstance.PublicIp

  WebUI:
    Description: LightOS Web UI
    Value: !Sub 'http://${LightOSInstance.PublicIp}:8080'

  JupyterNotebook:
    Description: Jupyter Notebook
    Value: !Sub 'http://${LightOSInstance.PublicIp}:8888'

  SSHCommand:
    Description: SSH command
    Value: !Sub 'ssh -i ${KeyName}.pem ubuntu@${LightOSInstance.PublicIp}'

  S3Bucket:
    Description: Model storage bucket
    Value: !Ref ModelStorageBucket
```

**Deploy:**
```bash
aws cloudformation create-stack \
  --stack-name lightos-production \
  --template-body file://lightos-stack.yaml \
  --parameters \
    ParameterKey=InstanceType,ParameterValue=g4dn.xlarge \
    ParameterKey=KeyName,ParameterValue=my-keypair \
    ParameterKey=VPC,ParameterValue=vpc-xxxxx \
    ParameterKey=Subnet,ParameterValue=subnet-xxxxx \
  --capabilities CAPABILITY_IAM
```

---

## Step 4: Marketplace Product Listing

### Product Information

**Product Title:**
```
LightOS - Neural Compute Engine for Fast LLM Training
```

**Short Description:**
```
Train LLMs 2-5x faster with 70% less memory. Platform-agnostic OS for AI accelerators with cutting-edge coding agents that beat GPT-4.
```

**Long Description:**
```
LightOS is a revolutionary neural compute engine that dramatically accelerates LLM training and AI development.

KEY FEATURES:
• ⚡ 2-5x Faster Training: Unsloth integration makes fine-tuning dramatically faster
• 💰 70% Less Memory: Train larger models on smaller, cheaper instances
• 🏆 Beats GPT-4: Local coding agents with 74.5% HumanEval (vs GPT-4's 67%)
• 🔓 100% Private: Your code and data stay on your infrastructure
• 🌐 Platform-Agnostic: Works across NVIDIA, AMD, ARM, Intel GPUs

WHAT'S INCLUDED:
• Fast LLM fine-tuning (Llama, Mistral, Qwen, GLM-4, Gemma)
• GLM-4 coding agent (71.8% HumanEval)
• Qwen2.5-Coder (74.5% HumanEval - beats GPT-4)
• Pre-configured development environment
• Interactive training UI
• Complete documentation

PERFECT FOR:
• AI/ML engineers training custom models
• Data scientists fine-tuning LLMs
• Developers building AI-powered applications
• Research teams experimenting with new architectures
• Companies requiring private AI infrastructure

PERFORMANCE:
Traditional: 10h training, 24GB VRAM, $10 cost
LightOS: 4h training, 7GB VRAM, $4 cost
Result: 2.5x faster, 71% less memory, 60% cheaper

SUPPORTED INSTANCES:
• g4dn series (T4 GPUs) - Recommended for development
• g5 series (A10G GPUs) - Recommended for production
• p3 series (V100 GPUs) - High performance
• p4d series (A100 GPUs) - Maximum performance

GET STARTED IN 5 MINUTES:
1. Launch from AWS Marketplace
2. SSH into instance
3. Run: lightos-train train llama-3.1-8b alpaca
4. Done! Your model is training

PRICING:
• Software: Free (MIT License) + Support plans available
• Infrastructure: Standard AWS EC2 rates apply
• No vendor lock-in, cancel anytime

SUPPORT:
• Documentation: https://lightos.dev/docs
• Community: GitHub Discussions
• Enterprise: 24/7 support available

Try LightOS today and experience the future of AI development!
```

### Product Logo
- Size: 1200x630px
- Format: PNG with transparency
- Include: LightOS branding

### Screenshots
1. Dashboard with statistics
2. Fine-tuning interface
3. Code generation demo
4. Training progress charts
5. Architecture diagram

### Product Categories
- Machine Learning & AI
- Developer Tools
- Data Science
- Deep Learning
- Natural Language Processing

### Keywords
```
llm, fine-tuning, ai, machine-learning, deep-learning, gpu, training,
coding-agent, gpt, llama, mistral, unsloth, transformer, nlp
```

---

## Step 5: Pricing Configuration

### Pricing Models

**Option 1: BYOL (Bring Your Own License)**
```
Software Cost: $0/hour
Customer pays only for EC2 instance
```

**Option 2: Hourly Pricing**
```
g4dn.xlarge:  Software $0.10/hr + EC2 $0.526/hr = $0.626/hr total
g4dn.2xlarge: Software $0.20/hr + EC2 $0.752/hr = $0.952/hr total
g5.xlarge:    Software $0.15/hr + EC2 $1.006/hr = $1.156/hr total
p3.2xlarge:   Software $0.50/hr + EC2 $3.06/hr  = $3.56/hr total
```

**Option 3: Annual Contract**
```
Standard: $999/year  (Save 20%)
Professional: $2,499/year (Priority support)
Enterprise: $9,999/year (24/7 support, SLA)
```

### License Types
- Free (MIT License)
- Standard (Email support)
- Professional (Priority support, dedicated Slack)
- Enterprise (24/7 support, custom features, SLA)

---

## Step 6: Compliance & Security

### Required Documentation

1. **Security Questionnaire**
   - Data encryption (at rest, in transit)
   - Network security
   - Access controls
   - Vulnerability scanning
   - Compliance certifications

2. **Architecture Diagram**
   - Component overview
   - Data flow
   - Network topology
   - Security boundaries

3. **User Guide**
   - Getting started
   - Configuration
   - Best practices
   - Troubleshooting

4. **API Documentation**
   - Endpoints
   - Authentication
   - Rate limits
   - Examples

### Security Checklist
- [ ] All credentials removed from AMI
- [ ] SSH keys unique per deployment
- [ ] Security groups properly configured
- [ ] Encryption enabled for EBS volumes
- [ ] IAM roles follow least privilege
- [ ] CloudWatch logging enabled
- [ ] Automatic security updates configured
- [ ] Vulnerability scan passed
- [ ] Penetration test completed

---

## Step 7: Testing & Validation

### Pre-Launch Checklist

```bash
# Test AMI deployment
aws ec2 run-instances \
  --image-id ami-xxxxxxxxx \
  --instance-type g4dn.xlarge \
  --key-name test-key

# Verify services
ssh ubuntu@<instance-ip>
systemctl status lightos
lightos --version

# Test fine-tuning
lightos-train train llama-3.1-8b alpaca --max-steps 10

# Test code generation
lightos-code qwen generate "hello world"

# Check logs
tail -f /var/log/lightos/*.log

# Performance test
nvidia-smi
lightos benchmark
```

### Validation Criteria
- ✅ AMI boots successfully in all regions
- ✅ All services start automatically
- ✅ GPU detected and functional
- ✅ Training completes successfully
- ✅ Web UI accessible
- ✅ Documentation complete
- ✅ CloudFormation template works
- ✅ Pricing configured correctly

---

## Step 8: Submission Process

### Submit to AWS Marketplace

1. **Create Seller Account**
   - Go to: https://aws.amazon.com/marketplace/management/
   - Complete seller registration
   - Set up bank account and tax information

2. **Create Product Listing**
   - Product Type: Machine Learning AMI
   - Upload product information
   - Add pricing
   - Upload AMI IDs for all regions

3. **Technical Review**
   - AWS reviews AMI
   - Security scan
   - Compliance check
   - Usually takes 2-4 weeks

4. **Marketing Review**
   - Product description review
   - Screenshot approval
   - Pricing validation

5. **Go Live**
   - Product published
   - Listed in AWS Marketplace
   - Available to all AWS customers

### Submission Timeline
- Week 1-2: AMI creation and testing
- Week 3: Product listing preparation
- Week 4-6: AWS review and approval
- Week 7: Launch and promotion

---

## Step 9: Post-Launch Operations

### Monitoring

```bash
# CloudWatch dashboard
aws cloudwatch put-dashboard \
  --dashboard-name LightOS-Marketplace \
  --dashboard-body file://dashboard.json

# Set up alerts
aws cloudwatch put-metric-alarm \
  --alarm-name lightos-high-cpu \
  --alarm-description "LightOS high CPU usage" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold
```

### Customer Support
- Monitor AWS Marketplace reviews
- Respond to customer questions
- Track deployment metrics
- Collect feature requests

### Updates
```bash
# Create new AMI version
packer build -var 'lightos_version=0.2.2' lightos.pkr.hcl

# Update marketplace listing
aws marketplace-catalog put-change-set \
  --catalog "AWSMarketplace" \
  --change-set file://update-product.json
```

---

## Resources

### AWS Documentation
- Marketplace Seller Guide: https://docs.aws.amazon.com/marketplace/
- AMI Best Practices: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AMIs.html
- CloudFormation Templates: https://aws.amazon.com/cloudformation/

### Support
- AWS Marketplace Support: aws-marketplace-seller-ops@amazon.com
- LightOS Documentation: https://lightos.dev/docs
- GitHub Issues: https://github.com/Lightiam/LightOS/issues

---

## Quick Start Commands

```bash
# Build AMI
cd marketplace/aws/images
packer build lightos.pkr.hcl

# Test deployment
aws cloudformation create-stack \
  --stack-name lightos-test \
  --template-body file://../templates/lightos-stack.yaml \
  --parameters file://test-params.json

# Monitor
aws cloudformation describe-stacks --stack-name lightos-test
aws ec2 describe-instances --filters "Name=tag:Application,Values=LightOS"

# Clean up
aws cloudformation delete-stack --stack-name lightos-test
```

---

**Next Steps:**
1. Review and customize AMI build scripts
2. Test AMI in all target regions
3. Prepare product listing materials
4. Complete seller registration
5. Submit for AWS review

For detailed questions, consult the AWS Marketplace Seller Guide or contact AWS Marketplace support.
