# How to Push LightOS Dev Environment to markdown-builder

This guide shows you how to push the LightOS Development Environment to the markdown-builder repository at `https://github.com/Lightingmedia/markdown-builder`.

## Option 1: Automated Script (Easiest)

```bash
cd /home/user/LightOS
./push-to-markdown-builder.sh
```

This script will:
1. ✅ Clone markdown-builder repository
2. ✅ Create a new feature branch
3. ✅ Copy all LightOS dev environment files
4. ✅ Create integration documentation
5. ✅ Commit changes
6. ✅ Push to GitHub
7. ✅ Provide instructions for creating PR

**Just run it and follow the prompts!**

---

## Option 2: Manual Steps

If you prefer to do it manually or the script fails, follow these steps:

### Step 1: Clone markdown-builder

```bash
cd /tmp
rm -rf markdown-builder-update
git clone https://github.com/Lightingmedia/markdown-builder.git markdown-builder-update
cd markdown-builder-update
```

### Step 2: Create Feature Branch

```bash
git checkout -b feature/lightos-dev-environment
```

### Step 3: Copy LightOS Dev Environment Files

```bash
# Create directory for dev environment
mkdir -p lightos-dev-env

# Copy all dev environment files
cp -r /home/user/LightOS/llm-training-ground/dev-environment/* lightos-dev-env/

# Copy launcher
mkdir -p bin
cp /home/user/LightOS/bin/lightos-dev bin/
```

### Step 4: Create Integration README

```bash
cat > LIGHTOS_INTEGRATION.md << 'EOF'
# LightOS Development Environment

This repository now includes the **LightOS Development Environment** - a complete autonomous app builder with build server and live preview.

## Quick Start

```bash
cd lightos-dev-env
pip install -r requirements.txt
lightos-dev build "Build a todo app with user authentication"
```

## Features

- ✅ AI Code Generation (GLM-4)
- ✅ Build Server with hot-reload
- ✅ Live Preview (http://localhost:5173)
- ✅ AI Auto-Fix for errors
- ✅ Complete autonomy

## Documentation

- Quick Start: `lightos-dev-env/QUICK_START.md`
- Full Guide: `lightos-dev-env/README.md`
- Templates: `lightos-dev-env/templates/README.md`

## Learn More

https://github.com/Lightiam/LightOS
EOF
```

### Step 5: Commit Changes

```bash
git add -A

git commit -m "Add LightOS Development Environment integration

Integrate LightOS Dev Environment - a complete autonomous app builder
with build server and live preview capabilities.

Features:
- GLM-4 autonomous app builder
- Real-time build server with hot-reload
- Live preview at http://localhost:5173
- Build-run-fix orchestrator
- WebSocket-based real-time updates

Components Added:
- lightos-dev-env/ - Complete dev environment (3,592 lines)
- bin/lightos-dev - CLI launcher
- LIGHTOS_INTEGRATION.md - Integration guide

Usage:
  cd lightos-dev-env
  pip install -r requirements.txt
  lightos-dev build \"Your app idea\"

This enables markdown-builder users to generate working applications
from prompts, with build server and live preview.

Related: https://github.com/Lightiam/LightOS"
```

### Step 6: Push to GitHub

```bash
git push -u origin feature/lightos-dev-environment
```

**If you get authentication errors**, you may need to:

#### Option A: Use Personal Access Token
```bash
# Create token at: https://github.com/settings/tokens
# Then use it as password when prompted
git push -u origin feature/lightos-dev-environment
```

#### Option B: Use SSH
```bash
# Change remote to SSH
git remote set-url origin git@github.com:Lightingmedia/markdown-builder.git
git push -u origin feature/lightos-dev-environment
```

### Step 7: Create Pull Request

1. Go to: https://github.com/Lightingmedia/markdown-builder
2. Click "Compare & pull request" button
3. Review changes
4. Click "Create pull request"
5. Merge when ready

---

