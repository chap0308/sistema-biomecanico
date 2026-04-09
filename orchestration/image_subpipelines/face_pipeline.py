"""Grouped face pipeline."""

from __future__ import annotations

from dataclasses import dataclass

from api.schemas.image import UploadedStaticImage
from biomechanics.face_metrics import compute_face_metrics
from orchestration.image_subpipelines.common import serialize_line, serialize_metric, serialize_metric_snapshot, serialize_named_points, serialize_pose_metadata
from pose.facemesh import FacePoint, MediaPipeFaceMeshExtractor

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


def _build_face_debug(landmarks: dict[int, FacePoint], metrics: dict[str, dict[str, object]]) -> dict[str, object]:
    left_iris = _average_point(landmarks, _LEFT_IRIS)
    right_iris = _average_point(landmarks, _RIGHT_IRIS)
    nose = landmarks[_NOSE_MIDLINE]
    chin = landmarks[_CHIN_MIDLINE]
    return {
        "landmarks": [
            {"x": float(point.x), "y": float(point.y)}
            for _, point in sorted(landmarks.items())
        ],
        "highlighted_points": serialize_named_points(
            {
                "left_iris_center": left_iris,
                "right_iris_center": right_iris,
                "nose_midline": nose,
                "chin_midline": chin,
            }
        ),
        "reference_lines": [
            serialize_line(left_iris, right_iris, label="bipupillary_line"),
            serialize_line(nose, chin, label="mandibular_shift_axis"),
        ],
        "metrics": serialize_metric_snapshot(metrics),
    }


@dataclass(slots=True)
class FacePipeline:
    """Run FaceMesh and compute facial asymmetry metrics."""

    extractor: MediaPipeFaceMeshExtractor

    def analyze(self, images: dict[str, UploadedStaticImage], *, include_placeholders: bool) -> dict[str, object]:
        """Analyze the front face image."""
        _ = include_placeholders
        result = self.extractor.extract_from_image_bytes(images["front_face"].payload)
        metrics = compute_face_metrics(result.landmarks)
        serialized_metrics = {name: serialize_metric(metric) for name, metric in metrics.items()}
        return {
            "status": "success",
            "pose": serialize_pose_metadata(result.metadata),
            "metrics": serialized_metrics,
            "debug": _build_face_debug(result.landmarks, serialized_metrics),
        }
