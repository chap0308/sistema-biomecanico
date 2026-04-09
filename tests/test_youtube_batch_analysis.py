"""Tests for per-video fallback behavior in YouTube batch analysis."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from src.pipelines import youtube_batch_analysis


def test_run_gemini_pipeline_falls_back_to_local_for_one_video(monkeypatch) -> None:
    video = SimpleNamespace(
        video_id="abc123",
        url="https://www.youtube.com/shorts/abc123",
        title="Test video",
        order_index=0,
    )
    output_dir = Path("D:/sistema-biomecanico/data/knowledge/rag_runs/test_gemini_fallback")
    output_dir.mkdir(parents=True, exist_ok=True)

    def _raise(*args, **kwargs):
        raise RuntimeError("quota exceeded")

    def _fake_local(video_obj, output_dir: Path) -> dict[str, object]:
        return {
            "video_id": video_obj.video_id,
            "url": video_obj.url,
            "title": video_obj.title,
            "rank": video_obj.order_index + 1,
            "level1_file": str(output_dir / "001_abc123_level1.json"),
            "draft_file": str(output_dir / "001_abc123_knowledge_draft.json"),
            "sync_file": str(output_dir / "001_abc123_sync.json"),
            "analysis_backend_used": "local",
        }

    monkeypatch.setattr(youtube_batch_analysis, "analyze_youtube_video", _raise)
    monkeypatch.setattr(youtube_batch_analysis, "_run_local_pipeline_for_video", _fake_local)
    monkeypatch.setattr(youtube_batch_analysis, "_refresh_scrape_flags", lambda videos: None)

    results = youtube_batch_analysis.run_gemini_pipeline([video], output_dir, model="gemini-2.5-flash")

    assert len(results) == 1
    assert results[0]["video_id"] == "abc123"
    assert results[0]["analysis_backend_requested"] == "gemini"
    assert results[0]["analysis_backend_used"] == "local_fallback"
    assert "quota exceeded" in str(results[0]["fallback_reason"])
