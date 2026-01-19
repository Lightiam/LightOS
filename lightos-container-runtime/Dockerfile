# Multi-stage build for LightOS Container Runtime

# Stage 1: Build runtime
FROM golang:1.21-alpine AS builder

WORKDIR /build

# Install build dependencies
RUN apk add --no-cache git make gcc musl-dev

# Copy go mod files
COPY go.mod go.sum* ./
RUN go mod download || true

# Copy source code
COPY . .

# Build runtime binary
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build \
    -ldflags="-w -s" \
    -o lightos-runtime \
    ./cmd/lightos-runtime/

# Build device plugin
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build \
    -ldflags="-w -s" \
    -o lightos-device-plugin \
    ./k8s-device-plugin/

# Stage 2: Runtime image
FROM alpine:latest

# Install runtime dependencies
RUN apk add --no-cache \
    ca-certificates \
    jq \
    bash

# Copy binaries from builder
COPY --from=builder /build/lightos-runtime /usr/bin/lightos-runtime
COPY --from=builder /build/lightos-device-plugin /usr/bin/lightos-device-plugin

# Copy hooks
COPY hooks/prestart /usr/libexec/oci/hooks.d/lightos-prestart
COPY hooks/poststop /usr/libexec/oci/hooks.d/lightos-poststop

RUN chmod +x /usr/bin/lightos-runtime \
    /usr/bin/lightos-device-plugin \
    /usr/libexec/oci/hooks.d/lightos-prestart \
    /usr/libexec/oci/hooks.d/lightos-poststop

# Create config directory
RUN mkdir -p /etc/lightos-runtime

# Add default config
COPY config/default.json /etc/lightos-runtime/config.json

# Create log directory
RUN mkdir -p /var/log && touch /var/log/lightos-runtime.log

ENTRYPOINT ["/usr/bin/lightos-runtime"]
CMD ["--help"]

# Metadata
LABEL org.opencontainers.image.title="LightOS Container Runtime"
LABEL org.opencontainers.image.description="Multi-vendor GPU container runtime"
LABEL org.opencontainers.image.vendor="LightOS"
LABEL org.opencontainers.image.source="https://github.com/Lightiam/LightOS"
LABEL org.opencontainers.image.documentation="https://github.com/Lightiam/LightOS/tree/main/lightos-container-runtime"
