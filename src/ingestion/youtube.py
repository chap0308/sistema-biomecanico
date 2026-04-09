"""Normalize YouTube sources for the RAG MVP."""

from __future__ import annotations

from urllib.parse import parse_qs, urlparse

from src.core.models import Source
from video.youtube_shorts import extract_video_id, normalize_channel_shorts_url


def normalize_youtube_uri(uri: str) -> str:
    """Normalize a YouTube watch or shorts URL into a canonical watch URL when possible."""
    cleaned = uri.strip()
    video_id = extract_video_id(cleaned)
    if video_id:
        return f"https://www.youtube.com/watch?v={video_id}"
    parsed = urlparse(cleaned)
    if "youtube.com" in parsed.netloc and cleaned.rstrip("/").endswith("/shorts"):
        return normalize_channel_shorts_url(cleaned)
    if parsed.path == "/watch":
        query_video_id = parse_qs(parsed.query).get("v", [""])[0]
        if query_video_id:
            return f"https://www.youtube.com/watch?v={query_video_id}"
    return cleaned


def build_youtube_source(
    *,
    uri: str,
    title: str | None = None,
    channel_or_author: str | None = None,
    language_hint: str = "es",
    tags: list[str] | None = None,
    duration_sec: float | None = None,
) -> Source:
    """Create a normalized YouTube source model."""
    canonical_uri = normalize_youtube_uri(uri)
    return Source(
        source_type="youtube",
        uri=uri,
        canonical_uri=canonical_uri,
        title=title,
        channel_or_author=channel_or_author,
        language_hint=language_hint,
        tags=tags or [],
        duration_sec=duration_sec,
        ingest_status="discovered",
    )
