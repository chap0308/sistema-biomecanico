"""Tests for anonymized repetition-event captures."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from src.squat.evidence import generate_repetition_event_captures
from src.squat.models import (
    SquatRepetition,
    SquatSegmentationArtifacts,
    SquatSegmentationSummary,
)


class _FakeCapture:
    def __init__(self) -> None:
        self.requested_frames: list[int] = []

    def isOpened(self) -> bool:
        return True

    def set(self, _property: int, frame_index: int) -> bool:
        self.requested_frames.append(int(frame_index))
        return True

    def read(self) -> tuple[bool, np.ndarray]:
        return True, np.zeros((32, 24, 3), dtype=np.uint8)

    def release(self) -> None:
        return None


def _segmentation() -> SquatSegmentationSummary:
    return SquatSegmentationSummary(
        case_id="caso_001",
        landmarks_csv="landmarks.csv",
        frame_quality_csv="quality.csv",
        fps=30.0,
        total_frames=100,
        repetitions_detected=1,
        repetitions=[
            SquatRepetition(
                repetition_index=1,
                start_frame=10,
                peak_depth_frame=20,
                end_frame=30,
                start_seconds=1.0,
                peak_depth_seconds=2.0,
                end_seconds=3.0,
                descent_duration_seconds=1.0,
                ascent_duration_seconds=1.0,
                total_duration_seconds=2.0,
                peak_hip_midpoint_y=0.7,
                valid_frames_percentage=100.0,
            )
        ],
        artifacts=SquatSegmentationArtifacts(
            frame_phases_csv="phases.csv",
            repetitions_csv="repetitions.csv",
            segmentation_plot="segmentation.png",
            summary_json="summary.json",
        ),
    )


def test_event_captures_export_three_anonymized_checkpoints(
    tmp_path: Path,
    monkeypatch,
) -> None:
    overlay = tmp_path / "overlay.mp4"
    overlay.write_bytes(b"video")
    fake_capture = _FakeCapture()
    written: list[str] = []
    monkeypatch.setattr(
        "src.squat.evidence.cv2.VideoCapture",
        lambda _: fake_capture,
    )
    monkeypatch.setattr(
        "src.squat.evidence.cv2.imwrite",
        lambda path, _frame: written.append(Path(path).name) is None or True,
    )

    captures = generate_repetition_event_captures(
        overlay,
        _segmentation(),
        output_dir=tmp_path / "outputs",
    )

    assert fake_capture.requested_frames == [10, 20, 30]
    assert written == [
        "rep_01_inicio_descenso.png",
        "rep_01_maxima_profundidad.png",
        "rep_01_final_ascenso.png",
    ]
    assert [item.event for item in captures] == [
        "inicio_descenso",
        "maxima_profundidad",
        "final_ascenso",
    ]


def test_event_captures_require_existing_overlay(tmp_path: Path) -> None:
    try:
        generate_repetition_event_captures(
            tmp_path / "missing.mp4",
            _segmentation(),
            output_dir=tmp_path,
        )
    except FileNotFoundError as exc:
        assert "does not exist" in str(exc)
    else:
        raise AssertionError("Expected FileNotFoundError")
