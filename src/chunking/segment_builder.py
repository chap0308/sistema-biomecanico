"""Construct retrieval-ready segments from multimodal inputs."""

from __future__ import annotations

from typing import Any

from src.core.models import Segment
from src.indexing.payloads import make_retrieval_text


def build_segment(
    *,
    source_id: str,
    segment_index: int,
    start_sec: float,
    end_sec: float,
    transcript: str = "",
    ocr_text: str = "",
    visual_description: str = "",
    segment_summary: str = "",
    topics: list[str] | None = None,
    keywords: list[str] | None = None,
    payload: dict[str, Any] | None = None,
) -> Segment:
    """Build one normalized segment and compute its retrieval text."""
    segment = Segment(
        source_id=source_id,
        segment_index=segment_index,
        start_sec=start_sec,
        end_sec=end_sec,
        transcript=transcript,
        ocr_text=ocr_text,
        visual_description=visual_description,
        segment_summary=segment_summary,
        topics=topics or [],
        keywords=keywords or [],
        payload=payload or {},
    )
    segment.retrieval_text = make_retrieval_text(segment)
    return segment


def build_segments(rows: list[dict[str, Any]]) -> list[Segment]:
    """Build multiple segments from normalized row dictionaries."""
    return [build_segment(**row) for row in rows]
