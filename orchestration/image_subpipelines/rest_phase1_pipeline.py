"""Grouped rest posture triad pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from api.schemas.image import UploadedStaticImage
from biomechanics.resting_metrics import ankle_center, neck_center, pelvis_center, thoracic_center
from orchestration.image_subpipelines.common import (
    serialize_line,
    serialize_metric_snapshot,
    serialize_named_points,
)
from orchestration.rest_pipeline import RestAnalysisPipeline

REST_PHASE1_METRICS_BY_VIEW: dict[str, tuple[str, ...]] = {
    "front": (
        "shoulder_height_difference",
        "torso_lateral_tilt",
        "pelvic_tilt",
        "head_tilt_angle",
    ),
    "side": (
        "pelvic_ankle_sagittal_offset",
        "cranio_shoulder_angle",
        "forward_center_of_mass_offset",
        "shoulder_protraction_angle_left",
        "shoulder_protraction_angle_right",
        "thoracic_kyphosis_angle",
        "thoracic_flattening_index",
        "scapular_anterior_tilt_left",
        "scapular_anterior_tilt_right",
    ),
    "back": (
        "shoulder_height_difference",
        "torso_lateral_tilt",
        "pelvic_tilt",
        "head_tilt_angle",
    ),
}

REST_PHASE1_READABLE_LAYERS: dict[str, tuple[str, ...]] = {
    "front": ("head_neck", "torso_pelvis", "support_axis"),
    "side": ("head_neck", "torso_pelvis", "support_axis"),
    "back": ("head_neck", "torso_pelvis", "support_axis"),
}

REST_PHASE1_FULL_LAYERS: dict[str, tuple[str, ...]] = {
    "front": ("landmarks", "head_neck", "torso_pelvis", "shoulder_scapula", "support_axis"),
    "side": ("landmarks", "head_neck", "torso_pelvis", "shoulder_scapula", "support_axis"),
    "back": ("landmarks", "head_neck", "torso_pelvis", "shoulder_scapula", "support_axis"),
}


def select_rest_phase1_metrics(view: str, metrics: Mapping[str, dict[str, object]]) -> dict[str, dict[str, object]]:
    """Return only the metrics explicitly assigned to the requested phase-1 view."""
    allowed_metrics = REST_PHASE1_METRICS_BY_VIEW[view]
    return {
        metric_name: dict(metrics[metric_name])
        for metric_name in allowed_metrics
        if metric_name in metrics
    }


def _append_unique_note(payload: dict[str, Any], note: str) -> None:
    quality_notes = list(payload.get("quality_notes", []))
    if note not in quality_notes:
        quality_notes.append(note)
    payload["quality_notes"] = quality_notes
    notes = list(payload.get("notes", []))
    if note not in notes:
        notes.append(note)
    payload["notes"] = notes


def _with_phase1_metric_metadata(view: str, metrics: dict[str, dict[str, object]]) -> dict[str, dict[str, object]]:
    enriched: dict[str, dict[str, object]] = {}
    for metric_name, metric in metrics.items():
        payload = dict(metric)
        if metric_name == "shoulder_height_difference":
            payload["calculation_status"] = payload.get("calculation_status") or "direct_vertical_difference"
            if view == "front":
                payload["source_of_truth"] = "front_primary"
                _append_unique_note(payload, "Frontal shoulder height difference is the primary source of truth for phase 1 because acromial contour is usually cleaner anteriorly.")
            elif view == "back":
                payload["source_of_truth"] = "back_corroborating"
                _append_unique_note(payload, "Posterior shoulder height difference is retained as a corroborating view because trapezius bulk and scapular contour can amplify apparent asymmetry.")
        elif metric_name in {"pelvic_tilt", "head_tilt_angle"}:
            payload["source_of_truth"] = f"{view}_horizontal_deviation"
            payload["calculation_status"] = payload.get("calculation_status") or "deviation_from_horizontal_reference"
        elif metric_name in {"thoracic_kyphosis_angle", "thoracic_flattening_index"}:
            payload["source_of_truth"] = payload.get("source_of_truth") or "side_view_proxy"
            payload["calculation_status"] = payload.get("calculation_status") or "proxy_from_profile_shoulder_offset"
        enriched[metric_name] = payload
    return enriched


def _metric_debug_details(metrics: dict[str, dict[str, object]]) -> dict[str, dict[str, object]]:
    detail_keys = (
        "value",
        "status",
        "confidence",
        "quality_notes",
        "source_of_truth",
        "calculation_status",
        "classification",
        "flags",
    )
    details: dict[str, dict[str, object]] = {}
    for metric_name, metric in metrics.items():
        details[metric_name] = {
            key: metric.get(key)
            for key in detail_keys
            if isinstance(metric, dict) and metric.get(key) is not None and metric.get(key) != []
        }
    return details


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


def _build_rest_phase1_layers(resting_landmarks: object, *, view: str) -> dict[str, dict[str, object]]:
    neck = neck_center(resting_landmarks)
    thorax = thoracic_center(resting_landmarks)
    pelvis = pelvis_center(resting_landmarks)
    ankle = ankle_center(resting_landmarks)

    base_layers = {
        "landmarks": _layer_payload(
            points={
                "nose": resting_landmarks.nose,
                "left_ear": resting_landmarks.left_ear,
                "right_ear": resting_landmarks.right_ear,
                "left_shoulder": resting_landmarks.left_shoulder,
                "right_shoulder": resting_landmarks.right_shoulder,
                "left_hip": resting_landmarks.left_hip,
                "right_hip": resting_landmarks.right_hip,
                "left_knee": resting_landmarks.left_knee,
                "right_knee": resting_landmarks.right_knee,
                "left_ankle": resting_landmarks.left_ankle,
                "right_ankle": resting_landmarks.right_ankle,
            }
        ),
        "head_neck": _layer_payload(
            points={
                "nose": resting_landmarks.nose,
                "left_ear": resting_landmarks.left_ear,
                "right_ear": resting_landmarks.right_ear,
                "left_shoulder": resting_landmarks.left_shoulder,
                "right_shoulder": resting_landmarks.right_shoulder,
            },
            highlighted_points={"neck_center": neck},
            reference_lines=[serialize_line(resting_landmarks.left_ear, resting_landmarks.right_ear, label="head_line")],
        ),
        "torso_pelvis": _layer_payload(
            points={
                "left_shoulder": resting_landmarks.left_shoulder,
                "right_shoulder": resting_landmarks.right_shoulder,
                "left_hip": resting_landmarks.left_hip,
                "right_hip": resting_landmarks.right_hip,
            },
            highlighted_points={
                "neck_center": neck,
                "thoracic_center": thorax,
                "pelvis_center": pelvis,
            },
            reference_lines=[
                serialize_line(resting_landmarks.left_hip, resting_landmarks.right_hip, label="pelvis_line"),
                serialize_line(neck, pelvis, label="torso_axis"),
            ],
        ),
        "shoulder_scapula": _layer_payload(
            points={
                "left_shoulder": resting_landmarks.left_shoulder,
                "right_shoulder": resting_landmarks.right_shoulder,
            },
            highlighted_points={"thoracic_center": thorax},
            reference_lines=[serialize_line(resting_landmarks.left_shoulder, resting_landmarks.right_shoulder, label="shoulder_line")],
        ),
    }

    if view == "side":
        base_layers["head_neck"]["reference_lines"] = [
            serialize_line(resting_landmarks.left_ear, resting_landmarks.right_ear, label="head_line"),
            serialize_line(resting_landmarks.left_ear, resting_landmarks.left_shoulder, label="cranio_shoulder_left"),
            serialize_line(resting_landmarks.right_ear, resting_landmarks.right_shoulder, label="cranio_shoulder_right"),
        ]
        base_layers["shoulder_scapula"]["reference_lines"] = [
            serialize_line(resting_landmarks.left_shoulder, resting_landmarks.right_shoulder, label="shoulder_line"),
            serialize_line(resting_landmarks.left_ear, resting_landmarks.left_hip, label="shoulder_protraction_left"),
            serialize_line(resting_landmarks.right_ear, resting_landmarks.right_hip, label="shoulder_protraction_right"),
            serialize_line(thorax, resting_landmarks.left_shoulder, label="scapular_anterior_tilt_left"),
            serialize_line(thorax, resting_landmarks.right_shoulder, label="scapular_anterior_tilt_right"),
        ]
        base_layers["support_axis"] = _layer_payload(
            points={
                "left_ankle": resting_landmarks.left_ankle,
                "right_ankle": resting_landmarks.right_ankle,
            },
            highlighted_points={
                "pelvis_center": pelvis,
                "ankle_center": ankle,
            },
            reference_lines=[serialize_line(pelvis, ankle, label="pelvis_to_ankle")],
        )
    else:
        base_layers["support_axis"] = _layer_payload(
            points={
                "left_ankle": resting_landmarks.left_ankle,
                "right_ankle": resting_landmarks.right_ankle,
            },
            highlighted_points={
                "thoracic_center": thorax,
                "ankle_center": ankle,
            },
            reference_lines=[serialize_line(thorax, ankle, label="torso_support_axis")],
        )

    return base_layers


def _flatten_reference_lines(layers: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    flattened: list[dict[str, object]] = []
    for layer in layers.values():
        for line in layer.get("reference_lines", []):
            flattened.append(line)
    return flattened


def _build_rest_phase1_debug(pose_result: object, *, view: str, metrics: dict[str, dict[str, object]]) -> dict[str, object]:
    resting_landmarks = pose_result.resting_landmarks
    named_landmarks = pose_result.named_landmarks
    neck = neck_center(resting_landmarks)
    thorax = thoracic_center(resting_landmarks)
    pelvis = pelvis_center(resting_landmarks)
    ankle = ankle_center(resting_landmarks)
    layers = _build_rest_phase1_layers(resting_landmarks, view=view)

    return {
        "landmarks": serialize_named_points(named_landmarks),
        "highlighted_points": serialize_named_points(
            {
                "neck_center": neck,
                "thoracic_center": thorax,
                "pelvis_center": pelvis,
                "ankle_center": ankle,
            }
        ),
        "reference_lines": _flatten_reference_lines(layers),
        "metrics": serialize_metric_snapshot(metrics),
        "metric_details": _metric_debug_details(metrics),
        "layers": layers,
        "available_layers": list(REST_PHASE1_FULL_LAYERS[view]),
        "overlay_modes": {
            "readable": list(REST_PHASE1_READABLE_LAYERS[view]),
            "full": list(REST_PHASE1_FULL_LAYERS[view]),
        },
        "default_overlay_mode": "readable",
        "view": view,
    }


@dataclass(slots=True)
class RestPhase1Pipeline:
    """Run the legacy rest pipeline for each required static posture view."""

    rest_pipeline: RestAnalysisPipeline

    def analyze(
        self,
        images: dict[str, UploadedStaticImage],
        *,
        include_placeholders: bool,
    ) -> dict[str, object]:
        """Analyze the front, side and back posture images."""
        metrics_by_view: dict[str, dict[str, object]] = {}
        debug_by_view: dict[str, dict[str, object]] = {}
        for view in ("front", "side", "back"):
            result = self.rest_pipeline.analyze_image_bytes(
                images[view].payload,
                view=view,
                include_placeholders=include_placeholders,
            )
            pose_result = self.rest_pipeline.pose_extractor.extract_from_image_bytes(images[view].payload)
            selected_metrics = _with_phase1_metric_metadata(
                view,
                select_rest_phase1_metrics(view, result.metrics),
            )
            metrics_by_view[view] = {
                "pose": result.pose,
                "metrics": selected_metrics,
            }
            debug_by_view[view] = _build_rest_phase1_debug(pose_result, view=view, metrics=selected_metrics)

        return {
            "status": "success",
            "metrics_by_view": metrics_by_view,
            "debug_by_view": debug_by_view,
        }
