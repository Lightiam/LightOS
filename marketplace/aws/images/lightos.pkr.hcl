packer {
  required_version = ">= 1.9.0"

  required_plugins {
    amazon = {
      version = ">= 1.2.0"
      source  = "github.com/hashicorp/amazon"
    }
  }
}

# Variables
variable "aws_region" {
  type    = string
  default = "us-east-1"
  description = "AWS region to build AMI"
}

variable "lightos_version" {
  type    = string
  default = "0.2.1"
  description = "LightOS version"
}

variable "instance_type" {
  type    = string
  default = "g4dn.xlarge"
  description = "EC2 instance type for building (requires GPU)"
}

variable "volume_size" {
  type    = number
  default = 100
  description = "Root volume size in GB"
}

variable "ami_name_prefix" {
  type    = string
  default = "LightOS"
  description = "Prefix for AMI name"
}

variable "ssh_username" {
  type    = string
  default = "ubuntu"
  description = "SSH username"
}

# Data source to get latest Ubuntu 22.04 AMI
data "amazon-ami" "ubuntu" {
  filters = {
    name                = "ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"
    root-device-type    = "ebs"
    virtualization-type = "hvm"
  }
  most_recent = true
  owners      = ["099720109477"] # Canonical
  region      = var.aws_region
}

# Source configuration
source "amazon-ebs" "lightos" {
  # AMI configuration
  ami_name        = "${var.ami_name_prefix}-${var.lightos_version}-{{timestamp}}"
  ami_description = "LightOS Neural Compute Engine v${var.lightos_version} - Fast LLM Training & AI Development Platform"

  # Instance configuration
  instance_type = var.instance_type
  region        = var.aws_region
  source_ami    = data.amazon-ami.ubuntu.id
  ssh_username  = var.ssh_username

  # Storage configuration
  launch_block_device_mappings {
    device_name           = "/dev/sda1"
    volume_size           = var.volume_size
    volume_type           = "gp3"
    iops                  = 3000
    throughput            = 125
    delete_on_termination = true
    encrypted             = false
  }

  # Network configuration
  associate_public_ip_address = true

  # SSH configuration
  ssh_timeout = "20m"

  # AMI configuration
  ena_support         = true
  sriov_support       = true
  force_deregister    = false
  force_delete_snapshot = false

  # Tags for AMI
  tags = {
    Name              = "${var.ami_name_prefix} v${var.lightos_version}"
    Version           = var.lightos_version
    OS                = "Ubuntu 22.04 LTS"
    Application       = "LightOS"
    Marketplace       = "AWS"
    BuildDate         = "{{timestamp}}"
    BaseAMI           = "{{.SourceAMI}}"
    BaseAMIName       = "{{.SourceAMIName}}"
  }

  # Tags for snapshot
  snapshot_tags = {
    Name        = "${var.ami_name_prefix} v${var.lightos_version} Snapshot"
    Version     = var.lightos_version
    Application = "LightOS"
  }

  # Instance tags during build
  run_tags = {
    Name = "Packer-LightOS-Builder"
    Purpose = "AMI-Build"
  }
}

# Build configuration
build {
  name    = "lightos-ami"
  sources = ["source.amazon-ebs.lightos"]

  # Wait for cloud-init to complete
  provisioner "shell" {
    inline = [
      "echo 'Waiting for cloud-init to complete...'",
      "cloud-init status --wait",
      "echo 'Cloud-init completed'"
    ]
  }

  # Update system
  provisioner "shell" {
    script = "${path.root}/scripts/01-system-update.sh"
    environment_vars = [
      "DEBIAN_FRONTEND=noninteractive"
    ]
  }

  # Install NVIDIA drivers
  provisioner "shell" {
    script = "${path.root}/scripts/02-install-nvidia.sh"
    environment_vars = [
      "DEBIAN_FRONTEND=noninteractive"
    ]
  }

  # Install base dependencies
  provisioner "shell" {
    script = "${path.root}/scripts/03-install-dependencies.sh"
    environment_vars = [
      "DEBIAN_FRONTEND=noninteractive"
    ]
  }

  # Upload LightOS source
  provisioner "file" {
    source      = "${path.root}/../../../"
    destination = "/tmp/LightOS"
  }

  # Install LightOS
  provisioner "shell" {
    script = "${path.root}/scripts/04-install-lightos.sh"
    environment_vars = [
      "LIGHTOS_VERSION=${var.lightos_version}"
    ]
  }

  # AWS-specific configuration
  provisioner "shell" {
    script = "${path.root}/scripts/05-configure-aws.sh"
  }

  # Create systemd services
  provisioner "shell" {
    script = "${path.root}/scripts/06-create-services.sh"
  }

  # Security hardening
  provisioner "shell" {
    script = "${path.root}/scripts/07-security-hardening.sh"
  }

  # CloudWatch agent
  provisioner "shell" {
    script = "${path.root}/scripts/08-install-cloudwatch.sh"
  }

  # Cleanup
  provisioner "shell" {
    script = "${path.root}/scripts/09-cleanup.sh"
  }

  # Validate installation
  provisioner "shell" {
    script = "${path.root}/scripts/10-validate.sh"
  }

  # Post-processor to create manifest
  post-processor "manifest" {
    output     = "manifest.json"
    strip_path = true
  }
}
