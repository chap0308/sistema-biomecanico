"""Tests for the posterior shoulder-abduction movement pipeline."""

from __future__ import annotations

import numpy as np

from biomechanics.movement_metrics import _apply_elevation_onset_consistency_degradation, compute_shoulder_abduction_metrics
from orchestration.movement_pipeline import MovementAnalysisPipeline
from pose.schemas import PoseExtractionMetadata, PoseExtractionResult, PoseLandmark


class _StubMovementExtractor:
    def extract_from_image_array(self, image_array: np.ndarray) -> PoseExtractionResult:
        frame_id = int(image_array[0, 0, 0])
        frames = {
            1: self._landmarks(0.30, 0.30, 0.38, 0.48, 0.62, 0.48),
            2: self._landmarks(0.28, 0.295, 0.30, 0.40, 0.70, 0.40),
            3: self._landmarks(0.25, 0.29, 0.22, 0.32, 0.78, 0.32),
            4: self._landmarks(0.22, 0.285, 0.18, 0.26, 0.82, 0.26),
            5: self._landmarks(0.24, 0.29, 0.24, 0.34, 0.76, 0.34),
            6: self._landmarks(0.27, 0.295, 0.32, 0.40, 0.68, 0.40),
            9: self._landmarks(0.30, 0.30, 0.38, 0.48, 0.62, 0.48, right_elbow_visibility=0.1),
        }
        return frames[frame_id]

    def _landmarks(
        self,
        left_shoulder_y: float,
        right_shoulder_y: float,
        left_elbow_x: float,
        left_elbow_y: float,
        right_elbow_x: float,
        right_elbow_y: float,
        *,
        right_elbow_visibility: float = 0.95,
    ) -> PoseExtractionResult:
        named_landmarks = {
            "left_shoulder": PoseLandmark(x=0.40, y=left_shoulder_y, z=0.0, visibility=0.95, presence=0.99),
            "right_shoulder": PoseLandmark(x=0.60, y=right_shoulder_y, z=0.0, visibility=0.95, presence=0.99),
            "left_elbow": PoseLandmark(x=left_elbow_x, y=left_elbow_y, z=0.0, visibility=0.95, presence=0.99),
            "right_elbow": PoseLandmark(x=right_elbow_x, y=right_elbow_y, z=0.0, visibility=right_elbow_visibility, presence=0.99),
            "left_hip": PoseLandmark(x=0.45, y=0.70, z=0.0, visibility=0.95, presence=0.99),
            "right_hip": PoseLandmark(x=0.55, y=0.70, z=0.0, visibility=0.95, presence=0.99),
        }
        return PoseExtractionResult(
            named_landmarks=named_landmarks,
            resting_landmarks=None,
            metadata=PoseExtractionMetadata(
                detector="mediapipe_pose",
                image_width=640,
                image_height=480,
                landmark_count=33,
                relevant_landmark_count=6,
                min_visibility=min(point.visibility for point in named_landmarks.values()),
            ),
        )


def _frames(*frame_ids: int) -> list[tuple[int, np.ndarray]]:
    return [(frame_id, np.full((2, 2, 3), fill_value=frame_id, dtype=np.uint8)) for frame_id in frame_ids]


def test_movement_pipeline_returns_dynamic_metrics_findings_and_deficiencies() -> None:
    pipeline = MovementAnalysisPipeline(pose_extractor=_StubMovementExtractor())
    prior_analysis = {
        "baseline_scapular_asymmetry": {
            "metrics": {
                "scapular_elevation_difference": {"value": 0.01},
            }
        },
        "baseline_scapular_proxy_metrics": {
            "metrics": {
                "scapula_spine_distance_left": {"value": 0.12},
                "scapula_spine_distance_right": {"value": 0.09},
                "scapular_upward_rotation_left": {"value": 18.0},
                "scapular_upward_rotation_right": {"value": 14.0},
                "winging_index": {"value": 0.01},
            }
        },
    }

    result = pipeline.analyze_indexed_frames(
        _frames(1, 2, 3, 4, 5, 6),
        movement_type="shoulder_abduction",
        prior_analysis=prior_analysis,
    )

    assert result["analysis_type"] == "movement"
    assert result["views"]["back"]["status"] == "processed"
    assert result["movement_phases"]["peak_frame"] == 5
    assert result["metrics"]["humeral_abduction_angle_left"]["value"] > 55.0
    assert result["metrics"]["dynamic_elevation_asymmetry"]["value"] is not None
    assert result["baseline_comparison"]["status"] == "completed"
    finding_ids = {item["id"] for item in result["findings"]["items"]}
    deficiency_ids = {item["id"] for item in result["deficiencies"]["items"]}
    assert "reduced_scapular_contribution_left" in finding_ids
    assert "possible_reduced_scapular_upward_rotation" in deficiency_ids


