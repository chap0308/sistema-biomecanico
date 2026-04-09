"""Payload and retrieval text construction for segments."""

from __future__ import annotations

from src.core.models import Segment


def make_retrieval_text(segment: Segment) -> str:
    """Build the canonical text that should be embedded for one segment."""
    parts = [
        segment.transcript.strip(),
        segment.ocr_text.strip(),
        segment.visual_description.strip(),
        segment.segment_summary.strip(),
        " ".join(part.strip() for part in segment.topics if part.strip()),
        " ".join(part.strip() for part in segment.keywords if part.strip()),
    ]
    return " | ".join(part for part in parts if part)


def make_qdrant_payload(segment: Segment) -> dict[str, object]:
    """Build a Qdrant-friendly payload for a segment."""
    payload = dict(segment.payload)
    payload.update(
        {
            "source_id": segment.source_id,
            "segment_id": segment.segment_id,
            "start_sec": segment.start_sec,
            "end_sec": segment.end_sec,
            "language": segment.language,
            "topics": segment.topics,
            "keywords": segment.keywords,
        }
    )
    return payload
