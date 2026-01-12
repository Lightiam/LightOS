# 🚀 Deploy LightOS DCIM to Netlify

Complete guide for deploying the LightOS DCIM Dashboard to Netlify with continuous deployment.

---

## 📋 Prerequisites

- ✅ Netlify CLI installed (`npm install -g netlify-cli`)
- ✅ GitHub repository with your code
- ✅ Netlify account (free tier available at https://netlify.com)

---

## 🎯 Quick Deploy (3 Steps)

### Step 1: Login to Netlify

```bash
netlify login
```

This will open your browser to authenticate with Netlify.

### Step 2: Initialize Netlify Site

```bash
cd /home/user/LightOS
netlify init
```

**Interactive prompts:**
1. **Create & configure a new site**
2. **Team:** Select your team
3. **Site name:** `lightos-dcim` (or your preferred name)
4. **Build command:** Leave empty (press Enter)
5. **Directory to deploy:** `docs-site`
6. **Netlify config file:** Yes (use existing netlify.toml)

### Step 3: Deploy

```bash
netlify deploy --prod
```

**Your site will be live at:** `https://lightos-dcim.netlify.app`

---

## 🔄 Automatic Deployments (Recommended)

Enable continuous deployment from GitHub for automatic updates on every push.

### Step 1: Connect to Git

```bash
cd /home/user/LightOS
netlify link
```

Or via Netlify Dashboard:
1. Go to https://app.netlify.com
2. Click **"Add new site"** → **"Import an existing project"**
3. Connect to **GitHub**
4. Select repository: `Lightiam/LightOS`
5. Configure build settings:
   - **Branch to deploy:** `main`
   - **Base directory:** (leave empty)
   - **Build command:** (leave empty)
   - **Publish directory:** `docs-site`
6. Click **"Deploy site"**

### Step 2: Configure Build Settings

In your Netlify dashboard:
- **Site settings** → **Build & deploy** → **Build settings**
- Verify:
  - Publish directory: `docs-site`
  - Builds: Enabled
  - Deploy previews: Enabled (optional)

### Step 3: Set Environment Variables (Optional)

If you need environment variables:
1. **Site settings** → **Build & deploy** → **Environment**
2. Add variables:
   - `NODE_VERSION`: `18`

---

## 🌐 Custom Domain Setup

### Option 1: Netlify Subdomain (Free)

Your site is automatically available at:
```
https://[your-site-name].netlify.app
```

To change the subdomain:
1. **Site settings** → **Domain management** → **Custom domains**
2. Click **"Options"** → **"Edit site name"**
3. Enter new name: `lightos-dcim`
4. Your site is now: `https://lightos-dcim.netlify.app`

### Option 2: Custom Domain

To use your own domain (e.g., `dcim.yourdomain.com`):

1. **In Netlify Dashboard:**
   - **Site settings** → **Domain management**
   - Click **"Add custom domain"**
   - Enter: `dcim.yourdomain.com`
   - Click **"Verify"**

2. **In Your DNS Provider:**
   - Add a **CNAME** record:
     ```
     Type: CNAME
     Name: dcim
     Value: [your-site-name].netlify.app
     TTL: 3600
     ```

3. **Enable HTTPS:**
   - Netlify automatically provisions SSL certificate
   - Wait 1-2 minutes for verification
   - Your site is now: `https://dcim.yourdomain.com`

---

## 🔗 Connecting to Deployed API

After deploying your API (see `dcim-api/DEPLOY_API.md`), update the dashboard to use it.

### Method 1: Environment Detection (Recommended)

Edit `/home/user/LightOS/docs-site/dcim.html` (around line 750):

```javascript
// Auto-detect environment and use appropriate API
const API_BASE = window.location.hostname === 'localhost'
  ? 'http://localhost:8001'  // Local development
  : 'https://lightos-dcim-api.onrender.com';  // Production (update with your API URL)

const WS_BASE = window.location.hostname === 'localhost'
  ? 'ws://localhost:8001'
  : 'wss://lightos-dcim-api.onrender.com';
```

### Method 2: Configuration File

Create `/home/user/LightOS/docs-site/config.js`:

```javascript
window.LIGHTOS_CONFIG = {
  API_BASE_URL: 'https://lightos-dcim-api.onrender.com',  // Your deployed API
  WEBSOCKET_URL: 'wss://lightos-dcim-api.onrender.com/ws/dcim',
  REFRESH_INTERVAL: 2000,
  ENABLE_REAL_TIME: true
};
```

Add to `dcim.html` before other scripts:
```html
<script src="config.js"></script>
<script>
  const API_BASE = window.LIGHTOS_CONFIG?.API_BASE_URL || 'http://localhost:8001';
  const WS_BASE = window.LIGHTOS_CONFIG?.WEBSOCKET_URL || 'ws://localhost:8001/ws/dcim';
  // ... rest of your code
</script>
```

### Method 3: Netlify Environment Variables

Set API URL via Netlify environment variables:

1. **Site settings** → **Environment variables**
2. Add variable:
   - **Key:** `API_BASE_URL`
   - **Value:** `https://lightos-dcim-api.onrender.com`

3. Create `/home/user/LightOS/docs-site/_headers`:
```
/*
  X-API-Base-URL: https://lightos-dcim-api.onrender.com
```

4. Update `dcim.html`:
```javascript
// Read from meta tag or use default
const apiBaseMeta = document.querySelector('meta[name="api-base-url"]');
const API_BASE = apiBaseMeta?.content || 'http://localhost:8001';
```

---

## 🔧 Deploy Configuration Options

### netlify.toml Configuration

Your `netlify.toml` file controls deployment behavior:

```toml
[build]
  publish = "docs-site"
  command = "echo 'Deploying LightOS DCIM Dashboard'"

# Redirect API calls to backend
[[redirects]]
  from = "/api/dcim/*"
  to = "https://lightos-dcim-api.onrender.com/api/dcim/:splat"
  status = 200
  force = true

# WebSocket proxy
[[redirects]]
  from = "/ws/dcim"
  to = "wss://lightos-dcim-api.onrender.com/ws/dcim"
  status = 200
  force = true

# CORS headers
[[headers]]
  for = "/*"
  [headers.values]
    Access-Control-Allow-Origin = "*"
    Access-Control-Allow-Methods = "GET, POST, OPTIONS"
```

**Update the API URLs** in `netlify.toml` after deploying your API backend.

---

## 🧪 Testing Before Production

### Deploy Preview

Test your changes before going live:

```bash
# Deploy to preview URL
netlify deploy

# Visit preview URL (provided in output)
# Example: https://5f6a3b2c1d0e9f8g7h6i5j4k3l2m1n0o--lightos-dcim.netlify.app
```

### Local Testing

Test the production build locally:

```bash
# Serve the docs-site directory
cd /home/user/LightOS/docs-site
python -m http.server 8000

# Open in browser
open http://localhost:8000/dcim.html
```

### Deploy to Production

When ready:

```bash
netlify deploy --prod
```

---

## 📊 Netlify Dashboard Features

### Analytics
- **Site overview** → View traffic, bandwidth, build history
- **Analytics** → Page views, unique visitors (upgrade required)

### Deploy Notifications
- **Site settings** → **Build & deploy** → **Deploy notifications**
- Add notifications for:
  - Slack
  - Email
  - Webhook

### Build Hooks
Create webhooks to trigger deployments:
- **Site settings** → **Build & deploy** → **Build hooks**
- Click **"Add build hook"**
- Name: `Rebuild DCIM Dashboard`
- Branch: `main`
- Copy webhook URL

Trigger rebuild:
```bash
curl -X POST -d '{}' https://api.netlify.com/build_hooks/[your-hook-id]
```

---

## 🐛 Troubleshooting

### Site Not Found (404)

**Cause:** Incorrect publish directory

**Fix:**
```bash
# Check your netlify.toml
cat netlify.toml

# Verify publish directory exists
ls -la docs-site/

# Redeploy
netlify deploy --prod --dir=docs-site
```

### API Calls Failing (CORS)

**Cause:** API not configured for cross-origin requests

**Fix in API (`dcim-api/main.py`):**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://lightos-dcim.netlify.app",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Build Failing

**Check build logs:**
```bash
netlify logs
```

**Common issues:**
- Missing files in `docs-site/`
- Incorrect `netlify.toml` configuration
- Build command errors (should be empty for static site)

### Assets Not Loading

**Cause:** Incorrect paths in HTML

**Fix:** Use relative paths in `dcim.html`:
```html
<!-- Wrong -->
<script src="/assets/script.js"></script>

<!-- Correct -->
<script src="./assets/script.js"></script>
```

### Deploy Takes Too Long

**Cause:** Large files or unnecessary files being uploaded

**Fix:** Add `.gitignore`:
```bash
# Netlify build cache
.netlify/

# Python cache
__pycache__/
*.pyc

# Data files
data/
*.csv
*.json
```

---

## 🚀 Advanced Configuration

### Deploy Previews for Pull Requests

Enable preview deployments for all PRs:
1. **Site settings** → **Build & deploy** → **Deploy contexts**
2. Enable **"Deploy Previews"**
3. Select **"Any pull request against your production branch"**

Now every PR gets a preview URL automatically!

### Branch Deploys

Deploy specific branches:
1. **Site settings** → **Build & deploy** → **Deploy contexts**
2. Enable **"Branch deploys"**
3. Select branches: `main`, `develop`, `staging`

Each branch gets its own URL:
- `main`: `https://lightos-dcim.netlify.app`
- `develop`: `https://develop--lightos-dcim.netlify.app`
- `staging`: `https://staging--lightos-dcim.netlify.app`

### Netlify Functions (Optional)

If you want to run serverless functions:

Create `/home/user/LightOS/netlify/functions/hello.js`:
```javascript
exports.handler = async function(event, context) {
  return {
    statusCode: 200,
    body: JSON.stringify({ message: "Hello from Netlify Functions!" })
  };
};
```

Access at: `https://lightos-dcim.netlify.app/.netlify/functions/hello`

---

## 📈 Performance Optimization

### Asset Optimization

Netlify automatically optimizes:
- Image compression
- CSS/JS minification
- Brotli compression

Enable in **Site settings** → **Build & deploy** → **Asset optimization**

### Caching Headers

Already configured in `netlify.toml`:
```toml
[[headers]]
  for = "/*.js"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"
```

### CDN Edge Locations

Netlify uses Akamai CDN with global edge nodes for fast delivery worldwide.

---

## 🔐 Security Best Practices

### HTTPS

Netlify provides automatic HTTPS with Let's Encrypt certificates.

Enable HSTS in `netlify.toml`:
```toml
[[headers]]
  for = "/*"
  [headers.values]
    Strict-Transport-Security = "max-age=31536000; includeSubDomains; preload"
```

### Access Control (Optional)

Password-protect your site:
1. **Site settings** → **Visitor access**
2. Enable **"Password protection"**
3. Set password
4. Your site now requires authentication

Or use Netlify Identity for user management:
```bash
netlify addons:create identity
```

### Environment Variables

Never commit secrets! Use Netlify environment variables:
1. **Site settings** → **Environment variables**
2. Add sensitive values
3. Access in build process (not in browser)

---

## 📦 Deployment Checklist

Before deploying to production:

- [ ] API backend is deployed and accessible
- [ ] Dashboard `API_BASE` URL is updated
- [ ] `netlify.toml` API redirects are configured
- [ ] CORS is enabled on API for your domain
- [ ] All assets load correctly (test locally)
- [ ] WebSocket connection works (if using real-time)
- [ ] Health check endpoint responds: `/health`
- [ ] API documentation is accessible: `/docs`
- [ ] Custom domain is configured (if applicable)
- [ ] HTTPS is enabled
- [ ] Site is tested on desktop and mobile
- [ ] Error pages are configured (404, 500)
- [ ] Analytics/monitoring is set up (optional)

---

## 🎉 Post-Deployment

### Share Your Site

Your DCIM dashboard is live! Share it:
- **Dashboard:** `https://lightos-dcim.netlify.app/dcim.html`
- **Main Site:** `https://lightos-dcim.netlify.app`
- **API Docs:** `https://lightos-dcim-api.onrender.com/docs`

### Monitor Traffic

View in Netlify Dashboard:
- Total page views
- Bandwidth usage
- Build history
- Deploy frequency

### Continuous Deployment

Every push to `main` branch automatically deploys:
```bash
git add .
git commit -m "Update DCIM dashboard"
git push origin main

# Netlify automatically builds and deploys!
```

---

## 🆘 Support & Resources

### Netlify Documentation
- https://docs.netlify.com
- https://docs.netlify.com/configure-builds/
- https://docs.netlify.com/routing/redirects/

### LightOS DCIM Documentation
- `dcim-api/DEMO_READY.md` - Demo guide
- `dcim-api/DEPLOY_API.md` - API deployment
- `dcim-api/README.md` - Full documentation

### Community Support
- Netlify Community: https://answers.netlify.com
- Netlify Status: https://www.netlifystatus.com

---

## 🚀 Quick Reference

```bash
# Login
netlify login

# Initialize site
netlify init

# Deploy preview
netlify deploy

# Deploy to production
netlify deploy --prod

# Open site in browser
netlify open:site

# Open admin dashboard
netlify open:admin

# View logs
netlify logs

# Link to existing site
netlify link

# Environment variables
netlify env:set KEY value
netlify env:list

# Build hooks
netlify build

# Functions
netlify functions:create
netlify functions:invoke hello

# Status
netlify status
```

---

**Deployment Status:** ✅ Ready for production
**Last Updated:** 2026-01-12
**Next Steps:** Deploy API backend → Update dashboard URLs → Deploy to Netlify → Share with client
