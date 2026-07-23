"""Tests for frontal 2D biomechanical proxy variables."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.squat.biomechanics import (
    _as_bool,
    calculate_biomechanical_frame_metrics,
    calculate_squat_biomechanics,
)


def _biomechanics_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    landmark_rows: list[dict[str, float | int | str]] = []
    phase_rows: list[dict[str, float | int | str | bool]] = []
    phases = ("reposo", "reposo", "descenso", "maxima_profundidad", "cierre")
    for frame_index, phase in enumerate(phases):
        pelvis_shift = 0.0 if frame_index < 2 else 0.02
        shoulder_shift = 0.0 if frame_index < 2 else 0.02
        points = {
            "left_shoulder": (0.70 + shoulder_shift, 0.30),
            "right_shoulder": (0.30 + shoulder_shift, 0.30),
            "left_hip": (0.65 + pelvis_shift, 0.50),
            "right_hip": (0.35 + pelvis_shift, 0.50),
            "left_knee": (0.62 if frame_index == 3 else 0.65, 0.70),
            "right_knee": (0.38 if frame_index == 3 else 0.35, 0.70),
            "left_ankle": (0.65, 0.90),
            "right_ankle": (0.35, 0.90),
        }
        for landmark, (x, y) in points.items():
            landmark_rows.append(
                {
                    "frame_index": frame_index,
                    "landmark": landmark,
                    "x": x,
                    "y": y,
                }
            )
        phase_rows.append(
            {
                "frame_index": frame_index,
                "timestamp_seconds": frame_index / 30.0,
                "valid_for_analysis": True,
                "repetition_index": 0 if frame_index < 2 else 1,
                "phase": phase,
            }
        )
    return pd.DataFrame(landmark_rows), pd.DataFrame(phase_rows)


def test_frame_metrics_follow_declared_sign_and_normalization() -> None:
    landmarks, phases = _biomechanics_tables()

    metrics, shoulder_width = calculate_biomechanical_frame_metrics(
        landmarks,
        phases,
    )

    peak = metrics[metrics["phase"] == "maxima_profundidad"].iloc[0]
    assert shoulder_width == pytest.approx(0.4)
    assert peak["trunk_inclination_deg"] == pytest.approx(0.0)
    assert peak["pelvis_lateral_shift_pct"] == pytest.approx(5.0)
    assert peak["left_knee_medial_deviation_pct"] == pytest.approx(10.0)
    assert peak["right_knee_medial_deviation_pct"] == pytest.approx(5.0)
    assert peak["bilateral_alignment_difference_pct"] == pytest.approx(5.0)


def test_frame_metrics_report_positive_left_trunk_inclination() -> None:
    landmarks, phases = _biomechanics_tables()
    mask = landmarks["landmark"].isin(("left_shoulder", "right_shoulder"))
    landmarks.loc[mask & (landmarks["frame_index"] == 3), "x"] += 0.05

    metrics, _ = calculate_biomechanical_frame_metrics(landmarks, phases)

    peak = metrics[metrics["phase"] == "maxima_profundidad"].iloc[0]
    assert peak["trunk_inclination_deg"] == pytest.approx(
        np.degrees(np.arctan2(0.05, 0.20))
    )


def test_calculate_squat_biomechanics_exports_metrics(tmp_path: Path) -> None:
    landmarks, phases = _biomechanics_tables()
    landmarks_path = tmp_path / "landmarks.csv"
    phases_path = tmp_path / "frame_phases.csv"
    landmarks.to_csv(landmarks_path, index=False)
    phases.to_csv(phases_path, index=False)

    summary = calculate_squat_biomechanics(
        landmarks_path,
        phases_path,
        case_id="caso_001",
        output_dir=tmp_path / "outputs",
    )

    assert summary.total_frames == 5
    assert summary.valid_metric_frames == 5
    assert len(summary.repetitions) == 1
    assert summary.repetitions[0].peak_depth_frame == 3
    assert Path(summary.artifacts.frame_metrics_csv).exists()
    assert Path(summary.artifacts.repetition_metrics_csv).exists()
    assert Path(summary.artifacts.metrics_plot).exists()
    assert Path(summary.artifacts.summary_json).exists()


def test_frame_metrics_mask_invalid_frames() -> None:
    landmarks, phases = _biomechanics_tables()
    phases.loc[3, "valid_for_analysis"] = False

    metrics, _ = calculate_biomechanical_frame_metrics(landmarks, phases)

    peak = metrics[metrics["phase"] == "maxima_profundidad"].iloc[0]
    assert peak[
        [
            "trunk_inclination_deg",
            "pelvis_lateral_shift_pct",
            "left_knee_medial_deviation_pct",
        ]
    ].isna().all()


def test_frame_metrics_reject_missing_columns_and_landmarks() -> None:
    landmarks, phases = _biomechanics_tables()
    with pytest.raises(ValueError, match="missing required columns"):
        calculate_biomechanical_frame_metrics(
            landmarks.drop(columns="x"),
            phases,
        )

    without_ankle = landmarks[landmarks["landmark"] != "left_ankle"]
    with pytest.raises(ValueError, match="missing required points"):
        calculate_biomechanical_frame_metrics(without_ankle, phases)


def test_frame_metrics_require_nonzero_shoulder_reference() -> None:
    landmarks, phases = _biomechanics_tables()
    shoulder_mask = landmarks["landmark"].isin(("left_shoulder", "right_shoulder"))
    landmarks.loc[shoulder_mask, "x"] = 0.5

    with pytest.raises(ValueError, match="shoulder-width"):
        calculate_biomechanical_frame_metrics(landmarks, phases)


def test_frame_metrics_fall_back_when_initial_rest_is_unavailable() -> None:
    landmarks, phases = _biomechanics_tables()
    phases["repetition_index"] = 1

    metrics, shoulder_width = calculate_biomechanical_frame_metrics(
        landmarks,
        phases,
    )

    assert shoulder_width == pytest.approx(0.4)
    assert len(metrics) == 5


def test_repetition_summary_skips_cycle_without_peak_phase(tmp_path: Path) -> None:
    landmarks, phases = _biomechanics_tables()
    phases.loc[phases["repetition_index"] == 1, "phase"] = "descenso"
    landmarks_path = tmp_path / "landmarks.csv"
    phases_path = tmp_path / "frame_phases.csv"
    landmarks.to_csv(landmarks_path, index=False)
    phases.to_csv(phases_path, index=False)

    summary = calculate_squat_biomechanics(
        landmarks_path,
        phases_path,
        case_id="sin_pico",
        output_dir=tmp_path / "outputs",
    )

    assert summary.repetitions == []


def test_repetition_summary_handles_no_valid_metric_frames(tmp_path: Path) -> None:
    landmarks, phases = _biomechanics_tables()
    phases.loc[phases["repetition_index"] == 1, "valid_for_analysis"] = False
    landmarks_path = tmp_path / "landmarks.csv"
    phases_path = tmp_path / "frame_phases.csv"
    landmarks.to_csv(landmarks_path, index=False)
    phases.to_csv(phases_path, index=False)

    summary = calculate_squat_biomechanics(
        landmarks_path,
        phases_path,
        case_id="pico_invalido",
        output_dir=tmp_path / "outputs",
    )

    repetition = summary.repetitions[0]
    assert repetition.valid_frames_percentage == 0.0
    assert repetition.trunk_max_abs_deg is None
    assert repetition.left_knee_max_medial_deviation_pct is None


def test_as_bool_accepts_native_and_serialized_values() -> None:
    assert _as_bool(True) is True
    assert _as_bool("sí") is True
    assert _as_bool("no") is False
