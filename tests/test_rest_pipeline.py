"""Integration tests for the resting-posture pipeline."""

from __future__ import annotations

import numpy as np

from biomechanics.models import RestingLandmarks
from orchestration.rest_pipeline import RestAnalysisPipeline
from pose.schemas import PoseExtractionMetadata, PoseExtractionResult, PoseLandmark


class _StubExtractor:
    def extract_from_image_bytes(self, image_bytes: bytes) -> PoseExtractionResult:
        _ = image_bytes
        return self._build_result(right_shoulder_y=0.30)

    def extract_from_image_array(self, image_array: np.ndarray) -> PoseExtractionResult:
        frame_id = int(image_array[0, 0, 0])
        right_shoulder_y = {
            1: 0.25,
            2: 0.26,
            3: 0.27,
            4: 0.60,
        }.get(frame_id, 0.30)
        return self._build_result(right_shoulder_y=right_shoulder_y)

    @staticmethod
    def _build_result(*, right_shoulder_y: float) -> PoseExtractionResult:
        resting_landmarks = RestingLandmarks.from_mapping(
            {
                "nose": (0.50, 0.15),
                "left_ear": (0.43, 0.18),
                "right_ear": (0.57, 0.22),
                "left_shoulder": (0.40, 0.24),
                "right_shoulder": (0.60, right_shoulder_y),
                "left_elbow": (0.37, 0.45),
                "right_elbow": (0.64, 0.43),
                "left_hip": (0.44, 0.52),
                "right_hip": (0.56, 0.58),
                "left_knee": (0.45, 0.75),
                "right_knee": (0.55, 0.77),
                "left_ankle": (0.46, 0.95),
                "right_ankle": (0.54, 0.95),
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


def test_rest_pipeline_returns_serializable_metrics_findings_and_deficiencies() -> None:
    """Pipeline should wrap pose output, filtered metrics, findings and deficiencies in a JSON-safe structure."""
    pipeline = RestAnalysisPipeline(pose_extractor=_StubExtractor())

    result = pipeline.analyze_image_bytes(b"fake-image", view="front")
    finding_ids = {item["id"] for item in result.findings["items"]}
    deficiency_ids = {item["id"] for item in result.deficiencies["items"]}

    assert result.analysis_type == "rest"
    assert result.status == "success"
    assert result.capture_mode == "single_image"
    assert result.pose["landmark_count"] == 33
    assert result.metrics["shoulder_height_difference"]["status"] == "computed"
    assert result.metrics["thoracic_kyphosis_angle"]["status"] == "not_applicable_for_view"
    assert result.findings["status"] == "completed"
    assert result.findings["ready_for_detection"] is True
    assert result.deficiencies["status"] == "completed"
    assert result.deficiencies["ready_for_recommendations"] is True
    assert "shoulder_height_asymmetry" in finding_ids
    assert "scapular_resting_asymmetry" in deficiency_ids
    assert "forward_head_posture" not in finding_ids


def test_rest_pipeline_side_view_generates_only_sagittal_findings_and_deficiencies() -> None:
    """Side view should produce sagittal groupings and ignore frontal-only deficiencies."""
    pipeline = RestAnalysisPipeline(pose_extractor=_StubExtractor())

    result = pipeline.analyze_image_bytes(b"fake-image", view="side")
    finding_ids = {item["id"] for item in result.findings["items"]}
    deficiency_ids = {item["id"] for item in result.deficiencies["items"]}

    assert result.view == "side"
    assert result.metrics["cranio_shoulder_angle"]["status"] == "computed"
    assert result.metrics["shoulder_height_difference"]["status"] == "not_applicable_for_view"
    assert result.metrics["thoracic_kyphosis_angle"]["status"] in {"placeholder", "low_confidence"}
    assert "thoracic_flattening_bias" not in finding_ids
    assert "thoracic_posture_pattern" not in deficiency_ids
    assert "postural_shoulder_asymmetry" not in deficiency_ids


def test_rest_pipeline_back_view_uses_back_applicability_policy() -> None:
    """Back view should keep frontal/transverse groupings and filter sagittal ones."""
    pipeline = RestAnalysisPipeline(pose_extractor=_StubExtractor())

    result = pipeline.analyze_image_bytes(b"fake-image", view="back")
    finding_ids = {item["id"] for item in result.findings["items"]}
    deficiency_ids = {item["id"] for item in result.deficiencies["items"]}

    assert result.view == "back"
    assert result.metrics["winging_index"]["status"] == "computed"
    assert result.metrics["cranio_shoulder_angle"]["status"] == "not_applicable_for_view"
    assert "scapular_position_asymmetry" in finding_ids
    assert "scapular_resting_asymmetry" in deficiency_ids
    assert "possible_winging_bias" not in finding_ids
    assert "forward_posture_pattern" not in deficiency_ids


def test_rest_pipeline_rejects_unknown_view() -> None:
    """Unsupported view values should fail before producing a payload."""
    pipeline = RestAnalysisPipeline(pose_extractor=_StubExtractor())

    try:
        pipeline.analyze_image_bytes(b"fake-image", view="oblique")
    except ValueError as exc:
        assert "Unsupported rest-analysis view" in str(exc)
    else:
        raise AssertionError("Expected ValueError for unsupported view")


def test_rest_pipeline_can_aggregate_multiple_frames() -> None:
    pipeline = RestAnalysisPipeline(pose_extractor=_StubExtractor())
    frames = [np.full((2, 2, 3), fill_value=value, dtype=np.uint8) for value in (1, 2, 3)]

    result = pipeline.analyze_frame_arrays(frames, view="front", aggregation="median")

    assert result.capture_mode == "multi_frame_sequence"
    assert result.pose["successful_frame_count"] == 3
    assert result.pose["failed_frame_count"] == 0
    assert result.pose["aggregation"] == "median"
    assert result.metrics["shoulder_height_difference"]["status"] == "computed"


def test_rest_pipeline_temporal_aggregation_stays_stable_with_outlier_frame() -> None:
    pipeline = RestAnalysisPipeline(pose_extractor=_StubExtractor())
    frames = [np.full((2, 2, 3), fill_value=value, dtype=np.uint8) for value in (1, 2, 3, 4)]

    result = pipeline.analyze_frame_arrays(
        frames,
        view="front",
        aggregation="median",
        reject_outliers=True,
    )

    metric_value = result.metrics["shoulder_height_difference"]["value"]
    assert isinstance(metric_value, float)
    assert metric_value < 0.1

