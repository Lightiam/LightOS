# LightOS Neural Compute Engine
# Ready-to-use Docker image with all features

FROM nvidia/cuda:12.1.0-devel-ubuntu22.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /lightos

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    build-essential \
    vim \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Copy LightOS files
COPY llm-training-ground /lightos/llm-training-ground
COPY fabric-os /lightos/fabric-os
COPY docs /lightos/docs
COPY build-system/edge-profiles /lightos/edge-profiles

# Create virtual environment
RUN python3 -m venv /lightos/venv

# Activate venv and install Python packages
RUN /lightos/venv/bin/pip install --upgrade pip && \
    /lightos/venv/bin/pip install \
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 && \
    /lightos/venv/bin/pip install \
    transformers \
    accelerate \
    datasets \
    bitsandbytes \
    trl \
    peft \
    unsloth

# Create launcher scripts
RUN echo '#!/bin/bash\nsource /lightos/venv/bin/activate\ncd /lightos/llm-training-ground/ui\npython3 enhanced_launcher.py "$@"' > /usr/local/bin/lightos && \
    chmod +x /usr/local/bin/lightos

RUN echo '#!/bin/bash\nsource /lightos/venv/bin/activate\ncd /lightos/llm-training-ground/coding_agents\npython3 qwen3_coder.py "$@"' > /usr/local/bin/lightos-code && \
    chmod +x /usr/local/bin/lightos-code

# Create welcome message
RUN echo '\n\
╔══════════════════════════════════════════════════════════════╗\n\
║           LightOS Neural Compute Engine v0.2.1               ║\n\
║              Running in Docker Container                     ║\n\
╚══════════════════════════════════════════════════════════════╝\n\
\n\
🚀 Quick Start:\n\
\n\
  lightos              - Launch training ground UI\n\
  lightos-code qwen generate "code description"\n\
\n\
📚 Documentation: /lightos/docs/\n\
💡 Examples: /lightos/llm-training-ground/examples/\n\
\n' > /etc/motd

# Set up entrypoint
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Expose ports
EXPOSE 8080 8888

# Set entrypoint
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["lightos"]
