$ErrorActionPreference = "Stop"

Write-Host "Creating Python virtual environment..."
python -m venv venv

Write-Host "Activating virtual environment..."
$venvPath = Join-Path $PWD "venv\Scripts\python.exe"
$pipPath = Join-Path $PWD "venv\Scripts\pip.exe"

# Upgrade pip
& $venvPath -m pip install --upgrade pip

Write-Host "Installing dependencies..."
& $pipPath install -r ..\dcim-api\requirements.txt
& $pipPath install -r .\context-engine\requirements.txt
& $pipPath install -r .\router\requirements.txt
& $pipPath install -r .\inference-proxy\requirements.txt
& $pipPath install -r .\telemetry\requirements.txt

Write-Host "Ensuring data directory exists..."
$dataDir = Join-Path $PWD "data"
if (-Not (Test-Path $dataDir)) {
    New-Item -ItemType Directory -Force -Path $dataDir | Out-Null
}

$env:DATA_DIR = $dataDir

Write-Host "Running telemetry seed script..."
$env:DATA_DIR = $dataDir
& $venvPath .\telemetry\seed.py

Write-Host "Starting services in separate windows..."

# Function to start a service
function Start-ServiceWindow {
    param (
        [string]$Name,
        [string]$Dir,
        [int]$Port
    )
    $workingDir = Join-Path $PWD $Dir
    $pythonExe = Join-Path $PWD "venv\Scripts\python.exe"
    $title = "LightOS - $Name ($Port)"
    $command = "`$env:DATA_DIR='$dataDir'; title '$title'; & `'$pythonExe`' -m uvicorn main:app --host 0.0.0.0 --port $Port"
    
    Start-Process powershell -ArgumentList "-NoExit","-WindowStyle","Normal","-Command",$command -WorkingDirectory $workingDir
}

Start-ServiceWindow -Name "Context Engine" -Dir "context-engine" -Port 8010
Start-ServiceWindow -Name "Router API" -Dir "router" -Port 8011
Start-ServiceWindow -Name "Inference Proxy" -Dir "inference-proxy" -Port 8012
Start-ServiceWindow -Name "Telemetry API" -Dir "telemetry" -Port 8013

$dcimPython = Join-Path $PWD "venv\Scripts\python.exe"
$dcimDir = Join-Path $PWD "..\dcim-api"
$dcimCommand = "title 'LightOS - DCIM API (8001)'; & `'$dcimPython`' -m uvicorn main:app --host 0.0.0.0 --port 8001"
Start-Process powershell -ArgumentList "-NoExit","-Command",$dcimCommand -WorkingDirectory $dcimDir

Write-Host "All services have been started."
Write-Host "You can access the UI at: http://localhost:8001/dcim.html"
Write-Host "Press any key to close this installer..."

