"""Tests for the post-pose analytical quality gate."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.squat.models import (
    SquatPoseArtifacts,
    SquatPoseSummary,
    SquatRepetition,
    SquatSegmentationArtifacts,
    SquatSegmentationSummary,
)
from src.squat.quality_gate import (
    SquatQualityPolicy,
    _as_bool,
    evaluate_squat_analysis_quality,
)


def _write_quality_inputs(
    tmp_path: Path,
    *,
    case_id: str = "caso_001",
    processed_percentage: float = 100.0,
    valid_percentage: float = 100.0,
    repetition_percentages: tuple[float, ...] = (100.0, 100.0, 100.0),
    invalid_peaks: tuple[int, ...] = (),
) -> tuple[Path, Path, Path]:
    pose_path = tmp_path / "pose_summary.json"
    segmentation_path = tmp_path / "segmentation_summary.json"
    quality_path = tmp_path / "frame_quality.csv"
    pose = SquatPoseSummary(
        case_id=case_id,
        video_path="case.mp4",
        min_visibility_threshold=0.5,
        total_frames=300,
        processed_frames=round(300 * processed_percentage / 100.0),
        frames_with_pose=300,
        valid_frames=round(300 * valid_percentage / 100.0),
        processed_frames_percentage=processed_percentage,
        valid_frames_percentage=valid_percentage,
        mean_detected_keypoints=13.0,
        artifacts=SquatPoseArtifacts(
            landmarks_csv="landmarks.csv",
            frame_quality_csv=str(quality_path),
            overlay_video="overlay.mp4",
            quality_plot="pose_quality.png",
            summary_json=str(pose_path),
        ),
    )
    repetitions = [
        SquatRepetition(
            repetition_index=index,
            start_frame=(index - 1) * 90,
            peak_depth_frame=(index - 1) * 90 + 45,
            end_frame=(index - 1) * 90 + 80,
            start_seconds=(index - 1) * 3.0,
            peak_depth_seconds=(index - 1) * 3.0 + 1.5,
            end_seconds=(index - 1) * 3.0 + 2.7,
            descent_duration_seconds=1.5,
            ascent_duration_seconds=1.2,
            total_duration_seconds=2.7,
            peak_hip_midpoint_y=0.7,
            valid_frames_percentage=percentage,
        )
        for index, percentage in enumerate(repetition_percentages, start=1)
    ]
    segmentation = SquatSegmentationSummary(
        case_id=case_id,
        landmarks_csv="landmarks.csv",
        frame_quality_csv=str(quality_path),
        fps=30.0,
        total_frames=300,
        repetitions_detected=len(repetitions),
        repetitions=repetitions,
        artifacts=SquatSegmentationArtifacts(
            frame_phases_csv="frame_phases.csv",
            repetitions_csv="repetitions.csv",
            segmentation_plot="segmentation.png",
            summary_json=str(segmentation_path),
        ),
    )
    pose_path.write_text(pose.model_dump_json(indent=2), encoding="utf-8")
    segmentation_path.write_text(
        segmentation.model_dump_json(indent=2),
        encoding="utf-8",
    )
    quality = pd.DataFrame(
        {
            "frame_index": range(300),
            "valid_for_analysis": [
                frame not in invalid_peaks for frame in range(300)
            ],
        }
    )
    quality.to_csv(quality_path, index=False)
    return pose_path, segmentation_path, quality_path


def test_quality_gate_accepts_complete_high_quality_video(tmp_path: Path) -> None:
    pose, segmentation, quality = _write_quality_inputs(tmp_path)

    result = evaluate_squat_analysis_quality(
        pose,
        segmentation,
        quality,
        case_id="caso_001",
        output_dir=tmp_path / "outputs",
    )

    assert result.status == "apto_para_analisis"
    assert result.eligible_for_analysis is True
    assert result.exclusion_reasons == []
    assert result.warnings == []
    assert Path(result.artifacts.summary_json).exists()


def test_quality_gate_requests_review_for_noncritical_warnings(
    tmp_path: Path,
) -> None:
    pose, segmentation, quality = _write_quality_inputs(
        tmp_path,
        valid_percentage=92.0,
        repetition_percentages=(85.0, 92.0, 92.0),
    )

    result = evaluate_squat_analysis_quality(
        pose,
        segmentation,
        quality,
        case_id="caso_001",
        output_dir=tmp_path / "outputs",
    )

    assert result.status == "revision_requerida"
    assert result.eligible_for_analysis is True
    assert result.exclusion_reasons == []
    assert len(result.warnings) == 2


def test_quality_gate_excludes_only_the_invalid_repetition(
    tmp_path: Path,
) -> None:
    pose, segmentation, quality = _write_quality_inputs(
        tmp_path,
        valid_percentage=94.9,
        repetition_percentages=(100.0, 100.0, 78.0),
        invalid_peaks=(225,),
    )

    result = evaluate_squat_analysis_quality(
        pose,
        segmentation,
        quality,
        case_id="caso_001",
        output_dir=tmp_path / "outputs",
    )

    assert result.status == "revision_requerida"
    assert result.eligible_for_analysis is True
    assert result.eligible_repetition_indexes == [1, 2]
    assert result.excluded_repetition_indexes == [3]
    assert result.exclusion_reasons == []
    assert any("3" in warning for warning in result.warnings)


def test_quality_gate_rejects_processing_and_repetition_count(
    tmp_path: Path,
) -> None:
    pose, segmentation, quality = _write_quality_inputs(
        tmp_path,
        processed_percentage=95.0,
        valid_percentage=85.0,
        repetition_percentages=(100.0, 100.0),
    )

    result = evaluate_squat_analysis_quality(
        pose,
        segmentation,
        quality,
        case_id="caso_001",
        output_dir=tmp_path / "outputs",
    )

    assert result.status == "no_apto_para_analisis"
    assert len(result.exclusion_reasons) == 2


def test_quality_gate_accepts_one_complete_repetition(tmp_path: Path) -> None:
    pose, segmentation, quality = _write_quality_inputs(
        tmp_path,
        repetition_percentages=(100.0,),
    )

    result = evaluate_squat_analysis_quality(
        pose,
        segmentation,
        quality,
        case_id="caso_001",
        output_dir=tmp_path / "outputs",
    )

    assert result.status == "apto_para_analisis"
    assert result.eligible_for_analysis is True
    assert result.eligible_repetition_indexes == [1]


def test_quality_gate_keeps_one_valid_repetition_among_multiple(
    tmp_path: Path,
) -> None:
    pose, segmentation, quality = _write_quality_inputs(
        tmp_path,
        repetition_percentages=(70.0, 100.0, 75.0),
    )

    result = evaluate_squat_analysis_quality(
        pose,
        segmentation,
        quality,
        case_id="caso_001",
        output_dir=tmp_path / "outputs",
    )

    assert result.status == "revision_requerida"
    assert result.eligible_for_analysis is True
    assert result.eligible_repetition_indexes == [2]
    assert result.excluded_repetition_indexes == [1, 3]


def test_quality_gate_rejects_one_invalid_repetition(tmp_path: Path) -> None:
    pose, segmentation, quality = _write_quality_inputs(
        tmp_path,
        repetition_percentages=(70.0,),
    )

    result = evaluate_squat_analysis_quality(
        pose,
        segmentation,
        quality,
        case_id="caso_001",
        output_dir=tmp_path / "outputs",
    )

    assert result.status == "no_apto_para_analisis"
    assert result.eligible_for_analysis is False
    assert result.eligible_repetition_indexes == []
    assert result.excluded_repetition_indexes == [1]


def test_quality_gate_rejects_video_without_complete_repetitions(
    tmp_path: Path,
) -> None:
    pose, segmentation, quality = _write_quality_inputs(
        tmp_path,
        repetition_percentages=(),
    )

    result = evaluate_squat_analysis_quality(
        pose,
        segmentation,
        quality,
        case_id="caso_001",
        output_dir=tmp_path / "outputs",
    )

    assert result.status == "no_apto_para_analisis"
    assert result.eligible_for_analysis is False
    assert result.eligible_repetition_indexes == []


def test_quality_gate_rejects_multiple_invalid_repetitions(
    tmp_path: Path,
) -> None:
    pose, segmentation, quality = _write_quality_inputs(
        tmp_path,
        repetition_percentages=(70.0, 75.0, 79.0),
    )

    result = evaluate_squat_analysis_quality(
        pose,
        segmentation,
        quality,
        case_id="caso_001",
        output_dir=tmp_path / "outputs",
    )

    assert result.status == "no_apto_para_analisis"
    assert result.eligible_for_analysis is False
    assert result.eligible_repetition_indexes == []
    assert result.excluded_repetition_indexes == [1, 2, 3]


def test_quality_gate_can_disable_peak_requirement(tmp_path: Path) -> None:
    pose, segmentation, quality = _write_quality_inputs(
        tmp_path,
        invalid_peaks=(45,),
    )

    result = evaluate_squat_analysis_quality(
        pose,
        segmentation,
        quality,
        case_id="caso_001",
        output_dir=tmp_path / "outputs",
        policy=SquatQualityPolicy(require_valid_peak_depth_frame=False),
    )

    assert result.status == "apto_para_analisis"


def test_quality_gate_requires_matching_case_ids(tmp_path: Path) -> None:
    pose, segmentation, quality = _write_quality_inputs(tmp_path)

    with pytest.raises(ValueError, match="case_id must match"):
        evaluate_squat_analysis_quality(
            pose,
            segmentation,
            quality,
            case_id="otro_caso",
            output_dir=tmp_path / "outputs",
        )


def test_quality_gate_requires_frame_quality_columns(tmp_path: Path) -> None:
    pose, segmentation, quality = _write_quality_inputs(tmp_path)
    pd.DataFrame({"frame_index": [0]}).to_csv(quality, index=False)

    with pytest.raises(ValueError, match="missing required columns"):
        evaluate_squat_analysis_quality(
            pose,
            segmentation,
            quality,
            case_id="caso_001",
            output_dir=tmp_path / "outputs",
        )


def test_quality_gate_bool_parser_supports_native_and_text_values() -> None:
    assert _as_bool(True) is True
    assert _as_bool("yes") is True
    assert _as_bool("no") is False
