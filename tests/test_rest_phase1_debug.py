"""Tests for rest_phase1 metric metadata and layered debug overlays."""

from __future__ import annotations

import cv2
import numpy as np

from api.schemas.image import UploadedStaticImage
from biomechanics.models import RestingLandmarks
from orchestration.image_subpipelines.rest_phase1_pipeline import RestPhase1Pipeline
from orchestration.rest_pipeline import RestAnalysisPipeline
from pose.schemas import PoseExtractionMetadata, PoseExtractionResult, PoseLandmark
from scripts.debug_utils.visualization import resolve_rest_overlay_layers


class _StubExtractor:
    def extract_from_image_bytes(self, image_bytes: bytes) -> PoseExtractionResult:
        _ = image_bytes
        resting_landmarks = RestingLandmarks.from_mapping(
            {
                "nose": (0.40, 0.15),
                "left_ear": (0.46, 0.12),
                "right_ear": (0.44, 0.12),
                "left_shoulder": (0.53, 0.23),
                "right_shoulder": (0.48, 0.25),
                "left_elbow": (0.50, 0.38),
                "right_elbow": (0.47, 0.38),
                "left_hip": (0.52, 0.48),
                "right_hip": (0.50, 0.49),
                "left_knee": (0.57, 0.68),
                "right_knee": (0.54, 0.68),
                "left_ankle": (0.60, 0.92),
                "right_ankle": (0.58, 0.92),
            }
        )
        named_landmarks = {
            name: PoseLandmark(x=point.x, y=point.y, z=0.0, visibility=0.95, presence=0.99)
            for name, point in {
                "nose": resting_landmarks.nose,
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
            }.items()
        }
        return PoseExtractionResult(
            named_landmarks=named_landmarks,
            resting_landmarks=resting_landmarks,
            metadata=PoseExtractionMetadata(
                detector="mediapipe_pose",
                image_width=640,
                image_height=480,
                landmark_count=33,
                relevant_landmark_count=13,
                min_visibility=0.95,
            ),
        )


def _uploaded_image() -> UploadedStaticImage:
    image = np.zeros((10, 10, 3), dtype=np.uint8)
    ok, encoded = cv2.imencode(".jpg", image)
    assert ok is True
    return UploadedStaticImage(filename="test.jpg", content_type="image/jpeg", payload=encoded.tobytes())


def test_rest_phase1_pipeline_enriches_metric_metadata_and_debug_details() -> None:
    pipeline = RestPhase1Pipeline(rest_pipeline=RestAnalysisPipeline(pose_extractor=_StubExtractor()))
    image = _uploaded_image()

    result = pipeline.analyze(
        {"front": image, "side": image, "back": image},
        include_placeholders=False,
    )

    front_metric = result["metrics_by_view"]["front"]["metrics"]["shoulder_height_difference"]
    back_metric = result["metrics_by_view"]["back"]["metrics"]["shoulder_height_difference"]
    side_kyphosis = result["metrics_by_view"]["side"]["metrics"]["thoracic_kyphosis_angle"]
    side_debug = result["debug_by_view"]["side"]

    assert front_metric["source_of_truth"] == "front_primary"
    assert back_metric["source_of_truth"] == "back_corroborating"
    assert side_kyphosis["status"] in {"placeholder", "low_confidence"}
    assert side_debug["metric_details"]["thoracic_kyphosis_angle"]["status"] == side_kyphosis["status"]
    assert "layers" in side_debug
    assert set(side_debug["overlay_modes"]) == {"readable", "full"}


def test_resolve_rest_overlay_layers_supports_readable_and_full_modes() -> None:
    debug_payload = {
        "layers": {
            "landmarks": {"points": {"nose": {"x": 0.5, "y": 0.2}}},
            "head_neck": {"reference_lines": [{"label": "head_line", "start": {"x": 0.4, "y": 0.2}, "end": {"x": 0.6, "y": 0.2}}]},
            "torso_pelvis": {"reference_lines": [{"label": "torso_axis", "start": {"x": 0.5, "y": 0.3}, "end": {"x": 0.5, "y": 0.6}}]},
            "shoulder_scapula": {"reference_lines": [{"label": "shoulder_line", "start": {"x": 0.4, "y": 0.3}, "end": {"x": 0.6, "y": 0.3}}]},
            "support_axis": {"reference_lines": [{"label": "pelvis_to_ankle", "start": {"x": 0.5, "y": 0.6}, "end": {"x": 0.55, "y": 0.9}}]},
        },
        "available_layers": ["landmarks", "head_neck", "torso_pelvis", "shoulder_scapula", "support_axis"],
        "overlay_modes": {
            "readable": ["head_neck", "torso_pelvis", "support_axis"],
            "full": ["landmarks", "head_neck", "torso_pelvis", "shoulder_scapula", "support_axis"],
        },
    }

    readable = resolve_rest_overlay_layers(debug_payload, overlay_mode="readable")
    full = resolve_rest_overlay_layers(debug_payload, overlay_mode="full")
    custom = resolve_rest_overlay_layers(debug_payload, overlay_mode="full", enabled_layers={"head_neck", "support_axis"})

    assert set(readable) == {"head_neck", "torso_pelvis", "support_axis"}
    assert set(full) == {"landmarks", "head_neck", "torso_pelvis", "shoulder_scapula", "support_axis"}
    assert set(custom) == {"head_neck", "support_axis"}