def test_movement_pipeline_marks_front_view_as_deferred_when_provided() -> None:
    pipeline = MovementAnalysisPipeline(pose_extractor=_StubMovementExtractor())

    result = pipeline.analyze_indexed_frames(
        _frames(1, 2, 3, 4, 5, 6),
        movement_type="shoulder_abduction",
        front_video_path="front.mp4",
    )

    assert result["views"]["front"]["status"] == "received_not_processed_in_iteration"
    assert any("Front video was received" in note for note in result["quality"]["quality_notes"])


def test_movement_pipeline_degrades_gracefully_when_some_frames_are_skipped() -> None:
    pipeline = MovementAnalysisPipeline(pose_extractor=_StubMovementExtractor())

    result = pipeline.analyze_indexed_frames(
        _frames(1, 2, 9, 3, 4, 5, 6),
        movement_type="shoulder_abduction",
    )

    assert result["status"] == "success"
    assert result["views"]["back"]["pose"]["failed_frame_count"] >= 1
    assert result["baseline_comparison"]["status"] == "not_available"
    assert any("skipped" in note for note in result["quality"]["quality_notes"])



def _synthetic_frame_record(
    frame_index: int,
    *,
    humeral_left: float,
    humeral_right: float,
    elevation_left: float,
    elevation_right: float,
    upward_left: float,
    upward_right: float,
    protraction_left: float,
    protraction_right: float,
) -> dict[str, float]:
    return {
        "frame_index": frame_index,
        "min_visibility": 0.95,
        "humeral_abduction_angle_left": humeral_left,
        "humeral_abduction_angle_right": humeral_right,
        "mean_humeral_abduction": (humeral_left + humeral_right) / 2.0,
        "scapular_elevation_dynamic_left": elevation_left,
        "scapular_elevation_dynamic_right": elevation_right,
        "scapular_upward_rotation_dynamic_left": upward_left,
        "scapular_upward_rotation_dynamic_right": upward_right,
        "scapular_internal_rotation_dynamic_left": protraction_left,
        "scapular_internal_rotation_dynamic_right": protraction_right,
    }


def test_onset_metrics_remain_computed_when_clip_includes_visible_start() -> None:
    frame_records = [
        _synthetic_frame_record(index, humeral_left=h_left, humeral_right=h_right, elevation_left=e_left, elevation_right=e_right, upward_left=u_left, upward_right=u_right, protraction_left=p_left, protraction_right=p_right)
        for index, h_left, h_right, e_left, e_right, u_left, u_right, p_left, p_right in [
            (0, 5.0, 4.0, 0.00, 0.00, 0.0, 0.0, 0.00, 0.00),
            (1, 10.0, 8.0, 0.00, 0.00, 0.2, 0.2, 0.00, 0.00),
            (2, 18.0, 15.0, 0.01, 0.01, 0.6, 0.5, 0.01, 0.01),
            (3, 28.0, 24.0, 0.03, 0.02, 1.5, 1.3, 0.02, 0.02),
            (4, 42.0, 38.0, 0.06, 0.05, 3.2, 2.9, 0.04, 0.03),
            (5, 58.0, 53.0, 0.09, 0.08, 5.8, 5.1, 0.06, 0.05),
            (6, 76.0, 70.0, 0.12, 0.10, 8.0, 7.1, 0.07, 0.06),
        ]
    ]

    result = compute_shoulder_abduction_metrics(frame_records)

    assert result["movement_phases"]["movement_start_frame"] > 0
    assert result["metrics"]["elevation_onset_angle_left"]["status"] == "computed"
    assert result["metrics"]["upward_rotation_onset_angle_right"]["status"] == "computed"
    assert "truncated_clip" not in result["metrics"]["elevation_onset_angle_left"]["flags"]


