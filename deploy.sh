#!/bin/bash
# 🚀 One-Command Deployment Script for LightOS DCIM

set -e  # Exit on error

echo "======================================"
echo "🚀 LightOS DCIM Deployment Script"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the correct directory
if [ ! -f "netlify.toml" ]; then
    echo -e "${RED}Error: netlify.toml not found. Please run this script from the LightOS root directory.${NC}"
    exit 1
fi

echo -e "${BLUE}Step 1/3: Checking Netlify CLI...${NC}"
if ! command -v netlify &> /dev/null; then
    echo -e "${YELLOW}Netlify CLI not found. Installing...${NC}"
    npm install -g netlify-cli
    echo -e "${GREEN}✓ Netlify CLI installed${NC}"
else
    echo -e "${GREEN}✓ Netlify CLI already installed${NC}"
fi
echo ""

echo -e "${BLUE}Step 2/3: Authenticating with Netlify...${NC}"
echo "This will open your browser for authentication."
echo "If you don't have a Netlify account, create one (it's free)."
echo ""
read -p "Press Enter to continue..."

netlify login

echo -e "${GREEN}✓ Authentication complete${NC}"
echo ""

echo -e "${BLUE}Step 3/3: Deploying to Netlify...${NC}"
echo "Deploying from: docs-site/"
echo ""

# Deploy to production
netlify deploy --dir=docs-site --prod

echo ""
echo -e "${GREEN}======================================"
echo "✓ Deployment Complete!"
echo "======================================${NC}"
echo ""
echo -e "${YELLOW}📊 Your DCIM Dashboard is now live!${NC}"
echo ""
echo "Next steps:"
echo "1. Visit your deployed site URL (shown above)"
echo "2. Deploy the API backend (see instructions below)"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}⚠️  API Backend Required${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "The dashboard is deployed, but you need to deploy the API backend"
echo "for the dashboard to display real-time data."
echo ""
echo -e "${GREEN}Quick API Deployment (Render.com):${NC}"
echo ""
echo "1. Go to: https://dashboard.render.com"
echo "2. Click 'New +' → 'Web Service'"
echo "3. Connect your GitHub: Lightiam/LightOS"
echo "4. Render will auto-detect render.yaml"
echo "5. Click 'Apply'"
echo "6. Your API will be live at: https://lightos-dcim-api.onrender.com"
echo ""
echo "The dashboard is already configured to use this API URL!"
echo ""
echo -e "${BLUE}Full deployment guide: ${NC}dcim-api/DEPLOY_API.md"
echo ""
echo -e "${GREEN}🎉 Enjoy your DCIM dashboard!${NC}"
