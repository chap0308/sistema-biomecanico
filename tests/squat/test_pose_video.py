"""Tests for temporal squat pose extraction and artifacts."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import builtins

import cv2
import numpy as np
import pytest

from src.squat.models import VideoTechnicalMetadata
from src.squat.pose_video import (
    SQUAT_LANDMARK_INDEXES,
    _percentage,
    _create_pose_model,
    _draw_pose_overlay,
    _pixelate_face,
    _pixelate_region,
    assess_pose_landmarks,
    extract_squat_pose_video,
)


def _landmarks(*, visibility: float = 0.95) -> list[SimpleNamespace]:
    return [
        SimpleNamespace(
            x=0.2 + (index % 5) * 0.1,
            y=0.1 + (index // 5) * 0.1,
            z=0.0,
            visibility=visibility,
            presence=0.99,
        )
        for index in range(33)
    ]


def test_assess_pose_landmarks_accepts_complete_visible_pose() -> None:
    assessment = assess_pose_landmarks(_landmarks(), min_visibility=0.5)

    assert assessment.pose_detected is True
    assert assessment.valid_for_analysis is True
    assert assessment.detected_keypoints == len(SQUAT_LANDMARK_INDEXES)
    assert assessment.invalid_reason == ""


def test_assess_pose_landmarks_rejects_missing_pose() -> None:
    assessment = assess_pose_landmarks(None, min_visibility=0.5)

    assert assessment.pose_detected is False
    assert assessment.valid_for_analysis is False
    assert assessment.invalid_reason == "pose_not_detected"


def test_assess_pose_landmarks_reports_core_and_distal_visibility() -> None:
    landmarks = _landmarks()
    landmarks[25].visibility = 0.2
    landmarks[29].visibility = 0.1
    landmarks[31].visibility = 0.1
    landmarks[30].visibility = 0.1
    landmarks[32].visibility = 0.1
    del landmarks[0].presence

    assessment = assess_pose_landmarks(landmarks, min_visibility=0.5)

    assert assessment.valid_for_analysis is False
    assert "left_knee" in assessment.invalid_reason
    assert "left_distal_foot" in assessment.invalid_reason
    assert "right_distal_foot" in assessment.invalid_reason
    assert assessment.all_landmarks[0].presence is None


def test_pixelation_changes_face_region_and_handles_empty_region() -> None:
    image = np.full((100, 80, 3), 127, dtype=np.uint8)
    image[:50, :, 0] = np.arange(80, dtype=np.uint8)
    original = image.copy()

    _pixelate_face(image, ())
    _pixelate_region(image, x0=10, y0=10, x1=10, y1=20)
    _pixelate_region(image, x0=200, y0=200, x1=210, y1=210)

    assert not np.array_equal(image[:50], original[:50])


def test_pixelation_uses_detected_face_landmarks() -> None:
    image = np.indices((100, 80))[1].astype(np.uint8)
    image = np.repeat(image[:, :, None], 3, axis=2)
    landmarks = _landmarks()

    _pixelate_face(image, tuple(
        SimpleNamespace(
            x=item.x,
            y=item.y,
            z=item.z,
            visibility=item.visibility,
            presence=item.presence,
        )
        for item in landmarks
    ))

    assert image.shape == (100, 80, 3)


class _FakeCapture:
    def __init__(self, frames: list[np.ndarray], *, opened: bool = True) -> None:
        self.frames = list(frames)
        self.opened = opened
        self.released = False

    def isOpened(self) -> bool:
        return self.opened

    def read(self) -> tuple[bool, np.ndarray | None]:
        if not self.frames:
            return False, None
        return True, self.frames.pop(0)

    def release(self) -> None:
        self.released = True


class _FakeWriter:
    def __init__(self, *, opened: bool = True) -> None:
        self.opened = opened
        self.frames: list[np.ndarray] = []
        self.released = False

    def isOpened(self) -> bool:
        return self.opened

    def write(self, frame: np.ndarray) -> None:
        self.frames.append(frame.copy())

    def release(self) -> None:
        self.released = True


class _FakePoseModel:
    def __init__(self) -> None:
        self.calls = 0

    def __enter__(self) -> "_FakePoseModel":
        return self

    def __exit__(self, *_args) -> None:
        return None

    def process(self, _frame_rgb: np.ndarray) -> SimpleNamespace:
        self.calls += 1
        if self.calls == 2:
            return SimpleNamespace(pose_landmarks=None)
        return SimpleNamespace(
            pose_landmarks=SimpleNamespace(landmark=_landmarks()),
        )


def _metadata(tmp_path: Path) -> VideoTechnicalMetadata:
    return VideoTechnicalMetadata(
        path=str(tmp_path / "case.mp4"),
        suffix=".mp4",
        width_px=80,
        height_px=100,
        fps=20.0,
        frame_count=2,
        duration_seconds=0.1,
        first_frame_readable=True,
    )


def test_extract_pose_video_writes_summary_and_csv_artifacts(tmp_path: Path, monkeypatch) -> None:
    capture = _FakeCapture([np.zeros((100, 80, 3), dtype=np.uint8) for _ in range(2)])
    overlay_writer = _FakeWriter()
    review_writer = _FakeWriter()
    writers = iter([overlay_writer, review_writer])
    encoded: list[tuple[Path, Path]] = []
    monkeypatch.setattr("src.squat.pose_video.probe_video", lambda _: _metadata(tmp_path))
    monkeypatch.setattr(cv2, "VideoCapture", lambda _: capture)
    monkeypatch.setattr(cv2, "VideoWriter", lambda *_args: next(writers))
    monkeypatch.setattr("src.squat.pose_video._create_pose_model", _FakePoseModel)
    monkeypatch.setattr(
        "src.squat.pose_video.encode_h264_mp4",
        lambda source, destination: encoded.append((Path(source), Path(destination))),
    )

    summary = extract_squat_pose_video(
        tmp_path / "case.mp4",
        case_id="case_001",
        output_dir=tmp_path / "outputs",
    )

    assert summary.processed_frames == 2
    assert summary.valid_frames == 1
    assert summary.valid_frames_percentage == 50.0
    assert Path(summary.artifacts.summary_json).exists()
    assert Path(summary.artifacts.landmarks_csv).exists()
    assert Path(summary.artifacts.frame_quality_csv).exists()
    assert Path(summary.artifacts.quality_plot).exists()
    assert summary.artifacts.review_video.endswith("review.mp4")
    assert len(overlay_writer.frames) == 2
    assert len(review_writer.frames) == 2
    assert not np.array_equal(
        overlay_writer.frames[0],
        review_writer.frames[0],
    )
    assert capture.released is True
    assert overlay_writer.released is True
    assert review_writer.released is True
    assert encoded == [
        (
            tmp_path / "outputs" / "case_001" / "overlay.intermediate.mp4",
            tmp_path / "outputs" / "case_001" / "overlay.mp4",
        ),
        (
            tmp_path / "outputs" / "case_001" / "review.intermediate.mp4",
            tmp_path / "outputs" / "case_001" / "review.mp4",
        ),
    ]


def test_extract_pose_video_validates_threshold(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="between 0 and 1"):
        extract_squat_pose_video(
            tmp_path / "case.mp4",
            case_id="case_001",
            output_dir=tmp_path,
            min_visibility=1.1,
        )


@pytest.mark.parametrize(("capture_opened", "writer_opened", "message"), [
    (False, True, "Unable to open squat video"),
    (True, False, "Unable to create squat overlay video"),
])
def test_extract_pose_video_rejects_unavailable_io(
    tmp_path: Path,
    monkeypatch,
    capture_opened: bool,
    writer_opened: bool,
    message: str,
) -> None:
    capture = _FakeCapture([], opened=capture_opened)
    writer = _FakeWriter(opened=writer_opened)
    monkeypatch.setattr("src.squat.pose_video.probe_video", lambda _: _metadata(tmp_path))
    monkeypatch.setattr(cv2, "VideoCapture", lambda _: capture)
    monkeypatch.setattr(cv2, "VideoWriter", lambda *_args: writer)

    with pytest.raises(RuntimeError, match=message):
        extract_squat_pose_video(
            tmp_path / "case.mp4",
            case_id="case_001",
            output_dir=tmp_path / "outputs",
        )


def test_create_pose_model_and_import_error(monkeypatch) -> None:
    model = _create_pose_model()
    model.close()

    original_import = builtins.__import__

    def fail_mediapipe(name: str, *args, **kwargs):
        if name == "mediapipe":
            raise ImportError("missing")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fail_mediapipe)
    with pytest.raises(RuntimeError, match="MediaPipe is required"):
        _create_pose_model()


def test_draw_overlay_handles_missing_landmark_connections() -> None:
    image = np.zeros((100, 80, 3), dtype=np.uint8)
    assessment = assess_pose_landmarks(None, min_visibility=0.5)

    _draw_pose_overlay(image, assessment, frame_index=1)

    assert image.sum() > 0


def test_percentage_handles_empty_denominator() -> None:
    assert _percentage(1, 4) == 25.0
    assert _percentage(0, 0) == 0.0
