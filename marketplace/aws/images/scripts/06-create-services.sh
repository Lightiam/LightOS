#!/bin/bash
# 06-create-services.sh
# Create systemd services for LightOS

set -e

echo "================================================"
echo "Step 6: Creating systemd services"
echo "================================================"

# Create LightOS web service
sudo tee /etc/systemd/system/lightos-web.service > /dev/null <<'EOF'
[Unit]
Description=LightOS Web UI
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/lightos
Environment="PATH=/opt/lightos/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStartPre=/opt/lightos/aws-init.sh
ExecStart=/opt/lightos/venv/bin/python3 -m uvicorn llm-training-ground.ui.app:app --host 0.0.0.0 --port 8080
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create LightOS API service
sudo tee /etc/systemd/system/lightos-api.service > /dev/null <<'EOF'
[Unit]
Description=LightOS API Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/lightos
Environment="PATH=/opt/lightos/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/opt/lightos/venv/bin/python3 -m uvicorn llm-training-ground.api.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create Jupyter service
sudo tee /etc/systemd/system/lightos-jupyter.service > /dev/null <<'EOF'
[Unit]
Description=LightOS Jupyter Notebook
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/lightos
Environment="PATH=/opt/lightos/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/opt/lightos/venv/bin/jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --NotebookApp.token='' --NotebookApp.password=''
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Install Jupyter in venv
source /opt/lightos/venv/bin/activate
pip install jupyter jupyterlab notebook
deactivate

# Reload systemd
sudo systemctl daemon-reload

# Enable services (but don't start yet, will start on first boot)
sudo systemctl enable lightos-web.service
sudo systemctl enable lightos-api.service
sudo systemctl enable lightos-jupyter.service

echo "✓ Systemd services created and enabled"
