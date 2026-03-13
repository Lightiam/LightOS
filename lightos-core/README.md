# LightOS Core — Control Plane & API Reference

LightOS Core is the orchestration backend for the LightOS Aurora dashboard and the **Control Plane** for data center integrations. It provides four microservices that power context retrieval, dynamic model routing, LightMicro/Base/Max inference, and telemetry collection.

## Data Center Integration Architecture

The LightOS Core exposes a REST control plane API that directly integrates with Kubernetes, SLURM, or custom orchestrators.

- **Orchestrator Integration:** Data centers interact with this API to register LightOS as a device plugin. This makes diverse underlying hardware (CUDA, ROCm, Photonic) appear as unified schedulable resources in the cluster.
- **Hyperscaler & Co-lo Support:** Scales seamlessly across hyperscalers (integrating via HAL for custom silicon) and on-prem enterprise clusters.
- **Photonic NPU Native:** Serves as the first unified control layer for next-generation photonic NPU clusters, providing the essential OS abstraction that hardware currently lacks.

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

## Swapping in Real Models (v0.2 Readiness)

The Inference Proxy automatically relies on rapid mock responses for testing if no real model is configured. 
To route inference to actual LLMs (via any OpenAI-compatible API such as vLLM, Groq, local Ollama, or OpenAI natively), set the corresponding environment variables for the model tier you want to power.

| Tier | Environment Variables | Example |
|---|---|---|
| **LightMicro** | `LIGHTMICRO_MODEL`<br>`LIGHTMICRO_BASE_URL`<br>`LIGHTMICRO_API_KEY` | `llama3-8b-8192`<br>`https://api.groq.com/openai/v1`<br>`gsk_...` |
| **LightBase** | `LIGHTBASE_MODEL`<br>`LIGHTBASE_BASE_URL`<br>`LIGHTBASE_API_KEY` | `mixtral-8x7b-32768`<br>`https://api.groq.com/openai/v1`<br>`gsk_...` |
| **LightMax** | `LIGHTMAX_MODEL`<br>`LIGHTMAX_BASE_URL`<br>`LIGHTMAX_API_KEY` | `gpt-4o`<br>`https://api.openai.com/v1`<br>`sk-...` |

When a `_MODEL` variable is detected for a tier, the Proxy provisions a real asyncio-powered OpenAI client and streams requests directly to that backend.

**Native Deployment:** Set these in your shell before running `.\run_all.ps1`. 
**Docker Deployment:** Add them to an `.env` file alongside `docker-compose.yml`.

---

## Netlify Deployment

1. Deploy each service to your cloud (Render, Railway, Fly.io)
2. Update `netlify.toml` proxy redirects with production URLs
3. Redeploy the Netlify site — Aurora UI connects automatically
