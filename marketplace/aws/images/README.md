# LightOS AMI Builder

Build production-ready LightOS AMIs for AWS Marketplace using Packer.

---

## 🚀 Quick Start

```bash
# 1. Install Packer
wget https://releases.hashicorp.com/packer/1.9.4/packer_1.9.4_linux_amd64.zip
unzip packer_1.9.4_linux_amd64.zip
sudo mv packer /usr/local/bin/

# 2. Configure AWS CLI
aws configure

# 3. Build AMI
./build.sh
```

**Build time:** 45-60 minutes
**Cost:** ~$2.25 per build

---

## 📋 Prerequisites

### Required Tools
- [Packer](https://www.packer.io/downloads) >= 1.9.0
- [AWS CLI](https://aws.amazon.com/cli/) >= 2.0
- [jq](https://stedolan.github.io/jq/) (for JSON parsing)

### AWS Requirements
- AWS account with marketplace seller registration
- IAM user with permissions:
  - EC2: Full access
  - VPC: Read access
  - S3: Read/Write (for Packer state)

### AWS Credentials
```bash
# Configure AWS CLI
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID="your-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-east-1"
```

---

## 🛠️ Build Process

### Step 1: Customize Variables

Copy and edit the variables file:

```bash
cp variables.pkrvars.hcl.example variables.pkrvars.hcl
vim variables.pkrvars.hcl
```

**Available variables:**
- `aws_region` - AWS region (default: us-east-1)
- `lightos_version` - LightOS version (default: 0.2.1)
- `instance_type` - Builder instance type (default: g4dn.xlarge)
- `volume_size` - Root volume size in GB (default: 100)

### Step 2: Validate Configuration

```bash
packer validate -var-file=variables.pkrvars.hcl lightos.pkr.hcl
```

### Step 3: Build AMI

```bash
./build.sh
```

**What happens:**
1. ✅ Validates Packer configuration
2. ✅ Launches temporary EC2 instance (g4dn.xlarge)
3. ✅ Runs 10 provisioning scripts:
   - System update
   - NVIDIA drivers & CUDA
   - Python & dependencies
   - LightOS installation
   - AWS configuration
   - Systemd services
   - Security hardening
   - CloudWatch agent
   - Cleanup
   - Validation
4. ✅ Creates AMI snapshot
5. ✅ Terminates builder instance
6. ✅ Outputs AMI ID

### Step 4: Test AMI

```bash
# Get AMI ID from build output or manifest.json
AMI_ID=$(cat ami-id.txt)

# Launch test instance
aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type g4dn.xlarge \
  --key-name YOUR_KEY_NAME \
  --security-group-ids sg-xxxxx \
  --subnet-id subnet-xxxxx

# SSH and test
ssh ubuntu@<instance-ip>
lightos --version
lightos-train list
```

---

## 📂 Directory Structure

```
marketplace/aws/images/
├── lightos.pkr.hcl              # Main Packer configuration
├── variables.pkrvars.hcl        # Build variables (create from .example)
├── variables.pkrvars.hcl.example # Example variables
├── build.sh                     # Build automation script
├── README.md                    # This file
├── scripts/                     # Provisioning scripts
│   ├── 01-system-update.sh      # Update Ubuntu packages
│   ├── 02-install-nvidia.sh     # Install NVIDIA drivers & CUDA
│   ├── 03-install-dependencies.sh # Install Python, Docker, etc.
│   ├── 04-install-lightos.sh    # Install LightOS
│   ├── 05-configure-aws.sh      # AWS-specific configuration
│   ├── 06-create-services.sh    # Create systemd services
│   ├── 07-security-hardening.sh # Security configuration
│   ├── 08-install-cloudwatch.sh # CloudWatch agent
│   ├── 09-cleanup.sh            # Clean up before AMI creation
│   └── 10-validate.sh           # Validate installation
├── manifest.json                # Build output (generated)
└── ami-id.txt                   # AMI ID (generated)
```

---

## 🔧 Customization

### Custom Instance Type

Edit `variables.pkrvars.hcl`:
```hcl
instance_type = "g5.xlarge"  # Use A10G GPU instead of T4
```

### Custom Volume Size

```hcl
volume_size = 200  # 200GB instead of 100GB
```

### Multi-Region Build

Build in multiple regions sequentially:

```bash
# Build in us-east-1
AWS_REGION=us-east-1 ./build.sh

# Build in us-west-2
AWS_REGION=us-west-2 ./build.sh

# Build in eu-west-1
AWS_REGION=eu-west-1 ./build.sh
```

Or copy AMI to other regions:

```bash
AMI_ID=$(cat ami-id.txt)

# Copy to us-west-2
aws ec2 copy-image \
  --source-image-id $AMI_ID \
  --source-region us-east-1 \
  --region us-west-2 \
  --name "LightOS-0.2.1-$(date +%Y%m%d)"

# Copy to eu-west-1
aws ec2 copy-image \
  --source-image-id $AMI_ID \
  --source-region us-east-1 \
  --region eu-west-1 \
  --name "LightOS-0.2.1-$(date +%Y%m%d)"
```

---

## 🐛 Troubleshooting

### Build Fails During NVIDIA Installation

**Problem:** NVIDIA driver installation fails

**Solution:** The GPU instance may not be available. Try different region or instance type:
```hcl
instance_type = "g4dn.2xlarge"
aws_region = "us-west-2"
```

### SSH Timeout

**Problem:** Packer can't SSH to instance

**Solution:** Check security group allows SSH from your IP:
```bash
# Get your IP
MY_IP=$(curl -s ifconfig.me)

# Update security group
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 22 \
  --cidr $MY_IP/32
```

### Insufficient Permissions

**Problem:** IAM permission errors

**Solution:** Ensure IAM user has required permissions:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:*",
        "vpc:Describe*"
      ],
      "Resource": "*"
    }
  ]
}
```

### Out of Disk Space During Build

**Problem:** Root volume fills up

**Solution:** Increase volume_size:
```hcl
volume_size = 150  # Increase to 150GB
```

### Build Takes Too Long

**Problem:** Build exceeds 60 minutes

**Cause:** Slow network, large downloads

**Solution:**
- Use larger instance type for faster builds
- Build in region closer to you
- Check network connectivity

---

## 📊 Build Costs

| Component | Cost | Duration |
|-----------|------|----------|
| g4dn.xlarge instance | $0.526/hr | ~1 hour |
| EBS storage (100GB) | $0.10/GB-month | 1 hour |
| Data transfer | ~$0.25 | - |
| **Total per build** | **~$2.25** | **45-60 min** |

**Cost optimization tips:**
- Use spot instances (50-70% cheaper)
- Build during off-peak hours
- Clean up failed builds promptly
- Reuse AMIs across accounts

---

## ✅ Post-Build Checklist

After successful build:

- [ ] Test AMI launches successfully
- [ ] Verify all LightOS commands work
- [ ] Check GPU is detected (`nvidia-smi`)
- [ ] Test fine-tuning workflow
- [ ] Test code generation
- [ ] Verify web UI accessible (port 8080)
- [ ] Check CloudWatch metrics
- [ ] Review security configuration
- [ ] Tag AMI appropriately
- [ ] Document AMI ID and region
- [ ] Copy to additional regions (if needed)
- [ ] Submit to AWS Marketplace

---

## 📝 AMI Details

**What's Installed:**
- Ubuntu 22.04 LTS (base)
- NVIDIA Driver 535
- CUDA 12.3 + cuDNN
- Python 3.10 + venv
- PyTorch 2.x with CUDA
- Transformers, Accelerate, Unsloth
- LightOS v0.2.1
- Systemd services (web, API, Jupyter)
- CloudWatch agent
- AWS CLI v2
- Docker & Docker Compose

**Services (auto-start):**
- `lightos-web` - Web UI on port 8080
- `lightos-api` - API server on port 8000
- `lightos-jupyter` - Jupyter on port 8888

**Security:**
- SSH hardened configuration
- UFW firewall enabled
- Automatic security updates
- No default passwords
- CloudWatch logging

---

## 🔗 Resources

- [Packer Documentation](https://www.packer.io/docs)
- [AWS EC2 AMI Documentation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AMIs.html)
- [AWS Marketplace Seller Guide](https://docs.aws.amazon.com/marketplace/)
- [LightOS Documentation](https://lightos.dev/docs)

---

## 🆘 Support

**Build Issues:**
- Check Packer logs in current directory
- Review AWS CloudTrail for API errors
- Verify IAM permissions

**LightOS Issues:**
- GitHub: https://github.com/Lightiam/LightOS/issues
- Docs: https://lightos.dev/docs

---

**Ready to build your AMI! Run `./build.sh` to get started.** 🚀
