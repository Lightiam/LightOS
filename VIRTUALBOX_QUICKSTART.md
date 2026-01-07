# LightOS VirtualBox Quick Setup Guide

**Choose your deployment method:**

---

## Method 1: Pre-built VM Image ⭐ RECOMMENDED (5-10 minutes)

This creates a VirtualBox image with LightOS already installed and configured.

### Prerequisites

1. **Install VirtualBox**:
   - **Windows/macOS**: Download from https://www.virtualbox.org/
   - **Ubuntu/Debian**: `sudo apt install virtualbox`
   - **Fedora**: `sudo dnf install VirtualBox`

2. **Install build dependencies** (on your host machine):
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install -y qemu-utils libguestfs-tools virt-builder

   # Fedora
   sudo dnf install qemu-img libguestfs-tools virt-install

   # macOS (via Homebrew)
   brew install qemu libguestfs
   ```

### Step-by-Step Instructions

#### Step 1: Navigate to LightOS Directory

```bash
cd /path/to/LightOS
```

#### Step 2: Build VirtualBox VDI Image

This creates a pre-installed VirtualBox disk image:

```bash
sudo ./build-system/build-vm-image.sh vdi
```

**What happens:**
- Downloads Ubuntu 22.04 base (~300 MB download)
- Installs LightOS components
- Configures services
- Installs VirtualBox Guest Additions
- Creates VDI file

**Time**: 10-15 minutes
**Output**: `output-vm/lightos-0.2.1.vdi` (~2-3 GB)

**Progress indicators:**
```
[VM-BUILDER] Checking dependencies...
[STEP] Building VM image with virt-builder...
[STEP] Applying VM-specific optimizations...
[STEP] Converting to VirtualBox VDI format...
[VM-BUILDER] VDI created: output-vm/lightos-0.2.1.vdi
```

#### Step 3: Import into VirtualBox (Automated)

```bash
./deployment/vm/setup-virtualbox.sh
```

**What this does:**
- Detects VirtualBox installation
- Creates new VM named "LightOS-NCE"
- Attaches the VDI disk
- Configures 4GB RAM, 4 CPUs
- Sets up port forwarding:
  - Host port 2222 → VM port 22 (SSH)
  - Host port 8080 → VM port 8080 (Web UI)
- Starts the VM

**Output:**
```
[VBOX-SETUP] VirtualBox 7.0.x detected
[STEP] Creating VM from VDI...
[STEP] Configuring port forwarding...
[VBOX-SETUP] VM created successfully
[VBOX-SETUP] VM started!

Access LightOS:
  • Console: VirtualBox window
  • SSH: ssh -p 2222 lightos@localhost
  • Web UI: http://localhost:8080

Default credentials:
  • Username: lightos
  • Password: lightos
```

#### Step 4: Access LightOS

**Option A: VirtualBox Console**
- The VM window will open automatically
- Login: `lightos` / `lightos`

**Option B: SSH from Host**
```bash
ssh -p 2222 lightos@localhost
```

**Option C: Web UI**
Open in browser: http://localhost:8080

#### Step 5: Change Default Password

```bash
# Inside VM
passwd
# Enter new password

# Change root password too
sudo passwd root
```

#### Step 6: Verify Installation

```bash
# Check LightOS services
systemctl status lightos-*

# View hardware detection
cat /etc/lightos/hardware-report.json

