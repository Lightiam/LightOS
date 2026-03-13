"""
Text chunker — fixed-size sliding window with overlap.
"""
from typing import List


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 64) -> List[str]:
    """
    Split text into overlapping chunks of approximately `chunk_size` words.
    Uses word boundaries to avoid splitting mid-word.
    """
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end == len(words):
            break
        start += chunk_size - overlap

    return chunks


def estimate_tokens(text: str) -> int:
    """Rough estimate: 0.75 words per token (GPT-style)."""
    return int(len(text.split()) / 0.75)
