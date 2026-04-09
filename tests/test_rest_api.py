"""API tests for grouped image, legacy image and video analysis endpoints."""

from __future__ import annotations

from pathlib import Path
import tempfile

import cv2
import numpy as np
from fastapi.testclient import TestClient

from app.dependencies import get_image_rest_pipeline, get_isa_video_pipeline, get_rest_baseline_pipeline, get_rest_pipeline
from app.main import app
from orchestration.rest_pipeline import RestAnalysisPipeline, RestPipelineResult
from pose.schemas import PoseExtractionMetadata, PoseExtractionResult, PoseLandmark
from biomechanics.models import RestingLandmarks


class _StubImagePipeline:
    def __init__(self) -> None:
        self.captured_groups: list[str] = []

    def analyze(self, request):
        self.captured_groups = list(request.image_groups.keys())
        return {
            "analysis_type": "rest",
            "status": "success",
            "capture_mode": "multipart_image_groups",
            "pipeline_version": "image-rest-v1",
            "requested_groups": self.captured_groups,
            "groups": {
                "rest_phase1": {
                    "status": "success",
                    "metrics_by_view": {
                        "front": {
                            "pose": {
                                "detected": True,
                                "detector": "mediapipe_pose",
                                "image_width": 100,
                                "image_height": 100,
                                "landmark_count": 33,
                                "relevant_landmark_count": 13,
                                "min_visibility": 0.95,
                                "notes": [],
                            },
                            "metrics": {
                                "shoulder_height_difference": {
                                    "name": "shoulder_height_difference",
                                    "value": 0.0,
                                    "plane": "frontal",
                                    "unit": "normalized",
                                    "measurement_type": "direct",
                                    "priority": "P0",
                                    "status": "computed",
                                    "notes": [],
                                }
                            },
                        }
                    },
                }
            },
            "findings": {"status": "pending", "items": [], "ready": False},
            "deficiencies": {"status": "pending", "items": [], "ready": False},
            "triggered_tests": {"status": "pending", "items": [], "ready": False},
        }


class _StubRestPipeline:
    def analyze_image_bytes(
        self,
        image_bytes: bytes,
        *,
        view: str = "front",
        include_placeholders: bool = True,
    ) -> RestPipelineResult:
        _ = (image_bytes, include_placeholders)
        return self._build_result(view=view, capture_mode="single_image")

    def analyze_video_path(
        self,
        video_path: str | Path,
        *,
        view: str = "front",
        include_placeholders: bool = True,
        max_frames: int = 9,
        frame_step: int = 5,
        aggregation: str = "median",
        reject_outliers: bool = True,
    ) -> RestPipelineResult:
        _ = (video_path, include_placeholders, max_frames, frame_step, aggregation, reject_outliers)
        return self._build_result(
            view=view,
            capture_mode="static_video",
            pose_extra={
                "input_frame_count": 9,
                "successful_frame_count": 9,
                "failed_frame_count": 0,
                "aggregation": aggregation,
                "outlier_rejection": reject_outliers,
            },
        )

    @staticmethod
    def _build_result(
        *,
        view: str,
        capture_mode: str,
        pose_extra: dict[str, object] | None = None,
    ) -> RestPipelineResult:
        pose = {
            "detected": True,
            "detector": "mediapipe_pose",
            "image_width": 100,
            "image_height": 100,
            "landmark_count": 33,
            "relevant_landmark_count": 13,
            "min_visibility": 0.95,
        }
        if pose_extra:
            pose.update(pose_extra)
        return RestPipelineResult(
            analysis_type="rest",
            status="success",
            view=view,
            capture_mode=capture_mode,
            pipeline_version="rest-v2",
            pose=pose,
            metrics={
                "shoulder_height_difference": {
                    "name": "shoulder_height_difference",
                    "value": 0.0,
                    "plane": "frontal",
                    "unit": "normalized",
                    "measurement_type": "direct",
                    "priority": "P0",
                    "status": "computed",
                }
            },
            findings={"status": "completed", "items": [], "ready_for_detection": True},
            deficiencies={"status": "completed", "items": [], "ready_for_recommendations": True},
        )


