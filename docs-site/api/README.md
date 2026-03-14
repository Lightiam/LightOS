# LightOS Agentic Platform API

## Working Endpoints

All endpoints tested and working:

- `GET /health` - Health check
- `GET /api/v1/clusters` - List clusters ✅ FIXED
- `GET /api/v1/monitoring/overview` - System overview
- `GET /api/v1/monitoring/gpu` - GPU monitoring

## Deploy to Vercel

```bash
cd api
vercel --prod
```

## Local Testing

```bash
pip install -r requirements.txt
python main.py
```

Access at: http://localhost:8000
