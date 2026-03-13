"""
Vector Store — FAISS-backed with numpy brute-force fallback.
Stores (chunk_text, embedding) pairs and supports top-k cosine similarity search.
"""
from typing import List, Dict, Any
import uuid
import math

try:
    import faiss
    import numpy as np
    _USE_FAISS = True
except Exception:
    _USE_FAISS = False

EMBEDDING_DIM = 384


class VectorStore:
    def __init__(self):
        self._chunks: List[Dict[str, Any]] = []  # {"id": str, "text": str, "embedding": List[float]}
        if _USE_FAISS:
            import numpy as np
            self._index = faiss.IndexFlatL2(EMBEDDING_DIM)
        else:
            self._index = None

    def add(self, text: str, embedding: List[float]) -> str:
        chunk_id = str(uuid.uuid4())[:8]
        self._chunks.append({"id": chunk_id, "text": text, "embedding": embedding})
        if _USE_FAISS and self._index is not None:
            import numpy as np
            vec = np.array([embedding], dtype="float32")
            self._index.add(vec)
        return chunk_id

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        if not self._chunks:
            return []

        k = min(top_k, len(self._chunks))

        if _USE_FAISS and self._index is not None and self._index.ntotal > 0:
            import numpy as np
            q = np.array([query_embedding], dtype="float32")
            distances, indices = self._index.search(q, k)
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx < 0:
                    continue
                chunk = self._chunks[idx]
                # Convert L2 distance to a similarity score in [0,1]
                score = float(1.0 / (1.0 + dist))
                results.append({"id": chunk["id"], "text": chunk["text"], "score": score})
            return results

        # Numpy brute-force cosine similarity
        return self._brute_force_search(query_embedding, k)

    def _brute_force_search(self, query: List[float], top_k: int) -> List[Dict[str, Any]]:
        def cosine_sim(a, b):
            dot = sum(x * y for x, y in zip(a, b))
            norm_a = math.sqrt(sum(x * x for x in a))
            norm_b = math.sqrt(sum(x * x for x in b))
            if norm_a == 0 or norm_b == 0:
                return 0.0
            return dot / (norm_a * norm_b)

        scored = []
        for chunk in self._chunks:
            score = cosine_sim(query, chunk["embedding"])
            scored.append({"id": chunk["id"], "text": chunk["text"], "score": score})

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def size(self) -> int:
        return len(self._chunks)
