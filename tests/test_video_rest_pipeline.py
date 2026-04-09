"""Tests for the single-video multiview rest pipeline."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from orchestration.rest_pipeline import RestAnalysisPipeline
from orchestration.video_rest_pipeline import VideoRestPipeline
from pose.schemas import PoseExtractionMetadata, PoseExtractionResult, PoseLandmark
from biomechanics.models import RestingLandmarks


class _StubExtractor:
    def extract_from_image_array(self, image_array: np.ndarray) -> PoseExtractionResult:
        frame_id = int(image_array[0, 0, 0])
        shoulder_x_by_frame = {
            1: (0.70, 0.38),
            2: (0.69, 0.37),
            3: (0.53, 0.46),
            4: (0.35, 0.66),
            5: (0.36, 0.67),
        }
        left_shoulder_x, right_shoulder_x = shoulder_x_by_frame.get(frame_id, (0.70, 0.38))
        resting_landmarks = RestingLandmarks.from_mapping(
            {
                "nose": (0.50, 0.15),
                "left_ear": (0.43, 0.18),
                "right_ear": (0.57, 0.22),
                "left_shoulder": (left_shoulder_x, 0.24),
                "right_shoulder": (right_shoulder_x, 0.30),
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


def test_video_rest_pipeline_groups_frames_into_front_side_and_back() -> None:
    pipeline = VideoRestPipeline(rest_pipeline=RestAnalysisPipeline(pose_extractor=_StubExtractor()))
    frames = [np.full((2, 2, 3), fill_value=value, dtype=np.uint8) for value in (1, 2, 3, 4, 5)]

    result = pipeline.analyze_frame_arrays(frames, aggregation="median")

    assert result["analysis_type"] == "rest"
    assert result["capture_mode"] == "single_video_multiview"
    assert result["requested_groups"] == ["rest_phase1"]
    rest_phase1 = result["groups"]["rest_phase1"]
    assert set(rest_phase1["metrics_by_view"]) == {"front", "side", "back"}
    assert set(rest_phase1["metrics_by_view"]["front"]["metrics"]) == {
        "shoulder_height_difference",
        "torso_lateral_tilt",
        "pelvic_tilt",
        "head_tilt_angle",
    }
    assert rest_phase1["metrics_by_view"]["side"]["pose"]["classified_frame_count"] == 1
    assert rest_phase1["metrics_by_view"]["back"]["pose"]["classified_frame_count"] == 2


def test_video_rest_pipeline_with_real_video_returns_phase1_views() -> None:
    pipeline = VideoRestPipeline(rest_pipeline=RestAnalysisPipeline(pose_extractor=_StubExtractor()))
    real_pipeline = VideoRestPipeline(rest_pipeline=RestAnalysisPipeline(pose_extractor=__import__('pose.mediapipe_pose', fromlist=['MediaPipePoseExtractor']).MediaPipePoseExtractor()))
    result = real_pipeline.analyze_video_path(Path("data/videos/rest/rest-1.mp4"))

    assert result["capture_mode"] == "single_video_multiview"
    rest_phase1 = result["groups"]["rest_phase1"]
    assert set(rest_phase1["metrics_by_view"]) == {"front", "side", "back"}
    assert set(rest_phase1["metrics_by_view"]["front"]["metrics"]) == {
        "shoulder_height_difference",
        "torso_lateral_tilt",
        "pelvic_tilt",
        "head_tilt_angle",
    }