# Check kernel modules
lsmod | grep lightos
```

### That's it! 🎉

Your LightOS VM is ready to use!

---

## Method 2: Install from LightOS Bootable ISO (30-40 minutes)

This is like installing a real operating system - you boot from ISO and install.

### Step 1: Build LightOS Bootable ISO

```bash
cd /path/to/LightOS
sudo ./build-system/lightos-builder.sh amd64 iso
```

**Time**: 15-20 minutes
**Output**: `output/lightos-0.2.1-amd64.iso` (~1.5 GB)

**What this creates:**
- Complete bootable operating system
- Based on Ubuntu 22.04 LTS
- All LightOS components integrated
- Bootloader configured
- Installation wizard included

### Step 2: Create New VM in VirtualBox

**Manual Creation:**

1. **Open VirtualBox**

2. **Click "New"**

3. **Configure VM**:
   ```
   Name: LightOS
   Type: Linux
   Version: Ubuntu (64-bit)
   ```
   Click "Next"

4. **Memory Size**:
   ```
   4096 MB (4GB)
   ```
   Adjust if you have more RAM available
   Click "Next"

5. **Hard Disk**:
   - Select: "Create a virtual hard disk now"
   - Click "Create"

6. **Hard Disk File Type**:
   - Select: "VDI (VirtualBox Disk Image)"
   - Click "Next"

7. **Storage on Physical Hard Disk**:
   - Select: "Dynamically allocated"
   - Click "Next"

8. **File Location and Size**:
   ```
   20 GB (minimum)
   50 GB (recommended)
   ```
   Click "Create"

### Step 3: Configure VM Settings

1. **Right-click VM** → **Settings**

2. **System** tab:
   - **Processor**: Set to 4 CPUs (or more)
   - **Enable PAE/NX**: ✓ Checked
   - **Acceleration**:
     - ✓ Enable VT-x/AMD-V
     - ✓ Enable Nested Paging

3. **Display** tab:
   - **Video Memory**: 128 MB
   - **Graphics Controller**: VMSVGA

4. **Storage** tab:
   - Click the empty CD icon under "Controller: IDE"
   - Click the CD icon on the right
   - Choose "Choose a disk file..."
   - Select `output/lightos-0.2.1-amd64.iso`

5. **Network** tab:
   - **Adapter 1**: Attached to: NAT
   - Click "Advanced" → "Port Forwarding"
   - Add rules:
     ```
     Name: SSH,  Protocol: TCP, Host Port: 2222, Guest Port: 22
     Name: Web,  Protocol: TCP, Host Port: 8080, Guest Port: 8080
     ```

6. **Click "OK"**

### Step 4: Start VM and Install

1. **Start the VM**

2. **Boot Menu Appears**:
   ```
   LightOS Neural Compute Engine v0.2.1

   > Start LightOS (Live Mode)
     Install LightOS to Disk
     Start LightOS (Safe Mode)
   ```

3. **Select "Install LightOS to Disk"** using arrow keys, press Enter

4. **Installation Wizard**:

   **Disk Selection:**
   ```
   Detecting available disks...
   [1] /dev/sda - 20GB

   Select disk number [1]: 1
   ```
   Press Enter

   **Confirmation:**
   ```
   ⚠️  WARNING ⚠️
   You are about to install LightOS on: /dev/sda
   Type 'yes' to continue: yes
   ```
   Type `yes` and press Enter

   **Installation Progress:**
   ```
   [INSTALLER] Partitioning disk: /dev/sda
   [INSTALLER] Formatting partitions...
   [INSTALLER] Installing base system (this may take several minutes)...
   [INSTALLER] Configuring system...
   [INSTALLER] Installing GRUB bootloader...
   [INSTALLER] Installing LightOS components...
   ```

5. **Installation Complete**:
   ```
   ═══════════════════════════════════════════
      LightOS Installation Complete! ✓
   ═══════════════════════════════════════════

   Installation Summary:
     • Device: /dev/sda
     • Hostname: lightos-edge
     • Default Username: lightos
     • Default Password: lightos

   ⚠️  Please change default passwords after first boot!

   Press Enter to reboot...
   ```

6. **Press Enter to reboot**

7. **Remove ISO**:
   - VM will reboot
   - VirtualBox → Devices → Optical Drives → Remove disk from virtual drive
   - Or: VM Settings → Storage → Remove ISO

### Step 5: First Boot

1. **VM Boots**:
   ```
       ╦  ┬┌─┐┬ ┬┌┬┐╔═╗╔═╗
       ║  ││ ┬├─┤ │ ║ ║╚═╗
       ╩═╝┴└─┘┴ ┴ ┴ ╚═╝╚═╝
   ```

2. **Hardware Detection Runs** (automatically on first boot):
   ```
   [HW-DETECT] LightOS Hardware Detection System v0.2.1
   [HW-DETECT] Architecture: amd64
   [HW-DETECT] Platform: virtual-machine
   [HW-DETECT] Total Memory: 4096 MB
   [HW-DETECT] GPU: none
   [HW-DETECT] Active profile: virtual-machine
   ```

3. **Login Prompt**:
   ```
   lightos-edge login: lightos
   Password: lightos
   ```

4. **Welcome Message**:
   ```
       ╦  ┬┌─┐┬ ┬┌┬┐╔═╗╔═╗
       ║  ││ ┬├─┤ │ ║ ║╚═╗
       ╩═╝┴└─┘┴ ┴ ┴ ╚═╝╚═╝
       Neural Compute Engine v0.2.1

   Welcome to LightOS - Edge Computing Ready!

   System Information:
     • Hardware Profile: /etc/lightos/hardware-report.json
     • LLM Training Ground: http://localhost:8080
     • System Metrics: /var/log/lightos/edge-metrics.log
   ```

5. **Change Password**:
   ```bash
   passwd
   # Enter new password

   sudo passwd root
   # Enter new root password
   ```

### Step 6: Verify Installation

```bash
# Check services
systemctl status lightos-*

# View hardware report
cat /etc/lightos/hardware-report.json

