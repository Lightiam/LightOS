# LightOS Documentation Deployment Guide

This guide explains how to deploy the LightOS documentation website to Netlify or integrate it with your main site at https://lighrail.ink.

---

## 📦 **Option 1: Deploy to Netlify (Recommended)**

Deploy the documentation as a standalone site on Netlify.

### **Method A: Netlify CLI (Fastest)**

```bash
# 1. Install Netlify CLI
npm install -g netlify-cli

# 2. Login to Netlify
netlify login

# 3. Deploy from LightOS directory
cd ~/LightOS
netlify deploy

# Follow prompts:
#   - Create & configure a new site? Yes
#   - Team: Select your team
#   - Site name: lightos-docs (or your choice)
#   - Publish directory: docs-site

# 4. Deploy to production
netlify deploy --prod
```

**Your docs will be live at:** `https://lightos-docs.netlify.app`

### **Method B: GitHub + Netlify Integration**

```bash
# 1. Push to GitHub
git add .
git commit -m "Add documentation website"
git push origin claude/refactor-lightos-ai-56dEr

# 2. Go to Netlify Dashboard
# https://app.netlify.com/

# 3. Click "Add new site" → "Import an existing project"

# 4. Connect to GitHub and select your repository

# 5. Configure build settings:
#   - Branch: claude/refactor-lightos-ai-56dEr (or main)
#   - Publish directory: docs-site
#   - Build command: (leave empty)

# 6. Click "Deploy site"
```

**Benefits:**
- Automatic deploys on git push
- Deploy previews for pull requests
- Free SSL certificate
- CDN distribution
- Custom domain support

### **Method C: Drag & Drop Deploy**

```bash
# 1. Create a zip of the docs-site directory
cd ~/LightOS
zip -r lightos-docs.zip docs-site/*

# 2. Go to Netlify Drop
# https://app.netlify.com/drop

# 3. Drag and drop lightos-docs.zip

# 4. Get your live URL immediately
```

---

## 🌐 **Option 2: Integrate with Main Site (https://lighrail.ink)**

Integrate the documentation into your existing site.

### **Method A: Subdirectory Integration**

Host docs at `https://lighrail.ink/docs`

#### **If using Lovable/Static Site:**

```bash
# 1. Copy docs to your main site
cp -r ~/LightOS/docs-site/* /path/to/lighrail.ink/public/docs/

# 2. Update navigation in your main site
# Add link to /docs in your header/navigation

# 3. Deploy your main site as usual
```

#### **If using Next.js/React:**

```bash
# 1. Copy docs to public directory
cp -r ~/LightOS/docs-site/* /path/to/lighrail.ink/public/docs/

# 2. Or create Next.js pages
# Create pages/docs/index.tsx, etc.

# 3. Deploy
npm run build
npm run deploy
```

### **Method B: Subdomain Integration**

Host docs at `https://docs.lighrail.ink`

#### **DNS Configuration:**

```
# Add CNAME record:
docs.lighrail.ink → lightos-docs.netlify.app

# Or A record if self-hosting:
docs.lighrail.ink → YOUR_SERVER_IP
```

#### **Netlify Custom Domain:**

```bash
# After deploying to Netlify:

# 1. Go to Site settings → Domain management

# 2. Click "Add custom domain"

# 3. Enter: docs.lighrail.ink

# 4. Follow DNS verification steps

# 5. Enable HTTPS (automatic with Netlify)
```

### **Method C: API/Backend Integration**

If your main site has a backend, serve docs dynamically.

```javascript
// Express.js example
const express = require('express');
const app = express();

// Serve static docs
app.use('/docs', express.static('path/to/docs-site'));

// Or proxy to Netlify
const { createProxyMiddleware } = require('http-proxy-middleware');
app.use('/docs', createProxyMiddleware({
  target: 'https://lightos-docs.netlify.app',
  changeOrigin: true
}));
```

---

## 🎨 **Customization for Your Main Site**

### **Match Your Brand Colors**

Edit `docs-site/index.html`:

```css
:root {
    /* Change these to match lighrail.ink */
    --primary: #4F46E5;        /* Your primary color */
    --primary-dark: #4338CA;    /* Darker shade */
    --secondary: #10B981;       /* Accent color */
    /* ... */
}
```

### **Add Your Logo**

```html
<!-- In docs-site/index.html -->
<a href="/" class="logo">
    <img src="/assets/logo.png" alt="LightRail" height="32">
    LightOS Docs
</a>
```

### **Update Links**

