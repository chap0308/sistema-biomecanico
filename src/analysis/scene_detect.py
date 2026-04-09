"""Scene boundary detection helpers for local video processing."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2


@dataclass(slots=True)
class SceneBoundary:
    """One detected or synthesized time window in a video."""

    start_sec: float
    end_sec: float


def get_video_duration_sec(video_path: str | Path) -> float | None:
    """Return video duration in seconds using OpenCV metadata when possible."""
    capture = cv2.VideoCapture(str(video_path))
    try:
        if not capture.isOpened():
            return None
        fps = float(capture.get(cv2.CAP_PROP_FPS) or 0.0)
        frame_count = float(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0.0)
        if fps <= 0.0 or frame_count <= 0.0:
            return None
        return frame_count / fps
    finally:
        capture.release()


def detect_scenes(
    video_path: str | Path,
    *,
    fallback_duration_sec: float | None = None,
) -> tuple[list[SceneBoundary], str]:
    """Detect scenes with PySceneDetect when present, otherwise return one fallback scene."""
    try:
        from scenedetect import ContentDetector, SceneManager, open_video
    except Exception:
        duration = fallback_duration_sec or get_video_duration_sec(video_path) or 10.0
        return [SceneBoundary(start_sec=0.0, end_sec=duration)], "fallback_single_scene"

    path = Path(video_path)
    if not path.exists():
        duration = fallback_duration_sec or 10.0
        return [SceneBoundary(start_sec=0.0, end_sec=duration)], "video_missing"

    try:
        video = open_video(str(path))
        manager = SceneManager()
        manager.add_detector(ContentDetector())
        manager.detect_scenes(video=video)
        detected = manager.get_scene_list()
        scenes = [
            SceneBoundary(
                start_sec=float(start.get_seconds()),
                end_sec=float(end.get_seconds()),
            )
            for start, end in detected
        ]
        if scenes:
            return scenes, "ok"
    except Exception:
        pass

    duration = fallback_duration_sec or get_video_duration_sec(video_path) or 10.0
    return [SceneBoundary(start_sec=0.0, end_sec=duration)], "fallback_single_scene"