class _StubExtractor:
    def extract_from_image_bytes(self, image_bytes: bytes) -> PoseExtractionResult:
        _ = image_bytes
        resting_landmarks = RestingLandmarks.from_mapping(
            {
                "nose": (0.50, 0.15),
                "left_ear": (0.43, 0.18),
                "right_ear": (0.57, 0.22),
                "left_shoulder": (0.40, 0.24),
                "right_shoulder": (0.60, 0.30),
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


def _make_test_image_bytes() -> bytes:
    image = np.zeros((10, 10, 3), dtype=np.uint8)
    ok, encoded = cv2.imencode(".jpg", image)
    assert ok is True
    return encoded.tobytes()


def _make_test_video_bytes() -> bytes:
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_file:
        tmp_path = Path(tmp_file.name)
    try:
        writer = cv2.VideoWriter(str(tmp_path), cv2.VideoWriter_fourcc(*"mp4v"), 5.0, (16, 16))
        assert writer.isOpened() is True
        for _ in range(3):
            writer.write(np.zeros((16, 16, 3), dtype=np.uint8))
        writer.release()
        return tmp_path.read_bytes()
    finally:
        tmp_path.unlink(missing_ok=True)


def test_grouped_rest_image_endpoint_accepts_named_fields() -> None:
    stub_pipeline = _StubImagePipeline()
    app.dependency_overrides[get_image_rest_pipeline] = lambda: stub_pipeline
    client = TestClient(app)

    response = client.post(
        "/api/v1/analyze/image/rest",
        files={
            "rest_phase1_front": ("front.jpg", _make_test_image_bytes(), "image/jpeg"),
            "rest_phase1_side": ("side.jpg", _make_test_image_bytes(), "image/jpeg"),
            "rest_phase1_back": ("back.jpg", _make_test_image_bytes(), "image/jpeg"),
        },
        data={"include_placeholders": "true"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["capture_mode"] == "multipart_image_groups"
    assert payload["requested_groups"] == ["rest_phase1"]
    assert stub_pipeline.captured_groups == ["rest_phase1"]
    assert "rest_phase1" in payload["groups"]

    app.dependency_overrides.clear()


def test_grouped_rest_image_endpoint_rejects_incomplete_group() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/analyze/image/rest",
        files={"rest_phase1_front": ("front.jpg", _make_test_image_bytes(), "image/jpeg")},
        data={"include_placeholders": "true"},
    )

    assert response.status_code == 400
    assert "Incomplete image group 'rest_phase1'" in response.json()["detail"]


def test_rest_video_endpoint_accepts_video_upload_and_returns_temporal_metadata() -> None:
    app.dependency_overrides[get_rest_pipeline] = lambda: _StubRestPipeline()
    client = TestClient(app)

    response = client.post(
        "/api/v1/analyze/video",
        files={"video": ("rest.mp4", _make_test_video_bytes(), "video/mp4")},
        data={
            "video_analysis_type": "rest",
            "view": "front",
            "include_placeholders": "true",
            "aggregation": "median",
            "frame_step": "5",
            "max_frames": "9",
            "reject_outliers": "true",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["analysis_type"] == "rest"
    assert payload["capture_mode"] == "static_video"
    assert payload["pose"]["successful_frame_count"] == 9
    assert payload["pose"]["aggregation"] == "median"

    app.dependency_overrides.clear()


def test_video_endpoint_rejects_unknown_video_analysis_type() -> None:
    app.dependency_overrides[get_rest_pipeline] = lambda: _StubRestPipeline()
    client = TestClient(app)

    response = client.post(
        "/api/v1/analyze/video",
        files={"video": ("rest.mp4", _make_test_video_bytes(), "video/mp4")},
        data={"video_analysis_type": "unknown_test", "view": "front"},
    )

    assert response.status_code == 400
    assert "Unsupported video_analysis_type" in response.json()["detail"]

    app.dependency_overrides.clear()


def test_legacy_rest_endpoint_remains_available_as_image_alias() -> None:
    app.dependency_overrides[get_rest_pipeline] = lambda: _StubRestPipeline()
    client = TestClient(app)

    response = client.post(
        "/api/v1/analyze/rest",
        files={"image": ("frame.jpg", _make_test_image_bytes(), "image/jpeg")},
        data={"view": "front", "include_placeholders": "true"},
    )

    assert response.status_code == 200
    assert response.json()["capture_mode"] == "single_image"

    app.dependency_overrides.clear()


def test_legacy_rest_endpoint_with_real_pipeline_returns_structured_deficiencies() -> None:
    app.dependency_overrides[get_rest_pipeline] = lambda: RestAnalysisPipeline(pose_extractor=_StubExtractor())
    client = TestClient(app)

    response = client.post(
        "/api/v1/analyze/rest",
        files={"image": ("frame.jpg", _make_test_image_bytes(), "image/jpeg")},
        data={"view": "front", "include_placeholders": "true"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["findings"]["status"] == "completed"
    assert payload["deficiencies"]["status"] == "completed"
    assert payload["deficiencies"]["ready_for_recommendations"] is True

    app.dependency_overrides.clear()


class _StubBaselinePipeline:
    def __init__(self) -> None:
        self.captured_groups: list[str] = []
        self.captured_breathing_filename: str | None = None

    def analyze(self, request):
        self.captured_groups = list(request.image_groups.keys())
        self.captured_breathing_filename = request.breathing_video.filename
        return {
            "analysis_type": "rest_baseline",
            "status": "success",
            "capture_mode": "multipart_image_groups_plus_breathing_video",
            "pipeline_version": "rest-baseline-v1",
            "requested_groups": [*self.captured_groups, "breathing_video"],
            "metrics_by_group": {
                "rest_phase1": {
                    "status": "success",
                    "metrics_by_view": {
                        "front": {
                            "pose": {
                                "detected": True,
                                "detector": "mediapipe_pose",
                                "image_width": 100,
                                "image_height": 100,
                                "landmark_count": 33,
                                "relevant_landmark_count": 13,
                                "min_visibility": 0.95,
                                "notes": [],
                            },
                            "metrics": {},
                        }
                    },
                },
                "breathing": {
                    "status": "success",
                    "pose": {
                        "detected": True,
                        "detector": "mediapipe_pose",
                        "image_width": 100,
                        "image_height": 100,
                        "landmark_count": 33,
                        "relevant_landmark_count": 13,
                        "min_visibility": 0.95,
                        "input_frame_count": 12,
                        "successful_frame_count": 10,
                        "failed_frame_count": 2,
                        "aggregation": "median",
                        "outlier_rejection": True,
                        "notes": [],
                    },
                    "metrics": {
                        "infra_sternal_angle_dynamic": {
                            "name": "infra_sternal_angle_dynamic",
                            "value": None,
                            "plane": "frontal",
                            "unit": "degrees",
                            "measurement_type": "placeholder",
                            "priority": "P1",
                            "status": "placeholder",
                            "notes": [],
                        }
                    },
                    "signals": {
                        "thoracic_state": "undetermined_placeholder",
                        "isa_source_of_truth": "breathing_video",
                        "static_isa_role": "reference_only",
                        "ready_for_clinical_decision": False,
                        "notes": [],
                    },
                },
            },
            "findings_by_group": {
                "rest_phase1": {"status": "completed", "items": [], "ready": True, "baseline_flags": [], "severity_score": 0.0},
                "scapula_rest": {"status": "completed", "items": [], "ready": True, "baseline_flags": [], "severity_score": 0.0},
                "breathing": {"status": "completed", "items": [], "ready": True, "baseline_flags": [], "severity_score": 0.0},
            },
            "deficiencies_by_group": {
                "rest_phase1": {"status": "completed", "items": [], "ready": True, "baseline_flags": [], "severity_score": 0.0},
                "scapula_rest": {"status": "completed", "items": [], "ready": True, "baseline_flags": [], "severity_score": 0.0},
                "breathing": {"status": "completed", "items": [], "ready": True, "baseline_flags": [], "severity_score": 0.0},
            },
            "integrated_findings": {"status": "completed", "items": [], "ready": True, "baseline_flags": [], "severity_score": 0.0},
            "preliminary_deficiencies": {"status": "completed", "items": [], "ready": True, "baseline_flags": [], "severity_score": 0.0},
            "triggered_tests_next": {"status": "completed", "items": [], "ready": True, "baseline_flags": [], "severity_score": 0.0},
            "baseline_scapular_state": {"status": "completed"},
            "baseline_scapular_asymmetry": {"status": "completed", "metrics": {}},
            "baseline_scapular_proxy_metrics": {"status": "completed", "metrics": {}},
            "baseline_scapula_context": {"elevation_asymmetry": False, "protraction_bias": "none", "winging_suspected": False, "rotation_asymmetry": False},
        }



class _StubIsaVideoPipeline:
    def __init__(self) -> None:
        self.captured_isa_filename: str | None = None
        self.captured_breathing_filename: str | None = None

    def analyze(self, request):
        self.captured_isa_filename = request.isa_image.filename
        self.captured_breathing_filename = request.breathing_video.filename
        return {
            "analysis_type": "isa_video",
            "status": "success",
            "capture_mode": "multipart_isa_image_plus_breathing_video",
            "pipeline_version": "isa-video-v1",
            "requested_groups": ["isa", "breathing_video"],
            "metrics_by_group": {
                "isa": {
                    "status": "success",
                    "pose": {
                        "detected": True,
                        "detector": "mediapipe_pose",
                        "image_width": 100,
                        "image_height": 100,
                        "landmark_count": 33,
                        "relevant_landmark_count": 13,
                        "min_visibility": 0.95,
                        "notes": [],
                    },
                    "metrics": {
                        "infra_sternal_angle": {
                            "name": "infra_sternal_angle",
                            "value": None,
                            "plane": "frontal",
                            "unit": "degrees",
                            "measurement_type": "placeholder",
                            "priority": "P1",
                            "status": "placeholder",
                            "notes": [],
                        }
                    },
                },
                "breathing": {
                    "status": "success",
                    "pose": {
                        "detected": True,
                        "detector": "mediapipe_pose",
                        "image_width": 100,
                        "image_height": 100,
                        "landmark_count": 33,
                        "relevant_landmark_count": 13,
                        "min_visibility": 0.95,
                        "input_frame_count": 12,
                        "successful_frame_count": 10,
                        "failed_frame_count": 2,
                        "aggregation": "median",
                        "outlier_rejection": True,
                        "notes": [],
                    },
                    "metrics": {
                        "infra_sternal_angle_dynamic": {
                            "name": "infra_sternal_angle_dynamic",
                            "value": None,
                            "plane": "frontal",
                            "unit": "degrees",
                            "measurement_type": "placeholder",
                            "priority": "P1",
                            "status": "placeholder",
                            "notes": [],
                        }
                    },
                    "signals": {
                        "thoracic_state": "undetermined_placeholder",
                        "isa_source_of_truth": "breathing_video",
                        "static_isa_role": "reference_only",
                        "ready_for_clinical_decision": False,
                        "notes": [],
                    },
                },
            },
        }


def test_rest_baseline_endpoint_accepts_grouped_images_plus_breathing_video() -> None:
    stub_pipeline = _StubBaselinePipeline()
    app.dependency_overrides[get_rest_baseline_pipeline] = lambda: stub_pipeline
    client = TestClient(app)

    response = client.post(
        "/api/v1/analyze/rest/baseline",
        files={
            "rest_phase1_front": ("front.jpg", _make_test_image_bytes(), "image/jpeg"),
            "rest_phase1_side": ("side.jpg", _make_test_image_bytes(), "image/jpeg"),
            "rest_phase1_back": ("back.jpg", _make_test_image_bytes(), "image/jpeg"),
            "face_front_face": ("face.jpg", _make_test_image_bytes(), "image/jpeg"),
            "foot_triptych_front": ("feet-front.jpg", _make_test_image_bytes(), "image/jpeg"),
            "foot_triptych_back": ("feet-back.jpg", _make_test_image_bytes(), "image/jpeg"),
            "foot_triptych_left_arch": ("left-arch.jpg", _make_test_image_bytes(), "image/jpeg"),
            "foot_triptych_right_arch": ("right-arch.jpg", _make_test_image_bytes(), "image/jpeg"),
            "isa_front_torso": ("isa.jpg", _make_test_image_bytes(), "image/jpeg"),
            "scapula_back_upper_body": ("scapula.jpg", _make_test_image_bytes(), "image/jpeg"),
            "breathing_video": ("breathing.mp4", _make_test_video_bytes(), "video/mp4"),
        },
        data={
            "include_placeholders": "true",
            "aggregation": "median",
            "frame_step": "5",
            "max_frames": "12",
            "reject_outliers": "true",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["analysis_type"] == "rest_baseline"
    assert payload["capture_mode"] == "multipart_image_groups_plus_breathing_video"
    assert payload["requested_groups"][-1] == "breathing_video"
    assert "breathing" in payload["metrics_by_group"]
    assert stub_pipeline.captured_groups == ["rest_phase1", "face", "foot_triptych", "isa", "scapula"]
    assert "scapula_rest" in payload["findings_by_group"]
    assert "scapula_rest" in payload["deficiencies_by_group"]
    assert stub_pipeline.captured_breathing_filename == "breathing.mp4"

    app.dependency_overrides.clear()


def test_rest_baseline_endpoint_rejects_missing_static_groups() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/analyze/rest/baseline",
        files={
            "rest_phase1_front": ("front.jpg", _make_test_image_bytes(), "image/jpeg"),
            "rest_phase1_side": ("side.jpg", _make_test_image_bytes(), "image/jpeg"),
            "rest_phase1_back": ("back.jpg", _make_test_image_bytes(), "image/jpeg"),
            "breathing_video": ("breathing.mp4", _make_test_video_bytes(), "video/mp4"),
        },
    )

    assert response.status_code == 400
    assert "Missing groups" in response.json()["detail"]



def test_isa_video_endpoint_accepts_static_isa_plus_breathing_video() -> None:
    stub_pipeline = _StubIsaVideoPipeline()
    app.dependency_overrides[get_isa_video_pipeline] = lambda: stub_pipeline
    client = TestClient(app)

    response = client.post(
        "/api/v1/analyze/video/isa",
        files={
            "isa_front_torso": ("isa.jpg", _make_test_image_bytes(), "image/jpeg"),
            "breathing_video": ("breathing.mp4", _make_test_video_bytes(), "video/mp4"),
        },
        data={
            "include_placeholders": "true",
            "aggregation": "median",
            "frame_step": "5",
            "max_frames": "12",
            "reject_outliers": "true",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["analysis_type"] == "isa_video"
    assert payload["capture_mode"] == "multipart_isa_image_plus_breathing_video"
    assert payload["requested_groups"] == ["isa", "breathing_video"]
    assert "isa" in payload["metrics_by_group"]
    assert "breathing" in payload["metrics_by_group"]
    assert stub_pipeline.captured_isa_filename == "isa.jpg"
    assert stub_pipeline.captured_breathing_filename == "breathing.mp4"

    app.dependency_overrides.clear()
