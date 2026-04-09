"""Helpers to track which YouTube videos were already analyzed."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_registry(path: Path) -> dict[str, Any]:
    """Load the global analysis registry or return an empty structure."""
    if not path.exists():
        return {"videos": {}, "runs": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save_registry(path: Path, registry: dict[str, Any]) -> None:
    """Persist the analysis registry to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8")


def get_analyzed_video_ids(registry: dict[str, Any]) -> set[str]:
    """Return the set of already analyzed video ids."""
    return set(registry.get("videos", {}).keys())


def is_video_analyzed(registry: dict[str, Any], video_id: str) -> bool:
    """Check whether a video id already exists in the registry."""
    return video_id in registry.get("videos", {})


def register_analysis(
    *,
    registry: dict[str, Any],
    video_id: str,
    video_url: str,
    title: str,
    channel_url: str,
    order: str,
    rank: int,
    model: str,
    analysis_file: str,
    usefulness: str,
    content_kind: str,
) -> dict[str, Any]:
    """Store or update a single analyzed video entry."""
    analyzed_at = datetime.now(timezone.utc).isoformat()
    videos = dict(registry.get("videos", {}))
    existing = dict(videos.get(video_id, {}))
    videos[video_id] = {
        **existing,
        "video_id": video_id,
        "url": video_url,
        "title": title,
        "channel_url": channel_url,
        "order": order,
        "rank": rank,
        "model": model,
        "analysis_file": analysis_file,
        "usefulness": usefulness,
        "content_kind": content_kind,
        "analyzed_at": analyzed_at,
    }
    updated = dict(registry)
    updated["videos"] = videos
    return updated


def append_run(
    *,
    registry: dict[str, Any],
    channel_url: str,
    order: str,
    start_rank: int,
    end_rank: int,
    analyzed_video_ids: list[str],
    skipped_video_ids: list[str],
    model: str,
) -> dict[str, Any]:
    """Append a run summary while keeping the registry compact."""
    run = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "channel_url": channel_url,
        "order": order,
        "start_rank": start_rank,
        "end_rank": end_rank,
        "analyzed_video_ids": analyzed_video_ids,
        "skipped_video_ids": skipped_video_ids,
        "model": model,
    }
    updated = dict(registry)
    updated["runs"] = [run, *registry.get("runs", [])][:50]
    return updated
