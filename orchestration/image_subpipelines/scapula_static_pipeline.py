"""Grouped static scapula pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from api.schemas.image import UploadedStaticImage
from biomechanics.resting_metrics import neck_center, pelvis_center, thoracic_center, upper_spine_reference
from biomechanics.specialty_metrics import compute_scapula_static_metrics
from orchestration.image_subpipelines.common import (
    serialize_line,
    serialize_metric,
    serialize_metric_snapshot,
    serialize_named_points,
    serialize_pose_metadata,
)
from pose.mediapipe_pose import MediaPipePoseExtractor

SCAPULA_READABLE_LAYERS = ("spine_reference", "scapula_distance", "upward_rotation")
SCAPULA_FULL_LAYERS = ("landmarks", "spine_reference", "scapula_distance", "internal_rotation", "upward_rotation")


def _metric_debug_details(metrics: dict[str, dict[str, object]]) -> dict[str, dict[str, object]]:
    detail_keys = (
        "value",
        "status",
        "confidence",
        "quality_notes",
        "source_of_truth",
        "calculation_status",
        "flags",
    )
    return {
        metric_name: {
            key: metric.get(key)
            for key in detail_keys
            if isinstance(metric, dict) and metric.get(key) is not None and metric.get(key) != []
        }
        for metric_name, metric in metrics.items()
    }


def _layer_payload(
    *,
    points: dict[str, object] | None = None,
    highlighted_points: dict[str, object] | None = None,
    reference_lines: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {}
    if points:
        payload["points"] = serialize_named_points(points)
    if highlighted_points:
        payload["highlighted_points"] = serialize_named_points(highlighted_points)
    if reference_lines:
        payload["reference_lines"] = reference_lines
    return payload


def _flatten_reference_lines(layers: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    flattened: list[dict[str, object]] = []
    for layer in layers.values():
        flattened.extend(layer.get("reference_lines", []))
    return flattened


def _build_scapula_layers(resting_landmarks: object) -> dict[str, dict[str, object]]:
    thorax = thoracic_center(resting_landmarks)
    neck = neck_center(resting_landmarks)
    pelvis = pelvis_center(resting_landmarks)
    upper_spine = upper_spine_reference(resting_landmarks)
    return {
        "landmarks": _layer_payload(
            points={
                "left_ear": resting_landmarks.left_ear,
                "right_ear": resting_landmarks.right_ear,
                "left_shoulder": resting_landmarks.left_shoulder,
                "right_shoulder": resting_landmarks.right_shoulder,
                "left_elbow": resting_landmarks.left_elbow,
                "right_elbow": resting_landmarks.right_elbow,
                "left_hip": resting_landmarks.left_hip,
                "right_hip": resting_landmarks.right_hip,
                "left_knee": resting_landmarks.left_knee,
                "right_knee": resting_landmarks.right_knee,
                "left_ankle": resting_landmarks.left_ankle,
                "right_ankle": resting_landmarks.right_ankle,
            }
        ),
        "spine_reference": _layer_payload(
            points={
                "left_shoulder": resting_landmarks.left_shoulder,
                "right_shoulder": resting_landmarks.right_shoulder,
                "left_hip": resting_landmarks.left_hip,
                "right_hip": resting_landmarks.right_hip,
            },
            highlighted_points={
                "neck_center": neck,
                "upper_spine_reference": upper_spine,
                "pelvis_center": pelvis,
                "thoracic_center": thorax,
            },
            reference_lines=[
                serialize_line(resting_landmarks.left_shoulder, resting_landmarks.right_shoulder, label="shoulder_line"),
                serialize_line(neck, pelvis, label="torso_axis"),
            ],
        ),
        "scapula_distance": _layer_payload(
            points={
                "left_shoulder": resting_landmarks.left_shoulder,
                "right_shoulder": resting_landmarks.right_shoulder,
            },
            highlighted_points={"upper_spine_reference": upper_spine},
            reference_lines=[
                serialize_line(upper_spine, resting_landmarks.left_shoulder, label="scapula_spine_distance_left"),
                serialize_line(upper_spine, resting_landmarks.right_shoulder, label="scapula_spine_distance_right"),
            ],
        ),
        "internal_rotation": _layer_payload(
            points={
                "left_shoulder": resting_landmarks.left_shoulder,
                "right_shoulder": resting_landmarks.right_shoulder,
            },
            highlighted_points={"upper_spine_reference": upper_spine},
            reference_lines=[
                serialize_line(upper_spine, resting_landmarks.left_shoulder, label="scapular_internal_rotation_left"),
                serialize_line(upper_spine, resting_landmarks.right_shoulder, label="scapular_internal_rotation_right"),
            ],
        ),
        "upward_rotation": _layer_payload(
            points={
                "left_shoulder": resting_landmarks.left_shoulder,
                "right_shoulder": resting_landmarks.right_shoulder,
            },
            highlighted_points={"upper_spine_reference": upper_spine},
            reference_lines=[
                serialize_line(upper_spine, resting_landmarks.left_shoulder, label="scapular_upward_rotation_left"),
                serialize_line(upper_spine, resting_landmarks.right_shoulder, label="scapular_upward_rotation_right"),
            ],
        ),
    }


def _build_scapula_debug(pose_result: object, metrics: dict[str, dict[str, object]]) -> dict[str, object]:
    resting_landmarks = pose_result.resting_landmarks
    thorax = thoracic_center(resting_landmarks)
    neck = neck_center(resting_landmarks)
    pelvis = pelvis_center(resting_landmarks)
    upper_spine = upper_spine_reference(resting_landmarks)
    layers = _build_scapula_layers(resting_landmarks)
    return {
        "landmarks": serialize_named_points(pose_result.named_landmarks),
        "highlighted_points": serialize_named_points(
            {
                "neck_center": neck,
                "thoracic_center": thorax,
                "pelvis_center": pelvis,
                "upper_spine_reference": upper_spine,
            }
        ),
        "reference_lines": _flatten_reference_lines(layers),
        "metrics": serialize_metric_snapshot(metrics),
        "metric_details": _metric_debug_details(metrics),
        "layers": layers,
        "available_layers": list(SCAPULA_FULL_LAYERS),
        "overlay_modes": {
            "readable": list(SCAPULA_READABLE_LAYERS),
            "full": list(SCAPULA_FULL_LAYERS),
        },
        "default_overlay_mode": "readable",
    }


@dataclass(slots=True)
class ScapulaStaticPipeline:
    """Compute scapula-focused static metrics from the posterior upper-body image."""

    pose_extractor: MediaPipePoseExtractor

    def analyze(self, images: dict[str, UploadedStaticImage], *, include_placeholders: bool) -> dict[str, object]:
        """Analyze the dedicated scapula image."""
        pose_result = self.pose_extractor.extract_from_image_bytes(images["back_upper_body"].payload)
        metrics = compute_scapula_static_metrics(
            pose_result.resting_landmarks,
            pose_result=pose_result,
            include_placeholders=include_placeholders,
        )
        serialized_metrics = {name: serialize_metric(metric) for name, metric in metrics.items()}
        return {
            "status": "success",
            "pose": serialize_pose_metadata(pose_result.metadata),
            "metrics": serialized_metrics,
            "debug": _build_scapula_debug(pose_result, serialized_metrics),
        }
