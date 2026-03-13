#!/usr/bin/env python3
"""
LightOS Telemetry API — Phase 1
Records every inference job, aggregates cost/utilization metrics,
and builds Model-Job Template clusters for Antigravity optimization.
Port: 8013
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import time
import os

from models import TelemetryDB

DATA_DIR = os.getenv("DATA_DIR", "/data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "telemetry.db")

app = FastAPI(
    title="LightOS Telemetry API",
    description="Records inference events, aggregates metrics, builds Model-Job Templates",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = TelemetryDB(DB_PATH)


# ─── Models ──────────────────────────────────────────────────────────────────

class TelemetryEvent(BaseModel):
    job_id: str
    model_tier: str                              # lightmicro | lightbase | lightmax
    tokens_used: int
    prompt_tokens: Optional[int] = 0
    completion_tokens: Optional[int] = 0
    latency_ms: float
    cache_hit: bool
    cache_type: Optional[str] = None            # exact | semantic | None
    topology_domain: Optional[str] = "dc-1-rack-a"
    user_id: Optional[str] = "anonymous"
    app_id: Optional[str] = "default"
    matched_rule: Optional[str] = "default"
    cost_usd: Optional[float] = 0.0
    context_chunks_used: Optional[int] = 0


# ─── Endpoints ───────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "service": "LightOS Telemetry API",
        "version": "1.0.0",
        "db_path": DB_PATH,
        "endpoints": {
            "event": "POST /telemetry/event",
            "jobs": "GET /telemetry/jobs",
            "summary": "GET /telemetry/summary",
            "templates": "GET /telemetry/templates",
            "health": "GET /telemetry/health"
        }
    }


@app.get("/telemetry/health")
async def health():
    count = db.count()
    return {"status": "healthy", "event_count": count, "db_path": DB_PATH, "timestamp": time.time()}


@app.post("/telemetry/event")
async def record_event(event: TelemetryEvent):
    """Store a single telemetry event."""
    db.insert(event.model_dump())
    return {"status": "recorded", "job_id": event.job_id}


@app.get("/telemetry/jobs")
async def list_jobs(limit: int = Query(default=50, le=500)):
    """Return recent jobs for the Workload List panel."""
    rows = db.recent_jobs(limit)
    return {"jobs": rows, "count": len(rows)}


@app.get("/telemetry/summary")
async def get_summary():
    """Return aggregated metrics for Cost & Utilization charts."""
    return db.summary()


@app.get("/telemetry/templates")
async def get_templates():
    """Return Model-Job Template clusters (grouped by tier + domain)."""
    return db.model_job_templates()


@app.get("/telemetry/timeseries")
async def get_timeseries(hours: int = Query(default=24, le=168)):
    """Return hourly aggregated metrics for time-series charts."""
    return db.hourly_series(hours)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8013)), log_level="info")
