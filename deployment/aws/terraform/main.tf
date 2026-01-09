# LightOS Neural Compute Engine - AWS Deployment
# Includes Infrastructure Autopilot for HVAC optimization

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Variables
variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"  # For basic deployment
  # Use p3.2xlarge for GPU, g4dn.xlarge for cheaper GPU
}

variable "enable_gpu" {
  description = "Deploy GPU instances"
  type        = bool
  default     = false
}

variable "enable_autopilot" {
  description = "Enable Infrastructure Autopilot"
  type        = bool
  default     = true
}

variable "num_compute_nodes" {
  description = "Number of compute nodes"
  type        = number
  default     = 2
}

# VPC and Networking
resource "aws_vpc" "lightos_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "lightos-vpc"
  }
}

resource "aws_subnet" "lightos_subnet" {
  vpc_id                  = aws_vpc.lightos_vpc.id
  cidr_block             = "10.0.1.0/24"
  availability_zone      = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name = "lightos-subnet"
  }
}

resource "aws_internet_gateway" "lightos_igw" {
  vpc_id = aws_vpc.lightos_vpc.id

  tags = {
    Name = "lightos-igw"
  }
}

resource "aws_route_table" "lightos_rt" {
  vpc_id = aws_vpc.lightos_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.lightos_igw.id
  }

  tags = {
    Name = "lightos-rt"
  }
}

resource "aws_route_table_association" "lightos_rta" {
  subnet_id      = aws_subnet.lightos_subnet.id
  route_table_id = aws_route_table.lightos_rt.id
}

# Security Group
resource "aws_security_group" "lightos_sg" {
  name        = "lightos-sg"
  description = "Security group for LightOS Neural Compute Engine"
  vpc_id      = aws_vpc.lightos_vpc.id

  # SSH access
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Restrict to your IP in production!
    description = "SSH access"
  }

  # LightOS gRPC (Fabric OS)
  ingress {
    from_port   = 50051
    to_port     = 50051
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
    description = "LightOS Fabric OS gRPC"
  }

  # Infrastructure Autopilot API
  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
    description = "Infrastructure Autopilot API"
  }

  # LLM Training Ground UI
  ingress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "LLM Training Ground UI"
  }

  # All outbound
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "lightos-sg"
  }
}

# IAM Role for EC2 instances
resource "aws_iam_role" "lightos_role" {
  name = "lightos-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lightos_cloudwatch" {
  role       = aws_iam_role.lightos_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

resource "aws_iam_instance_profile" "lightos_profile" {
  name = "lightos-instance-profile"
  role = aws_iam_role.lightos_role.name
}

# User data script for instance initialization
locals {
  user_data = <<-EOF
    #!/bin/bash
    set -e

    # Update system
    apt-get update
    apt-get install -y build-essential linux-headers-$(uname -r) git python3-pip

    # Clone LightOS
    cd /home/ubuntu
    git clone https://github.com/Lightiam/LightOS.git
    cd LightOS
    git checkout claude/refactor-lightos-ai-56dEr

    # Build LightOS
    make all
    make install

    # Load kernel module
    modprobe lightos || echo "Note: Kernel module load may fail in some environments"

    # Install Python dependencies for LLM Training Ground
    pip3 install torch transformers datasets flask

    ${var.enable_autopilot ? "# Setup Infrastructure Autopilot\ncd fabric-os/infrastructure-autopilot\ngcc -pthread -o autopilot autopilot.c -lm\n./autopilot &" : ""}

    # Setup systemd service
    cat > /etc/systemd/system/lightos.service << 'SYSTEMD'
    [Unit]
    Description=LightOS Neural Compute Engine
    After=network.target

    [Service]
    Type=simple
    User=root
    ExecStart=/usr/local/bin/lightos-agent
    Restart=always

    [Install]
    WantedBy=multi-user.target
    SYSTEMD

    systemctl enable lightos.service
    systemctl start lightos.service

    # Create completion marker
    touch /var/lib/cloud/instance/lightos-setup-complete
  EOF
}

# Launch Template for compute nodes
resource "aws_launch_template" "lightos_compute" {
  name_prefix   = "lightos-compute-"
  image_id      = data.aws_ami.ubuntu.id
  instance_type = var.enable_gpu ? "g4dn.xlarge" : var.instance_type

  iam_instance_profile {
    arn = aws_iam_instance_profile.lightos_profile.arn
  }

  network_interfaces {
    associate_public_ip_address = true
    security_groups            = [aws_security_group.lightos_sg.id]
  }

  user_data = base64encode(local.user_data)

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "lightos-compute-node"
      Role = "compute"
    }
  }
}

# Auto Scaling Group for compute nodes
resource "aws_autoscaling_group" "lightos_compute" {
  name                = "lightos-compute-asg"
  vpc_zone_identifier = [aws_subnet.lightos_subnet.id]
  desired_capacity    = var.num_compute_nodes
  max_size           = var.num_compute_nodes * 2
  min_size           = 1

  launch_template {
    id      = aws_launch_template.lightos_compute.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "lightos-compute"
    propagate_at_launch = true
  }
}

# ElastiCache Redis for distributed KV cache
resource "aws_elasticache_subnet_group" "lightos_cache" {
  name       = "lightos-cache-subnet"
  subnet_ids = [aws_subnet.lightos_subnet.id]
}

resource "aws_elasticache_cluster" "lightos_kv_cache" {
  cluster_id           = "lightos-kv-cache"
  engine               = "redis"
  node_type            = "cache.t3.medium"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.lightos_cache.name
  security_group_ids   = [aws_security_group.lightos_sg.id]

  tags = {
    Name = "lightos-kv-cache"
  }
}

# Application Load Balancer
resource "aws_lb" "lightos_alb" {
  name               = "lightos-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.lightos_sg.id]
  subnets            = [aws_subnet.lightos_subnet.id, aws_subnet.lightos_subnet2.id]

  tags = {
    Name = "lightos-alb"
  }
}

# Second subnet for ALB (requires 2 AZs)
resource "aws_subnet" "lightos_subnet2" {
  vpc_id                  = aws_vpc.lightos_vpc.id
  cidr_block             = "10.0.2.0/24"
  availability_zone      = data.aws_availability_zones.available.names[1]
  map_public_ip_on_launch = true

  tags = {
    Name = "lightos-subnet-2"
  }
}

resource "aws_route_table_association" "lightos_rta2" {
  subnet_id      = aws_subnet.lightos_subnet2.id
  route_table_id = aws_route_table.lightos_rt.id
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]  # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Outputs
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.lightos_vpc.id
}

output "alb_dns_name" {
  description = "Application Load Balancer DNS name"
  value       = aws_lb.lightos_alb.dns_name
}

output "redis_endpoint" {
  description = "Redis cluster endpoint for KV cache"
  value       = aws_elasticache_cluster.lightos_kv_cache.cache_nodes[0].address
}

output "compute_asg_name" {
  description = "Auto Scaling Group name for compute nodes"
  value       = aws_autoscaling_group.lightos_compute.name
}
