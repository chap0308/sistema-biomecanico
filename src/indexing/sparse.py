"""Sparse token weights for lightweight hybrid retrieval placeholders."""

from __future__ import annotations

import re
from collections import Counter

TOKEN_RE = re.compile(r"[A-Za-zÁÉÍÓÚáéíóúÑñ0-9_/-]+")


def tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase terms for sparse retrieval."""
    return [match.group(0).lower() for match in TOKEN_RE.finditer(text)]


def build_sparse_weights(text: str) -> dict[str, float]:
    """Build normalized term-frequency weights for one text."""
    tokens = tokenize(text)
    if not tokens:
        return {}
    counts = Counter(tokens)
    total = float(sum(counts.values()))
    return {token: count / total for token, count in counts.items()}
