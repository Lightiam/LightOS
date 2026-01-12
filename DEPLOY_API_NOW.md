# 🚀 Deploy DCIM API Backend (5 Minutes)

Your dashboard is live at: **https://lightos.netlify.app/**

Now deploy the API backend to make it fully functional with real-time data!

---

## ✅ Current Status

- ✅ **Frontend:** Live at https://lightos.netlify.app/
- ⏳ **API Backend:** Needs deployment
- 🎯 **Goal:** Deploy API to https://lightos-dcim-api.onrender.com

---

## 🚀 Quick Deploy to Render.com (5 Minutes)

### Step 1: Sign Up for Render

1. Go to: **https://dashboard.render.com**
2. Click **"Get Started"** or **"Sign Up"**
3. Choose **"Sign up with GitHub"** (recommended)
4. Authorize Render to access your GitHub account

### Step 2: Create New Web Service

1. Click **"New +"** (top right)
2. Select **"Web Service"**
3. Click **"Connect account"** if prompted
4. Find and select your repository: **Lightiam/LightOS**

### Step 3: Configure the Service

Render will auto-detect the `render.yaml` configuration file!

**Auto-detected settings:**
- **Name:** `lightos-dcim-api`
- **Region:** Oregon (US West)
- **Branch:** `main` (or `claude/refactor-lightos-ai-56dEr`)
- **Root Directory:** `dcim-api`
- **Environment:** Python 3.11
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1`
- **Plan:** **Free**

**Click: "Apply"** or **"Create Web Service"**

### Step 4: Set Environment Variables (Optional)

For real Kaggle dataset integration:

1. In Render dashboard, go to **Environment** tab
2. Click **"Add Environment Variable"**
3. Add:
   - **Key:** `KAGGLE_API_TOKEN`
   - **Value:** `KGAT_2a4e49d583b937d8c08c972945c4b110`
4. Click **"Save Changes"**

### Step 5: Wait for Deployment

- Initial deployment takes **2-5 minutes**
- Watch the logs in real-time
- Status will change from "Building" → "Live"

### Step 6: Get Your API URL

After deployment completes:
- Your API will be live at: `https://lightos-dcim-api.onrender.com`
- Test it: Open `https://lightos-dcim-api.onrender.com/health`
- Should return: `{"status":"healthy"}`

---

## 🧪 Test Your API

After deployment, test these endpoints:

```bash
# Health check
curl https://lightos-dcim-api.onrender.com/health

# KPI data
curl https://lightos-dcim-api.onrender.com/api/dcim/kpi

# GPU metrics
curl https://lightos-dcim-api.onrender.com/api/dcim/gpu/0

# Cluster status
curl https://lightos-dcim-api.onrender.com/api/dcim/cluster
```

Or visit the interactive API documentation:
**https://lightos-dcim-api.onrender.com/docs**

---

## 🔗 Connect Dashboard to API

Good news! **Your dashboard is already configured** to use this API URL!

The dashboard auto-detects the environment:
- **Production:** Uses `https://lightos-dcim-api.onrender.com`
- **Development:** Uses `http://localhost:8001`

**No changes needed!** Once the API is deployed, refresh your dashboard and it will automatically connect.

---

## ✅ Verify Everything Works

### 1. Visit Your Dashboard

Open: **https://lightos.netlify.app/**

You should see:
- ✅ Automatic redirect to `/dcim.html`
- ✅ DCIM dashboard loads
- ✅ KPI cards display data (after API deployment)
- ✅ Real-time updates every 2 seconds

### 2. Check Browser Console

Press **F12** to open developer tools:
- ✅ Look for: `DCIM Dashboard loaded. API Base: https://lightos-dcim-api.onrender.com`
- ✅ No CORS errors
- ✅ No 404 errors
- ✅ Network tab shows successful API calls

### 3. Test Features

- ✅ 8 KPI cards updating with live data
- ✅ Clock Stability: ~99.8%
- ✅ Zero Throttling: 0 events
- ✅ Thermal Headroom: ~15°C
- ✅ Power Utilization: ~92%
- ✅ AI-OEE: 0.95
- ✅ MFU: 87.5%
- ✅ PUE: 1.10
- ✅ ESS SOC: ~65%

---

## 🐛 Troubleshooting

### API Returns 404

**Cause:** API not deployed yet or deployment failed

**Solution:**
1. Check Render dashboard for deployment status
2. Review logs for errors
3. Ensure `render.yaml` is in repository root or `dcim-api/` folder

### Dashboard Shows "Loading..." Forever

**Cause:** API not responding or CORS issue

**Solution:**

1. **Test API directly:**
   ```bash
   curl https://lightos-dcim-api.onrender.com/health
   ```

2. **Check browser console (F12):**
   - Look for CORS errors
   - Look for network errors

