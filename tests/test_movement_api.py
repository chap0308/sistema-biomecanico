"""API tests for the dedicated movement-analysis endpoint."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import cv2
import numpy as np
from fastapi.testclient import TestClient

from app.dependencies import get_movement_pipeline
from app.main import app


class _StubMovementPipeline:
    def __init__(self) -> None:
        self.captured_request = None

    def analyze(self, request):
        self.captured_request = request
        return {
            "analysis_type": "movement",
            "status": "success",
            "movement_type": request.movement_type,
            "capture_mode": "multipart_video_views",
            "pipeline_version": "movement-v1",
            "views": {
                "back": {"status": "processed", "role": "primary"},
                "front": {
                    "status": "received_not_processed_in_iteration" if request.video_front else "not_provided",
                    "role": "optional",
                },
            },
            "movement_phases": {"status": "completed", "peak_frame": 10},
            "metrics": {
                "humeral_abduction_angle_left": {"name": "humeral_abduction_angle_left", "value": 102.0, "status": "computed"},
                "dynamic_elevation_asymmetry": {"name": "dynamic_elevation_asymmetry", "value": 0.04, "status": "computed"},
            },
            "findings": {"status": "completed", "items": [], "ready": True},
            "deficiencies": {"status": "completed", "items": [], "ready": True},
            "baseline_comparison": {"status": "completed" if request.prior_analysis else "not_available", "metrics": {}},
            "quality": {"status": "completed", "quality_notes": []},
        }


def _make_test_video_bytes() -> bytes:
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_file:
        tmp_path = Path(tmp_file.name)
    try:
        writer = cv2.VideoWriter(str(tmp_path), cv2.VideoWriter_fourcc(*"mp4v"), 5.0, (16, 16))
        assert writer.isOpened() is True
        for _ in range(4):
            writer.write(np.zeros((16, 16, 3), dtype=np.uint8))
        writer.release()
        return tmp_path.read_bytes()
    finally:
        tmp_path.unlink(missing_ok=True)


def test_movement_video_endpoint_parses_back_video_and_prior_analysis() -> None:
    stub_pipeline = _StubMovementPipeline()
    app.dependency_overrides[get_movement_pipeline] = lambda: stub_pipeline
    client = TestClient(app)

    prior_analysis = {
        "baseline_scapular_proxy_metrics": {
            "metrics": {
                "winging_index": {"value": 0.02},
            }
        }
    }
    response = client.post(
        "/api/v1/analyze/video/movement",
        files={"video_back": ("back.mp4", _make_test_video_bytes(), "video/mp4")},
        data={
            "movement_type": "shoulder_abduction",
            "prior_analysis": json.dumps(prior_analysis),
            "frame_step": "2",
            "max_frames": "20",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["analysis_type"] == "movement"
    assert payload["movement_type"] == "shoulder_abduction"
    assert stub_pipeline.captured_request is not None
    assert stub_pipeline.captured_request.video_back.filename == "back.mp4"
    assert stub_pipeline.captured_request.prior_analysis == prior_analysis

    app.dependency_overrides.clear()


def test_movement_video_endpoint_accepts_optional_front_video() -> None:
    stub_pipeline = _StubMovementPipeline()
    app.dependency_overrides[get_movement_pipeline] = lambda: stub_pipeline
    client = TestClient(app)

    response = client.post(
        "/api/v1/analyze/video/movement",
        files={
            "video_back": ("back.mp4", _make_test_video_bytes(), "video/mp4"),
            "video_front": ("front.mp4", _make_test_video_bytes(), "video/mp4"),
        },
        data={"movement_type": "shoulder_abduction"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["views"]["front"]["status"] == "received_not_processed_in_iteration"
    assert stub_pipeline.captured_request is not None
    assert stub_pipeline.captured_request.video_front is not None
    assert stub_pipeline.captured_request.video_front.filename == "front.mp4"

    app.dependency_overrides.clear()


def test_movement_video_endpoint_rejects_invalid_prior_analysis_json() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/analyze/video/movement",
        files={"video_back": ("back.mp4", _make_test_video_bytes(), "video/mp4")},
        data={
            "movement_type": "shoulder_abduction",
            "prior_analysis": "{not-json}",
        },
    )

    assert response.status_code == 400
    assert "prior_analysis" in response.json()["detail"]
