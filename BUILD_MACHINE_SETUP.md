# LightOS Build Machine Setup Guide

## WHERE TO RUN THESE COMMANDS

This guide explains exactly where and how to build LightOS VM images.

---

## 🖥️ Build Machine Requirements

### You Need a Linux Machine for Building

**Supported Systems:**
- ✅ Ubuntu 22.04 or newer (Recommended)
- ✅ Debian 11 or newer
- ✅ Fedora 38 or newer
- ✅ Other Linux distros (may need package adjustments)

**NOT Supported for Building:**
- ❌ Windows directly (use WSL2 Ubuntu instead)
- ⚠️ macOS (limited support, some tools may not work)

**Hardware Requirements:**
- **RAM**: 8GB minimum, 16GB recommended
- **Disk**: 10GB free space
- **CPU**: Any modern CPU (4+ cores recommended)
- **Internet**: Required for downloading packages

---

## 🚀 Complete Setup Instructions

Choose your scenario:

---

## Scenario 1: You Have Ubuntu 22.04+ Desktop ✅ (Easiest)

Perfect! Your current machine is ready to be the build machine.

### Step 1: Open Terminal

Press `Ctrl+Alt+T` or search for "Terminal" in applications

### Step 2: Install Prerequisites

```bash
# Update system
sudo apt update

# Install VirtualBox
sudo apt install -y virtualbox

# Install build tools
sudo apt install -y \
    git \
    qemu-utils \
    libguestfs-tools \
    virt-builder \
    debootstrap \
    squashfs-tools \
    genisoimage
```

### Step 3: Clone LightOS Repository

```bash
# Navigate to your home directory
cd ~

# Clone the repository
git clone https://github.com/Lightiam/LightOS.git

# Enter the directory
cd LightOS

# Verify you're in the right place
pwd
# Should show: /home/YOUR_USERNAME/LightOS

ls
# Should show: build-system/, deployment/, kernel/, etc.
```

### Step 4: Build VM Image

```bash
# Make sure you're in the LightOS directory
cd ~/LightOS

# Build VirtualBox VM image
sudo ./build-system/build-vm-image.sh vdi
```

**This will take 10-15 minutes.**

You'll see output like:
```
    ╦  ┬┌─┐┬ ┬┌┬┐╔═╗╔═╗
    ║  ││ ┬├─┤ │ ║ ║╚═╗
    ╩═╝┴└─┘┴ ┴ ┴ ╚═╝╚═╝
    VM Image Builder v0.2.1

[VM-BUILDER] Checking dependencies...
[VM-BUILDER] All dependencies satisfied
[STEP] Building VM image with virt-builder...
[STEP] Applying VM-specific optimizations...
[STEP] Converting to VirtualBox VDI format...
[VM-BUILDER] VDI created: output-vm/lightos-0.2.1.vdi
```

### Step 5: Import into VirtualBox

```bash
# Still in ~/LightOS directory
./deployment/vm/setup-virtualbox.sh
```

**This will:**
- Create VM in VirtualBox
- Configure it automatically
- Start the VM

### Step 6: Access LightOS

**Option 1: VirtualBox Window** (opens automatically)
- Login: `lightos` / `lightos`

**Option 2: Web Browser** (on your build machine)
```bash
# Open browser
firefox http://localhost:8080
# Or
google-chrome http://localhost:8080
# Or just open: http://localhost:8080
```

**Option 3: SSH** (from your build machine terminal)
```bash
ssh -p 2222 lightos@localhost
```

---

## Scenario 2: You Have Windows PC 💻

You need to use WSL2 (Windows Subsystem for Linux).

### Step 1: Install WSL2 with Ubuntu

Open **PowerShell as Administrator** and run:

```powershell
# Install WSL2
wsl --install -d Ubuntu-22.04

# Reboot if prompted
```

After reboot, Ubuntu will open automatically.

### Step 2: Setup Ubuntu in WSL2

```bash
# Update Ubuntu
sudo apt update && sudo apt upgrade -y

# Install build tools
sudo apt install -y \
    git \
    qemu-utils \
    libguestfs-tools \
    virt-builder \
    debootstrap \
    squashfs-tools \
    genisoimage
```

### Step 3: Install VirtualBox on Windows

**Download** from https://www.virtualbox.org/

**Install** normally (on Windows, not in WSL)

### Step 4: Clone LightOS in WSL2

```bash
# In WSL2 Ubuntu terminal
cd ~
git clone https://github.com/Lightiam/LightOS.git
cd LightOS
```

### Step 5: Build VM Image

```bash
# In WSL2 Ubuntu terminal
cd ~/LightOS
sudo ./build-system/build-vm-image.sh vdi
```

### Step 6: Copy VDI to Windows

