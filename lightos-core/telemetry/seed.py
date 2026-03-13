#!/usr/bin/env python3
"""
Seed script — populates the Telemetry DB with 200+ demo events
so dashboards are "alive" on first run.
"""
import random
import time
import uuid
import os
import sys

# Add parent dir so models can be imported
sys.path.insert(0, os.path.dirname(__file__))
from models import TelemetryDB

DATA_DIR = os.getenv("DATA_DIR", "/data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "telemetry.db")

TIERS = ["lightmicro", "lightbase", "lightmax"]
DOMAINS = ["dc-1-rack-a", "dc-1-rack-b", "dc-2-edge"]
RULES = ["ultra_fast_slo", "premium_user_large", "premium_user_standard", "fast_slo_medium_context", "default"]
USERS = [f"user_{i}" for i in range(1, 21)]
APPS = ["aurora-ui", "api-client", "notebook", "production-app"]
CACHE_TYPES = ["exact", "semantic", None]

TIER_CONFIG = {
    "lightmicro": {"base_latency": 45, "variance": 20, "base_tokens": 150, "cost_per_1k": 0.0002},
    "lightbase":  {"base_latency": 175, "variance": 60, "base_tokens": 600, "cost_per_1k": 0.001},
    "lightmax":   {"base_latency": 580, "variance": 130, "base_tokens": 1800, "cost_per_1k": 0.005},
}


def generate_event(hours_ago: float) -> dict:
    tier = random.choices(TIERS, weights=[40, 45, 15])[0]
    cfg = TIER_CONFIG[tier]

    tokens = int(cfg["base_tokens"] * random.uniform(0.6, 1.6))
    latency = cfg["base_latency"] + random.uniform(-cfg["variance"], cfg["variance"])
    latency = max(10, latency)
    cache_hit = random.random() < 0.38  # 38% cache hit rate
    cache_type = random.choice(CACHE_TYPES[:2]) if cache_hit else None
    cost = (tokens / 1000) * cfg["cost_per_1k"]
    domain = random.choices(DOMAINS, weights=[60, 30, 10])[0]

    return {
        "job_id": str(uuid.uuid4())[:12],
        "model_tier": tier,
        "tokens_used": tokens,
        "prompt_tokens": int(tokens * 0.6),
        "completion_tokens": int(tokens * 0.4),
        "latency_ms": latency,
        "cache_hit": cache_hit,
        "cache_type": cache_type,
        "topology_domain": domain,
        "user_id": random.choice(USERS),
        "app_id": random.choice(APPS),
        "matched_rule": random.choice(RULES),
        "cost_usd": round(cost, 6),
        "context_chunks_used": random.randint(0, 5),
    }


def main():
    db = TelemetryDB(DB_PATH)
    existing = db.count()
    if existing > 50:
        print(f"Telemetry DB already has {existing} events. Skipping seed.")
        return

    print(f"Seeding telemetry DB at {DB_PATH} ...")
    n = 250
    now = time.time()

    for i in range(n):
        # Spread events over the last 48 hours
        hours_ago = random.uniform(0, 48)
        event = generate_event(hours_ago)
        db.insert(event)

    total = db.count()
    print(f"Seeded {n} events. Total in DB: {total}")


if __name__ == "__main__":
    main()
