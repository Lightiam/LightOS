#!/bin/bash
# LightOS VPS Deployment Script for ai.lightos.sh
# This script deploys LightOS on a fresh VPS (Ubuntu 22.04/24.04)

set -e

echo "================================================"
echo "LightOS VPS Deployment Script"
echo "Target: ai.lightos.sh"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="ai.lightos.sh"
APP_DIR="/opt/lightos"
USER="lightos"
EMAIL="admin@lightos.sh"  # Change this to your email for Let's Encrypt

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

echo -e "${GREEN}Step 1: System Update${NC}"
apt-get update && apt-get upgrade -y

echo -e "${GREEN}Step 2: Install Dependencies${NC}"
apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    nginx \
    certbot \
    python3-certbot-nginx \
    git \
    curl \
    build-essential

echo -e "${GREEN}Step 3: Create Application User${NC}"
if ! id "$USER" &>/dev/null; then
    useradd -r -m -s /bin/bash $USER
    echo -e "${YELLOW}Created user: $USER${NC}"
else
    echo -e "${YELLOW}User $USER already exists${NC}"
fi

echo -e "${GREEN}Step 4: Clone/Update Repository${NC}"
if [ ! -d "$APP_DIR" ]; then
    git clone https://github.com/Lightiam/LightOS.git $APP_DIR
else
    cd $APP_DIR && git pull
fi

cd $APP_DIR
git checkout claude/combine-lightos-functions-deploy-r5jOD

echo -e "${GREEN}Step 5: Setup Python Virtual Environment${NC}"
python3.11 -m venv $APP_DIR/venv
source $APP_DIR/venv/bin/activate
pip install --upgrade pip
pip install -r dcim-api/requirements.txt

echo -e "${GREEN}Step 6: Build Frontend${NC}"
# Install Node.js if not present
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
fi

cd $APP_DIR/web-ui
npm install
npm run build

echo -e "${GREEN}Step 7: Configure Nginx${NC}"
cp $APP_DIR/deployment/vps/nginx/lightos.conf /etc/nginx/sites-available/lightos
ln -sf /etc/nginx/sites-available/lightos /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
nginx -t

echo -e "${GREEN}Step 8: Setup SSL with Let's Encrypt${NC}"
certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email $EMAIL

echo -e "${GREEN}Step 9: Setup Systemd Service${NC}"
cp $APP_DIR/deployment/vps/systemd/lightos.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable lightos
systemctl start lightos

echo -e "${GREEN}Step 10: Start Nginx${NC}"
systemctl restart nginx
systemctl enable nginx

echo -e "${GREEN}Step 11: Setup Firewall${NC}"
if command -v ufw &> /dev/null; then
    ufw allow 'Nginx Full'
    ufw allow 22/tcp
    ufw --force enable
fi

echo -e "${GREEN}Step 12: Set Permissions${NC}"
chown -R $USER:$USER $APP_DIR
chmod -R 755 $APP_DIR

echo -e "${GREEN}Step 13: Setup Log Rotation${NC}"
cat > /etc/logrotate.d/lightos << EOF
/var/log/nginx/lightos-*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        systemctl reload nginx > /dev/null 2>&1
    endscript
}
EOF

echo ""
echo "================================================"
echo -e "${GREEN}LightOS Deployment Complete!${NC}"
echo "================================================"
echo ""
echo "Access your LightOS instance at: https://$DOMAIN"
echo ""
echo "Useful Commands:"
echo "  - Check API status: systemctl status lightos"
echo "  - View API logs: journalctl -u lightos -f"
echo "  - Check Nginx status: systemctl status nginx"
echo "  - View Nginx logs: tail -f /var/log/nginx/lightos-*.log"
echo "  - Restart services: systemctl restart lightos nginx"
echo ""
echo "API Documentation: https://$DOMAIN/docs"
echo "Health Check: https://$DOMAIN/health"
echo ""
