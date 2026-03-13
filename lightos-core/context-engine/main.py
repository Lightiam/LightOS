#!/usr/bin/env python3
"""
LightOS Context Engine — Phase 1
Handles: text chunking, embedding, vector search, semantic + exact cache.
Port: 8010
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import hashlib
import time
import uuid
import asyncio

from chunker import chunk_text
from embedder import embed_texts, embed_query
from vector_store import VectorStore
from cache import ContextCache

app = FastAPI(
    title="LightOS Context Engine",
    description="Log-cost context orchestration: chunking, embedding, semantic cache, vector retrieval",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
vector_store = VectorStore()
cache = ContextCache(exact_ttl=300, semantic_threshold=0.92)

# Seed with a small knowledge base at startup
SEED_DOCS = [
    "LightOS is an AI-native operating system designed for photonic computing clusters.",
    "Photonic interconnects provide orders-of-magnitude bandwidth improvements over electrical NVLink.",
    "LightMicro is a 1-3B parameter model tier used for fast routing decisions and simple tasks.",
    "LightBase is a 13-30B parameter model tier for standard inference workloads.",
    "LightMax is a 70B+ model tier backed by photonic compute for complex reasoning.",
    "The LightOS scheduler performs topology-aware placement across photonic fabric domains.",
    "KV cache sharing across nodes is enabled by the low-latency photonic memory fabric.",
    "Antigravity is the AI architect layer that synthesizes routing, scheduling, and placement policies.",
    "The Context Engine retrieves relevant chunks from a global knowledge store, reducing per-request token costs.",
    "Semantic caching reuses past answers for semantically similar queries, cutting inference costs by 30-60%.",
    "Model FLOPS Utilization (MFU) is a key metric for LightOS cluster efficiency.",
    "The Router API selects model tiers based on SLO, user priority, and context length.",
    "PUE (Power Usage Effectiveness) of the LightOS cluster is maintained below 1.12 via dynamic power capping.",
    "Topology fingerprints capture node inventory, rack layout, link bandwidth, and failure domains.",
    "Graph IR defines compute ops as nodes and tensor/collective communication as edges.",
]


@app.on_event("startup")
async def startup():
    """Seed the vector store with domain knowledge on startup."""
    chunks = []
    for doc in SEED_DOCS:
        chunks.extend(chunk_text(doc, chunk_size=256, overlap=32))

    embeddings = embed_texts(chunks)
    for chunk, embedding in zip(chunks, embeddings):
        vector_store.add(chunk, embedding)


# ─── Request / Response models ───────────────────────────────────────────────

class ContextRequest(BaseModel):
    prompt: str
    user_id: str
    app_id: str
    max_tokens: Optional[int] = 4096
    top_k: Optional[int] = 5
    semantic_threshold: Optional[float] = None


class ChunkResult(BaseModel):
    text: str
    score: float
    chunk_id: str


class ContextResponse(BaseModel):
    request_id: str
    chunks: List[ChunkResult]
    cache_hit: bool
    cache_type: Optional[str]   # "exact" | "semantic" | None
    cache_key: str
    total_tokens_estimated: int
    latency_ms: float


# ─── Endpoints ─────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "service": "LightOS Context Engine",
        "version": "1.0.0",
        "endpoints": {
            "retrieve": "POST /context/retrieve",
            "health": "GET /context/health",
            "stats": "GET /context/stats"
        }
    }


@app.get("/context/health")
async def health():
    return {
        "status": "healthy",
        "vector_store_size": vector_store.size(),
        "cache_size": cache.size(),
        "timestamp": time.time()
    }


@app.get("/context/stats")
async def stats():
    return {
        "vector_store_chunks": vector_store.size(),
        "cache_entries": cache.size(),
        "cache_hit_rate": cache.hit_rate(),
        "exact_hits": cache.exact_hits,
        "semantic_hits": cache.semantic_hits,
        "misses": cache.misses
    }


@app.post("/context/retrieve", response_model=ContextResponse)
async def retrieve_context(req: ContextRequest):
    t0 = time.time()
    request_id = str(uuid.uuid4())[:8]

    # 1. Compute exact cache key
    cache_key = hashlib.md5(f"{req.prompt}:{req.app_id}".encode()).hexdigest()

    # 2. Check exact cache
    exact_result = cache.get_exact(cache_key)
    if exact_result is not None:
        latency_ms = (time.time() - t0) * 1000
        return ContextResponse(
            request_id=request_id,
            chunks=exact_result,
            cache_hit=True,
            cache_type="exact",
            cache_key=cache_key,
            total_tokens_estimated=sum(len(c["text"].split()) for c in exact_result),
            latency_ms=latency_ms
        )

    # 3. Embed query
    q_emb = embed_query(req.prompt)

    # 4. Check semantic cache
    threshold = req.semantic_threshold or cache.semantic_threshold
    semantic_result = cache.get_semantic(q_emb, threshold)
    if semantic_result is not None:
        latency_ms = (time.time() - t0) * 1000
        return ContextResponse(
            request_id=request_id,
            chunks=semantic_result,
            cache_hit=True,
            cache_type="semantic",
            cache_key=cache_key,
            total_tokens_estimated=sum(len(c["text"].split()) for c in semantic_result),
            latency_ms=latency_ms
        )

    # 5. Vector search
    results = vector_store.search(q_emb, top_k=req.top_k)
    chunks = [
        ChunkResult(text=r["text"], score=r["score"], chunk_id=r["id"])
        for r in results
    ]

    # 6. Store in cache
    serialized = [{"text": c.text, "score": c.score, "chunk_id": c.chunk_id} for c in chunks]
    cache.set_exact(cache_key, serialized)
    cache.set_semantic(q_emb, serialized)

    latency_ms = (time.time() - t0) * 1000
    token_estimate = sum(len(c.text.split()) for c in chunks)

    return ContextResponse(
        request_id=request_id,
        chunks=chunks,
        cache_hit=False,
        cache_type=None,
        cache_key=cache_key,
        total_tokens_estimated=token_estimate,
        latency_ms=latency_ms
    )


if __name__ == "__main__":
    import uvicorn, os
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8010)), log_level="info")
