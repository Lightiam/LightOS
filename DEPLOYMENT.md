# LightOS Combined Deployment Guide

LightOS with integrated LightRail_AI_Aurora Web UI - Ready for deployment to ai.lightos.sh

## What's Integrated

This deployment combines:

1. **LightOS DCIM API** (`dcim-api/`) - FastAPI backend with ISA-95 architecture
2. **LightRail_AI_Aurora UI** (`web-ui/`) - React/TypeScript frontend for datacenter management

## Features

### Backend (DCIM API)
- ISA-95 5-layer architecture
- ML-based peak shaving
- Predictive cooling
- Dynamic power capping
- Carbon-aware scheduling
- Real-time GPU telemetry
- WebSocket streaming (1 Hz)
- REST API endpoints

### Frontend (Web UI)
- Dashboard - Infrastructure overview
- Fleet Explorer - Node monitoring & capacity planning
- DCIM Control - Power, thermal, fabric management
- HCI Orchestrator - Hyper-converged infrastructure
- Workloads - Job orchestration
- Cost Control - Analytics & optimization
- Real-time telemetry visualization

## Quick Start

### Local Development

```bash
# Terminal 1: Start Backend
cd dcim-api
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
python main.py
# API running on http://localhost:8001

# Terminal 2: Start Frontend
cd web-ui
npm install
npm run dev
# UI running on http://localhost:3000
```

Access:
- Frontend: http://localhost:3000
- API Docs: http://localhost:8001/docs
- Health: http://localhost:8001/health

### Production Deployment to ai.lightos.sh

See detailed guide: [`deployment/vps/README.md`](deployment/vps/README.md)

#### Quick Deploy (Automated)

```bash
# On your VPS
sudo bash <(curl -s https://raw.githubusercontent.com/Lightiam/LightOS/claude/combine-lightos-functions-deploy-r5jOD/deployment/vps/scripts/deploy.sh)
```

#### Docker Deploy

```bash
git clone https://github.com/Lightiam/LightOS.git
cd LightOS
git checkout claude/combine-lightos-functions-deploy-r5jOD

# Build frontend
cd web-ui && npm install && npm run build && cd ..

# Deploy
cd deployment/vps
docker compose up -d
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Internet (HTTPS)                     │
└────────────────────────┬────────────────────────────────┘
                         │
                         │ Port 443
                         │
┌────────────────────────▼────────────────────────────────┐
│              Nginx Reverse Proxy                        │
│  - SSL Termination (Let's Encrypt)                      │
│  - Static File Serving (/assets/, index.html)           │
│  - Proxy /api/* → Backend                               │
│  - Proxy /ws/* → Backend (WebSocket)                    │
└────────────┬───────────────────────┬────────────────────┘
             │                       │
             │ Static Files          │ API/WebSocket
             │                       │
┌────────────▼────────────┐  ┌───────▼──────────────────┐
│   Frontend (SPA)        │  │  LightOS DCIM API        │
│   /web-ui/dist/         │  │  Port 8001               │
│   - index.html          │  │  - FastAPI               │
│   - assets/             │  │  - WebSocket (/ws/dcim)  │
│   - React App           │  │  - REST API (/api/*)     │
└─────────────────────────┘  └──────────────────────────┘
```

## Directory Structure

```
LightOS/
├── dcim-api/                    # Backend API
│   ├── main.py                  # FastAPI application
│   ├── requirements.txt         # Python dependencies
│   └── ...
├── web-ui/                      # Frontend application
│   ├── components/              # React components
│   ├── pages/                   # Page components
│   ├── services/                # Data services
│   ├── types.ts                 # TypeScript types
│   ├── App.tsx                  # Main app
│   ├── package.json             # Node dependencies
│   ├── vite.config.ts           # Build configuration
│   └── dist/                    # Production build (generated)
├── deployment/
│   └── vps/                     # VPS deployment files
│       ├── nginx/               # Nginx configuration
│       ├── systemd/             # Systemd service
│       ├── scripts/             # Deployment scripts
│       ├── docker-compose.yml   # Docker deployment
│       ├── Dockerfile           # Container image
│       └── README.md            # Deployment guide
├── llm-training-ground/         # LLM training features
├── fabric-os/                   # Platform abstraction
├── kernel/                      # OS kernel components
└── DEPLOYMENT.md                # This file
```

## API Endpoints

### UI Data Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/providers` | Infrastructure providers |
| `GET /api/jobs` | Workload jobs |
| `GET /api/sites` | Datacenter sites |
| `GET /api/racks` | Rack information |
| `GET /api/nodes` | Node metrics |
| `GET /api/hci-nodes` | HCI nodes |
| `GET /api/tenant-isolation` | Tenant isolation data |

