"""Tests for temporal segmentation of bilateral-squat pose artifacts."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.squat.segmentation import (
    _as_bool,
    detect_squat_repetitions,
    segment_squat_pose_artifacts,
)


def _synthetic_squat_signal(
    *,
    frame_count: int = 480,
    centers: tuple[int, ...] = (100, 250, 400),
) -> np.ndarray:
    frames = np.arange(frame_count)
    signal = np.full(frame_count, 0.38, dtype=float)
    for center in centers:
        signal += 0.27 * np.exp(-0.5 * ((frames - center) / 24.0) ** 2)
    return signal


def _write_pose_tables(
    tmp_path: Path,
    *,
    signal: np.ndarray,
    fps: float = 30.0,
    timestamps: np.ndarray | None = None,
) -> tuple[Path, Path]:
    time_values = (
        np.arange(len(signal), dtype=float) / fps
        if timestamps is None
        else timestamps
    )
    landmark_rows = []
    quality_rows = []
    for frame_index, (timestamp, hip_y) in enumerate(
        zip(time_values, signal, strict=True)
    ):
        for landmark, offset in (("left_hip", -0.002), ("right_hip", 0.002)):
            landmark_rows.append(
                {
                    "frame_index": frame_index,
                    "timestamp_seconds": timestamp,
                    "landmark": landmark,
                    "y": hip_y + offset,
                }
            )
        quality_rows.append(
            {
                "frame_index": frame_index,
                "valid_for_analysis": "false" if frame_index == 100 else "true",
            }
        )

    landmarks_path = tmp_path / "landmarks.csv"
    quality_path = tmp_path / "frame_quality.csv"
    pd.DataFrame(landmark_rows).to_csv(landmarks_path, index=False)
    pd.DataFrame(quality_rows).to_csv(quality_path, index=False)
    return landmarks_path, quality_path


def test_detect_squat_repetitions_finds_three_complete_cycles() -> None:
    smoothed, repetitions = detect_squat_repetitions(
        _synthetic_squat_signal(),
        fps=30.0,
    )

    assert len(smoothed) == 480
    assert len(repetitions) == 3
    assert all(
        abs(detected.peak_depth_frame - expected) <= 1
        for detected, expected in zip(repetitions, (100, 250, 400), strict=True)
    )
    assert all(
        item.start_frame < item.peak_depth_frame < item.end_frame
        for item in repetitions
    )


def test_detect_squat_repetitions_returns_empty_for_stationary_signal() -> None:
    smoothed, repetitions = detect_squat_repetitions([0.4] * 120, fps=30.0)

    assert np.allclose(smoothed, 0.4)
    assert repetitions == []


@pytest.mark.parametrize(
    ("signal", "fps", "message"),
    [
        ([0.1, 0.2], 30.0, "one-dimensional"),
        ([[0.1, 0.2], [0.3, 0.4]], 30.0, "one-dimensional"),
        ([np.nan, np.nan, np.nan], 30.0, "finite"),
        ([0.1, 0.2, 0.3], 0.0, "greater than zero"),
    ],
)
def test_detect_squat_repetitions_rejects_invalid_signals(
    signal: list[float] | list[list[float]],
    fps: float,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        detect_squat_repetitions(signal, fps=fps)


def test_segment_squat_pose_artifacts_exports_traceable_evidence(
    tmp_path: Path,
) -> None:
    landmarks_path, quality_path = _write_pose_tables(
        tmp_path,
        signal=_synthetic_squat_signal(frame_count=180, centers=(90,)),
    )

    summary = segment_squat_pose_artifacts(
        landmarks_path,
        quality_path,
        case_id="caso_001",
        output_dir=tmp_path / "outputs",
    )

    assert summary.repetitions_detected == 1
    assert abs(summary.repetitions[0].peak_depth_frame - 90) <= 1
    assert summary.repetitions[0].valid_frames_percentage < 100.0
    assert Path(summary.artifacts.frame_phases_csv).exists()
    assert Path(summary.artifacts.repetitions_csv).exists()
    assert Path(summary.artifacts.segmentation_plot).exists()
    assert Path(summary.artifacts.summary_json).exists()

    phases = pd.read_csv(summary.artifacts.frame_phases_csv)
    assert set(phases["phase"]) == {
        "reposo",
        "descenso",
        "maxima_profundidad",
        "ascenso",
        "cierre",
    }


def test_segment_squat_pose_artifacts_rejects_missing_columns(
    tmp_path: Path,
) -> None:
    landmarks_path = tmp_path / "landmarks.csv"
    quality_path = tmp_path / "frame_quality.csv"
    pd.DataFrame({"frame_index": [0]}).to_csv(landmarks_path, index=False)
    pd.DataFrame(
        {"frame_index": [0], "valid_for_analysis": [True]}
    ).to_csv(quality_path, index=False)

    with pytest.raises(ValueError, match="missing required columns"):
        segment_squat_pose_artifacts(
            landmarks_path,
            quality_path,
            case_id="caso_001",
            output_dir=tmp_path / "outputs",
        )


def test_segment_squat_pose_artifacts_requires_progressing_timestamps(
    tmp_path: Path,
) -> None:
    signal = _synthetic_squat_signal(frame_count=20, centers=(10,))
    landmarks_path, quality_path = _write_pose_tables(
        tmp_path,
        signal=signal,
        timestamps=np.zeros(len(signal)),
    )

    with pytest.raises(ValueError, match="Unable to infer fps"):
        segment_squat_pose_artifacts(
            landmarks_path,
            quality_path,
            case_id="caso_001",
            output_dir=tmp_path / "outputs",
        )


def test_as_bool_accepts_native_and_serialized_values() -> None:
    assert _as_bool(True) is True
    assert _as_bool("yes") is True
    assert _as_bool("no") is False
