"""Tests for interface-ready squat JSON contracts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.squat.contracts import (
    SquatManualProtocolReview,
    build_case_report,
    export_contract_schemas,
    write_case_record_contract,
)
from src.squat.models import (
    SquatCaseRecord,
    SquatPoseArtifacts,
    SquatPoseSummary,
    SquatRegistrationResult,
    VideoTechnicalMetadata,
)


def _registration(*, status: str = "aceptado") -> SquatRegistrationResult:
    case = SquatCaseRecord(
        case_id="caso_001",
        video_path="video.mp4",
        protocol_review_status=status,
        exclusion_reason="Incumple protocolo" if status == "rechazado" else None,
    )
    video = VideoTechnicalMetadata(
        path="video.mp4",
        suffix=".mp4",
        width_px=1080,
        height_px=1920,
        fps=30.0,
        frame_count=300,
        duration_seconds=10.0,
        first_frame_readable=True,
    )
    return SquatRegistrationResult.from_case(case, video)


def _pose(case_id: str = "caso_001") -> SquatPoseSummary:
    return SquatPoseSummary(
        case_id=case_id,
        video_path="video.mp4",
        min_visibility_threshold=0.5,
        total_frames=300,
        processed_frames=300,
        frames_with_pose=300,
        valid_frames=290,
        processed_frames_percentage=100.0,
        valid_frames_percentage=96.6667,
        mean_detected_keypoints=12.7,
        artifacts=SquatPoseArtifacts(
            landmarks_csv="outputs/caso_001/landmarks.csv",
            frame_quality_csv="outputs/caso_001/frame_quality.csv",
            overlay_video="outputs/caso_001/overlay.mp4",
            quality_plot="outputs/caso_001/pose_quality.png",
            summary_json="outputs/caso_001/pose_summary.json",
        ),
    )


def test_case_record_and_partial_report_are_persisted(tmp_path: Path) -> None:
    record_path = tmp_path / "case_record.json"
    report_path = tmp_path / "case_report.json"
    write_case_record_contract(
        _registration(),
        record_path,
        manual_review=SquatManualProtocolReview(
            lighting="adecuada",
            landmark_availability={"left_hip": "B", "nose": "C"},
        ),
    )

    report = build_case_report(
        record_path,
        output_path=report_path,
        pose=_pose(),
    )

    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert report.status == "analisis_parcial"
    assert payload["pose"]["mean_detected_keypoints"] == 12.7
    assert payload["pose"]["video_path"] == "video.mp4"
    assert payload["pose"]["artifacts"]["landmarks_csv"] == "landmarks.csv"
    assert payload["artifacts"]["overlay_video"] == "overlay.mp4"
    assert payload["case_record_path"] == "case_record.json"


def test_report_rejects_mismatched_stage_case_id(tmp_path: Path) -> None:
    record_path = tmp_path / "case_record.json"
    write_case_record_contract(_registration(), record_path)

    with pytest.raises(ValueError, match="pose"):
        build_case_report(
            record_path,
            output_path=tmp_path / "case_report.json",
            pose=_pose("otro_caso"),
        )


def test_manual_review_rejects_unknown_landmark() -> None:
    with pytest.raises(ValueError, match="unsupported landmark"):
        SquatManualProtocolReview(
            landmark_availability={"left_scapula": "B"}
        )


def test_contract_schemas_are_exported(tmp_path: Path) -> None:
    record_path, report_path = export_contract_schemas(tmp_path)

    record_schema = json.loads(record_path.read_text(encoding="utf-8"))
    report_schema = json.loads(report_path.read_text(encoding="utf-8"))
    assert record_schema["title"] == "SquatCaseRecordContract"
    assert report_schema["title"] == "SquatCaseReport"