def test_onset_metrics_are_degraded_when_clip_starts_mid_abduction() -> None:
    frame_records = [
        _synthetic_frame_record(index, humeral_left=h_left, humeral_right=h_right, elevation_left=e_left, elevation_right=e_right, upward_left=u_left, upward_right=u_right, protraction_left=p_left, protraction_right=p_right)
        for index, h_left, h_right, e_left, e_right, u_left, u_right, p_left, p_right in [
            (0, 68.0, 62.0, 0.01, 0.01, 1.0, 0.8, 0.01, 0.01),
            (1, 74.0, 68.0, 0.01, 0.01, 1.1, 0.9, 0.01, 0.01),
            (2, 81.0, 74.0, 0.02, 0.02, 1.3, 1.0, 0.02, 0.01),
            (3, 92.0, 85.0, 0.03, 0.03, 2.0, 1.7, 0.03, 0.02),
            (4, 108.0, 99.0, 0.05, 0.04, 3.8, 3.2, 0.05, 0.03),
            (5, 124.0, 114.0, 0.07, 0.06, 5.6, 4.8, 0.07, 0.05),
            (6, 138.0, 128.0, 0.09, 0.08, 7.2, 6.5, 0.08, 0.06),
        ]
    ]

    result = compute_shoulder_abduction_metrics(frame_records)
    elevation_onset = result["metrics"]["elevation_onset_angle_right"]
    upward_onset = result["metrics"]["upward_rotation_onset_angle_left"]

    assert result["movement_phases"]["movement_start_frame"] == 0
    assert result["debug"]["clip_context"]["is_truncated"] is True
    assert elevation_onset["status"] == "low_confidence"
    assert upward_onset["status"] == "low_confidence"
    assert elevation_onset["calculation_status"] == "first_detectable_within_clip"
    assert "truncated_clip" in elevation_onset["flags"]
    assert any("movement already in progress" in note for note in elevation_onset["quality_notes"])
    assert result["key_frames"]["truncated_clip_frame"] == 0



def test_upward_rotation_onset_detects_early_rise_before_late_peak_crossing() -> None:
    frame_records = [
        _synthetic_frame_record(index, humeral_left=h_left, humeral_right=h_right, elevation_left=e_left, elevation_right=e_right, upward_left=u_left, upward_right=u_right, protraction_left=p_left, protraction_right=p_right)
        for index, h_left, h_right, e_left, e_right, u_left, u_right, p_left, p_right in [
            (0, 5.0, 5.0, 0.00, 0.00, 0.0, 0.0, 0.00, 0.00),
            (1, 12.0, 12.0, 0.00, 0.00, 0.1, 0.1, 0.00, 0.00),
            (2, 20.0, 20.0, 0.01, 0.01, 0.4, 0.4, 0.01, 0.01),
            (3, 30.0, 30.0, 0.02, 0.02, 0.9, 0.9, 0.01, 0.01),
            (4, 40.0, 40.0, 0.03, 0.03, 1.2, 1.1, 0.02, 0.02),
            (5, 55.0, 55.0, 0.05, 0.05, 1.6, 1.4, 0.03, 0.03),
            (6, 72.0, 72.0, 0.07, 0.07, 3.5, 3.0, 0.04, 0.04),
        ]
    ]

    result = compute_shoulder_abduction_metrics(frame_records)

    assert result["metrics"]["upward_rotation_onset_angle_left"]["status"] == "computed"
    assert result["metrics"]["upward_rotation_onset_angle_left"]["value"] <= 45.0
    assert result["key_frames"]["left_upward_rotation_onset_frame"] == 4



