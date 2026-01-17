# LightOS VPS Deployment Guide

Complete guide to deploy LightOS on ai.lightos.sh VPS (Namecheap)

## Prerequisites

- Ubuntu 22.04 or 24.04 LTS VPS
- Domain: `ai.lightos.sh` pointed to your VPS IP
- Root or sudo access
- Minimum 2GB RAM, 2 CPU cores, 20GB storage

## Quick Deploy (Automated)

### Option 1: One-Command Deployment

```bash
# SSH into your VPS
ssh root@ai.lightos.sh

# Clone the repository
git clone https://github.com/Lightiam/LightOS.git /opt/lightos-temp
cd /opt/lightos-temp
git checkout claude/combine-lightos-functions-deploy-r5jOD

# Run deployment script
sudo bash deployment/vps/scripts/deploy.sh
```

The script will:
1. Update system packages
2. Install dependencies (Python, Nginx, Node.js)
3. Create application user
4. Setup Python virtual environment
5. Build frontend
6. Configure Nginx
7. Setup SSL with Let's Encrypt
8. Create systemd service
9. Start all services

### Option 2: Docker Deployment

```bash
# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt-get install docker-compose-plugin

# Clone repository
git clone https://github.com/Lightiam/LightOS.git /opt/lightos
cd /opt/lightos
git checkout claude/combine-lightos-functions-deploy-r5jOD

# Build frontend first
cd web-ui
npm install
npm run build
cd ..

# Deploy with Docker Compose
cd deployment/vps
docker compose up -d
```

## Manual Deployment

### Step 1: DNS Configuration

Point your domain to the VPS IP:
- Go to Namecheap DNS settings
- Add A record: `ai` → Your VPS IP
- Wait for DNS propagation (5-30 minutes)

### Step 2: Server Preparation

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y python3.11 python3.11-venv python3-pip \
    nginx certbot python3-certbot-nginx git curl build-essential

# Install Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -
sudo apt-get install -y nodejs
```

### Step 3: Clone Repository

```bash
sudo mkdir -p /opt/lightos
sudo git clone https://github.com/Lightiam/LightOS.git /opt/lightos
cd /opt/lightos
sudo git checkout claude/combine-lightos-functions-deploy-r5jOD
```

### Step 4: Setup Backend

```bash
# Create virtual environment
cd /opt/lightos
sudo python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r dcim-api/requirements.txt
```

### Step 5: Build Frontend

```bash
cd /opt/lightos/web-ui
sudo npm install
sudo npm run build
```

This creates `/opt/lightos/web-ui/dist/` with the production build.

### Step 6: Configure Nginx

```bash
# Copy nginx config
sudo cp deployment/vps/nginx/lightos.conf /etc/nginx/sites-available/lightos
sudo ln -s /etc/nginx/sites-available/lightos /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# If test passes, reload nginx
sudo systemctl reload nginx
```

### Step 7: Setup SSL Certificate

```bash
sudo certbot --nginx -d ai.lightos.sh --non-interactive --agree-tos --email your-email@example.com
```

### Step 8: Setup Systemd Service

```bash
# Create lightos user
sudo useradd -r -m -s /bin/bash lightos

# Copy service file
sudo cp deployment/vps/systemd/lightos.service /etc/systemd/system/

# Set permissions
sudo chown -R lightos:lightos /opt/lightos

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable lightos
sudo systemctl start lightos
```

### Step 9: Configure Firewall

```bash
# Allow HTTP, HTTPS, and SSH
sudo ufw allow 'Nginx Full'
sudo ufw allow 22/tcp
sudo ufw enable
```

## Verification

### Check Services

```bash
# Check API service
sudo systemctl status lightos

# Check Nginx
sudo systemctl status nginx

# Test API health
curl http://localhost:8001/health
```

### Access the Application

- Web UI: https://ai.lightos.sh
- API Docs: https://ai.lightos.sh/docs
- Health Check: https://ai.lightos.sh/health

## Monitoring & Logs

### View Logs

```bash
# API logs (real-time)
sudo journalctl -u lightos -f

# API logs (last 100 lines)
sudo journalctl -u lightos -n 100

# Nginx access logs
sudo tail -f /var/log/nginx/lightos-access.log

# Nginx error logs
sudo tail -f /var/log/nginx/lightos-error.log
```

### Service Management

```bash
# Restart services
sudo systemctl restart lightos
sudo systemctl restart nginx

# Stop services
sudo systemctl stop lightos
sudo systemctl stop nginx

# View service status
sudo systemctl status lightos nginx
```

## Updates

### Automated Update

```bash
sudo bash /opt/lightos/deployment/vps/scripts/update.sh
```

### Manual Update

```bash
# Stop service
sudo systemctl stop lightos

# Backup (optional)
sudo cp -r /opt/lightos /opt/lightos-backup-$(date +%Y%m%d)

# Pull latest changes
cd /opt/lightos
sudo git pull origin claude/combine-lightos-functions-deploy-r5jOD

# Update dependencies
source venv/bin/activate
pip install -r dcim-api/requirements.txt

# Rebuild frontend
cd web-ui
npm install
npm run build

# Restart services
sudo systemctl start lightos
sudo systemctl restart nginx
```

## Troubleshooting

### API Not Starting

```bash
# Check logs
sudo journalctl -u lightos -n 50 --no-pager

# Test manually
cd /opt/lightos
source venv/bin/activate
python dcim-api/main.py
```

### Frontend Not Loading

```bash
# Verify build exists
ls -la /opt/lightos/web-ui/dist/

# Rebuild if needed
cd /opt/lightos/web-ui
npm run build

# Check nginx config
sudo nginx -t
```

### SSL Certificate Issues

```bash
# Renew certificate
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run
```

### Port Already in Use

```bash
# Check what's using port 8001
sudo lsof -i :8001

# Kill process if needed
sudo kill -9 <PID>
```

## Performance Optimization

### Enable Nginx Caching

Add to nginx config in http block:

```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=100m inactive=60m;
```

### Increase Worker Processes

Edit `/etc/nginx/nginx.conf`:

```nginx
worker_processes auto;
worker_connections 1024;
```

### Python Process Manager

For production, consider using Gunicorn:

```bash
pip install gunicorn uvloop httptools

# Update systemd ExecStart
ExecStart=/opt/lightos/venv/bin/gunicorn dcim-api.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8001 \
    --access-logfile -
```

## Security Hardening

### Update SSH Configuration

```bash
# Edit /etc/ssh/sshd_config
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes

# Restart SSH
sudo systemctl restart sshd
```

### Setup Fail2Ban

```bash
sudo apt-get install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### Regular Updates

```bash
# Setup automatic security updates
sudo apt-get install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

## Architecture

```
┌─────────────────────────────────────────┐
│         Internet (HTTPS/WSS)            │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│  Nginx (Port 80/443)                    │
│  - SSL Termination                      │
│  - Static File Serving                  │
│  - Reverse Proxy                        │
└────────────────┬────────────────────────┘
                 │
       ┌─────────┴─────────┐
       │                   │
┌──────▼──────┐   ┌────────▼────────────┐
│  Static     │   │  LightOS API        │
│  Files      │   │  (Port 8001)        │
│  (dist/)    │   │  - FastAPI          │
│             │   │  - WebSocket        │
│             │   │  - DCIM Backend     │
└─────────────┘   └─────────────────────┘
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/Lightiam/LightOS/issues
- Documentation: https://ai.lightos.sh/docs

## License

See LICENSE file in the repository.
