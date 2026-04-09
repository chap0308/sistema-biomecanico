"""Normalize webpage sources for future content extraction."""

from __future__ import annotations

from src.core.models import Source


def build_webpage_source(uri: str, *, title: str | None = None, author: str | None = None, language_hint: str = "es") -> Source:
    """Create a normalized webpage source."""
    return Source(
        source_type="webpage",
        uri=uri.strip(),
        canonical_uri=uri.strip(),
        title=title,
        channel_or_author=author,
        language_hint=language_hint,
        ingest_status="discovered",
    )
