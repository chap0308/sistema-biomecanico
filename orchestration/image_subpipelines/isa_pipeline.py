"""Grouped infra-sternal-angle pipeline."""

from __future__ import annotations

from dataclasses import dataclass

from api.schemas.image import UploadedStaticImage
from biomechanics.specialty_metrics import (
    IsaMeasurement,
    RibFlareStaticMeasurement,
    compute_infra_sternal_angle_placeholder,
    estimate_static_infrasternal_angle,
    estimate_static_rib_flare,
)
from orchestration.image_subpipelines.common import decode_image_or_raise, serialize_pose_metadata
from pose.mediapipe_pose import MediaPipePoseExtractor, PoseExtractionError


@dataclass(slots=True)
class IsaPipeline:
    """Return the frontal thoracic specialty metrics using a controlled classic-vision heuristic."""

    pose_extractor: MediaPipePoseExtractor

    def analyze(self, images: dict[str, UploadedStaticImage], *, include_placeholders: bool) -> dict[str, object]:
        """Analyze the frontal torso image for static ISA and rib-flare baseline estimates."""
        image_bgr, width, height = decode_image_or_raise(images["front_torso"].payload)
        pose_result = None
        pose_notes: list[str] = []
        try:
            pose_result = self.pose_extractor.extract_from_image_array(image_bgr)
            pose = serialize_pose_metadata(pose_result.metadata, notes=pose_notes)
        except PoseExtractionError:
            pose = {
                "detected": False,
                "detector": "mediapipe_pose",
                "image_width": width,
                "image_height": height,
                "notes": ["Pose ROI fallback was used for thoracic specialty metrics because MediaPipe Pose could not localize the torso."],
            }

        isa_measurement = estimate_static_infrasternal_angle(image_bgr, pose_result=pose_result)
        rib_measurement = estimate_static_rib_flare(image_bgr, pose_result=pose_result)
        metrics: dict[str, dict[str, object]] = {}

        if isa_measurement.angle_degrees is not None or include_placeholders:
            metrics["infra_sternal_angle"] = self._serialize_isa_metric(
                name="infra_sternal_angle",
                measurement=isa_measurement,
            )
            metrics["isa_static_baseline"] = self._serialize_isa_metric(
                name="isa_static_baseline",
                measurement=isa_measurement,
            )
        if rib_measurement.rib_flare_presence_score is not None or include_placeholders:
            metrics.update(self._serialize_rib_metrics(rib_measurement))

        return {
            "status": "success",
            "pose": pose,
            "metrics": metrics,
        }

    def _serialize_isa_metric(self, *, name: str, measurement: IsaMeasurement) -> dict[str, object]:
        value = measurement.angle_degrees
        metric = compute_infra_sternal_angle_placeholder(name=name)
        payload = {
            "name": metric.name,
            "value": value,
            "plane": metric.plane,
            "unit": metric.unit,
            "measurement_type": "specialty_metric",
            "priority": metric.priority,
            "status": measurement.status if value is not None else "placeholder",
            "notes": measurement.quality_notes,
            "confidence": measurement.confidence,
            "quality_notes": measurement.quality_notes,
            "landmarks": None,
            "frame_index": measurement.frame_index,
        }
        if measurement.landmarks is not None:
            payload["landmarks"] = self._serialize_landmarks(measurement.landmarks)
        return payload

    def _serialize_rib_metrics(self, measurement: RibFlareStaticMeasurement) -> dict[str, dict[str, object]]:
        landmarks = self._serialize_landmarks(measurement.landmarks) if measurement.landmarks is not None else None
        return {
            "rib_flare_presence_score": self._build_metric_payload(
                name="rib_flare_presence_score",
                value=measurement.rib_flare_presence_score,
                unit="score",
                confidence=measurement.confidence,
                status=measurement.status,
                quality_notes=measurement.quality_notes,
                landmarks=landmarks,
                frame_index=measurement.frame_index,
            ),
            "rib_flare_asymmetry": self._build_metric_payload(
                name="rib_flare_asymmetry",
                value=measurement.rib_flare_asymmetry,
                unit="degrees",
                confidence=measurement.confidence,
                status=measurement.status,
                quality_notes=measurement.quality_notes,
                landmarks=landmarks,
                frame_index=measurement.frame_index,
            ),
            "left_costal_margin_angle": self._build_metric_payload(
                name="left_costal_margin_angle",
                value=measurement.left_costal_margin_angle,
                unit="degrees",
                confidence=measurement.confidence,
                status=measurement.status,
                quality_notes=measurement.quality_notes,
                landmarks=landmarks,
                frame_index=measurement.frame_index,
            ),
            "right_costal_margin_angle": self._build_metric_payload(
                name="right_costal_margin_angle",
                value=measurement.right_costal_margin_angle,
                unit="degrees",
                confidence=measurement.confidence,
                status=measurement.status,
                quality_notes=measurement.quality_notes,
                landmarks=landmarks,
                frame_index=measurement.frame_index,
            ),
            "costal_projection_index": self._build_metric_payload(
                name="costal_projection_index",
                value=measurement.costal_projection_index,
                unit="index",
                confidence=measurement.confidence,
                status=measurement.status,
                quality_notes=measurement.quality_notes,
                landmarks=landmarks,
                frame_index=measurement.frame_index,
            ),
        }

    def _build_metric_payload(
        self,
        *,
        name: str,
        value: float | None,
        unit: str,
        confidence: float,
        status: str,
        quality_notes: list[str],
        landmarks: dict[str, object] | None,
        frame_index: int | None,
    ) -> dict[str, object]:
        return {
            "name": name,
            "value": value,
            "plane": "frontal",
            "unit": unit,
            "measurement_type": "specialty_metric",
            "priority": "P1",
            "status": status if value is not None else "placeholder",
            "notes": quality_notes,
            "confidence": confidence,
            "quality_notes": quality_notes,
            "landmarks": landmarks,
            "frame_index": frame_index,
        }

    def _serialize_landmarks(self, landmarks) -> dict[str, object]:
        return {
            "left_costal_margin": {
                "x": landmarks.left_costal_margin.x,
                "y": landmarks.left_costal_margin.y,
            },
            "substernal_vertex": {
                "x": landmarks.substernal_vertex.x,
                "y": landmarks.substernal_vertex.y,
            },
            "right_costal_margin": {
                "x": landmarks.right_costal_margin.x,
                "y": landmarks.right_costal_margin.y,
            },
        }
