.PHONY: all build install clean test docker-build docker-push k8s-deploy help

# Variables
BINARY_NAME=lightos-runtime
DEVICE_PLUGIN_BINARY=lightos-device-plugin
VERSION?=1.0.0
DOCKER_IMAGE?=lightos/container-runtime
DOCKER_TAG?=$(VERSION)
GO=go
GOFLAGS=-v
LDFLAGS=-ldflags="-w -s -X main.version=$(VERSION)"

# Directories
BIN_DIR=bin
INSTALL_DIR=/usr/bin
CONFIG_DIR=/etc/lightos-runtime
HOOKS_DIR=/usr/libexec/oci/hooks.d

all: build

help:
	@echo "LightOS Container Runtime - Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  build          - Build binaries"
	@echo "  install        - Install to system"
	@echo "  uninstall      - Remove from system"
	@echo "  clean          - Clean build artifacts"
	@echo "  test           - Run tests"
	@echo "  docker-build   - Build Docker image"
	@echo "  docker-push    - Push Docker image"
	@echo "  k8s-deploy     - Deploy to Kubernetes"
	@echo "  k8s-undeploy   - Remove from Kubernetes"
	@echo ""
	@echo "Variables:"
	@echo "  VERSION=$(VERSION)"
	@echo "  DOCKER_IMAGE=$(DOCKER_IMAGE)"
	@echo "  DOCKER_TAG=$(DOCKER_TAG)"

build: build-runtime build-device-plugin

build-runtime:
	@echo "Building runtime..."
	@mkdir -p $(BIN_DIR)
	$(GO) build $(GOFLAGS) $(LDFLAGS) -o $(BIN_DIR)/$(BINARY_NAME) ./cmd/lightos-runtime/
	@echo "✓ Runtime built: $(BIN_DIR)/$(BINARY_NAME)"

build-device-plugin:
	@echo "Building device plugin..."
	@mkdir -p $(BIN_DIR)
	$(GO) build $(GOFLAGS) $(LDFLAGS) -o $(BIN_DIR)/$(DEVICE_PLUGIN_BINARY) ./k8s-device-plugin/
	@echo "✓ Device plugin built: $(BIN_DIR)/$(DEVICE_PLUGIN_BINARY)"

install: build
	@echo "Installing LightOS Container Runtime..."
	@install -m 755 $(BIN_DIR)/$(BINARY_NAME) $(INSTALL_DIR)/$(BINARY_NAME)
	@install -m 755 $(BIN_DIR)/$(DEVICE_PLUGIN_BINARY) $(INSTALL_DIR)/$(DEVICE_PLUGIN_BINARY)
	@mkdir -p $(HOOKS_DIR)
	@install -m 755 hooks/prestart $(HOOKS_DIR)/lightos-prestart
	@install -m 755 hooks/poststop $(HOOKS_DIR)/lightos-poststop
	@mkdir -p $(CONFIG_DIR)
	@if [ ! -f $(CONFIG_DIR)/config.json ]; then \
		install -m 644 config/default.json $(CONFIG_DIR)/config.json; \
	fi
	@echo "✓ Installation complete"
	@echo ""
	@echo "Configure Docker daemon:"
	@echo "  sudo $(INSTALL_DIR)/$(BINARY_NAME) configure"
	@echo "  sudo systemctl restart docker"

uninstall:
	@echo "Uninstalling LightOS Container Runtime..."
	@rm -f $(INSTALL_DIR)/$(BINARY_NAME)
	@rm -f $(INSTALL_DIR)/$(DEVICE_PLUGIN_BINARY)
	@rm -f $(HOOKS_DIR)/lightos-prestart
	@rm -f $(HOOKS_DIR)/lightos-poststop
	@echo "✓ Uninstalled"
	@echo ""
	@echo "Note: Configuration files in $(CONFIG_DIR) were not removed"

clean:
	@echo "Cleaning build artifacts..."
	@rm -rf $(BIN_DIR)
	@rm -f $(BINARY_NAME) $(DEVICE_PLUGIN_BINARY)
	@$(GO) clean
	@echo "✓ Clean complete"

test:
	@echo "Running tests..."
	@$(GO) test -v ./...

test-coverage:
	@echo "Running tests with coverage..."
	@$(GO) test -v -coverprofile=coverage.out ./...
	@$(GO) tool cover -html=coverage.out -o coverage.html
	@echo "✓ Coverage report: coverage.html"

docker-build:
	@echo "Building Docker image: $(DOCKER_IMAGE):$(DOCKER_TAG)"
	@docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .
	@docker tag $(DOCKER_IMAGE):$(DOCKER_TAG) $(DOCKER_IMAGE):latest
	@echo "✓ Docker image built"

docker-push: docker-build
	@echo "Pushing Docker image: $(DOCKER_IMAGE):$(DOCKER_TAG)"
	@docker push $(DOCKER_IMAGE):$(DOCKER_TAG)
	@docker push $(DOCKER_IMAGE):latest
	@echo "✓ Docker image pushed"

k8s-deploy:
	@echo "Deploying to Kubernetes..."
	@kubectl apply -f k8s/lightos-device-plugin.yaml
	@echo "✓ Deployed to Kubernetes"
	@echo ""
	@echo "Check status:"
	@echo "  kubectl get pods -n kube-system | grep lightos"

k8s-undeploy:
	@echo "Removing from Kubernetes..."
	@kubectl delete -f k8s/lightos-device-plugin.yaml
	@echo "✓ Removed from Kubernetes"

detect:
	@$(BIN_DIR)/$(BINARY_NAME) detect

info:
	@$(BIN_DIR)/$(BINARY_NAME) info

lint:
	@echo "Running linters..."
	@golangci-lint run ./...

format:
	@echo "Formatting code..."
	@gofmt -w .
	@$(GO) mod tidy

# Development targets
dev-install: build
	@echo "Installing for development..."
	@sudo install -m 755 $(BIN_DIR)/$(BINARY_NAME) $(INSTALL_DIR)/$(BINARY_NAME)
	@echo "✓ Development install complete"

dev-uninstall:
	@sudo rm -f $(INSTALL_DIR)/$(BINARY_NAME)

# Quick test with Docker
docker-test:
	@echo "Testing with Docker..."
	@docker run --runtime=lightos alpine:latest echo "LightOS runtime working!"

# Generate documentation
docs:
	@echo "Generating documentation..."
	@godoc -http=:6060
	@echo "Documentation server running on http://localhost:6060"

.DEFAULT_GOAL := help
