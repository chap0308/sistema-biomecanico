"""Tests for the pose extraction layer."""

from __future__ import annotations

from math import isclose
from types import SimpleNamespace

import numpy as np

from pose.mediapipe_pose import MediaPipePoseExtractor


class _FakeExtractor(MediaPipePoseExtractor):
    def _run_pose(self, image_rgb):
        _ = image_rgb
        landmarks: list[SimpleNamespace] = []
        for index in range(33):
            landmarks.append(
                SimpleNamespace(
                    x=0.10 + (index * 0.01),
                    y=0.20 + (index * 0.01),
                    z=0.0,
                    visibility=0.95,
                    presence=0.99,
                )
            )
        return SimpleNamespace(pose_landmarks=SimpleNamespace(landmark=landmarks))


def test_pose_extractor_maps_relevant_landmarks() -> None:
    """The pose layer should convert MediaPipe output to internal models."""
    extractor = _FakeExtractor()

    image = np.zeros((120, 200, 3), dtype=np.uint8)
    result = extractor.extract_from_image_array(image)

    assert result.metadata.image_width == 200
    assert result.metadata.image_height == 120
    assert result.metadata.landmark_count == 33
    assert result.metadata.relevant_landmark_count == 13
    assert isclose(result.resting_landmarks.left_shoulder.x, 0.21, rel_tol=0.0, abs_tol=1e-9)
    assert isclose(result.resting_landmarks.right_ankle.y, 0.48, rel_tol=0.0, abs_tol=1e-9)
