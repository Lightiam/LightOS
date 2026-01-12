#!/bin/bash
# Push LightOS Dev Environment to markdown-builder repository

set -e

echo "================================="
echo "Push to markdown-builder Guide"
echo "================================="
echo ""

# Configuration
LIGHTOS_REPO="/home/user/LightOS"
MARKDOWN_BUILDER_REPO="https://github.com/Lightingmedia/markdown-builder"
TARGET_DIR="/tmp/markdown-builder-update"

echo "This script will:"
echo "1. Clone markdown-builder repository"
echo "2. Copy LightOS dev environment files"
echo "3. Commit and push to markdown-builder"
echo ""

read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Step 1: Clean and clone markdown-builder
echo ""
echo "Step 1: Cloning markdown-builder repository..."
rm -rf "$TARGET_DIR"
git clone "$MARKDOWN_BUILDER_REPO" "$TARGET_DIR"
cd "$TARGET_DIR"

# Create a new branch for this feature
BRANCH_NAME="feature/lightos-dev-environment-$(date +%s)"
git checkout -b "$BRANCH_NAME"

echo "✓ Repository cloned and branch created: $BRANCH_NAME"

# Step 2: Copy LightOS dev environment
echo ""
echo "Step 2: Copying LightOS dev environment files..."

# Create directory structure
mkdir -p lightos-dev-env

# Copy dev environment files
cp -r "$LIGHTOS_REPO/llm-training-ground/dev-environment/"* lightos-dev-env/

# Copy launcher
mkdir -p bin
cp "$LIGHTOS_REPO/bin/lightos-dev" bin/

# Create integration README
cat > LIGHTOS_INTEGRATION.md << 'EOF'
# LightOS Development Environment

This repository now includes the **LightOS Development Environment** - a complete autonomous app builder with build server and live preview.

## What is LightOS Dev Environment?

A full-featured development environment powered by GLM-4 that turns single prompts into working web applications with:

- ✅ **AI Code Generation** - GLM-4 autonomous builder
- ✅ **Build Server** - Real-time compilation with hot-reload
- ✅ **Live Preview** - See your app at http://localhost:5173
- ✅ **Auto-Fix** - AI fixes build errors automatically
- ✅ **Build-Run-Fix Loop** - Fully autonomous development

## Quick Start

```bash
# Install dependencies
cd lightos-dev-env
pip install -r requirements.txt

# Build an app
./bin/lightos-dev build "Build a todo app with user authentication"

# Wait 3-5 minutes, then open:
# - Frontend: http://localhost:5173
# - API: http://localhost:8000/docs
```

## Documentation

- **Quick Start:** `lightos-dev-env/QUICK_START.md`
- **Full Guide:** `lightos-dev-env/README.md`
- **Templates:** `lightos-dev-env/templates/README.md`

## vs Lovable

| Feature | Lovable | LightOS Dev |
|---------|---------|-------------|
| Code Generation | ✅ | ✅ |
| Build Server | ❌ | ✅ |
| Live Preview | ❌ | ✅ |
| Hot Reload | ❌ | ✅ |
| AI Auto-Fix | ❌ | ✅ |

## Integration with Markdown Builder

The LightOS dev environment can be used alongside markdown-builder to:

1. **Generate Documentation Sites:** Build doc sites from prompts
2. **Create Interactive Demos:** Build working demos of concepts
3. **Rapid Prototyping:** Turn documentation into working code

## Examples

```bash
# Build a documentation site
lightos-dev build "Build a documentation site with search and navigation"

# Build an interactive demo
lightos-dev build "Build a code playground for testing markdown components"

# Build a dashboard
lightos-dev build "Build an analytics dashboard for documentation metrics"
```

## Learn More

- **LightOS Repository:** https://github.com/Lightiam/LightOS
- **Documentation:** https://docs.lightrail.ink
- **Issues:** https://github.com/Lightiam/LightOS/issues
EOF

echo "✓ Files copied"

# Step 3: Commit changes
echo ""
echo "Step 3: Committing changes..."

git add -A

git commit -m "$(cat <<'EOF'
Add LightOS Development Environment integration

Integrate LightOS Dev Environment - a complete autonomous app builder
with build server and live preview capabilities.

Features:
- GLM-4 autonomous app builder
- Real-time build server with hot-reload
- Live preview at http://localhost:5173
- Build-run-fix orchestrator
- WebSocket-based real-time updates
- Complete CLI: lightos-dev

Components Added:
- lightos-dev-env/ - Complete dev environment
  * build_server.py (593 lines)
  * glm4_app_builder.py (798 lines)
  * orchestrator.py (500 lines)
  * lightos_dev.py (308 lines)
  * Examples and templates
  * Complete documentation

- bin/lightos-dev - CLI launcher
- LIGHTOS_INTEGRATION.md - Integration guide

Usage:
  cd lightos-dev-env
  pip install -r requirements.txt
  lightos-dev build "Your app idea"

This enables markdown-builder users to generate working applications
from prompts, with build server and live preview - going beyond code
generation to provide a complete development environment.

Build time: 3-5 minutes from prompt to running app
Preview: http://localhost:5173 (auto-reload)
API: http://localhost:8000/docs

Related: https://github.com/Lightiam/LightOS
EOF
)"

echo "✓ Changes committed"

# Step 4: Push to GitHub
echo ""
echo "Step 4: Pushing to GitHub..."
echo ""
echo "Branch: $BRANCH_NAME"
echo ""

# Show what will be pushed
git log origin/main..$BRANCH_NAME --oneline

echo ""
echo "Files to be pushed:"
git diff --stat origin/main..$BRANCH_NAME

echo ""
echo "Ready to push to: $MARKDOWN_BUILDER_REPO"
echo "Branch: $BRANCH_NAME"
echo ""

read -p "Push to GitHub? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted. Changes are committed locally at: $TARGET_DIR"
    echo "You can push manually with:"
    echo "  cd $TARGET_DIR"
    echo "  git push -u origin $BRANCH_NAME"
    exit 1
fi

# Push to GitHub
git push -u origin "$BRANCH_NAME"

echo ""
echo "================================="
echo "✓ SUCCESS!"
echo "================================="
echo ""
echo "Pushed to: $MARKDOWN_BUILDER_REPO"
echo "Branch: $BRANCH_NAME"
echo ""
echo "Next steps:"
echo "1. Go to: https://github.com/Lightingmedia/markdown-builder"
echo "2. Create a Pull Request from branch: $BRANCH_NAME"
echo "3. Review the changes"
echo "4. Merge to main"
echo ""
echo "Or merge directly:"
echo "  cd $TARGET_DIR"
echo "  git checkout main"
echo "  git merge $BRANCH_NAME"
echo "  git push origin main"
echo ""
