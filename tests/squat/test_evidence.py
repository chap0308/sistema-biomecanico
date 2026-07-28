"""Tests for anonymized repetition-event captures."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from src.squat.evidence import (
    generate_analysis_overlay_video,
    generate_repetition_event_captures,
)
from src.squat.models import (
    SquatFindingsArtifacts,
    SquatFindingsSummary,
    SquatRepetition,
    SquatRuleDecision,
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


class _FakeAnalysisCapture:
    def __init__(self) -> None:
        self.frame_index = 0

    def isOpened(self) -> bool:
        return True

    def get(self, property_id: int) -> float:
        values = {5: 30.0, 3: 640.0, 4: 480.0}
        return values[property_id]

    def read(self) -> tuple[bool, np.ndarray | None]:
        if self.frame_index >= 2:
            return False, None
        self.frame_index += 1
        return True, np.zeros((480, 640, 3), dtype=np.uint8)

    def release(self) -> None:
        return None


class _FakeWriter:
    def __init__(self) -> None:
        self.frames: list[np.ndarray] = []

    def isOpened(self) -> bool:
        return True

    def write(self, frame: np.ndarray) -> None:
        self.frames.append(frame.copy())

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


def test_analysis_overlay_adds_compact_frame_evidence(
    tmp_path: Path,
    monkeypatch,
) -> None:
    overlay = tmp_path / "overlay.mp4"
    overlay.write_bytes(b"video")
    phases = tmp_path / "phases.csv"
    metrics = tmp_path / "metrics.csv"
    quality = tmp_path / "quality.csv"
    phases.write_text(
        "frame_index,repetition_index,phase\n"
        "0,1,descenso\n1,1,maxima_profundidad\n",
        encoding="utf-8",
    )
    metrics.write_text(
        "frame_index,trunk_inclination_deg,pelvis_lateral_shift_pct,"
        "left_knee_medial_deviation_pct,right_knee_medial_deviation_pct,"
        "bilateral_alignment_difference_pct\n"
        "0,1,2,3,4,1\n1,5,6,7,8,1\n",
        encoding="utf-8",
    )
    quality.write_text(
        "frame_index,valid_for_analysis,minimum_critical_visibility\n"
        "0,True,0.9\n1,True,0.8\n",
        encoding="utf-8",
    )
    fake_capture = _FakeAnalysisCapture()
    fake_writer = _FakeWriter()
    monkeypatch.setattr(
        "src.squat.evidence.cv2.VideoCapture",
        lambda _: fake_capture,
    )
    monkeypatch.setattr(
        "src.squat.evidence.cv2.VideoWriter",
        lambda *_args: fake_writer,
    )
    monkeypatch.setattr(
        "src.squat.evidence.encode_h264_mp4",
        lambda _source, target: Path(target).write_bytes(b"h264"),
    )

    output = generate_analysis_overlay_video(
        overlay,
        phases,
        metrics,
        quality,
        _findings(),
        output_dir=tmp_path / "outputs",
    )

    assert output.name == "analysis_overlay.mp4"
    assert output.read_bytes() == b"h264"
    assert len(fake_writer.frames) == 2
    assert np.any(fake_writer.frames[0])


def _findings() -> SquatFindingsSummary:
    return SquatFindingsSummary(
        case_id="caso_001",
        ruleset_version="test",
        ruleset_status="provisional",
        quality_gate_status="apto_para_analisis",
        decisions=[
            SquatRuleDecision(
                repetition_index=1,
                finding="inclinacion_lateral_tronco",
                status="presente",
                direction="izquierda",
                metric="trunk",
                unit="deg",
                aggregate_value=12.0,
                repetition_values=[12.0],
                repetition_states=["presente"],
                absent_max=8.0,
                present_min=12.0,
                rationale="test",
            )
        ],
        detected_findings=["repeticion_1:inclinacion_lateral_tronco"],
        inconclusive_findings=[],
        notes=[],
        artifacts=SquatFindingsArtifacts(
            rule_evidence_csv="rules.csv",
            findings_json="findings.json",
        ),
    )
