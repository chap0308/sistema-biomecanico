"""OpenCV-based technical inspection for squat video inputs."""

from __future__ import annotations

from pathlib import Path

import cv2

from src.squat.models import VideoTechnicalMetadata

SUPPORTED_VIDEO_SUFFIXES = frozenset({".mp4", ".mov", ".avi", ".mkv", ".webm"})


class SquatVideoReadError(RuntimeError):
    """Raised when a local squat video cannot be inspected reliably."""


def probe_video(video_path: str | Path) -> VideoTechnicalMetadata:
    """Read basic video properties and verify that the first frame is decodable."""
    resolved = Path(video_path).expanduser().resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"Squat video does not exist: {resolved}")
    if resolved.suffix.lower() not in SUPPORTED_VIDEO_SUFFIXES:
        supported = ", ".join(sorted(SUPPORTED_VIDEO_SUFFIXES))
        raise ValueError(f"Unsupported video format '{resolved.suffix}'. Expected: {supported}")

    capture = cv2.VideoCapture(str(resolved))
    try:
        if not capture.isOpened():
            raise SquatVideoReadError(f"OpenCV could not open the video: {resolved}")

        width = int(round(capture.get(cv2.CAP_PROP_FRAME_WIDTH)))
        height = int(round(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        fps = float(capture.get(cv2.CAP_PROP_FPS))
        frame_count = int(round(capture.get(cv2.CAP_PROP_FRAME_COUNT)))
        first_frame_readable, _ = capture.read()
    finally:
        capture.release()

    if width <= 0 or height <= 0 or fps <= 0 or frame_count <= 0 or not first_frame_readable:
        raise SquatVideoReadError(
            "Video metadata is incomplete or its first frame is not readable: "
            f"{resolved}"
        )

    return VideoTechnicalMetadata(
        path=str(resolved),
        suffix=resolved.suffix.lower(),
        width_px=width,
        height_px=height,
        fps=fps,
        frame_count=frame_count,
        duration_seconds=frame_count / fps,
        first_frame_readable=True,
    )


__all__ = ["SUPPORTED_VIDEO_SUFFIXES", "SquatVideoReadError", "probe_video"]
