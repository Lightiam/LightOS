#!/bin/bash
# 07-security-hardening.sh
# Security hardening for production AMI

set -e

echo "================================================"
echo "Step 7: Applying security hardening"
echo "================================================"

# Update SSH configuration
sudo tee -a /etc/ssh/sshd_config > /dev/null <<'EOF'

# LightOS Security Settings
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
ChallengeResponseAuthentication no
UsePAM yes
X11Forwarding no
PrintMotd no
AcceptEnv LANG LC_*
Subsystem sftp /usr/lib/openssh/sftp-server
EOF

# Configure firewall (UFW)
sudo apt-get install -y ufw

# Allow SSH
sudo ufw allow 22/tcp

# Allow LightOS Web UI
sudo ufw allow 8080/tcp

# Allow LightOS API
sudo ufw allow 8000/tcp

# Allow Jupyter
sudo ufw allow 8888/tcp

# Enable firewall (with --force to avoid prompt)
sudo ufw --force enable

# Configure automatic security updates
sudo apt-get install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades

# Set up log rotation
sudo tee /etc/logrotate.d/lightos > /dev/null <<'EOF'
/var/log/lightos/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 ubuntu ubuntu
    sharedscripts
}
EOF

# Disable unnecessary services
sudo systemctl disable bluetooth.service || true
sudo systemctl disable cups.service || true

# Set secure permissions
sudo chmod 700 /home/ubuntu/.ssh
sudo chmod 600 /home/ubuntu/.ssh/authorized_keys || true

# Create MOTD
sudo tee /etc/motd > /dev/null <<'EOF'
╦  ┬┌─┐┬ ┬┌┬┐╔═╗╔═╗
║  ││ ┬├─┤ │ ║ ║╚═╗
╩═╝┴└─┘┴ ┴ ┴ ╚═╝╚═╝

Neural Compute Engine v0.2.1
Fast LLM Training & AI Development

Quick Start:
  lightos          - Interactive UI
  lightos-train    - Train models
  lightos-code     - Code generation

Documentation: /opt/lightos/docs/
Logs: /var/log/lightos/

Instance Info: cat /var/log/lightos/aws-info.log
EOF

echo "✓ Security hardening completed"