```html
<!-- Link back to main site -->
<nav>
    <a href="https://lighrail.ink">Home</a>
    <a href="https://lighrail.ink/about">About</a>
    <a href="/docs">Docs</a>
</nav>
```

### **Add Analytics**

```html
<!-- Before </head> in index.html -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

---

## 📊 **What Gets Deployed**

```
docs-site/
├── index.html              # Landing page
├── guides/                 # User guides
│   ├── installation.html
│   ├── fine-tuning.html
│   └── coding-agents.html
├── api/                    # API reference
│   ├── unsloth.html
│   ├── coding-agents.html
│   └── cli.html
├── examples/               # Code examples
│   ├── basic.html
│   ├── advanced.html
│   └── use-cases.html
└── assets/                 # Images, CSS, JS
    ├── logo.png
    └── images/
```

---

## 🚀 **Recommended Approach**

For your use case, I recommend:

### **Best Option: Subdomain on Netlify**

```bash
# 1. Deploy to Netlify (fastest)
cd ~/LightOS
netlify deploy --prod

# 2. Configure custom domain
# Netlify Dashboard → Domain management
# Add: docs.lighrail.ink

# 3. Update DNS
# Add CNAME: docs.lighrail.ink → your-site.netlify.app

# 4. Link from main site
# Add to lighrail.ink navigation:
# <a href="https://docs.lighrail.ink">Documentation</a>
```

**Benefits:**
- Fast deployment (5 minutes)
- Automatic HTTPS
- Free hosting
- CDN distribution
- Separate from main site (easier updates)
- Auto-deploy on git push

**Live URLs:**
- Main site: `https://lighrail.ink`
- Documentation: `https://docs.lighrail.ink`

---

## 🔄 **Continuous Deployment**

### **Auto-deploy on Git Push**

```bash
# 1. Link Netlify to GitHub repo
# (Use Method B above)

# 2. Every time you update docs:
git add docs-site/
git commit -m "Update documentation"
git push

# 3. Netlify automatically deploys!
# Check status at: https://app.netlify.com/sites/your-site/deploys
```

### **Deploy Previews**

Every pull request gets a preview URL:
```
https://deploy-preview-123--lightos-docs.netlify.app
```

Perfect for reviewing changes before merging!

---

## 🛠️ **Maintenance**

### **Update Documentation**

```bash
# 1. Edit files in docs-site/
vim docs-site/guides/installation.html

# 2. Test locally (optional)
cd docs-site
python3 -m http.server 8000
# Visit: http://localhost:8000

# 3. Deploy
git add docs-site/
git commit -m "Update installation guide"
git push  # Auto-deploys if Netlify connected
```

### **Monitor Site**

```bash
# View deploy logs
netlify logs

# Check site status
netlify status

# Open site in browser
netlify open:site
```

---

## 🐛 **Troubleshooting**

### **Deploy Failed**

```bash
# Check build logs
netlify logs

# Common issues:
# - Missing files: Ensure docs-site/ exists
# - Wrong directory: Check netlify.toml publish path
# - Build command error: Set to empty in settings
```

### **404 Errors**

```bash
# Ensure all paths are correct
# Check netlify.toml redirect rules
# Test locally first:
cd docs-site && python3 -m http.server
```

### **Custom Domain Not Working**

```bash
# Verify DNS propagation
dig docs.lighrail.ink

# Check Netlify DNS settings
netlify deploy --prod
netlify open:admin
# Go to Domain management
```

---

## 📞 **Support**

### **Netlify Issues:**
- Docs: https://docs.netlify.com
- Community: https://answers.netlify.com

### **LightOS Issues:**
- GitHub: https://github.com/Lightiam/LightOS/issues
- Main site integration: Contact your web dev team

---

## ✅ **Quick Start Summary**

**For fastest deployment:**

```bash
# 1. Install Netlify CLI
npm install -g netlify-cli

# 2. Deploy
cd ~/LightOS
netlify login
netlify deploy --prod

# 3. Done! You'll get a URL like:
# https://lightos-docs.netlify.app
```

**For integration with lighrail.ink:**

```bash
# 1. Deploy to Netlify (as above)

# 2. Add custom domain in Netlify dashboard:
# docs.lighrail.ink

# 3. Update DNS for lighrail.ink:
# CNAME: docs → your-site.netlify.app

# 4. Wait for DNS propagation (5-60 minutes)

# 5. Access at: https://docs.lighrail.ink
```

---

**Choose your deployment method and let me know if you need help!**
