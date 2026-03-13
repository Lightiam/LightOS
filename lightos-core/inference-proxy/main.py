#!/usr/bin/env python3
"""
LightOS Inference Proxy — Phase 1
Routes inference requests to LightMicro / LightBase / LightMax mock adapters.
Schema-compatible for real vLLM/SGLang swap-in.
Port: 8012
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import time
import uuid
import os

from model_adapters import get_adapter

app = FastAPI(
    title="LightOS Inference Proxy",
    description="Inference dispatcher for LightMicro / LightBase / LightMax model tiers",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Models ──────────────────────────────────────────────────────────────────

class ChunkInput(BaseModel):
    text: str
    score: float
    chunk_id: str


class InferenceRequest(BaseModel):
    model_tier: str                          # lightmicro | lightbase | lightmax
    prompt: str
    context_chunks: Optional[List[ChunkInput]] = []
    cache_key: Optional[str] = ""
    user_id: Optional[str] = "anonymous"
    app_id: Optional[str] = "default"
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.7


class InferenceResponse(BaseModel):
    job_id: str
    model_tier: str
    model_display_name: str
    answer: str
    tokens_used: int
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float
    cost_usd: float
    context_chunks_used: int


# ─── Endpoints ───────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "service": "LightOS Inference Proxy",
        "version": "1.0.0",
        "tiers": {
            "lightmicro": "1-3B · ultra-fast · simple tasks",
            "lightbase": "13-30B · standard inference",
            "lightmax": "70B+ · complex reasoning · photonic-backed"
        },
        "endpoints": {
            "run": "POST /inference/run",
            "health": "GET /inference/health"
        }
    }


@app.get("/inference/health")
async def health():
    return {"status": "healthy", "timestamp": time.time()}


@app.post("/inference/run", response_model=InferenceResponse)
async def run_inference(req: InferenceRequest):
    tier = req.model_tier.lower()
    adapter = get_adapter(tier)
    if adapter is None:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model tier '{tier}'. Use: lightmicro, lightbase, lightmax"
        )

    job_id = str(uuid.uuid4())[:12]
    context_text = "\n".join(c.text for c in req.context_chunks) if req.context_chunks else ""
    full_prompt = f"{context_text}\n\nUser: {req.prompt}" if context_text else f"User: {req.prompt}"

    result = adapter.generate(full_prompt, max_tokens=req.max_tokens, temperature=req.temperature)

    return InferenceResponse(
        job_id=job_id,
        model_tier=tier,
        model_display_name=result["display_name"],
        answer=result["answer"],
        tokens_used=result["tokens_used"],
        prompt_tokens=result["prompt_tokens"],
        completion_tokens=result["completion_tokens"],
        latency_ms=result["latency_ms"],
        cost_usd=result["cost_usd"],
        context_chunks_used=len(req.context_chunks)
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8012)), log_level="info")
