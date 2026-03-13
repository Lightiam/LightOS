"""
Model Adapters — LightMicro / LightBase / LightMax mock implementations.
Each adapter simulates realistic latency, token usage, and response content.
Schema-compatible for real model backend (vLLM, SGLang) swap-in.
"""
import time
import random
import math
import os
import asyncio
import logging
from typing import Dict, Any, Optional

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


LIGHTOS_ANSWERS = {
    "lightmicro": [
        "LightOS routes this request via the photonic fabric for ultra-low latency. The LightMicro tier handles classification and simple Q&A tasks efficiently.",
        "Confirmed. The LightMicro model processed your request in the photonic-accelerated inference lane.",
        "LightMicro response: Task classified as low-complexity. Result delivered from fast-path inference node.",
        "LightOS Context Engine returned 3 relevant chunks. LightMicro synthesized the answer in under 50ms.",
        "Photonic routing confirmed. LightMicro tier executing on DC1 Rack A fabric node.",
    ],
    "lightbase": [
        "LightBase analysis: Photonic interconnects achieve 3.2 Tbps aggregate bandwidth across the fabric, enabling all-reduce operations 40× faster than electrical NVLink at scale.",
        "The LightOS scheduler uses topology fingerprints to place distributed jobs within high-bandwidth photonic domains, reducing inter-node communication overhead by up to 70%.",
        "Context retrieved from Global Knowledge Store: 5 relevant chunks. LightBase synthesized a comprehensive answer leveraging the semantic cache layer.",
        "LightBase inference complete. Model FLOPS Utilization (MFU) maintained at 89.3% during this request via dynamic batch packing.",
        "LightRail AI's photonic fabric disaggregates compute and memory, allowing LightBase to access a shared 512GB KV cache across all nodes simultaneously.",
    ],
    "lightmax": [
        "LightMax — Deep Analysis: The photonic matrix-vector multiply units in LightRail's fabric perform GEMM operations at near-optical speeds, reducing the energy cost per FLOP by 10–100× versus CMOS-only systems. This enables LightMax to deliver GPT-4-class reasoning at a fraction of the latency at scale, particularly for long-context workloads exceeding 32K tokens where inter-layer communication dominates end-to-end latency.",
        "LightMax Reasoning Engine: Your query touches on graph partitioning for distributed transformer inference. Antigravity's partitioner solves a mixed-integer program to minimize communication volume × latency subject to per-device memory constraints. The resulting PlacementPlan maps attention heads to photonic fabric nodes such that all-reduce patterns align to the ring topology, achieving near-zero residual communication overhead.",
        "LightMax Complex Synthesis: Integrating your cluster topology fingerprint with the model graph IR — the optimal partition assigns the embedding and output projection layers to electrical fabric nodes (lower bandwidth sensitivity) while routing attention QKV projections to photonic fabric nodes (bandwidth-sensitive, benefit from 3.2 Tbps paths). Estimated 2.8× throughput improvement over naive placement.",
        "LightMax — Code Generation: Here is the Router Policy DSL entry for your workload: `if context_tokens >= 8000 and user_tier == 'premium': model_tier=lightmax, context_budget=16384, cache_strategy=semantic`. This rule ensures long-context premium requests are served by the photonic-backed tier with semantic caching enabled.",
    ]
}

TIER_CONFIG = {
    "lightmicro": {
        "display_name": "LightMicro",
        "base_latency_ms": 40,
        "latency_variance": 15,
        "tokens_per_word": 1.3,
        "cost_per_1k": 0.0002,
        "avg_completion_words": 35,
    },
    "lightbase": {
        "display_name": "LightBase",
        "base_latency_ms": 160,
        "latency_variance": 50,
        "tokens_per_word": 1.3,
        "cost_per_1k": 0.001,
        "avg_completion_words": 95,
    },
    "lightmax": {
        "display_name": "LightMax",
        "base_latency_ms": 550,
        "latency_variance": 120,
        "tokens_per_word": 1.3,
        "cost_per_1k": 0.005,
        "avg_completion_words": 210,
    }
}


class ModelAdapter:
    def __init__(self, tier: str):
        self.tier = tier
        self.config = TIER_CONFIG[tier]

    async def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> Dict[str, Any]:
        t0 = time.time()

        # Simulate processing latency
        cfg = self.config
        latency_s = (cfg["base_latency_ms"] + random.uniform(-cfg["latency_variance"], cfg["latency_variance"])) / 1000
        latency_s = max(0.01, latency_s)
        await asyncio.sleep(latency_s)

        # Pick an answer
        answers = LIGHTOS_ANSWERS.get(self.tier, ["LightOS processed your request."])
        answer = random.choice(answers)

        # Calculate tokens
        prompt_tokens = int(len(prompt.split()) * cfg["tokens_per_word"])
        completion_words = random.randint(
            int(cfg["avg_completion_words"] * 0.7),
            int(cfg["avg_completion_words"] * 1.3)
        )
        completion_tokens = int(completion_words * cfg["tokens_per_word"])
        completion_tokens = min(completion_tokens, max_tokens)
        total_tokens = prompt_tokens + completion_tokens

        cost = (total_tokens / 1000) * cfg["cost_per_1k"]
        actual_latency_ms = (time.time() - t0) * 1000

        return {
            "display_name": cfg["display_name"],
            "answer": answer,
            "tokens_used": total_tokens,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "latency_ms": actual_latency_ms,
            "cost_usd": round(cost, 6)
        }


class RealModelAdapter:
    def __init__(self, tier: str, model_name: str, base_url: str, api_key: str):
        self.tier = tier
        self.config = TIER_CONFIG[tier]
        self.model_name = model_name
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> Dict[str, Any]:
        t0 = time.time()
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            answer = response.choices[0].message.content
            
            prompt_tokens = response.usage.prompt_tokens if response.usage else int(len(prompt.split()) * 1.3)
            completion_tokens = response.usage.completion_tokens if response.usage else int(len(answer.split()) * 1.3)
            total_tokens = response.usage.total_tokens if response.usage else prompt_tokens + completion_tokens
            
        except Exception as e:
            logging.error(f"Error calling real model API for tier {self.tier}: {e}")
            answer = f"Error generating response: {e}"
            prompt_tokens = int(len(prompt.split()) * 1.3)
            completion_tokens = int(len(answer.split()) * 1.3)
            total_tokens = prompt_tokens + completion_tokens
            
        cost = (total_tokens / 1000) * self.config["cost_per_1k"]
        actual_latency_ms = (time.time() - t0) * 1000

        return {
            "display_name": f"{self.config['display_name']} (Real)",
            "answer": answer,
            "tokens_used": total_tokens,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "latency_ms": actual_latency_ms,
            "cost_usd": round(cost, 6)
        }


def get_adapter(tier: str):
    if tier not in TIER_CONFIG:
        return None

    tier_upper = tier.upper()
    model_env = os.getenv(f"{tier_upper}_MODEL")
    base_url_env = os.getenv(f"{tier_upper}_BASE_URL")
    api_key_env = os.getenv(f"{tier_upper}_API_KEY", "dummy-key")

    if model_env and OPENAI_AVAILABLE:
        return RealModelAdapter(tier, model_name=model_env, base_url=base_url_env, api_key=api_key_env)
        
    return ModelAdapter(tier)