def test_upward_rotation_onset_is_degraded_when_proxy_lags_far_behind_elevation() -> None:
    frame_records = [
        _synthetic_frame_record(index, humeral_left=h_left, humeral_right=h_right, elevation_left=e_left, elevation_right=e_right, upward_left=u_left, upward_right=u_right, protraction_left=p_left, protraction_right=p_right)
        for index, h_left, h_right, e_left, e_right, u_left, u_right, p_left, p_right in [
            (0, 5.0, 5.0, 0.00, 0.00, 0.0, 0.0, 0.00, 0.00),
            (1, 10.0, 10.0, 0.00, 0.00, 0.0, 0.0, 0.00, 0.00),
            (2, 18.0, 18.0, 0.01, 0.01, 0.0, 0.0, 0.01, 0.01),
            (3, 28.0, 28.0, 0.02, 0.02, 0.0, 0.0, 0.02, 0.02),
            (4, 40.0, 40.0, 0.03, 0.03, 0.0, 0.0, 0.03, 0.03),
            (5, 55.0, 55.0, 0.05, 0.05, 0.0, 0.0, 0.04, 0.04),
            (6, 72.0, 72.0, 0.07, 0.07, 0.0, 0.0, 0.05, 0.05),
            (7, 90.0, 90.0, 0.09, 0.09, 0.0, 0.0, 0.06, 0.06),
            (8, 108.0, 108.0, 0.10, 0.10, 0.0, 0.0, 0.06, 0.06),
            (9, 124.0, 124.0, 0.11, 0.11, 0.0, 0.0, 0.07, 0.07),
            (10, 138.0, 138.0, 0.12, 0.12, 1.2, 1.1, 0.08, 0.08),
            (11, 152.0, 152.0, 0.13, 0.13, 3.4, 3.2, 0.09, 0.09),
        ]
    ]

    result = compute_shoulder_abduction_metrics(frame_records)
    upward_onset = result["metrics"]["upward_rotation_onset_angle_left"]

    assert result["debug"]["clip_context"]["is_truncated"] is False
    assert upward_onset["status"] == "low_confidence"
    assert upward_onset["calculation_status"] == "threshold_limited_proxy_onset"
    assert "late_proxy_onset" in upward_onset["flags"]



def test_short_rest_uses_prior_analysis_as_context_for_onset_confidence() -> None:
    frame_records = [
        _synthetic_frame_record(index, humeral_left=h_left, humeral_right=h_right, elevation_left=e_left, elevation_right=e_right, upward_left=u_left, upward_right=u_right, protraction_left=p_left, protraction_right=p_right)
        for index, h_left, h_right, e_left, e_right, u_left, u_right, p_left, p_right in [
            (0, 5.0, 5.0, 0.00, 0.00, 0.0, 0.0, 0.00, 0.00),
            (1, 14.0, 14.0, 0.01, 0.01, 0.2, 0.2, 0.00, 0.00),
            (2, 28.0, 28.0, 0.03, 0.03, 0.8, 0.8, 0.01, 0.01),
            (3, 44.0, 44.0, 0.06, 0.06, 1.6, 1.6, 0.03, 0.03),
            (4, 62.0, 62.0, 0.09, 0.09, 3.1, 3.1, 0.05, 0.05),
        ]
    ]
    prior_analysis = {
        "scapula": {
            "metrics": {
                "scapular_upward_rotation_left": {"value": 120.0},
                "scapular_upward_rotation_right": {"value": 118.0},
                "winging_index": {"value": 0.2},
            }
        }
    }

    result = compute_shoulder_abduction_metrics(frame_records, prior_analysis=prior_analysis)
    elevation_onset = result["metrics"]["elevation_onset_angle_left"]

    assert result["debug"]["baseline_context"]["has_prior_analysis"] is True
    assert result["debug"]["baseline_context"]["is_short_rest"] is True
    assert elevation_onset["status"] == "computed"
    assert "short_dynamic_rest" in elevation_onset["flags"]
    assert "prior_static_baseline_available" in elevation_onset["flags"]



def test_elevation_onset_is_degraded_when_proxy_lags_far_behind_upward_rotation() -> None:
    elevation_onset = {
        "value": 98.0,
        "status": "computed",
        "confidence": 0.68,
        "quality_notes": [],
        "flags": [],
        "calculation_status": None,
    }
    upward_onset = {
        "value": 42.0,
        "status": "computed",
        "confidence": 0.6,
        "quality_notes": [],
        "flags": [],
        "calculation_status": None,
    }

    _apply_elevation_onset_consistency_degradation(
        elevation_onset,
        upward_payload=upward_onset,
        peak_humeral=132.0,
        clip_context={"is_truncated": False},
    )

    assert elevation_onset["status"] == "low_confidence"
    assert elevation_onset["calculation_status"] == "threshold_limited_proxy_onset"
    assert "elevation_onset_inconsistent" in elevation_onset["flags"]
