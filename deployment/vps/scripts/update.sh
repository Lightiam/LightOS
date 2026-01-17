#!/bin/bash
# LightOS Update Script
# Updates LightOS to the latest version

set -e

echo "================================================"
echo "LightOS Update Script"
echo "================================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

APP_DIR="/opt/lightos"
BRANCH="claude/combine-lightos-functions-deploy-r5jOD"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

echo -e "${GREEN}Step 1: Stop Services${NC}"
systemctl stop lightos

echo -e "${GREEN}Step 2: Backup Current Installation${NC}"
BACKUP_DIR="/opt/lightos-backup-$(date +%Y%m%d-%H%M%S)"
cp -r $APP_DIR $BACKUP_DIR
echo -e "${YELLOW}Backup created at: $BACKUP_DIR${NC}"

echo -e "${GREEN}Step 3: Pull Latest Changes${NC}"
cd $APP_DIR
git fetch origin
git checkout $BRANCH
git pull origin $BRANCH

echo -e "${GREEN}Step 4: Update Python Dependencies${NC}"
source $APP_DIR/venv/bin/activate
pip install --upgrade pip
pip install -r dcim-api/requirements.txt

echo -e "${GREEN}Step 5: Rebuild Frontend${NC}"
cd $APP_DIR/web-ui
npm install
npm run build

echo -e "${GREEN}Step 6: Restart Services${NC}"
systemctl daemon-reload
systemctl start lightos
systemctl restart nginx

echo -e "${GREEN}Step 7: Verify Deployment${NC}"
sleep 3
if systemctl is-active --quiet lightos; then
    echo -e "${GREEN}✓ LightOS service is running${NC}"
else
    echo -e "${RED}✗ LightOS service failed to start${NC}"
    echo "Check logs with: journalctl -u lightos -n 50"
    exit 1
fi

if curl -sf http://localhost:8001/health > /dev/null; then
    echo -e "${GREEN}✓ API health check passed${NC}"
else
    echo -e "${RED}✗ API health check failed${NC}"
    exit 1
fi

echo ""
echo "================================================"
echo -e "${GREEN}Update Complete!${NC}"
echo "================================================"
echo ""
echo "Backup location: $BACKUP_DIR"
echo "To rollback: sudo systemctl stop lightos && sudo rm -rf $APP_DIR && sudo mv $BACKUP_DIR $APP_DIR && sudo systemctl start lightos"
echo ""
