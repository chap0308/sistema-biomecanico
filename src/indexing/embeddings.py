"""Embedding helpers for the RAG MVP."""

from __future__ import annotations

import hashlib
from typing import Iterable


def embed_text(text: str, *, dimensions: int = 32) -> list[float]:
    """Return a deterministic lightweight embedding placeholder for one text."""
    normalized = text.strip().encode("utf-8")
    if not normalized:
        return [0.0] * dimensions

    values: list[float] = []
    seed = normalized
    while len(values) < dimensions:
        digest = hashlib.sha256(seed).digest()
        for byte in digest:
            values.append((byte / 255.0) * 2.0 - 1.0)
            if len(values) >= dimensions:
                break
        seed = digest + normalized
    return values


def embed_many(texts: Iterable[str], *, dimensions: int = 32) -> list[list[float]]:
    """Embed multiple texts using the deterministic placeholder encoder."""
    return [embed_text(text, dimensions=dimensions) for text in texts]