3. **Verify CORS is enabled:**
   - Check `dcim-api/main.py` has CORS middleware configured
   - Should allow: `https://lightos.netlify.app`

### API Takes 30+ Seconds to Respond

**Cause:** Render free tier "cold start" (API sleeps after 15 min inactivity)

**Expected behavior:**
- First request: ~30 seconds (waking up)
- Subsequent requests: <1 second

**Solutions:**
- Wait for first request to complete
- Upgrade to Render paid tier ($7/month) for always-on
- Implement keep-alive pings

### CORS Errors

**Symptom:** Browser console shows CORS errors

**Fix:** Update `dcim-api/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://lightos.netlify.app",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then push to GitHub and Render will auto-redeploy.

---

## 🔄 Automatic Updates

After initial setup, deployments are automatic!

**To update your API:**

```bash
# Make changes to dcim-api/
cd /home/user/LightOS/dcim-api

# Edit files...
vim main.py

# Commit and push
git add .
git commit -m "Update API"
git push origin main

# Render automatically rebuilds and deploys!
```

**To update your dashboard:**

```bash
# Make changes to docs-site/
cd /home/user/LightOS/docs-site

# Edit files...
vim dcim.html

# Commit and push
git add .
git commit -m "Update dashboard"
git push origin main

# Netlify automatically rebuilds and deploys!
```

---

## 💰 Cost

**Free tier is perfect for demos and development:**

| Service | Cost | Limits |
|---------|------|--------|
| Netlify | $0/month | 100 GB bandwidth/month |
| Render | $0/month | 750 hours/month, sleeps after 15 min |
| **Total** | **$0/month** | ✅ Zero cost! |

**Upgrade if needed:**
- **Render Starter:** $7/month (always-on, no cold starts)
- **Netlify Pro:** $19/month (more bandwidth, analytics)

---

## 📊 Architecture Diagram

```
┌───────────────────────────────────────────────┐
│  User visits: https://lightos.netlify.app/   │
└────────────────────┬──────────────────────────┘
                     │ 302 Redirect
┌────────────────────▼──────────────────────────┐
│  Dashboard: /dcim.html                        │
│  • Detects production environment             │
│  • Loads JavaScript                           │
│  • API_BASE = lightos-dcim-api.onrender.com   │
└────────────────────┬──────────────────────────┘
                     │ fetch() every 2s
┌────────────────────▼──────────────────────────┐
│  API: https://lightos-dcim-api.onrender.com   │
│  • FastAPI backend                            │
│  • DCIMSimulator (real-time metrics)          │
│  • Returns JSON data                          │
└────────────────────┬──────────────────────────┘
                     │ JSON Response
┌────────────────────▼──────────────────────────┐
│  Dashboard updates KPI cards                  │
│  • Clock Stability: 99.8%                     │
│  • Zero Throttling: 0 events                  │
│  • Live telemetry streaming                   │
└───────────────────────────────────────────────┘
```

---

## 📚 Documentation

- **DEPLOY_COMPLETE.md** - Complete deployment guide
- **dcim-api/DEPLOY_API.md** - Detailed API deployment options
- **dcim-api/README.md** - Full DCIM documentation
- **dcim-api/DEMO_READY.md** - Client demo talking points

---

## 🎯 Quick Reference

### Render Dashboard
- **URL:** https://dashboard.render.com
- **Service:** lightos-dcim-api
- **Logs:** Dashboard → Service → Logs
- **Environment Variables:** Dashboard → Service → Environment

### API Endpoints
- **Health:** `/health`
- **Docs:** `/docs`
- **KPIs:** `/api/dcim/kpi`
- **GPU Metrics:** `/api/dcim/gpu/{id}`
- **Cluster:** `/api/dcim/cluster`
- **Power:** `/api/dcim/power`
- **Thermal:** `/api/dcim/thermal`

### Your Live URLs
- **Dashboard:** https://lightos.netlify.app/
- **API:** https://lightos-dcim-api.onrender.com
- **API Docs:** https://lightos-dcim-api.onrender.com/docs

---

## ✅ Final Checklist

Before sharing with your client:

- [ ] API deployed to Render
- [ ] Health check responds: `/health`
- [ ] Dashboard loads at https://lightos.netlify.app/
- [ ] KPI cards show live data (not "--")
- [ ] No errors in browser console (F12)
- [ ] Tested on desktop browser
- [ ] Tested on mobile browser
- [ ] API documentation accessible: `/docs`
- [ ] Real-time updates working (every 2 seconds)

---

## 🎉 You're Done!

Once the API is deployed:

1. ✅ Dashboard: https://lightos.netlify.app/
2. ✅ API: https://lightos-dcim-api.onrender.com
3. ✅ Fully functional with real-time data
4. ✅ Ready to share with your client!

**Deploy now:** https://dashboard.render.com

**It takes less than 5 minutes! 🚀**
