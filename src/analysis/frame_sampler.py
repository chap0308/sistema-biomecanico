"""Keyframe sampling helpers for local video processing."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2

from src.analysis.scene_detect import SceneBoundary


@dataclass(slots=True)
class FrameSample:
    """One saved representative frame with timestamp."""

    sec: float
    path: str


def sample_scene_keyframes(
    video_path: str | Path,
    *,
    scenes: list[SceneBoundary],
    output_dir: str | Path,
) -> tuple[list[FrameSample], str]:
    """Sample one representative frame near the middle of each scene."""
    source = Path(video_path)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    if not source.exists():
        return [], "video_missing"

    capture = cv2.VideoCapture(str(source))
    try:
        if not capture.isOpened():
            return [], "opencv_open_failed"
        fps = float(capture.get(cv2.CAP_PROP_FPS) or 0.0)
        if fps <= 0.0:
            return [], "fps_missing"

        samples: list[FrameSample] = []
        for index, scene in enumerate(scenes, start=1):
            midpoint_sec = max(scene.start_sec, (scene.start_sec + scene.end_sec) / 2.0)
            frame_index = int(midpoint_sec * fps)
            capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            success, frame = capture.read()
            if not success or frame is None:
                continue
            frame_path = destination / f"scene_{index:03d}_{int(midpoint_sec * 1000):07d}ms.jpg"
            cv2.imwrite(str(frame_path), frame)
            samples.append(FrameSample(sec=midpoint_sec, path=str(frame_path)))
        return samples, "ok" if samples else "no_frames_sampled"
    finally:
        capture.release()
