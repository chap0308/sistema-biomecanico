"""Tests for scapula static metrics stability and confidence metadata."""

from __future__ import annotations

from types import SimpleNamespace

from biomechanics.models import RestingLandmarks
from biomechanics.specialty_metrics import compute_scapula_static_metrics
from pose.schemas import PoseLandmark


def _base_posture_points() -> dict[str, tuple[float, float]]:
    return {
        "nose": (0.50, 0.12),
        "left_ear": (0.42, 0.14),
        "right_ear": (0.58, 0.14),
        "left_shoulder": (0.34, 0.26),
        "right_shoulder": (0.66, 0.24),
        "left_elbow": (0.30, 0.42),
        "right_elbow": (0.70, 0.40),
        "left_hip": (0.40, 0.52),
        "right_hip": (0.60, 0.50),
        "left_knee": (0.42, 0.74),
        "right_knee": (0.60, 0.74),
        "left_ankle": (0.43, 0.94),
        "right_ankle": (0.59, 0.94),
    }


def _transform_points(
    points: dict[str, tuple[float, float]],
    *,
    scale_x: float,
    scale_y: float,
    offset_x: float,
    offset_y: float,
) -> RestingLandmarks:
    transformed = {
        name: (offset_x + scale_x * x, offset_y + scale_y * y)
        for name, (x, y) in points.items()
    }
    return RestingLandmarks.from_mapping(transformed)


def _pose_result_for(landmarks: RestingLandmarks, *, shoulder_visibility: float = 0.95) -> object:
    point_map = {
        "nose": landmarks.nose,
        "left_ear": landmarks.left_ear,
        "right_ear": landmarks.right_ear,
        "left_shoulder": landmarks.left_shoulder,
        "right_shoulder": landmarks.right_shoulder,
        "left_elbow": landmarks.left_elbow,
        "right_elbow": landmarks.right_elbow,
        "left_hip": landmarks.left_hip,
        "right_hip": landmarks.right_hip,
        "left_knee": landmarks.left_knee,
        "right_knee": landmarks.right_knee,
        "left_ankle": landmarks.left_ankle,
        "right_ankle": landmarks.right_ankle,
    }
    named_landmarks = {}
    for name, point in point_map.items():
        visibility = shoulder_visibility if "shoulder" in name else 0.95
        z = -0.12 if name == "left_shoulder" else 0.12 if name == "right_shoulder" else 0.0
        named_landmarks[name] = PoseLandmark(x=point.x, y=point.y, z=z, visibility=visibility, presence=0.99)
    return SimpleNamespace(named_landmarks=named_landmarks)


def test_scapula_metrics_are_reasonably_stable_under_crop_rescaling() -> None:
    base = _base_posture_points()
    torso_crop = _transform_points(base, scale_x=0.72, scale_y=0.56, offset_x=0.12, offset_y=0.06)
    full_body = _transform_points(base, scale_x=0.38, scale_y=0.84, offset_x=0.28, offset_y=0.04)

    torso_metrics = compute_scapula_static_metrics(torso_crop, include_placeholders=False)
    full_metrics = compute_scapula_static_metrics(full_body, include_placeholders=False)

    assert abs(torso_metrics["scapula_spine_distance_left"].value - full_metrics["scapula_spine_distance_left"].value) < 0.08
    assert abs(torso_metrics["scapula_spine_distance_right"].value - full_metrics["scapula_spine_distance_right"].value) < 0.08
    assert abs(torso_metrics["scapular_internal_rotation_left"].value - full_metrics["scapular_internal_rotation_left"].value) < 8.0
    assert abs(torso_metrics["scapular_upward_rotation_left"].value - full_metrics["scapular_upward_rotation_left"].value) < 8.0


def test_scapular_upward_rotation_uses_interpretable_horizontal_deviation() -> None:
    landmarks = _transform_points(_base_posture_points(), scale_x=0.60, scale_y=0.70, offset_x=0.18, offset_y=0.08)
    metrics = compute_scapula_static_metrics(landmarks, include_placeholders=False)

    left = metrics["scapular_upward_rotation_left"].value
    right = metrics["scapular_upward_rotation_right"].value

    assert 0.0 <= left <= 90.0
    assert 0.0 <= right <= 90.0
    assert left > 0.0
    assert right > 0.0


def test_scapula_static_metrics_add_confidence_and_crop_notes() -> None:
    base = _base_posture_points()
    torso_crop = _transform_points(base, scale_x=0.74, scale_y=0.58, offset_x=0.10, offset_y=0.06)
    full_body = _transform_points(base, scale_x=0.30, scale_y=0.86, offset_x=0.31, offset_y=0.04)

    torso_metrics = compute_scapula_static_metrics(
        torso_crop,
        pose_result=_pose_result_for(torso_crop),
        include_placeholders=False,
    )
    full_metrics = compute_scapula_static_metrics(
        full_body,
        pose_result=_pose_result_for(full_body),
        include_placeholders=False,
    )

    torso_distance = torso_metrics["scapula_spine_distance_left"]
    full_distance = full_metrics["scapula_spine_distance_left"]
    full_upward = full_metrics["scapular_upward_rotation_left"]

    assert torso_distance.confidence is not None
    assert full_distance.confidence is not None
    assert torso_distance.confidence > full_distance.confidence
    assert torso_distance.confidence_base == "low_medium"
    assert full_distance.proxy_type == "posterior_shoulder_girdle"
    assert full_distance.anatomical_directness == "indirect"
    assert "posterior_view_proxy" in full_distance.quality_notes
    assert "scapula_not_directly_tracked" in full_distance.quality_notes
    assert any("Full body crop reduces scapular precision" in note for note in full_distance.quality_notes)
    assert "full_body_crop_reduces_scapular_precision" in full_distance.flags
    assert "fragile_scapular_proxy" in full_distance.flags
    assert full_upward.status in {"computed", "low_confidence"}
    assert full_upward.quality_notes
