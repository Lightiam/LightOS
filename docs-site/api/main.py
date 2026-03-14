"""
LightOS Agentic Platform API - Production Ready
All endpoints working with mock data
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import random

app = FastAPI(title="LightOS Agentic API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CLUSTERS = [
    {"id": 1, "name": "Production Cluster", "region": "us-west-2", "gpu_type": "H100", "gpu_count": 8, "status": "running", "created_at": "2024-01-15T10:30:00Z", "utilization": 78.5},
    {"id": 2, "name": "Development Cluster", "region": "us-east-1", "gpu_type": "A100", "gpu_count": 4, "status": "running", "created_at": "2024-02-01T14:20:00Z", "utilization": 45.2},
    {"id": 3, "name": "Training Cluster", "region": "eu-west-1", "gpu_type": "H100", "gpu_count": 16, "status": "running", "created_at": "2024-03-01T09:15:00Z", "utilization": 92.1}
]

@app.get("/")
async def root():
    return {"service": "LightOS Agentic API", "version": "1.0.0", "status": "operational"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/api/v1/clusters")
async def get_clusters():
    return {"clusters": CLUSTERS, "total": len(CLUSTERS)}

@app.get("/api/v1/monitoring/overview")
async def overview():
    return {
        "total_agents": 42, "active_clusters": 8, "running_jobs": 15,
        "gpu_utilization": 78.5, "photonic_fabric_status": "operational",
        "thermal_status": "normal"
    }

@app.get("/api/v1/monitoring/gpu")
async def gpu():
    gpus = [{"id": i, "name": f"NVIDIA H100 #{i}", "utilization": random.randint(65, 95), 
             "memory_used_gb": random.randint(50, 78), "memory_total_gb": 80,
             "temperature_c": random.randint(65, 82)} for i in range(8)]
    return {"gpus": gpus}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