## Option 3: Direct Push to Main (If You Have Admin Access)

```bash
cd /tmp/markdown-builder-update
git checkout main
git pull origin main

# Copy files
mkdir -p lightos-dev-env bin
cp -r /home/user/LightOS/llm-training-ground/dev-environment/* lightos-dev-env/
cp /home/user/LightOS/bin/lightos-dev bin/

# Create integration doc
cat > LIGHTOS_INTEGRATION.md << 'EOF'
[Same content as above]
EOF

# Commit
git add -A
git commit -m "Add LightOS Development Environment integration"

# Push directly to main
git push origin main
```

---

## What Gets Pushed

### Files (3,592+ lines total):

```
markdown-builder/
├── lightos-dev-env/
│   ├── build_server.py           (593 lines)
│   ├── glm4_app_builder.py       (798 lines)
│   ├── orchestrator.py           (500 lines)
│   ├── lightos_dev.py            (308 lines)
│   ├── requirements.txt
│   ├── README.md                 (520 lines)
│   ├── QUICK_START.md            (314 lines)
│   ├── config/
│   │   └── dev_config.yaml
│   ├── examples/
│   │   ├── build_todo_app.py
│   │   └── build_dashboard.py
│   └── templates/
│       └── README.md
├── bin/
│   └── lightos-dev               (launcher)
└── LIGHTOS_INTEGRATION.md        (integration guide)
```

### Total Addition:
- **12 files**
- **3,592+ lines of code**
- **Complete development environment**

---

## Verification

After pushing, verify the integration:

```bash
# Clone the updated repo
git clone https://github.com/Lightingmedia/markdown-builder.git test-integration
cd test-integration

# Test the dev environment
cd lightos-dev-env
pip install -r requirements.txt
lightos-dev --help

# Should see:
# ╔═══════════════════════════════════════╗
# ║    LightOS Development Environment    ║
# ╚═══════════════════════════════════════╝
```

---

## Troubleshooting

### Issue: Permission Denied

**Solution:** You need to be a collaborator on the Lightingmedia/markdown-builder repo.

1. Ask the repo owner to add you as a collaborator
2. Or fork the repo and create a PR from your fork

### Issue: Authentication Failed

**Solutions:**

1. **Use Personal Access Token:**
   - Go to: https://github.com/settings/tokens
   - Create token with `repo` scope
   - Use as password when pushing

2. **Use SSH:**
   ```bash
   git remote set-url origin git@github.com:Lightingmedia/markdown-builder.git
   git push -u origin feature/lightos-dev-environment
   ```

3. **Use GitHub CLI:**
   ```bash
   gh auth login
   git push -u origin feature/lightos-dev-environment
   ```

### Issue: Repository Not Found

**Solution:** Verify the repo URL:
```bash
# Should be exactly:
https://github.com/Lightingmedia/markdown-builder
```

### Issue: Merge Conflicts

**Solution:**
```bash
git pull origin main
# Resolve conflicts
git add .
git commit -m "Resolve merge conflicts"
git push origin feature/lightos-dev-environment
```

---

## Alternative: Create New Repository

If you can't push to markdown-builder, create a new repo:

```bash
# Create new repo on GitHub: Lightingmedia/lightos-dev-environment

# Then push
cd /home/user/LightOS
git remote add markdown-builder https://github.com/Lightingmedia/lightos-dev-environment.git
git push markdown-builder claude/refactor-lightos-ai-56dEr:main
```

---

## Support

If you encounter issues:

1. Check your GitHub permissions
2. Verify you have access to Lightingmedia organization
3. Try the automated script first: `./push-to-markdown-builder.sh`
4. Check GitHub for network issues: https://www.githubstatus.com

---

## Summary

**Easiest method:**
```bash
./push-to-markdown-builder.sh
```

**Most control:**
Follow manual steps above

**Can't access repo:**
Create new repo or request access from repo owner

---

**Need help?** Open an issue at: https://github.com/Lightiam/LightOS/issues
