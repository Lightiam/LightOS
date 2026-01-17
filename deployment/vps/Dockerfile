# LightOS VPS Deployment Dockerfile
FROM python:3.11-slim

LABEL maintainer="LightOS Team"
LABEL description="LightOS DCIM Pro API with Web UI"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY dcim-api/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY dcim-api/ /app/dcim-api/
COPY web-ui/dist/ /app/web-ui/dist/

# Create logs directory
RUN mkdir -p /app/logs

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run the application
CMD ["python", "dcim-api/main.py"]
