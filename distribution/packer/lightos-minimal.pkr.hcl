# Packer template for LightOS Minimal VM (CPU-only, 8GB disk)
# Build: packer build lightos-minimal.pkr.hcl
# Result: lightos-minimal-v1.0.ova (VirtualBox/VMware compatible)

packer {
  required_plugins {
    virtualbox = {
      version = ">= 1.0.0"
      source  = "github.com/hashicorp/virtualbox"
    }
    vmware = {
      version = ">= 1.0.0"
      source  = "github.com/hashicorp/vmware"
    }
  }
}

variable "vm_name" {
  type    = string
  default = "lightos-minimal-v1.0"
}

variable "iso_url" {
  type    = string
  default = "https://releases.ubuntu.com/22.04.3/ubuntu-22.04.3-live-server-amd64.iso"
}

variable "iso_checksum" {
  type    = string
  default = "sha256:a4acfda10b18da50e2ec50ccaf860d7f20b389df8765611142305c0e911d16fd"
}

# VirtualBox Builder
source "virtualbox-iso" "lightos-minimal" {
  guest_os_type        = "Ubuntu_64"
  vm_name              = var.vm_name
  iso_url              = var.iso_url
  iso_checksum         = var.iso_checksum

  # Hardware specs
  cpus                 = 2
  memory               = 4096
  disk_size            = 8192  # 8GB
  hard_drive_interface = "sata"

  # Network
  guest_additions_mode = "upload"
  headless             = false

  # SSH settings for provisioning
  ssh_username         = "lightos"
  ssh_password         = "lightos123"
  ssh_timeout          = "20m"

  # Shutdown command
  shutdown_command     = "echo 'lightos123' | sudo -S shutdown -P now"

  # Export settings
  format               = "ova"
  export_opts = [
    "--manifest",
    "--vsys", "0",
    "--description", "LightOS Minimal - CPU-only inference environment",
    "--version", "1.0.0"
  ]

  # Boot command for automated installation
  boot_command = [
    "<esc><wait>",
    "linux /casper/vmlinuz autoinstall ds=nocloud-net;s=http://{{ .HTTPIP }}:{{ .HTTPPort }}/ <wait>",
    "--- <wait>",
    "initrd /casper/initrd <wait>",
    "boot <wait>"
  ]

  boot_wait = "5s"
  http_directory = "http"
}

# VMware Builder
source "vmware-iso" "lightos-minimal" {
  guest_os_type        = "ubuntu-64"
  vm_name              = var.vm_name
  iso_url              = var.iso_url
  iso_checksum         = var.iso_checksum

  # Hardware specs
  cpus                 = 2
  memory               = 4096
  disk_size            = 8192
  disk_type_id         = "0"

  # VMware tools
  tools_upload_flavor  = "linux"

  # SSH settings
  ssh_username         = "lightos"
  ssh_password         = "lightos123"
  ssh_timeout          = "20m"

  # Shutdown
  shutdown_command     = "echo 'lightos123' | sudo -S shutdown -P now"

  # Boot command
  boot_command = [
    "<esc><wait>",
    "linux /casper/vmlinuz autoinstall ds=nocloud-net;s=http://{{ .HTTPIP }}:{{ .HTTPPort }}/ <wait>",
    "--- <wait>",
    "initrd /casper/initrd <wait>",
    "boot <wait>"
  ]

  boot_wait = "5s"
  http_directory = "http"
}

