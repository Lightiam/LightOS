"""
Context Cache — Exact-match (MD5) + Semantic (embedding cosine similarity) cache.
Pure Python in-memory with LRU eviction.
"""
from typing import List, Dict, Any, Optional
import time
import math
from collections import OrderedDict


class ContextCache:
    def __init__(self, exact_ttl: int = 300, semantic_threshold: float = 0.92, max_size: int = 1000):
        self.exact_ttl = exact_ttl
        self.semantic_threshold = semantic_threshold
        self.max_size = max_size

        # Exact cache: key -> (value, timestamp)
        self._exact: OrderedDict = OrderedDict()
        # Semantic cache: list of (embedding, value, timestamp)
        self._semantic: List[Dict[str, Any]] = []

        # Stats
        self.exact_hits = 0
        self.semantic_hits = 0
        self.misses = 0
        self._total_requests = 0

    def get_exact(self, key: str) -> Optional[List[Dict]]:
        self._total_requests += 1
        entry = self._exact.get(key)
        if entry is None:
            self.misses += 1
            return None
        value, ts = entry
        if time.time() - ts > self.exact_ttl:
            del self._exact[key]
            self.misses += 1
            return None
        self.exact_hits += 1
        # Move to end (LRU)
        self._exact.move_to_end(key)
        return value

    def set_exact(self, key: str, value: List[Dict]):
        if len(self._exact) >= self.max_size:
            # Evict oldest
            self._exact.popitem(last=False)
        self._exact[key] = (value, time.time())

    def get_semantic(self, query_embedding: List[float], threshold: float) -> Optional[List[Dict]]:
        now = time.time()
        best_score = 0.0
        best_value = None

        for entry in self._semantic:
            # Check TTL
            if now - entry["ts"] > self.exact_ttl * 2:
                continue
            score = _cosine_sim(query_embedding, entry["embedding"])
            if score > best_score:
                best_score = score
                best_value = entry["value"]

        if best_score >= threshold and best_value is not None:
            self.semantic_hits += 1
            return best_value
        return None

    def set_semantic(self, embedding: List[float], value: List[Dict]):
        if len(self._semantic) >= self.max_size:
            self._semantic.pop(0)
        self._semantic.append({"embedding": embedding, "value": value, "ts": time.time()})

    def size(self) -> int:
        return len(self._exact) + len(self._semantic)

    def hit_rate(self) -> float:
        total = self.exact_hits + self.semantic_hits + self.misses
        if total == 0:
            return 0.0
        return (self.exact_hits + self.semantic_hits) / total


def _cosine_sim(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
