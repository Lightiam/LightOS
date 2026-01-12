#!/bin/bash
# LightOS DCIM Demo Launcher
# Starts the complete DCIM system for client demos

set -e

echo "=========================================="
echo "LightOS DCIM Demo Launcher"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if running in virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}⚠️  Not in virtual environment${NC}"
    echo ""
    echo "Recommended: Activate LightOS venv first"
    echo "  source /opt/lightos/venv/bin/activate"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check dependencies
echo "Checking dependencies..."
python -c "import fastapi, uvicorn, pandas" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Missing dependencies${NC}"
    echo ""
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi
echo -e "${GREEN}✓ Dependencies OK${NC}"
echo ""

# Start options
echo "Select demo mode:"
echo ""
echo "  1. Full Demo (API + Dashboard + AI Demo)"
echo "  2. API Only"
echo "  3. AI Demo Only"
echo "  4. Dashboard Only"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo -e "${BLUE}Starting Full Demo...${NC}"
        echo ""

        # Start API in background
        echo "Starting DCIM API..."
        python main.py &
        API_PID=$!
        sleep 3

        # Check if API started
        curl -s http://localhost:8001/health >/dev/null
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ API running at http://localhost:8001${NC}"
        else
            echo -e "${RED}✗ API failed to start${NC}"
            kill $API_PID 2>/dev/null
            exit 1
        fi

        # Start dashboard
        echo ""
        echo "Starting Dashboard..."
        cd ../docs-site
        python -m http.server 8000 &
        DASH_PID=$!
        cd ../dcim-api
        sleep 2

        echo -e "${GREEN}✓ Dashboard running at http://localhost:8000/dcim.html${NC}"
        echo ""

        # Display URLs
        echo "=========================================="
        echo "🚀 LightOS DCIM is running!"
        echo "=========================================="
        echo ""
        echo "Dashboard:    http://localhost:8000/dcim.html"
        echo "API:          http://localhost:8001"
        echo "API Docs:     http://localhost:8001/docs"
        echo "WebSocket:    ws://localhost:8001/ws/dcim"
        echo ""
        echo "Press Ctrl+C to stop all services"
        echo ""

        # Run AI demo
        echo "Running LightRail AI Demo..."
        echo ""
        python lightrail_ai_demo.py

        # Wait for interrupt
        wait $API_PID $DASH_PID
        ;;

    2)
        echo ""
        echo -e "${BLUE}Starting API Only...${NC}"
        echo ""
        python main.py
        ;;

    3)
        echo ""
        echo -e "${BLUE}Running AI Demo...${NC}"
        echo ""
        python lightrail_ai_demo.py
        ;;

    4)
        echo ""
        echo -e "${BLUE}Starting Dashboard...${NC}"
        echo ""
        cd ../docs-site
        python -m http.server 8000
        ;;

    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac
