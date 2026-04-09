"""Normalize local video file sources."""

from __future__ import annotations

from pathlib import Path

from src.core.models import Source


def build_local_video_source(path: str | Path, *, language_hint: str = "es", tags: list[str] | None = None) -> Source:
    """Create a source from a local video path."""
    resolved = Path(path).resolve()
    return Source(
        source_type="local_video",
        uri=str(resolved),
        canonical_uri=str(resolved),
        title=resolved.stem,
        language_hint=language_hint,
        tags=tags or [],
        ingest_status="discovered",
        metadata={"path": str(resolved)},
    )
