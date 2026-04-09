"""Placeholder premium Gemini-backed video pipeline."""

from __future__ import annotations

from src.core.models import Source


def process_video_premium(source: Source) -> dict[str, str]:
    """Stub premium processing response for future implementation."""
    return {
        "source_id": source.source_id or "",
        "pipeline": "process_video_premium",
        "status": "not_implemented",
    }
