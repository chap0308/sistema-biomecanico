"""Tests for lightweight second-layer knowledge analysis."""

from src.analysis.knowledge_draft import build_knowledge_draft
from src.chunking.segment_builder import build_segment
from src.core.models import Source


def test_build_knowledge_draft_extracts_protocol_like_structure() -> None:
    source = Source(
        source_type="youtube",
        uri="https://www.youtube.com/watch?v=abc123",
        title="Foot Drill",
        channel_or_author="Conor Harris",
        language_hint="en",
        tags=["foot", "ankle"],
        duration_sec=30.0,
    )
    segments = [
        build_segment(
            source_id=source.source_id or "",
            segment_index=1,
            start_sec=0.0,
            end_sec=8.0,
            transcript="Most people with plantar fasciitis roll randomly and keep having problems with their feet.",
            ocr_text="PLANTAR FASCIITIS",
            topics=["foot"],
            keywords=["fasciitis", "foot"],
            payload={"source_type": "youtube"},
        ),
        build_segment(
            source_id=source.source_id or "",
            segment_index=2,
            start_sec=8.0,
            end_sec=18.0,
            transcript="Start with the lacrosse ball under the big toe, keep the foot relaxed, and slowly roll toward the heel.",
            topics=["drill"],
            keywords=["lacrosse", "roll"],
            payload={"source_type": "youtube"},
        ),
        build_segment(
            source_id=source.source_id or "",
            segment_index=3,
            start_sec=18.0,
            end_sec=26.0,
            transcript="Don't roll mindlessly. After all three rolls, you should feel better contact with the ground.",
            topics=["retest"],
            keywords=["contact", "ground"],
            payload={"source_type": "youtube"},
        ),
    ]

    draft = build_knowledge_draft(source=source, segments=segments, analysis_report={"transcript_status": "ok"})

    assert draft["classification"]["usefulness"] == "useful"
    assert draft["classification"]["suitable_for_protocol_database"] is True
    assert "foot" in [item.lower() for item in draft["classification"]["body_regions"]]
    assert draft["exercises_mentioned"]
    assert draft["problem_statements"]
    assert draft["knowledge_units"]
    assert draft["knowledge_units"][1]["unit_type"] == "corrective_exercise"