```bash
# Create shared location
mkdir -p /mnt/c/Users/YOUR_WINDOWS_USERNAME/LightOS-VM

# Copy VDI file
cp output-vm/lightos-0.2.1.vdi /mnt/c/Users/YOUR_WINDOWS_USERNAME/LightOS-VM/
```

### Step 7: Import in VirtualBox (on Windows)

1. Open **VirtualBox** (on Windows)
2. Click **"New"**
3. Configure:
   ```
   Name: LightOS
   Type: Linux
   Version: Ubuntu (64-bit)
   Memory: 4096 MB
   ```
4. **Hard Disk**: Use existing → Browse to `C:\Users\YOUR_USERNAME\LightOS-VM\lightos-0.2.1.vdi`
5. **Create**

6. **Settings** → **Network** → **Port Forwarding**:
   - SSH: Host 2222 → Guest 22
   - Web: Host 8080 → Guest 8080

7. **Start VM**

### Step 8: Access LightOS

**On Windows:**
- Open browser: http://localhost:8080
- SSH: Use PuTTY or Windows Terminal: `ssh -p 2222 lightos@localhost`

---

## Scenario 3: You Have macOS 🍎

macOS has limited support. Better to use a Linux VM.

### Option A: Install Ubuntu VM First (Recommended)

1. Install VirtualBox on macOS
2. Create Ubuntu 22.04 VM
3. Follow "Scenario 1" inside that Ubuntu VM

### Option B: Try Native macOS (Experimental)

```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install tools
brew install qemu libguestfs

# Clone LightOS
cd ~
git clone https://github.com/Lightiam/LightOS.git
cd LightOS

# Try to build (may have issues)
sudo ./build-system/build-vm-image.sh vdi
```

**Note**: Some tools may not work on macOS. Ubuntu VM recommended.

---

## Scenario 4: You Have a Linux Server (No GUI) 🖥️

Perfect for building!

### Step 1: SSH into Server

```bash
ssh your-username@your-server-ip
```

### Step 2: Install Prerequisites

```bash
# Update system
sudo apt update

# Install build tools (no VirtualBox needed on server)
sudo apt install -y \
    git \
    qemu-utils \
    libguestfs-tools \
    virt-builder \
    debootstrap \
    squashfs-tools \
    genisoimage
```

### Step 3: Clone and Build

```bash
cd ~
git clone https://github.com/Lightiam/LightOS.git
cd LightOS

# Build VM image
sudo ./build-system/build-vm-image.sh vdi
```

### Step 4: Transfer to Your Desktop

```bash
# On your desktop/laptop (with VirtualBox installed)
# Download the VDI file
scp your-username@your-server-ip:~/LightOS/output-vm/lightos-0.2.1.vdi ~/Downloads/

# Then import in VirtualBox on your desktop
```

---

## 🗂️ Directory Structure Explanation

After cloning, you'll have this structure:

```
LightOS/                           ← Main directory (you'll be here)
├── build-system/                  ← Build scripts location
│   ├── lightos-builder.sh         ← ISO builder
│   ├── build-vm-image.sh          ← VM image builder ⭐
│   ├── edge-profiles/             ← Hardware profiles
│   └── hardware-detection/        ← Auto-detection scripts
├── deployment/                    ← Deployment scripts
│   ├── vm/
│   │   ├── setup-virtualbox.sh   ← VirtualBox automation ⭐
│   │   ├── setup-kvm.sh           ← KVM automation
│   │   └── Vagrantfile            ← Vagrant config
│   ├── edge/                      ← Edge deployment
│   └── aws/                       ← AWS deployment
├── kernel/                        ← Kernel modules
├── fabric-os/                     ← FabricOS components
├── llm-training-ground/           ← Training UI
├── output-vm/                     ← VM images go here (created during build)
└── output/                        ← ISO images go here (created during build)
```

**Important Locations:**

- **Build scripts**: `build-system/`
- **Setup scripts**: `deployment/vm/`
- **Output**: `output-vm/` (VMs) or `output/` (ISOs)

---

## 📋 Command Summary by Location

### Commands to Run on Build Machine

```bash
# Navigate to LightOS directory
cd ~/LightOS

# Build VM image (Method 1 - Recommended)
sudo ./build-system/build-vm-image.sh vdi

# OR build bootable ISO (Method 2)
sudo ./build-system/lightos-builder.sh amd64 iso

# Import VM into VirtualBox (Method 1)
./deployment/vm/setup-virtualbox.sh
```

### Commands to Run Inside VM (After It Starts)

```bash
# Change password
passwd

# Check services
systemctl status lightos-*

# View hardware report
cat /etc/lightos/hardware-report.json

# Check logs
journalctl -u lightos-autopilot -f
```

### Commands to Run on Build Machine to Access VM

```bash
# SSH to VM
ssh -p 2222 lightos@localhost

# Or just open browser
firefox http://localhost:8080
```

