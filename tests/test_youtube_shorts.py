"""Tests for YouTube Shorts discovery helpers."""

from pathlib import Path

from video.youtube_shorts import ShortsVideo, diff_new_videos, extract_video_id, load_seen_state, normalize_channel_shorts_url, update_seen_state


def test_normalize_channel_shorts_url_adds_suffix() -> None:
    assert normalize_channel_shorts_url("https://www.youtube.com/@conorharris") == "https://www.youtube.com/@conorharris/shorts"


def test_extract_video_id_supports_shorts_and_watch_urls() -> None:
    assert extract_video_id("https://www.youtube.com/shorts/uKWBut2eFYI") == "uKWBut2eFYI"
    assert extract_video_id("https://www.youtube.com/watch?v=uKWBut2eFYI") == "uKWBut2eFYI"


def test_load_seen_state_returns_defaults_when_missing() -> None:
    state = load_seen_state(Path("D:/sistema-biomecanico/.tmp/nonexistent_seen_state.json"))

    assert state["seen_video_ids"] == []
    assert state["seen_urls"] == []


def test_diff_new_videos_filters_seen_ids() -> None:
    videos = [
        ShortsVideo("a1", "https://www.youtube.com/shorts/a1", "A", "1 view", 0),
        ShortsVideo("b2", "https://www.youtube.com/shorts/b2", "B", "2 views", 1),
    ]

    new_videos = diff_new_videos(videos, {"a1"})

    assert [item.video_id for item in new_videos] == ["b2"]


def test_update_seen_state_merges_without_duplicates() -> None:
    state = {
        "channel_url": "https://www.youtube.com/@conorharris/shorts",
        "last_checked_at": "",
        "seen_video_ids": ["a1"],
        "seen_urls": ["https://www.youtube.com/shorts/a1"],
        "history": [],
    }
    videos = [
        ShortsVideo("a1", "https://www.youtube.com/shorts/a1", "A", "1 view", 0),
        ShortsVideo("b2", "https://www.youtube.com/shorts/b2", "B", "2 views", 1),
    ]

    updated = update_seen_state(
        state=state,
        channel_url="https://www.youtube.com/@conorharris/shorts",
        order="newest",
        limit=90,
        videos=videos,
    )

    assert updated["seen_video_ids"] == ["a1", "b2"]
    assert updated["seen_urls"] == ["https://www.youtube.com/shorts/a1", "https://www.youtube.com/shorts/b2"]
    assert updated["history"]
