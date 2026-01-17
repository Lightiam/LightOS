# LightOS Setup Guide for WSL Ubuntu

Complete guide to run LightOS locally on WSL Ubuntu for development and testing.

## Prerequisites

- WSL2 with Ubuntu 22.04 or 24.04
- Windows 10/11 with WSL enabled

## Quick Setup

### Step 1: Clone Repository (if not already done)

```bash
cd ~
git clone https://github.com/Lightiam/LightOS.git
cd LightOS
git checkout claude/combine-lightos-functions-deploy-r5jOD
```

### Step 2: Install System Dependencies

```bash
# Update package list
sudo apt-get update

# Install Python 3.11 and dependencies
sudo apt-get install -y python3.11 python3.11-venv python3-pip curl build-essential

# Install Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installations
python3.11 --version
node --version
npm --version
```

### Step 3: Setup Backend

```bash
cd ~/LightOS

# Create Python virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r dcim-api/requirements.txt
```

### Step 4: Setup Frontend

```bash
cd ~/LightOS/web-ui

# Install Node.js dependencies
npm install

# Build for production (optional, for testing production build)
npm run build
```

## Running LightOS

### Development Mode (Recommended for Testing)

**Terminal 1: Start Backend API**

```bash
cd ~/LightOS
source venv/bin/activate
cd dcim-api
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001
```

**Terminal 2: Start Frontend Dev Server**

```bash
cd ~/LightOS/web-ui
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: http://192.168.x.x:3000/
```

**Access the Application:**

- Frontend UI: http://localhost:3000
- API Docs: http://localhost:8001/docs
- Health Check: http://localhost:8001/health

The frontend dev server will proxy API requests to the backend automatically.

### Production Mode (Test Production Build)

**Build Frontend:**

```bash
cd ~/LightOS/web-ui
npm run build
```

**Run Backend (serves both API and frontend):**

```bash
cd ~/LightOS
source venv/bin/activate
cd dcim-api
python main.py
```

**Access:**

- Full Application: http://localhost:8001
- API Docs: http://localhost:8001/docs

## Verify Everything Works

### Test Backend API

```bash
# Health check
curl http://localhost:8001/health

# Get KPI data
curl http://localhost:8001/api/dcim/kpi

# Get providers
curl http://localhost:8001/api/providers
```

### Test Frontend

1. Open browser to http://localhost:3000 (dev) or http://localhost:8001 (prod)
2. You should see the LightOS Dashboard
3. Navigate through:
   - Dashboard
   - Fleet Explorer
   - DCIM Control
   - HCI Orchestrator
   - Workloads
   - Cost Control

### Test WebSocket

```bash
# Install wscat if needed
npm install -g wscat

# Connect to WebSocket
wscat -c ws://localhost:8001/ws/dcim

# You should see real-time telemetry streaming
```

## Common Issues

### Port Already in Use

```bash
# Check what's using port 8001
sudo lsof -i :8001

# Kill process if needed
sudo kill -9 <PID>
```

### Python Module Not Found

```bash
# Make sure virtual environment is activated
source ~/LightOS/venv/bin/activate

# Reinstall dependencies
pip install -r dcim-api/requirements.txt
```

### Frontend Build Fails

```bash
# Clear cache and reinstall
cd ~/LightOS/web-ui
rm -rf node_modules package-lock.json
npm install
```

### Cannot Access from Windows Browser

WSL2 networking sometimes requires port forwarding. Access using:

```
http://localhost:3000
http://localhost:8001
```

If issues persist, get WSL IP:

```bash
ip addr show eth0 | grep inet
```

Then access via: `http://<WSL-IP>:3000`

## Development Workflow

### Making Changes

**Backend Changes:**

```bash
# Edit dcim-api/main.py or other Python files
# Stop the server (Ctrl+C) and restart
cd ~/LightOS/dcim-api
python main.py
```

**Frontend Changes:**

With `npm run dev`, changes are automatically reflected (hot reload).

### Running Tests

```bash
# Backend tests (if available)
cd ~/LightOS
source venv/bin/activate
pytest

# Frontend type checking
cd ~/LightOS/web-ui
npm run type-check
```

## Preparing for VPS Deployment

Once you've tested locally and everything works:

### 1. Build Production Frontend

```bash
cd ~/LightOS/web-ui
npm run build
```

### 2. Commit Any Changes

```bash
cd ~/LightOS
git add -A
git commit -m "Your changes"
git push origin claude/combine-lightos-functions-deploy-r5jOD
```

### 3. Deploy to VPS

Use one of the deployment methods from `deployment/vps/README.md`:

**Option A: Automated Script**

On your VPS:
```bash
ssh root@ai.lightos.sh
bash <(curl -s https://raw.githubusercontent.com/Lightiam/LightOS/claude/combine-lightos-functions-deploy-r5jOD/deployment/vps/scripts/deploy.sh)
```

**Option B: Manual Deployment**

Follow steps in `deployment/vps/README.md`

**Option C: Docker**

```bash
cd ~/LightOS
# Build frontend first
cd web-ui && npm run build && cd ..

# Deploy with Docker
cd deployment/vps
docker compose up -d
```

## Tips for WSL

### Faster File Access

Keep your project in WSL filesystem (`~/LightOS`), not Windows (`/mnt/c/...`)

### VSCode Integration

Install "WSL" extension in VSCode:

```bash
# Open project in VSCode from WSL
cd ~/LightOS
code .
```

### Resource Limits

If WSL is slow, adjust `.wslconfig` in Windows:

```
[wsl2]
memory=4GB
processors=2
```

### Windows Firewall

If you can't access from Windows browser, ensure Windows Firewall allows WSL ports.

## Next Steps

1. **Test Locally**: Run both backend and frontend, test all features
2. **Review Logs**: Check for any errors in terminal output
3. **Test API**: Use http://localhost:8001/docs to test API endpoints
4. **Test UI**: Navigate through all pages and features
5. **Deploy to VPS**: Once satisfied, deploy to ai.lightos.sh

## Support

- **Local Testing Issues**: Check logs in terminal
- **Build Errors**: See error messages in npm/pip output
- **Runtime Errors**: Check browser console (F12) for frontend errors
- **API Errors**: Check FastAPI logs in terminal

## Quick Commands Reference

```bash
# Start backend
cd ~/LightOS && source venv/bin/activate && cd dcim-api && python main.py

# Start frontend dev
cd ~/LightOS/web-ui && npm run dev

# Build frontend
cd ~/LightOS/web-ui && npm run build

# Test API
curl http://localhost:8001/health

# View API docs
# Open browser to http://localhost:8001/docs
```
