# 🚀 Deploying LightOS DCIM API

This guide covers multiple deployment options for the LightOS DCIM FastAPI backend.

---

## 📋 Deployment Options

### Option 1: Render.com (Recommended - Free Tier Available)
### Option 2: Railway.app (Easy deployment)
### Option 3: Fly.io (Globally distributed)
### Option 4: Docker + VPS (Full control)

---

## 🎯 Option 1: Deploy to Render.com (Recommended)

Render offers free tier Python web services with automatic deployments from Git.

### Prerequisites
- GitHub account (this repo must be on GitHub)
- Render account (sign up at https://render.com)

### Step 1: Create `render.yaml`

This file is already included in the repository at `/home/user/LightOS/dcim-api/render.yaml`

### Step 2: Push to GitHub

```bash
cd /home/user/LightOS
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

### Step 3: Deploy on Render

1. Go to https://dashboard.render.com/
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository: `Lightiam/LightOS`
4. Render will auto-detect the `render.yaml` configuration
5. Click **"Apply"** to deploy

**Configuration:**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Environment:** `Python 3.11`
- **Root Directory:** `dcim-api`

### Step 4: Set Environment Variables (Optional)

In Render dashboard, add these environment variables:
- `KAGGLE_API_TOKEN`: `KGAT_2a4e49d583b937d8c08c972945c4b110`
- `PYTHONUNBUFFERED`: `1`

### Step 5: Get Your API URL

After deployment, Render will provide a URL like:
```
https://lightos-dcim-api.onrender.com
```

### Step 6: Update Dashboard Configuration

Edit `/home/user/LightOS/docs-site/dcim.html` and update the API URL:

```javascript
// Change this line (around line 750)
const API_BASE = 'http://localhost:8001';

// To your Render URL
const API_BASE = 'https://lightos-dcim-api.onrender.com';
```

Also update `/home/user/LightOS/netlify.toml`:

```toml
[[redirects]]
  from = "/api/dcim/*"
  to = "https://lightos-dcim-api.onrender.com/api/dcim/:splat"
  status = 200
  force = true
```

---

## 🎯 Option 2: Deploy to Railway.app

Railway provides easy deployments with automatic HTTPS.

### Step 1: Create `railway.json`

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

### Step 2: Deploy

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize and deploy
cd /home/user/LightOS/dcim-api
railway init
railway up
```

### Step 3: Get URL

```bash
railway domain
```

Your API will be available at: `https://your-project.railway.app`

---

## 🎯 Option 3: Deploy to Fly.io

Fly.io provides globally distributed deployments.

### Step 1: Create `fly.toml`

```toml
app = "lightos-dcim-api"
primary_region = "iad"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8080"
  PYTHONUNBUFFERED = "1"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

[[services]]
  protocol = "tcp"
  internal_port = 8080

  [[services.ports]]
    port = 80
    handlers = ["http"]

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]
```

### Step 2: Create `Procfile`

```
web: uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
```

### Step 3: Deploy

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Launch (creates app)
cd /home/user/LightOS/dcim-api
flyctl launch --name lightos-dcim-api

# Deploy
flyctl deploy
```

Your API will be at: `https://lightos-dcim-api.fly.dev`

---

## 🎯 Option 4: Docker + VPS Deployment

For full control, deploy using Docker on any VPS (DigitalOcean, AWS, etc.)

### Step 1: Create `Dockerfile`

This file is already included at `/home/user/LightOS/dcim-api/Dockerfile`

### Step 2: Create `docker-compose.yml`

```yaml
version: '3.8'

services:
  dcim-api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8001:8001"
    environment:
      - KAGGLE_API_TOKEN=${KAGGLE_API_TOKEN}
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    volumes:
      - ./data:/app/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Step 3: Deploy on VPS

```bash
# On your VPS (Ubuntu/Debian)
sudo apt update
sudo apt install -y docker.io docker-compose git

# Clone repository
git clone https://github.com/Lightiam/LightOS.git
cd LightOS/dcim-api

# Set environment variables
export KAGGLE_API_TOKEN=KGAT_2a4e49d583b937d8c08c972945c4b110

# Build and run
docker-compose up -d

# View logs
docker-compose logs -f
```

### Step 4: Configure Nginx (Optional)

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 📦 Pre-Deployment Checklist

Before deploying, ensure:

- [ ] `requirements.txt` is up to date
- [ ] All environment variables are set
- [ ] Health check endpoint works: `/health`
- [ ] API documentation is accessible: `/docs`
- [ ] CORS is properly configured for your domain
- [ ] Database connections are configured (if using external DB)
- [ ] Kaggle API token is valid (optional, for real data)

---

## 🔍 Verify Deployment

After deployment, test these endpoints:

```bash
# Health check
curl https://your-api-url.com/health

# API documentation
open https://your-api-url.com/docs

# DCIM KPIs
curl https://your-api-url.com/api/dcim/kpi

# GPU metrics
curl https://your-api-url.com/api/dcim/gpu/0

# Cluster status
curl https://your-api-url.com/api/dcim/cluster
```

---

## 🌐 Update Dashboard to Use Deployed API

### Method 1: Environment-based Configuration

Edit `/home/user/LightOS/docs-site/dcim.html`:

```javascript
// Add at the top of the <script> section
const API_BASE = window.location.hostname === 'localhost'
  ? 'http://localhost:8001'
  : 'https://lightos-dcim-api.onrender.com';  // Your deployed API URL

// Use API_BASE throughout the code
async function fetchKPIs() {
  const response = await fetch(`${API_BASE}/api/dcim/kpi`);
  // ...
}
```

### Method 2: Configuration File

Create `/home/user/LightOS/docs-site/config.js`:

```javascript
window.LIGHTOS_CONFIG = {
  API_BASE_URL: 'https://lightos-dcim-api.onrender.com',
  WEBSOCKET_URL: 'wss://lightos-dcim-api.onrender.com/ws/dcim',
  REFRESH_INTERVAL: 2000
};
```

Include in `dcim.html`:
```html
<script src="config.js"></script>
```

Use in code:
```javascript
const API_BASE = window.LIGHTOS_CONFIG.API_BASE_URL;
```

---

## 🐛 Troubleshooting

### API Won't Start

**Check logs:**
```bash
# Render
# View logs in dashboard: https://dashboard.render.com

# Railway
railway logs

# Fly.io
flyctl logs

# Docker
docker-compose logs -f dcim-api
```

**Common issues:**
- Port binding: Ensure `--host 0.0.0.0 --port $PORT`
- Dependencies: Verify `requirements.txt` includes all packages
- Python version: Use Python 3.11+

### CORS Errors

Update `main.py` to allow your Netlify domain:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-site.netlify.app",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### WebSocket Connection Fails

Most free tiers don't support WebSockets well. Consider:
- Using polling instead of WebSockets for free deployments
- Upgrading to paid tier
- Using a WebSocket-friendly host like Render or Fly.io

### 502 Bad Gateway

**Causes:**
- API is starting up (wait 1-2 minutes)
- Health check failing
- Port misconfiguration

**Fix:**
Ensure your API responds to health checks:
```python
@app.get("/health")
async def health():
    return {"status": "healthy"}
```

---

## 💰 Cost Comparison

| Platform | Free Tier | Paid Tier | WebSocket Support |
|----------|-----------|-----------|-------------------|
| **Render.com** | 750 hours/month | $7/month | ✅ Yes |
| **Railway.app** | $5 credit/month | $0.000231/GB-hour | ✅ Yes |
| **Fly.io** | 3 shared-cpu VMs | $0.0000022/sec | ✅ Yes |
| **Heroku** | Deprecated | $7/month | ✅ Yes |
| **DigitalOcean** | None | $4/month | ✅ Yes (DIY) |

**Recommendation:** Start with **Render.com** free tier for testing, upgrade to paid if needed.

---

## 🔐 Security Best Practices

### 1. Environment Variables
Never commit secrets to Git:
```bash
# Use .env file (add to .gitignore)
KAGGLE_API_TOKEN=your-token-here
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
```

### 2. HTTPS Only
Always use HTTPS in production. Most platforms provide it automatically.

### 3. Rate Limiting
Add rate limiting to prevent abuse:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/dcim/kpi")
@limiter.limit("60/minute")
async def get_kpi(request: Request):
    # ...
```

### 4. Authentication (Optional)
For sensitive data, add API key authentication:
```python
from fastapi.security import APIKeyHeader

API_KEY = os.getenv("API_KEY", "your-secret-api-key")
api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key
```

---

## 📊 Monitoring & Analytics

### Health Checks
All platforms support health checks:
```python
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
```

### Logging
Use structured logging:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@app.get("/api/dcim/kpi")
async def get_kpi():
    logger.info("KPI endpoint accessed")
    # ...
```

### Error Tracking (Optional)
Integrate Sentry for error monitoring:
```bash
pip install sentry-sdk[fastapi]
```

```python
import sentry_sdk

sentry_sdk.init(dsn="your-sentry-dsn")
```

---

## 🚀 Continuous Deployment

### GitHub Actions (Automated Deployments)

Create `.github/workflows/deploy-api.yml`:

```yaml
name: Deploy DCIM API

on:
  push:
    branches: [main]
    paths:
      - 'dcim-api/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to Render
        env:
          RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}
        run: |
          curl -X POST "https://api.render.com/v1/services/${{ secrets.RENDER_SERVICE_ID }}/deploys" \
            -H "Authorization: Bearer $RENDER_API_KEY" \
            -H "Content-Type: application/json"
```

---

## 📚 Next Steps

After deploying the API:

1. **Update Dashboard**: Change `API_BASE` URL in `dcim.html`
2. **Update Netlify Config**: Point API proxy to your deployed URL
3. **Test All Endpoints**: Verify health, KPIs, GPU metrics, etc.
4. **Set Up Monitoring**: Configure health checks and alerts
5. **Deploy Dashboard**: Push to Netlify (see main README)
6. **Share with Client**: Provide dashboard URL

---

## 🆘 Support

If you encounter issues:

1. Check platform-specific documentation
2. Review logs for error messages
3. Test API locally first: `python main.py`
4. Verify CORS configuration
5. Check environment variables are set

**Quick Test Script:**
```bash
#!/bin/bash
API_URL="https://your-api-url.com"

echo "Testing health check..."
curl -s "$API_URL/health" | jq

echo "Testing KPI endpoint..."
curl -s "$API_URL/api/dcim/kpi" | jq

echo "Testing GPU metrics..."
curl -s "$API_URL/api/dcim/gpu/0" | jq

echo "All tests complete!"
```

---

**Deployment Status:** Ready for production deployment
**Last Updated:** 2026-01-12
**Next:** Deploy to Netlify (see main repository README)
