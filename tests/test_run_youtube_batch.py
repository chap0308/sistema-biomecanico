"""Tests for the short YouTube batch wrapper."""

from scripts.run_youtube_batch import build_output_dir, parse_range


def test_parse_range_accepts_valid_bounds() -> None:
    assert parse_range("21-30") == (21, 30)


def test_build_output_dir_uses_channel_and_range() -> None:
    output_dir = build_output_dir(
        channel_url="https://www.youtube.com/@conorharris/shorts",
        order="newest",
        start_rank=21,
        end_rank=30,
        output_base="data/knowledge/video_knowledge_drafts",
        backend="local",
    )

    assert output_dir == "data/knowledge/video_knowledge_drafts/conorharris_newest_21_30_local"