# Check network
ip addr show
```

### Step 7: Access from Host

**SSH:**
```bash
ssh -p 2222 lightos@localhost
```

**Web UI:**
Open browser: http://localhost:8080

---

## Method 3: Manual Ubuntu + LightOS Installation (Advanced)

If you want to install LightOS on an existing Ubuntu VM:

### Step 1: Create Ubuntu VM

1. Download Ubuntu 22.04 ISO from https://ubuntu.com/download/server
2. Create VM in VirtualBox
3. Install Ubuntu 22.04
4. Update system: `sudo apt update && sudo apt upgrade`

### Step 2: Install LightOS Components

```bash
# Clone LightOS repository
git clone https://github.com/your-org/LightOS.git
cd LightOS

# Install dependencies
sudo apt install -y build-essential linux-headers-$(uname -r) \
    dkms python3 python3-pip

# Copy LightOS components
sudo mkdir -p /opt/lightos /etc/lightos /usr/src/lightos-0.2.1
sudo cp -r kernel/modules/lightos-core /usr/src/lightos-0.2.1/
sudo cp -r kernel/drivers/photonic /usr/src/lightos-0.2.1/
sudo cp -r fabric-os/* /opt/lightos/
sudo cp -r llm-training-ground /opt/lightos/
sudo cp -r build-system/edge-profiles /opt/lightos/
sudo cp -r build-system/hardware-detection /opt/lightos/

# Build kernel modules
cd /usr/src/lightos-0.2.1/lightos-core
make
sudo make install

# Install Python dependencies
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip3 install transformers datasets accelerate

# Run hardware detection
sudo bash /opt/lightos/hardware-detection/detect-hardware.sh

# Create systemd services
# (Copy service files from build-system/lightos-builder.sh)

# Enable services
sudo systemctl enable lightrail-scheduler
sudo systemctl enable lightos-autopilot
sudo systemctl enable lightos-kvcache

# Start services
sudo systemctl start lightrail-scheduler
sudo systemctl start lightos-autopilot
sudo systemctl start lightos-kvcache
```

---

## Comparison of Methods

| Method | Time | Difficulty | When to Use |
|--------|------|------------|-------------|
| **Method 1: Pre-built VM** | 10 min | ⭐ Easy | **Recommended** - Fastest, automated |
| **Method 2: ISO Install** | 40 min | ⭐⭐ Medium | Learn installation process, custom partitioning |
| **Method 3: Manual** | 60 min | ⭐⭐⭐ Hard | Educational, existing Ubuntu VM |

---

## Troubleshooting

### Build Issues

**Problem**: virt-builder not found
```bash
# Ubuntu/Debian
sudo apt install libguestfs-tools

# macOS
brew install libguestfs
```

**Problem**: Permission denied
```bash
# Use sudo for build commands
sudo ./build-system/build-vm-image.sh vdi
```

### VirtualBox Issues

**Problem**: VT-x is disabled
- **Solution**: Enable VT-x/AMD-V in BIOS
- Restart → Enter BIOS (F2/DEL/F12) → Enable Virtualization

**Problem**: VM won't start
- **Solution**: Check RAM allocation (reduce if needed)
- Disable Hyper-V on Windows:
  ```cmd
  bcdedit /set hypervisorlaunchtype off
  ```

**Problem**: Can't access web UI
- **Solution**: Check port forwarding in VM Settings → Network
- Verify service: `systemctl status lightrail-scheduler`

### Network Issues

**Problem**: No internet in VM
- **Solution**: VM Settings → Network → Adapter 1 → Attached to: NAT
- Or use Bridged Adapter for direct network access

**Problem**: Can't SSH to VM
- **Solution**: Verify port forwarding: Host 2222 → Guest 22
- Check SSH service: `systemctl status sshd`

---

## Quick Command Reference

```bash
# Build VDI image
sudo ./build-system/build-vm-image.sh vdi

# Build bootable ISO
sudo ./build-system/lightos-builder.sh amd64 iso

# Setup VirtualBox (automated)
./deployment/vm/setup-virtualbox.sh

# SSH to VM
ssh -p 2222 lightos@localhost

# Access web UI
open http://localhost:8080  # macOS
xdg-open http://localhost:8080  # Linux
start http://localhost:8080  # Windows

# Inside VM - check services
systemctl status lightos-*

# Inside VM - view logs
journalctl -u lightos-autopilot -f

# Inside VM - hardware report
cat /etc/lightos/hardware-report.json
```

---

## Next Steps

After your VM is running:

1. ✅ Change default passwords
2. ✅ Update system: `sudo apt update && sudo apt upgrade`
3. ✅ Explore LLM Training Ground: http://localhost:8080
4. ✅ Read documentation: `/opt/lightos/docs/`
5. ✅ Start training models!

---

## Support

- **Full VM Guide**: `deployment/vm/VM_DEPLOYMENT_GUIDE.md`
- **Edge Deployment**: `EDGE_QUICKSTART.md`
- **GitHub Issues**: https://github.com/your-org/LightOS/issues

---

**LightOS v0.2.1 - Neural Compute Engine**
*Virtual Machines Made Easy*
