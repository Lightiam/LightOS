#!/usr/bin/env python3
"""
LightOS Router API — Phase 1
Dynamic model routing: selects LightMicro / LightBase / LightMax based on SLO, context, and user tier.
Port: 8011
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import time
import yaml
import os

from policy_engine import PolicyEngine

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")

app = FastAPI(
    title="LightOS Router API",
    description="Dynamic model routing: selects LightMicro / LightBase / LightMax per request",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load policy engine
policy = PolicyEngine(CONFIG_PATH)


# ─── Request / Response Models ────────────────────────────────────────────────

class RouteRequest(BaseModel):
    prompt_length: int                          # characters
    context_tokens: Optional[int] = 0          # tokens already retrieved
    user_tier: Optional[str] = "standard"      # free | standard | premium
    latency_slo_ms: Optional[int] = 500        # target P99 latency
    app_id: Optional[str] = "default"
    task_type: Optional[str] = "inference"     # inference | training | routing


class RouteResponse(BaseModel):
    model_tier: str               # lightmicro | lightbase | lightmax
    model_display_name: str
    context_budget: int
    cache_strategy: str           # exact | semantic | aggressive | none
    matched_rule: str
    estimated_latency_ms: int
    estimated_cost_per_1k: float
    topology_domain: str


class PolicyUpdateRequest(BaseModel):
    rules_yaml: str               # full YAML string for routing_rules block


# ─── Endpoints ───────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "service": "LightOS Router API",
        "version": "1.0.0",
        "model_tiers": ["lightmicro", "lightbase", "lightmax"],
        "endpoints": {
            "route": "POST /router/route",
            "policy": "GET /router/policy",
            "config_update": "POST /config/update",
            "health": "GET /router/health"
        }
    }


@app.get("/router/health")
async def health():
    return {
        "status": "healthy",
        "rules_count": policy.rules_count(),
        "config_path": CONFIG_PATH,
        "timestamp": time.time()
    }


@app.get("/router/policy")
async def get_policy():
    """Return current routing rules and tier definitions."""
    return policy.get_full_policy()


@app.post("/router/route", response_model=RouteResponse)
async def route_request(req: RouteRequest):
    """Evaluate routing rules and return optimal model tier + context config."""
    result = policy.evaluate(
        prompt_length=req.prompt_length,
        context_tokens=req.context_tokens,
        user_tier=req.user_tier,
        latency_slo_ms=req.latency_slo_ms,
        task_type=req.task_type
    )
    return RouteResponse(**result)


@app.post("/config/update")
async def update_policy(req: PolicyUpdateRequest):
    """Hot-reload routing rules from submitted YAML."""
    try:
        new_rules = yaml.safe_load(req.rules_yaml)
        policy.update_rules(new_rules, CONFIG_PATH)
        return {"status": "ok", "rules_count": policy.rules_count()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid YAML: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8011)), log_level="info")
