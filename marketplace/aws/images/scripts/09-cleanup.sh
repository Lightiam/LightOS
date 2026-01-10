#!/bin/bash
# 09-cleanup.sh
# Clean up before creating AMI

set -e

echo "================================================"
echo "Step 9: Cleaning up"
echo "================================================"

# Clean apt cache
sudo apt-get clean
sudo apt-get autoclean
sudo apt-get autoremove -y

# Remove temporary files
sudo rm -rf /tmp/*
sudo rm -rf /var/tmp/*

# Clear log files
sudo find /var/log -type f -name "*.log" -exec truncate -s 0 {} \;
sudo find /var/log -type f -name "*.gz" -delete
sudo find /var/log -type f -name "*.1" -delete

# Clear bash history
cat /dev/null > ~/.bash_history
history -c

# Remove SSH host keys (will be regenerated on first boot)
sudo rm -f /etc/ssh/ssh_host_*

# Remove cloud-init artifacts
sudo cloud-init clean --logs --seed

# Remove machine-id (will be regenerated)
sudo truncate -s 0 /etc/machine-id
sudo rm -f /var/lib/dbus/machine-id
sudo ln -s /etc/machine-id /var/lib/dbus/machine-id

# Clear network interface persistence
sudo rm -f /etc/udev/rules.d/70-persistent-net.rules

# Remove any leftover credentials
sudo find / -name "authorized_keys" -type f -delete 2>/dev/null || true
sudo find / -name ".aws" -type d -exec rm -rf {} \; 2>/dev/null || true
sudo find / -name ".ssh/id_*" -delete 2>/dev/null || true

# Clear pip cache
rm -rf ~/.cache/pip

# Clear Python cache
find /opt/lightos -type d -name __pycache__ -exec rm -rf {} \; 2>/dev/null || true
find /opt/lightos -type f -name "*.pyc" -delete 2>/dev/null || true

# Sync filesystem
sync

echo "✓ Cleanup completed"