### DCIM Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/dcim/kpi` | Real-time KPI summary |
| `GET /api/dcim/gpu/{gpu_id}` | GPU-specific metrics |
| `GET /api/dcim/cluster` | Cluster-wide metrics |
| `GET /api/dcim/power` | Power distribution |
| `GET /api/dcim/peak-shaving` | ML peak shaving status |
| `GET /api/dcim/advanced-features` | AI-driven features |
| `GET /api/dcim/isa95` | ISA-95 architecture details |
| `WS /ws/dcim` | Real-time telemetry stream |

### System Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | API information |
| `GET /health` | Health check |
| `GET /docs` | Interactive API docs |

## Configuration

### Backend Configuration

Environment variables for `dcim-api/main.py`:

```bash
PORT=8001  # API port (default: 8001)
```

### Frontend Configuration

Create `web-ui/.env.local`:

```env
VITE_API_BASE_URL=http://localhost:8001
GEMINI_API_KEY=your-key  # Optional
```

### Nginx Configuration

The nginx config (`deployment/vps/nginx/lightos.conf`) handles:

- SSL/TLS with Let's Encrypt
- Static file serving from `web-ui/dist/`
- API reverse proxy to port 8001
- WebSocket support
- Security headers
- Gzip compression

### Systemd Service

The systemd service (`deployment/vps/systemd/lightos.service`):

- Runs as `lightos` user
- Auto-restarts on failure
- Logs to systemd journal
- Resource limits configured

## Monitoring

### Service Status

```bash
# Check services
systemctl status lightos
systemctl status nginx

# View logs
journalctl -u lightos -f
tail -f /var/log/nginx/lightos-access.log
```

### Health Checks

```bash
# API health
curl https://ai.lightos.sh/health

# WebSocket connection
wscat -c wss://ai.lightos.sh/ws/dcim
```

### Metrics

The API provides comprehensive metrics:

- GPU utilization and temperature
- Power consumption and PUE
- Thermal metrics
- Job queue depth
- Cost analytics
- Carbon footprint

## Updates

### Automated Update

```bash
cd /opt/lightos
sudo bash deployment/vps/scripts/update.sh
```

### Manual Update

```bash
# Pull changes
cd /opt/lightos
git pull

# Update backend
cd dcim-api
source ../venv/bin/activate
pip install -r requirements.txt

# Update frontend
cd ../web-ui
npm install
npm run build

# Restart services
sudo systemctl restart lightos nginx
```

## Backup

### Configuration Backup

```bash
# Backup nginx config
sudo cp /etc/nginx/sites-available/lightos ~/lightos-nginx-backup.conf

# Backup systemd service
sudo cp /etc/systemd/system/lightos.service ~/lightos-service-backup.service
```

### SSL Certificates

Let's Encrypt certificates are in `/etc/letsencrypt/live/ai.lightos.sh/`

Renewal is automatic via certbot timer.

## Troubleshooting

### Common Issues

**Frontend doesn't load:**
- Check if build exists: `ls /opt/lightos/web-ui/dist/`
- Rebuild: `cd /opt/lightos/web-ui && npm run build`
- Check nginx: `nginx -t && systemctl reload nginx`

**API not responding:**
- Check service: `systemctl status lightos`
- View logs: `journalctl -u lightos -n 50`
- Test directly: `curl http://localhost:8001/health`

**WebSocket connection fails:**
- Check nginx WebSocket config
- Verify backend is running
- Check browser console for errors

**SSL issues:**
- Renew certificate: `certbot renew`
- Check cert files: `ls /etc/letsencrypt/live/ai.lightos.sh/`

### Debug Mode

Run backend manually for debugging:

```bash
cd /opt/lightos/dcim-api
source ../venv/bin/activate
python main.py
```

## Performance Tuning

### Backend

- Use Gunicorn with multiple workers
- Enable uvloop for async performance
- Configure appropriate worker count

### Frontend

- Assets are automatically minified and cached
- Code splitting by route
- Lazy loading for components

### Nginx

- Gzip compression enabled
- Browser caching for static assets
- Connection pooling to backend

## Security

### Implemented

- HTTPS with TLS 1.2/1.3
- Security headers (HSTS, X-Frame-Options, etc.)
- Non-root user for API service
- Systemd security features
- Firewall configuration (UFW)

### Recommendations

- Keep system updated
- Use SSH key authentication
- Setup fail2ban
- Regular security audits
- Monitor access logs

## Support

- **Documentation**: https://ai.lightos.sh/docs
- **Health Status**: https://ai.lightos.sh/health
- **GitHub**: https://github.com/Lightiam/LightOS

## License

See LICENSE file in repository.
