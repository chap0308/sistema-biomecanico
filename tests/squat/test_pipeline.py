"""Tests for initial squat pipeline orchestration."""

from __future__ import annotations

import json
from pathlib import Path

from src.squat.models import SquatCaseRecord, VideoTechnicalMetadata
from src.squat.pipeline import register_squat_case
from src.squat.registry import load_case_registry


def test_register_squat_case_persists_registry_and_json(tmp_path: Path, monkeypatch) -> None:
    resolved_video = tmp_path / "raw" / "case.mp4"
    metadata = VideoTechnicalMetadata(
        path=str(resolved_video),
        suffix=".mp4",
        width_px=1280,
        height_px=720,
        fps=30.0,
        frame_count=180,
        duration_seconds=6.0,
        first_frame_readable=True,
    )
    monkeypatch.setattr("src.squat.pipeline.probe_video", lambda _: metadata)
    case = SquatCaseRecord(
        case_id="caso_001",
        video_path="relative/case.mp4",
        protocol_review_status="aceptado",
    )
    registry = tmp_path / "metadata" / "casos.csv"

    result, result_path = register_squat_case(
        case,
        registry_path=registry,
        output_dir=tmp_path / "outputs",
    )

    payload = json.loads(result_path.read_text(encoding="utf-8"))
    registered = load_case_registry(registry)
    assert result.ready_for_pose is True
    assert payload["analysis_id"] == result.analysis_id
    assert payload["case"]["video_path"] == str(resolved_video)
    assert registered[0].video_path == str(resolved_video)
