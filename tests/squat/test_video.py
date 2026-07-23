"""Tests for OpenCV squat video inspection."""

from __future__ import annotations

from pathlib import Path

import cv2
import pytest

from src.squat.video import SquatVideoReadError, probe_video


class _FakeCapture:
    def __init__(
        self,
        *,
        opened: bool = True,
        readable: bool = True,
        properties: dict[int, float] | None = None,
    ) -> None:
        self.opened = opened
        self.readable = readable
        self.properties = properties or {
            cv2.CAP_PROP_FRAME_WIDTH: 1080.0,
            cv2.CAP_PROP_FRAME_HEIGHT: 1920.0,
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_COUNT: 300.0,
        }
        self.released = False

    def isOpened(self) -> bool:
        return self.opened

    def get(self, property_id: int) -> float:
        return self.properties.get(property_id, 0.0)

    def read(self) -> tuple[bool, None]:
        return self.readable, None

    def release(self) -> None:
        self.released = True


def test_probe_video_extracts_technical_metadata(tmp_path: Path, monkeypatch) -> None:
    path = tmp_path / "case.mp4"
    path.touch()
    fake_capture = _FakeCapture()
    monkeypatch.setattr(cv2, "VideoCapture", lambda _: fake_capture)

    metadata = probe_video(path)

    assert metadata.width_px == 1080
    assert metadata.height_px == 1920
    assert metadata.duration_seconds == 10.0
    assert fake_capture.released is True


def test_probe_video_rejects_missing_or_unsupported_files(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        probe_video(tmp_path / "missing.mp4")

    unsupported = tmp_path / "case.txt"
    unsupported.touch()
    with pytest.raises(ValueError, match="Unsupported video format"):
        probe_video(unsupported)


def test_probe_video_rejects_unopenable_capture(tmp_path: Path, monkeypatch) -> None:
    path = tmp_path / "case.mp4"
    path.touch()
    fake_capture = _FakeCapture(opened=False)
    monkeypatch.setattr(cv2, "VideoCapture", lambda _: fake_capture)

    with pytest.raises(SquatVideoReadError, match="could not open"):
        probe_video(path)
    assert fake_capture.released is True


@pytest.mark.parametrize(
    ("properties", "readable"),
    [
        ({cv2.CAP_PROP_FRAME_WIDTH: 0.0}, True),
        ({
            cv2.CAP_PROP_FRAME_WIDTH: 1080.0,
            cv2.CAP_PROP_FRAME_HEIGHT: 1920.0,
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_COUNT: 300.0,
        }, False),
    ],
)
def test_probe_video_rejects_incomplete_metadata(
    tmp_path: Path,
    monkeypatch,
    properties: dict[int, float],
    readable: bool,
) -> None:
    path = tmp_path / "case.mp4"
    path.touch()
    fake_capture = _FakeCapture(properties=properties, readable=readable)
    monkeypatch.setattr(cv2, "VideoCapture", lambda _: fake_capture)

    with pytest.raises(SquatVideoReadError, match="metadata is incomplete"):
        probe_video(path)
