"""Converters between MediaPipe landmarks and internal biomechanical models."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from biomechanics.models import RestingLandmarks
from pose.schemas import PoseLandmark

RELEVANT_LANDMARK_INDEXES: Mapping[str, int] = {
    "nose": 0,
    "left_ear": 7,
    "right_ear": 8,
    "left_shoulder": 11,
    "right_shoulder": 12,
    "left_elbow": 13,
    "right_elbow": 14,
    "left_hip": 23,
    "right_hip": 24,
    "left_knee": 25,
    "right_knee": 26,
    "left_ankle": 27,
    "right_ankle": 28,
}


def _get_attr(landmark: Any, attr: str, default: float | None = 0.0) -> float | None:
    value = getattr(landmark, attr, default)
    if value is None:
        return None
    return float(value)


def to_pose_landmark(landmark: Any) -> PoseLandmark:
    """Convert a MediaPipe landmark-like object to the internal pose schema."""
    return PoseLandmark(
        x=float(_get_attr(landmark, "x", 0.0) or 0.0),
        y=float(_get_attr(landmark, "y", 0.0) or 0.0),
        z=float(_get_attr(landmark, "z", 0.0) or 0.0),
        visibility=float(_get_attr(landmark, "visibility", 0.0) or 0.0),
        presence=_get_attr(landmark, "presence", None),
    )


def to_pose_landmark_map(landmarks: Sequence[Any]) -> dict[str, PoseLandmark]:
    """Extract the subset of landmarks required by the resting pipeline."""
    missing = [name for name, index in RELEVANT_LANDMARK_INDEXES.items() if index >= len(landmarks)]
    if missing:
        raise ValueError(f"Missing pose landmarks for resting analysis: {', '.join(missing)}")
    return {
        name: to_pose_landmark(landmarks[index])
        for name, index in RELEVANT_LANDMARK_INDEXES.items()
    }


def to_resting_landmarks(landmarks: Sequence[Any]) -> RestingLandmarks:
    """Convert MediaPipe landmarks to the typed resting-landmarks domain model."""
    named = to_pose_landmark_map(landmarks)
    return RestingLandmarks.from_mapping({name: (point.x, point.y) for name, point in named.items()})


__all__ = [
    "RELEVANT_LANDMARK_INDEXES",
    "to_pose_landmark",
    "to_pose_landmark_map",
    "to_resting_landmarks",
]
