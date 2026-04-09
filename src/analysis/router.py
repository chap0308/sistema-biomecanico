"""Choose the appropriate source processing pipeline."""

from __future__ import annotations

from src.core.models import Source
from src.core.settings import RagSettings


def choose_pipeline(source: Source, settings: RagSettings) -> str:
    """Route a source to the correct processing pipeline."""
    if source.source_type == "webpage":
        return "process_webpage"
    if source.source_type in {"youtube", "local_video", "public_video_url"}:
        if settings.use_gemini_first:
            return "process_video_premium"
        return "process_video_local"
    return "process_source"
