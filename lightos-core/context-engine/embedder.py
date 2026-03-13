"""
Embedder — wraps sentence-transformers for vector embeddings.
Falls back to a deterministic hash-based mock if torch/transformers not available.
"""
from typing import List
import hashlib
import math

try:
    from sentence_transformers import SentenceTransformer
    _model = SentenceTransformer("all-MiniLM-L6-v2")
    _USE_REAL = True
except Exception:
    _model = None
    _USE_REAL = False

EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 output dim


def _mock_embed(text: str) -> List[float]:
    """Deterministic pseudo-embedding based on text hash. Used when torch unavailable."""
    seed = int(hashlib.sha256(text.encode()).hexdigest(), 16) % (10**9)
    result = []
    for i in range(EMBEDDING_DIM):
        val = math.sin(seed * (i + 1) * 0.0001)
        result.append(val)
    norm = math.sqrt(sum(v * v for v in result))
    return [v / norm for v in result]


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed a list of text chunks."""
    if _USE_REAL and _model is not None:
        embeddings = _model.encode(texts, convert_to_numpy=True)
        return [emb.tolist() for emb in embeddings]
    return [_mock_embed(t) for t in texts]


def embed_query(text: str) -> List[float]:
    """Embed a single query string."""
    if _USE_REAL and _model is not None:
        emb = _model.encode([text], convert_to_numpy=True)
        return emb[0].tolist()
    return _mock_embed(text)
