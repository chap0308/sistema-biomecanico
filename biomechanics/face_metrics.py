"""Facial asymmetry metrics computed from FaceMesh landmarks."""

from __future__ import annotations

from math import atan2, degrees

from biomechanics.models import BiomechanicsMetric
from pose.facemesh import FacePoint

_LEFT_IRIS = (474, 475, 476, 477)
_RIGHT_IRIS = (469, 470, 471, 472)
_NOSE_MIDLINE = 1
_CHIN_MIDLINE = 152


def _average_point(landmarks: dict[int, FacePoint], indices: tuple[int, ...]) -> FacePoint:
    points = [landmarks[index] for index in indices]
    return FacePoint(
        x=sum(point.x for point in points) / len(points),
        y=sum(point.y for point in points) / len(points),
    )


def _interpupillary_distance(landmarks: dict[int, FacePoint]) -> float:
    left = _average_point(landmarks, _LEFT_IRIS)
    right = _average_point(landmarks, _RIGHT_IRIS)
    return max(abs(right.x - left.x), 1e-6)


def bipupilar_tilt(landmarks: dict[int, FacePoint]) -> float:
    """Angle of the bipupillary line relative to the horizontal."""
    left = _average_point(landmarks, _LEFT_IRIS)
    right = _average_point(landmarks, _RIGHT_IRIS)
    return degrees(atan2(right.y - left.y, right.x - left.x))


def mandibular_lateral_shift(landmarks: dict[int, FacePoint]) -> float:
    """Normalized horizontal shift of the chin center relative to the nasal midline."""
    nose = landmarks[_NOSE_MIDLINE]
    chin = landmarks[_CHIN_MIDLINE]
    return (chin.x - nose.x) / _interpupillary_distance(landmarks)


def compute_face_metrics(landmarks: dict[int, FacePoint]) -> dict[str, BiomechanicsMetric]:
    """Compute the facial metrics used by the grouped static image endpoint."""
    return {
        "bipupilar_tilt": BiomechanicsMetric(
            name="bipupilar_tilt",
            value=bipupilar_tilt(landmarks),
            plane="frontal",
            unit="degrees",
            measurement_type="direct",
            priority="P0",
        ),
        "mandibular_lateral_shift": BiomechanicsMetric(
            name="mandibular_lateral_shift",
            value=mandibular_lateral_shift(landmarks),
            plane="frontal",
            unit="normalized",
            measurement_type="proxy",
            priority="P0",
        ),
    }


__all__ = [
    "bipupilar_tilt",
    "compute_face_metrics",
    "mandibular_lateral_shift",
]
