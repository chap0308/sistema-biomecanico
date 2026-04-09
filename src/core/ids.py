"""Stable id helpers for the RAG MVP."""

from __future__ import annotations

import hashlib


def stable_id(prefix: str, value: str, *, length: int = 16) -> str:
    """Build a deterministic short id from arbitrary input text."""
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]
    return f"{prefix}_{digest}"
