"""Placeholder webpage ingestion pipeline."""

from __future__ import annotations

from src.core.models import Source


def process_webpage(source: Source) -> dict[str, str]:
    """Stub webpage processing response for future implementation."""
    return {
        "source_id": source.source_id or "",
        "pipeline": "process_webpage",
        "status": "not_implemented",
    }
