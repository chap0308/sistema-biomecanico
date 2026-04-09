"""Unit tests for the thoracic specialty-metric helpers."""

from __future__ import annotations

from pathlib import Path

import cv2

from biomechanics.models import Point2D
from biomechanics.specialty_metrics import (
    compute_costal_projection_index,
    compute_infrasternal_angle,
    compute_thoracic_abdominal_dynamic_metrics,
    estimate_static_infrasternal_angle,
    estimate_static_rib_flare,
    estimate_thoracic_abdominal_frame,
)
from pose.mediapipe_pose import MediaPipePoseExtractor


def test_compute_infrasternal_angle_returns_expected_geometry() -> None:
    angle = compute_infrasternal_angle(
        Point2D(x=-1.0, y=1.0),
        Point2D(x=0.0, y=0.0),
        Point2D(x=1.0, y=1.0),
    )

    assert round(angle, 2) == 90.0


def test_compute_costal_projection_index_returns_positive_proxy() -> None:
    projection_index = compute_costal_projection_index(
        left_point=Point2D(x=0.40, y=0.50),
        right_point=Point2D(x=0.60, y=0.50),
        substernal_vertex=Point2D(x=0.50, y=0.42),
        torso_width=0.35,
    )

    assert projection_index > 0.0


def test_estimate_static_infrasternal_angle_returns_value_for_controlled_asset() -> None:
    image_path = Path("data/images/evaluations/isa/isa-5.JPG")
    image = cv2.imread(str(image_path))
    assert image is not None

    pose_result = MediaPipePoseExtractor().extract_from_image_array(image)
    measurement = estimate_static_infrasternal_angle(image, pose_result=pose_result)

    assert measurement.angle_degrees is not None
    assert 40.0 <= measurement.angle_degrees <= 150.0
    assert measurement.status in {"computed", "low_confidence"}
    assert measurement.confidence > 0.0
    assert measurement.landmarks is not None


def test_estimate_static_rib_flare_returns_proxy_metrics_for_controlled_asset() -> None:
    image_path = Path("data/images/evaluations/isa/isa-5.JPG")
    image = cv2.imread(str(image_path))
    assert image is not None

    pose_result = MediaPipePoseExtractor().extract_from_image_array(image)
    measurement = estimate_static_rib_flare(image, pose_result=pose_result)

    assert measurement.rib_flare_presence_score is not None
    assert 0.0 <= measurement.rib_flare_presence_score <= 1.0
    assert measurement.left_costal_margin_angle is not None
    assert measurement.right_costal_margin_angle is not None
    assert measurement.costal_projection_index is not None
    assert measurement.status in {"computed", "low_confidence"}
    assert measurement.confidence > 0.0



def test_estimate_thoracic_abdominal_frame_returns_proxy_for_video_frame() -> None:
    video_path = Path("data/videos/breathing_cycle_test/respiracion.mp4")
    capture = cv2.VideoCapture(str(video_path))
    ok, frame = capture.read()
    capture.release()
    assert ok is True
    assert frame is not None

    pose_result = MediaPipePoseExtractor().extract_from_image_array(frame)
    isa_measurement = estimate_static_infrasternal_angle(frame, pose_result=pose_result)
    measurement = estimate_thoracic_abdominal_frame(frame, pose_result=pose_result, isa_measurement=isa_measurement)

    assert measurement.thoracic_width_proxy is not None
    assert measurement.upper_abdominal_width_proxy is not None
    assert measurement.confidence > 0.0


def test_compute_thoracic_abdominal_dynamic_metrics_returns_value_for_controlled_video() -> None:
    video_path = Path("data/videos/breathing_cycle_test/respiracion.mp4")
    capture = cv2.VideoCapture(str(video_path))
    frames = []
    for _ in range(6):
        ok, frame = capture.read()
        if not ok or frame is None:
            break
        frames.append(frame)
    capture.release()
    assert frames

    extractor = MediaPipePoseExtractor()
    measurements = []
    for index, frame in enumerate(frames):
        pose_result = extractor.extract_from_image_array(frame)
        isa_measurement = estimate_static_infrasternal_angle(frame, pose_result=pose_result)
        measurement = estimate_thoracic_abdominal_frame(frame, pose_result=pose_result, isa_measurement=isa_measurement)
        measurement.frame_index = index
        measurements.append(measurement)

    summary = compute_thoracic_abdominal_dynamic_metrics(measurements, total_frame_count=len(frames), reject_outliers=True)

    assert summary.dissociation_score is not None
    assert summary.phase_offset is not None
    assert summary.amplitude_ratio is not None
    assert summary.exhalation_mismatch is not None