# Provisioning
build {
  sources = [
    "source.virtualbox-iso.lightos-minimal",
    "source.vmware-iso.lightos-minimal"
  ]

  # Wait for cloud-init
  provisioner "shell" {
    inline = [
      "while [ ! -f /var/lib/cloud/instance/boot-finished ]; do echo 'Waiting for cloud-init...'; sleep 1; done"
    ]
  }

  # Update system
  provisioner "shell" {
    inline = [
      "sudo apt-get update",
      "sudo apt-get upgrade -y",
      "sudo apt-get install -y build-essential cmake ninja-build python3-pip python3-dev",
      "sudo apt-get install -y git curl wget htop vim"
    ]
  }

  # Install LightOS dependencies
  provisioner "shell" {
    inline = [
      "sudo apt-get install -y libgomp1 libopenblas-dev libnuma1",
      "pip3 install --upgrade pip",
      "pip3 install numpy onnx protobuf"
    ]
  }

  # Clone and build LightOS
  provisioner "shell" {
    inline = [
      "cd /home/lightos",
      "git clone https://github.com/lightiam/lightos.git",
      "cd lightos/inference-subsystem/core",
      "cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF",
      "cmake --build build --parallel",
      "sudo cmake --install build"
    ]
  }

  # Install Python bindings
  provisioner "shell" {
    inline = [
      "cd /home/lightos/lightos/inference-subsystem/python-bindings",
      "pip3 install -e ."
    ]
  }

  # Install gRPC server
  provisioner "file" {
    source      = "../../inference-subsystem/deployment/grpc_server.py"
    destination = "/home/lightos/lightos-server.py"
  }

  # Create systemd service
  provisioner "file" {
    source      = "../systemd/lightos.service"
    destination = "/tmp/lightos.service"
  }

  provisioner "shell" {
    inline = [
      "sudo mv /tmp/lightos.service /etc/systemd/system/",
      "sudo systemctl daemon-reload",
      "sudo systemctl enable lightos"
    ]
  }

  # Setup welcome message
  provisioner "shell" {
    inline = [
      "echo '#!/bin/bash' | sudo tee /etc/profile.d/lightos-welcome.sh",
      "echo 'cat <<EOF' | sudo tee -a /etc/profile.d/lightos-welcome.sh",
      "echo '╔════════════════════════════════════════════════════════════╗' | sudo tee -a /etc/profile.d/lightos-welcome.sh",
      "echo '║  LightOS Minimal v1.0 - CPU Inference Environment         ║' | sudo tee -a /etc/profile.d/lightos-welcome.sh",
      "echo '╠════════════════════════════════════════════════════════════╣' | sudo tee -a /etc/profile.d/lightos-welcome.sh",
      "echo '║  Quick Start:                                              ║' | sudo tee -a /etc/profile.d/lightos-welcome.sh",
      "echo '║    python3 -c \"from lightos_accelerated import *\"         ║' | sudo tee -a /etc/profile.d/lightos-welcome.sh",
      "echo '║    systemctl start lightos   # Start gRPC server           ║' | sudo tee -a /etc/profile.d/lightos-welcome.sh",
      "echo '║                                                            ║' | sudo tee -a /etc/profile.d/lightos-welcome.sh",
      "echo '║  Examples: ~/lightos/inference-subsystem/notebooks/        ║' | sudo tee -a /etc/profile.d/lightos-welcome.sh",
      "echo '║  Docs:     ~/lightos/inference-subsystem/docs/             ║' | sudo tee -a /etc/profile.d/lightos-welcome.sh",
      "echo '╚════════════════════════════════════════════════════════════╝' | sudo tee -a /etc/profile.d/lightos-welcome.sh",
      "echo 'EOF' | sudo tee -a /etc/profile.d/lightos-welcome.sh",
      "sudo chmod +x /etc/profile.d/lightos-welcome.sh"
    ]
  }

  # Clean up
  provisioner "shell" {
    inline = [
      "sudo apt-get autoremove -y",
      "sudo apt-get clean",
      "sudo rm -rf /tmp/*",
      "sudo rm -rf /var/tmp/*",
      "history -c"
    ]
  }

  # Post-processor: Create OVA
  post-processor "shell-local" {
    inline = [
      "echo 'LightOS Minimal VM built successfully!'",
      "echo 'Import with: VBoxManage import ${var.vm_name}.ova'",
      "echo 'Credentials: lightos / lightos123'"
    ]
  }
}
