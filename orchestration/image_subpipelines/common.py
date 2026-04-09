"""Shared serialization helpers for grouped image subpipelines."""

from __future__ import annotations

from dataclasses import asdict
from math import isnan
from typing import Any

from biomechanics.models import BiomechanicsMetric
from pose.mediapipe_pose import PoseExtractionError


def serialize_metric(metric: BiomechanicsMetric, *, notes: list[str] | None = None) -> dict[str, object]:
    """Convert a metric dataclass into a JSON-safe response block."""
    output = asdict(metric)
    value = metric.value
    output["value"] = None if isinstance(value, float) and isnan(value) else value
    output["status"] = metric.status or ("placeholder" if output["value"] is None else "computed")
    output["notes"] = notes or []
    return output


def serialize_pose_metadata(metadata: object, *, notes: list[str] | None = None) -> dict[str, object]:
    """Normalize pose or face metadata for the response layer."""
    payload = asdict(metadata)
    payload["detected"] = True
    payload["notes"] = notes or []
    return payload


def serialize_named_points(points: dict[str, Any]) -> dict[str, dict[str, float]]:
    """Convert a mapping of point-like objects into JSON-safe point dictionaries."""
    serialized: dict[str, dict[str, float]] = {}
    for name, point in points.items():
        if point is None:
            continue
        x = getattr(point, "x", None)
        y = getattr(point, "y", None)
        if x is None or y is None:
            continue
        payload = {"x": float(x), "y": float(y)}
        z = getattr(point, "z", None)
        visibility = getattr(point, "visibility", None)
        if z is not None:
            payload["z"] = float(z)
        if visibility is not None:
            payload["visibility"] = float(visibility)
        serialized[name] = payload
    return serialized


def serialize_line(start: Any, end: Any, *, label: str) -> dict[str, object]:
    """Serialize a reference line between two point-like objects."""
    return {
        "label": label,
        "start": {"x": float(start.x), "y": float(start.y)},
        "end": {"x": float(end.x), "y": float(end.y)},
    }


def serialize_polyline(points: list[Any], *, label: str) -> dict[str, object]:
    """Serialize a polyline for debug overlays."""
    return {
        "label": label,
        "points": [{"x": float(point.x), "y": float(point.y)} for point in points],
    }


def serialize_metric_snapshot(metrics: dict[str, dict[str, object]]) -> dict[str, float | None]:
    """Extract only metric values for compact debug payloads."""
    return {
        name: metric.get("value")
        for name, metric in metrics.items()
        if isinstance(metric, dict)
    }


def decode_image_or_raise(image_bytes: bytes) -> tuple[object, int, int]:
    """Decode a BGR image and return both the array and its dimensions."""
    import cv2
    import numpy as np

    image_buffer = np.frombuffer(image_bytes, dtype=np.uint8)
    image_bgr = cv2.imdecode(image_buffer, cv2.IMREAD_COLOR)
    if image_bgr is None:
        raise PoseExtractionError("Unable to decode the uploaded image.")
    return image_bgr, int(image_bgr.shape[1]), int(image_bgr.shape[0])

