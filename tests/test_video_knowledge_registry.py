"""Tests for the video knowledge analysis registry."""

from pathlib import Path

from video.video_knowledge_registry import (
    append_run,
    get_analyzed_video_ids,
    is_video_analyzed,
    load_registry,
    register_analysis,
)


def test_load_registry_returns_defaults_for_missing_file() -> None:
    registry = load_registry(Path("D:/sistema-biomecanico/.tmp/nonexistent_video_registry.json"))

    assert registry == {"videos": {}, "runs": []}


def test_register_analysis_stores_video_metadata() -> None:
    registry = {"videos": {}, "runs": []}

    updated = register_analysis(
        registry=registry,
        video_id="abc123",
        video_url="https://www.youtube.com/shorts/abc123",
        title="Example",
        channel_url="https://www.youtube.com/@conorharris/shorts",
        order="newest",
        rank=21,
        model="gemini-2.5-flash",
        analysis_file="data/knowledge/video_knowledge_drafts/example.json",
        usefulness="useful",
        content_kind="informational_concept",
    )

    assert is_video_analyzed(updated, "abc123")
    assert get_analyzed_video_ids(updated) == {"abc123"}
    assert updated["videos"]["abc123"]["rank"] == 21
    assert updated["videos"]["abc123"]["content_kind"] == "informational_concept"


def test_append_run_prepends_latest_run() -> None:
    registry = {"videos": {}, "runs": [{"run_at": "older"}]}

    updated = append_run(
        registry=registry,
        channel_url="https://www.youtube.com/@conorharris/shorts",
        order="newest",
        start_rank=11,
        end_rank=20,
        analyzed_video_ids=["a1"],
        skipped_video_ids=["b2"],
        model="gemini-2.5-flash",
    )

    assert len(updated["runs"]) == 2
    assert updated["runs"][0]["analyzed_video_ids"] == ["a1"]
