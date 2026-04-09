"""Tests for RAG MVP core models."""

from src.core.models import Asset, Segment, Source


def test_source_generates_stable_defaults() -> None:
    source = Source(source_type="youtube", uri="https://www.youtube.com/shorts/abc12345")

    assert source.source_id
    assert source.canonical_uri == source.uri


def test_asset_generates_asset_id() -> None:
    asset = Asset(source_id="src_1", kind="audio", path="data/audio.wav", mime_type="audio/wav")

    assert asset.asset_id


def test_segment_computes_duration_and_id() -> None:
    segment = Segment(source_id="src_1", segment_index=1, start_sec=1.0, end_sec=4.5)

    assert segment.segment_id
    assert segment.duration_sec == 3.5
