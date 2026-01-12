#!/bin/bash
# build.sh
# Build LightOS AMI with Packer

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╦  ┬┌─┐┬ ┬┌┬┐╔═╗╔═╗"
echo "║  ││ ┬├─┤ │ ║ ║╚═╗"
echo "╩═╝┴└─┘┴ ┴ ┴ ╚═╝╚═╝"
echo ""
echo "AMI Builder for AWS Marketplace"
echo -e "${NC}"

# Check if Packer is installed
if ! command -v packer &> /dev/null; then
    echo -e "${RED}Error: Packer is not installed${NC}"
    echo "Install Packer from: https://www.packer.io/downloads"
    echo ""
    echo "Quick install:"
    echo "  wget https://releases.hashicorp.com/packer/1.9.4/packer_1.9.4_linux_amd64.zip"
    echo "  unzip packer_1.9.4_linux_amd64.zip"
    echo "  sudo mv packer /usr/local/bin/"
    exit 1
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not configured${NC}"
    echo "Run: aws configure"
    exit 1
fi

# Get AWS account info
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=${AWS_REGION:-us-east-1}

echo -e "${GREEN}AWS Configuration:${NC}"
echo "  Account: $AWS_ACCOUNT"
echo "  Region: $AWS_REGION"
echo ""

# Check if variables file exists
if [ ! -f "variables.pkrvars.hcl" ]; then
    echo -e "${YELLOW}Creating default variables file...${NC}"
    cat > variables.pkrvars.hcl <<EOF
aws_region = "$AWS_REGION"
lightos_version = "0.2.1"
instance_type = "g4dn.xlarge"
volume_size = 100
EOF
    echo -e "${GREEN}✓ Created variables.pkrvars.hcl${NC}"
    echo "  Edit this file to customize build settings"
    echo ""
fi

# Validate Packer configuration
echo -e "${BLUE}Validating Packer configuration...${NC}"
if packer validate -var-file=variables.pkrvars.hcl lightos.pkr.hcl; then
    echo -e "${GREEN}✓ Packer configuration is valid${NC}"
else
    echo -e "${RED}✗ Packer configuration validation failed${NC}"
    exit 1
fi
echo ""

# Estimate costs
echo -e "${YELLOW}⚠  Estimated Build Cost:${NC}"
echo "  Instance time (~45 minutes): $1.50"
echo "  Storage (100GB): $0.50"
echo "  Data transfer: $0.25"
echo "  Total: ~$2.25"
echo ""

# Confirm build
read -p "Continue with build? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Build cancelled"
    exit 0
fi

# Initialize Packer
echo -e "${BLUE}Initializing Packer...${NC}"
packer init lightos.pkr.hcl
echo ""

# Build AMI
echo -e "${BLUE}Starting AMI build...${NC}"
echo "This will take approximately 45-60 minutes"
echo ""

# Run packer build with timestamp
START_TIME=$(date +%s)

if packer build -var-file=variables.pkrvars.hcl lightos.pkr.hcl; then
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    MINUTES=$((DURATION / 60))
    SECONDS=$((DURATION % 60))

    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ AMI Build Successful!              ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
    echo ""
    echo "Build time: ${MINUTES}m ${SECONDS}s"
    echo ""

    # Extract AMI ID from manifest
    if [ -f "manifest.json" ]; then
        AMI_ID=$(jq -r '.builds[0].artifact_id' manifest.json | cut -d':' -f2)
        AMI_REGION=$(jq -r '.builds[0].artifact_id' manifest.json | cut -d':' -f1)

        echo -e "${GREEN}AMI Details:${NC}"
        echo "  AMI ID: $AMI_ID"
        echo "  Region: $AMI_REGION"
        echo ""

        # Get AMI details
        AMI_INFO=$(aws ec2 describe-images --image-ids $AMI_ID --region $AMI_REGION 2>/dev/null || echo "")
        if [ -n "$AMI_INFO" ]; then
            AMI_NAME=$(echo "$AMI_INFO" | jq -r '.Images[0].Name')
            AMI_SIZE=$(echo "$AMI_INFO" | jq -r '.Images[0].BlockDeviceMappings[0].Ebs.VolumeSize')
            echo "  Name: $AMI_NAME"
            echo "  Size: ${AMI_SIZE}GB"
        fi

        echo ""
        echo -e "${BLUE}Next Steps:${NC}"
        echo "  1. Test the AMI:"
        echo "     aws ec2 run-instances --image-id $AMI_ID --instance-type g4dn.xlarge --key-name YOUR_KEY"
        echo ""
        echo "  2. Copy to other regions (optional):"
        echo "     aws ec2 copy-image --source-image-id $AMI_ID --source-region $AMI_REGION --region us-west-2 --name \"$AMI_NAME\""
        echo ""
        echo "  3. Submit to AWS Marketplace:"
        echo "     https://aws.amazon.com/marketplace/management/"
        echo ""

        # Save AMI ID to file
        echo "$AMI_ID" > ami-id.txt
        echo "  AMI ID saved to: ami-id.txt"
    fi
else
    echo -e "${RED}✗ AMI build failed${NC}"
    echo "Check the logs above for error details"
    exit 1
fi
