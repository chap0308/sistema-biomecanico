"""Tests for initial ingestion and segment construction helpers."""

from src.analysis.router import choose_pipeline
from src.chunking.segment_builder import build_segment
from src.core.settings import RagSettings
from src.ingestion.local_video import build_local_video_source
from src.ingestion.webpage import build_webpage_source
from src.ingestion.youtube import build_youtube_source
from src.indexing.payloads import make_qdrant_payload


def test_build_youtube_source_normalizes_watch_url() -> None:
    source = build_youtube_source(uri="https://www.youtube.com/shorts/uKWBut2eFYI", title="Example")

    assert source.source_type == "youtube"
    assert source.canonical_uri == "https://www.youtube.com/watch?v=uKWBut2eFYI"


def test_build_local_video_source_uses_resolved_path() -> None:
    source = build_local_video_source("data/videos/example.mp4")

    assert source.source_type == "local_video"
    assert source.metadata["path"].endswith("example.mp4")


def test_choose_pipeline_prefers_webpage() -> None:
    source = build_webpage_source("https://example.com/article")
    settings = RagSettings(use_gemini_first=True)

    assert choose_pipeline(source, settings) == "process_webpage"


def test_choose_pipeline_uses_premium_when_enabled() -> None:
    source = build_youtube_source(uri="https://www.youtube.com/shorts/uKWBut2eFYI")
    settings = RagSettings(use_gemini_first=True)

    assert choose_pipeline(source, settings) == "process_video_premium"


def test_build_segment_creates_retrieval_text_and_payload() -> None:
    segment = build_segment(
        source_id="src_1",
        segment_index=1,
        start_sec=0.0,
        end_sec=8.0,
        transcript="Scapula moves upward.",
        ocr_text="UPWARD ROTATION",
        visual_description="Posterior shoulder view.",
        segment_summary="Explains the start of scapular upward rotation.",
        topics=["scapula"],
        keywords=["rotation"],
        payload={"source_type": "youtube"},
    )

    assert "Scapula moves upward." in segment.retrieval_text
    qdrant_payload = make_qdrant_payload(segment)
    assert qdrant_payload["segment_id"] == segment.segment_id
    assert qdrant_payload["source_type"] == "youtube"
