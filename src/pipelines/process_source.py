"""Generic source processing entrypoint."""

from __future__ import annotations

from src.analysis.router import choose_pipeline
from src.core.models import Source
from src.core.settings import RagSettings


def process_source(source: Source, settings: RagSettings) -> dict[str, str]:
    """Return the selected processing route for one source."""
    return {
        "source_id": source.source_id or "",
        "pipeline": choose_pipeline(source, settings),
        "status": "selected",
    }