---

## ⚠️ Common Mistakes

### Mistake 1: Running on Windows Directly

```bash
# ❌ WRONG - This won't work on Windows CMD/PowerShell
C:\> ./build-system/build-vm-image.sh

# ✅ CORRECT - Use WSL2 Ubuntu
PS> wsl -d Ubuntu-22.04
$ cd /home/your-username/LightOS
$ sudo ./build-system/build-vm-image.sh vdi
```

### Mistake 2: Wrong Directory

```bash
# ❌ WRONG - Not in LightOS directory
$ pwd
/home/user
$ ./build-system/build-vm-image.sh
bash: ./build-system/build-vm-image.sh: No such file or directory

# ✅ CORRECT - In LightOS directory
$ cd ~/LightOS
$ pwd
/home/user/LightOS
$ sudo ./build-system/build-vm-image.sh vdi
```

### Mistake 3: Forgetting sudo

```bash
# ❌ WRONG - Missing sudo
$ ./build-system/build-vm-image.sh vdi
Permission denied

# ✅ CORRECT - With sudo
$ sudo ./build-system/build-vm-image.sh vdi
```

### Mistake 4: Running VM Commands on Build Machine

```bash
# These commands only work INSIDE the VM, not on build machine:
$ systemctl status lightos-*          # ❌ Won't work on build machine
$ cat /etc/lightos/hardware-report.json  # ❌ Won't work on build machine

# First SSH into VM:
$ ssh -p 2222 lightos@localhost        # ✅ Connect to VM
$ systemctl status lightos-*            # ✅ Now it works
```

---

## 🔍 Verification Checklist

### On Build Machine (Before Building)

```bash
# Check you're in right directory
pwd
# Should show: /home/YOUR_USERNAME/LightOS

# Check files exist
ls build-system/build-vm-image.sh
# Should show: build-system/build-vm-image.sh

# Check VirtualBox installed
VBoxManage --version
# Should show: 7.0.x or similar
```

### During Build

```bash
# You should see:
[VM-BUILDER] Checking dependencies...
[VM-BUILDER] All dependencies satisfied
[STEP] Building VM image with virt-builder...

# NOT errors like:
command not found
Permission denied (forgot sudo)
No such file or directory (wrong directory)
```

### After Build

```bash
# Check output file exists
ls -lh output-vm/lightos-0.2.1.vdi
# Should show: ~2-3 GB file
```

---

## 🆘 Quick Troubleshooting

### "Command not found"

**Problem**: Build tools not installed

**Solution**:
```bash
sudo apt install qemu-utils libguestfs-tools virt-builder
```

### "Permission denied"

**Problem**: Forgot sudo

**Solution**:
```bash
# Add sudo
sudo ./build-system/build-vm-image.sh vdi
```

### "No such file or directory"

**Problem**: Wrong directory

**Solution**:
```bash
# Go to LightOS directory
cd ~/LightOS
pwd  # Verify location
```

### "virt-builder: command not found"

**Problem**: Missing libguestfs-tools

**Solution**:
```bash
sudo apt install libguestfs-tools
```

---

## 📞 Need Help?

**Before asking for help, provide:**

1. **Your build OS**: `cat /etc/os-release`
2. **Directory location**: `pwd`
3. **Error message**: Copy full error
4. **Command used**: What you typed

**Example help request:**
```
I'm on Ubuntu 22.04, in /home/user/LightOS
Running: sudo ./build-system/build-vm-image.sh vdi
Error: virt-builder: command not found
```

---

## ✅ Success Indicators

You'll know it worked when:

1. **Build completes** with:
   ```
   [VM-BUILDER] VDI created: output-vm/lightos-0.2.1.vdi
   ```

2. **VirtualBox VM starts** and shows:
   ```
       ╦  ┬┌─┐┬ ┬┌┬┐╔═╗╔═╗
       ║  ││ ┬├─┤ │ ║ ║╚═╗
       ╩═╝┴└─┘┴ ┴ ┴ ╚═╝╚═╝
   ```

3. **Browser opens**: http://localhost:8080 shows LLM Training Ground

4. **SSH works**: `ssh -p 2222 lightos@localhost` connects

---

## 🎯 Quick Start (Copy-Paste)

**For Ubuntu 22.04 Desktop:**

```bash
# Install everything
sudo apt update
sudo apt install -y virtualbox git qemu-utils libguestfs-tools virt-builder

# Clone and build
cd ~
git clone https://github.com/Lightiam/LightOS.git
cd LightOS
sudo ./build-system/build-vm-image.sh vdi

# Import and start
./deployment/vm/setup-virtualbox.sh

# Access
firefox http://localhost:8080
```

**Total time**: 15-20 minutes

---

**LightOS v0.2.1 - Build Machine Setup**
*Know Where You Are, Know What to Run*
