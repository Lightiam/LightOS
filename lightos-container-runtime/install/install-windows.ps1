# LightOS Container Runtime Installer for Windows
# Requires: Docker Desktop for Windows with WSL2 backend

#Requires -RunAsAdministrator

$ErrorActionPreference = "Stop"

Write-Host @"

╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║          LightOS Container Runtime Installer                 ║
║                        Windows                                ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# Check WSL2
Write-Host "Checking WSL2..." -ForegroundColor Blue

$wslVersion = wsl --status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: WSL2 not installed" -ForegroundColor Red
    Write-Host "Please install WSL2 first:" -ForegroundColor Yellow
    Write-Host "  wsl --install" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ WSL2 detected" -ForegroundColor Green

# Check Docker Desktop
Write-Host "`nChecking Docker Desktop..." -ForegroundColor Blue

$dockerRunning = docker version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker Desktop not running" -ForegroundColor Red
    Write-Host "Please start Docker Desktop" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Docker Desktop running" -ForegroundColor Green

# Check if using WSL2 backend
$dockerInfo = docker info --format "{{.OSType}}" 2>&1
if ($dockerInfo -ne "linux") {
    Write-Host "WARNING: Docker not using WSL2 backend" -ForegroundColor Yellow
    Write-Host "Please enable WSL2 backend in Docker Desktop settings" -ForegroundColor Yellow
}

# Install in WSL
Write-Host "`nInstalling LightOS runtime in WSL..." -ForegroundColor Blue

$installScript = @'
#!/bin/bash
set -e

echo "Installing LightOS Container Runtime..."

# Clone repository if not exists
if [ ! -d "/opt/lightos-container-runtime" ]; then
    git clone https://github.com/Lightiam/LightOS.git /opt/lightos-container-runtime
fi

cd /opt/lightos-container-runtime/lightos-container-runtime

# Run Linux installer
chmod +x install/install-linux.sh
sudo ./install/install-linux.sh

echo "Installation complete!"
'@

# Write script to temp file
$tempScript = [System.IO.Path]::GetTempFileName()
Set-Content -Path $tempScript -Value $installScript -Encoding ASCII

# Copy to WSL and execute
wsl -e bash -c "cat > /tmp/install-lightos.sh" < $tempScript
wsl -e bash -c "chmod +x /tmp/install-lightos.sh && /tmp/install-lightos.sh"

Remove-Item $tempScript

Write-Host "`n✓ Installation complete!" -ForegroundColor Green

# Display usage
Write-Host @"

╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║          ✓ Installation Complete!                            ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

Usage:

  # Run container with automatic GPU selection:
  docker run --runtime=lightos your-image:latest

  # Run with specific GPU type:
  docker run --runtime=lightos `
    -e LIGHTOS_DEVICE_TYPE=nvidia `
    -e LIGHTOS_MIN_VRAM=8GB `
    -e LIGHTOS_STRATEGY=performance `
    your-image:latest

  # Detect available devices:
  wsl lightos-runtime detect

  # View runtime info:
  wsl lightos-runtime info

Documentation: https://github.com/Lightiam/LightOS

Happy computing! 🚀

"@ -ForegroundColor Blue

# Optional: Create desktop shortcut
$createShortcut = Read-Host "`nCreate desktop shortcut for LightOS tools? (Y/N)"
if ($createShortcut -eq "Y" -or $createShortcut -eq "y") {
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\LightOS Runtime.lnk")
    $Shortcut.TargetPath = "wsl.exe"
    $Shortcut.Arguments = "lightos-runtime detect"
    $Shortcut.IconLocation = "powershell.exe,0"
    $Shortcut.Save()

    Write-Host "✓ Desktop shortcut created" -ForegroundColor Green
}

Write-Host "`nInstallation finished!" -ForegroundColor Green
