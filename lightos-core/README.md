# LightOS Core — API Reference

LightOS Core is the orchestration backend for the LightOS Aurora dashboard.
It provides four microservices that power context retrieval, dynamic model routing,
LightMicro/Base/Max inference, and telemetry collection.

---

## Quick Start (Local Dev)

```bash
cd lightos-core

# Build and start all services
docker-compose up --build

# Seed demo telemetry (first run)
docker-compose --profile seed run seed

# Open Aurora dashboard
open ../docs-site/dcim.html
```

All services start with automatic health checks. The Aurora UI polls them at startup.

---

## Services & Ports

| Service | Port | Description |
|---|---|---|
| Context Engine | **8010** | Chunking, embedding, semantic cache, vector retrieval |
| Router API | **8011** | LightMicro/Base/Max routing with policy DSL |
| Inference Proxy | **8012** | Model dispatch (mock → vLLM/SGLang swap-in) |
| Telemetry API | **8013** | Event store, aggregation, Model-Job Templates |
| DCIM API | **8001** | Existing GPU/cluster telemetry (ISA-95) |

---

## API Reference

### Context Engine — Port 8010

#### `POST /context/retrieve`
Chunk, embed, and retrieve relevant context for a prompt.

**Request:**
```json
{
  "prompt": "what is photonic computing",
  "user_id": "u1",
  "app_id": "aurora-ui",
  "max_tokens": 4096,
  "top_k": 5
}
```

**Response:**
```json
{
  "request_id": "a3f1b2c4",
  "chunks": [{"text": "...", "score": 0.94, "chunk_id": "e1f2a3"}],
  "cache_hit": false,
  "cache_type": null,
  "cache_key": "md5hash",
  "total_tokens_estimated": 340,
  "latency_ms": 12.5
}
```

---

### Router API — Port 8011

#### `POST /router/route`
Select optimal model tier based on SLO, context, and user tier.

**Request:**
```json
{
  "prompt_length": 512,
  "context_tokens": 800,
  "user_tier": "standard",
  "latency_slo_ms": 400,
  "app_id": "aurora-ui"
}
```

**Response:**
```json
{
  "model_tier": "lightbase",
  "model_display_name": "LightBase",
  "context_budget": 4096,
  "cache_strategy": "exact",
  "matched_rule": "fast_slo_medium_context",
  "estimated_latency_ms": 175,
  "estimated_cost_per_1k": 0.001,
  "topology_domain": "dc-1-rack-a"
}
```

#### `GET /router/policy`
Returns current routing rules and model tier definitions.

#### `POST /config/update`
Hot-reload routing rules from YAML string.

**Request:**
```json
{"rules_yaml": "- name: my_rule\n  condition: {latency_slo_ms_lt: 100}\n  result: {model_tier: lightmicro, ...}"}
```

---

### Inference Proxy — Port 8012

#### `POST /inference/run`
Run inference on the selected model tier.

**Request:**
```json
{
  "model_tier": "lightbase",
  "prompt": "Explain photonic tensor cores",
  "context_chunks": [{"text": "...", "score": 0.92, "chunk_id": "ab12"}],
  "cache_key": "md5hash",
  "user_id": "u1",
  "max_tokens": 512,
  "temperature": 0.7
}
```

**Response:**
```json
{
  "job_id": "a1b2c3d4e5f6",
  "model_tier": "lightbase",
  "model_display_name": "LightBase",
  "answer": "Photonic tensor cores...",
  "tokens_used": 730,
  "prompt_tokens": 480,
  "completion_tokens": 250,
  "latency_ms": 168.3,
  "cost_usd": 0.00073,
  "context_chunks_used": 1
}
```

---

### Telemetry API — Port 8013

#### `POST /telemetry/event`
Record a telemetry event.

**Key fields:** `job_id`, `model_tier`, `tokens_used`, `latency_ms`, `cache_hit`, `cache_type`, `topology_domain`, `cost_usd`

#### `GET /telemetry/jobs?limit=50`
Returns recent jobs for the Workload List panel.

#### `GET /telemetry/summary`
Returns aggregated totals + breakdowns by tier and topology domain.

#### `GET /telemetry/templates`
Returns Model-Job Template clusters for Antigravity optimization.

#### `GET /telemetry/timeseries?hours=24`
Returns hourly aggregated metrics for time-series charts.

---

## Configuration

Edit `router/config.yaml` to adjust:
- **Model tier definitions** (LightMicro/Base/Max params)
- **Routing rules DSL** (SLO conditions, priority tiers)
- **Topology domains** (fabric zones, bandwidth labels)
- **Context budgets** (hard caps, per-tier limits)

Changes take effect on next request (hot-reload via `POST /config/update`).

---

## Model Tiers

| Tier | Params | Avg Latency | Use Case |
|---|---|---|---|
| **LightMicro** | 1–3B | ~45ms | Routing, classification, simple Q&A |
| **LightBase** | 13–30B | ~175ms | Standard inference workloads |
| **LightMax** | 70B+ | ~580ms | Complex reasoning, long context (photonic-backed) |

---

## Swapping in Real Models

Replace the mock adapters in `inference-proxy/model_adapters.py` with:
- **vLLM**: `from vllm import LLM; llm = LLM(model="...")`
- **SGLang**: Point the adapter at an SGLang server endpoint
- **OpenAI-compatible API**: Replace `generate()` with an HTTP call

The adapter interface is fixed: `generate(prompt, max_tokens, temperature) → dict`

---

## Netlify Deployment

1. Deploy each service to your cloud (Render, Railway, Fly.io)
2. Update `netlify.toml` proxy redirects with production URLs
3. Redeploy the Netlify site — Aurora UI connects automatically
