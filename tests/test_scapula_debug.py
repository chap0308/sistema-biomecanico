"""Tests for scapula debug layering and metadata."""

from __future__ import annotations

import cv2
import numpy as np

from api.schemas.image import UploadedStaticImage
from biomechanics.models import RestingLandmarks
from orchestration.image_subpipelines.scapula_static_pipeline import ScapulaStaticPipeline
from pose.schemas import PoseExtractionMetadata, PoseExtractionResult, PoseLandmark
from scripts.debug_utils.visualization import resolve_rest_overlay_layers


class _StubExtractor:
    def extract_from_image_bytes(self, image_bytes: bytes) -> PoseExtractionResult:
        _ = image_bytes
        resting_landmarks = RestingLandmarks.from_mapping(
            {
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
        )
        named_landmarks = {
            name: PoseLandmark(x=point.x, y=point.y, z=(-0.12 if name == "left_shoulder" else 0.12 if name == "right_shoulder" else 0.0), visibility=0.95, presence=0.99)
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
    return UploadedStaticImage(filename="scapula.jpg", content_type="image/jpeg", payload=encoded.tobytes())


def test_scapula_pipeline_builds_layered_debug_payload() -> None:
    pipeline = ScapulaStaticPipeline(pose_extractor=_StubExtractor())
    result = pipeline.analyze({"back_upper_body": _uploaded_image()}, include_placeholders=False)
    debug_payload = result["debug"]

    assert "metric_details" in debug_payload
    assert set(debug_payload["overlay_modes"]) == {"readable", "full"}
    assert "spine_reference" in debug_payload["layers"]
    assert "scapula_distance" in debug_payload["layers"]
    assert "upward_rotation" in debug_payload["layers"]

    readable = resolve_rest_overlay_layers(debug_payload, overlay_mode="readable")
    full = resolve_rest_overlay_layers(debug_payload, overlay_mode="full")

    assert set(readable) == {"spine_reference", "scapula_distance", "upward_rotation"}
    assert set(full) == {"landmarks", "spine_reference", "scapula_distance", "internal_rotation", "upward_rotation"}
