"""Tests for the bounded squat explanation contract."""

from __future__ import annotations

from src.squat.contracts import SquatArtifactManifest, SquatCaseReport
from src.squat.explanation import build_case_explanation
from src.squat.models import (
    SquatPoseArtifacts,
    SquatPoseSummary,
    SquatRepetition,
    SquatSegmentationArtifacts,
    SquatSegmentationSummary,
)


def test_explanation_joins_canonical_series_without_recalculating() -> None:
    report = SquatCaseReport(
        case_id="case_explanation_001",
        status="analisis_parcial",
        case_record_path="case_record.json",
        pipeline_version="test",
        artifacts=SquatArtifactManifest(
            frame_quality_csv="frame_quality.csv",
            frame_phases_csv="frame_phases.csv",
            biomechanical_frame_metrics_csv="metrics.csv",
            pose_quality_plot="pose_quality.png",
        ),
    )
    artifacts = {
        "frame_quality.csv": _csv(
            "frame_index,timestamp_seconds,valid_for_analysis,"
            "detected_keypoints,minimum_critical_visibility\n"
            "0,0.0,True,13,0.95\n"
            "1,0.1,True,13,0.90\n"
            "2,0.2,False,9,0.30\n"
            "3,0.3,True,13,0.92\n"
        ),
        "frame_phases.csv": _csv(
            "frame_index,timestamp_seconds,hip_midpoint_y,"
            "hip_midpoint_y_smoothed,valid_for_analysis,"
            "repetition_index,phase\n"
            "0,0.0,0.40,0.41,True,0,reposo\n"
            "1,0.1,0.50,0.49,True,1,descenso\n"
            "2,0.2,0.60,0.58,False,1,maxima_profundidad\n"
            "3,0.3,0.42,0.43,True,1,cierre\n"
        ),
        "metrics.csv": _csv(
            "frame_index,timestamp_seconds,valid_for_analysis,"
            "repetition_index,phase,trunk_inclination_deg,"
            "pelvis_lateral_shift_pct,left_knee_medial_deviation_pct,"
            "right_knee_medial_deviation_pct,"
            "bilateral_alignment_difference_pct\n"
            "0,0.0,True,0,reposo,1,2,3,4,1\n"
            "1,0.1,True,1,descenso,5,6,7,8,1\n"
            "2,0.2,False,1,maxima_profundidad,,,,,\n"
            "3,0.3,True,1,cierre,9,10,11,12,1\n"
        ),
        "landmarks.csv": _csv(
            "frame_index,landmark,x,y,z,visibility\n"
            "1,left_hip,0.4,0.5,0,0.90\n"
            "1,right_hip,0.6,0.5,0,0.85\n"
            "2,left_hip,0.4,0.6,0,0.40\n"
            "2,right_hip,0.6,0.6,0,0.90\n"
            "3,left_hip,0.4,0.4,0,0.80\n"
            "3,right_hip,0.6,0.4,0,0.95\n"
        ),
    }
    report.artifacts.landmarks_csv = "landmarks.csv"
    report.segmentation = SquatSegmentationSummary(
        case_id=report.case_id,
        landmarks_csv="landmarks.csv",
        frame_quality_csv="frame_quality.csv",
        fps=10,
        total_frames=4,
        repetitions_detected=1,
        repetitions=[
            SquatRepetition(
                repetition_index=1,
                start_frame=1,
                peak_depth_frame=2,
                end_frame=3,
                start_seconds=0.1,
                peak_depth_seconds=0.2,
                end_seconds=0.3,
                descent_duration_seconds=0.1,
                ascent_duration_seconds=0.1,
                total_duration_seconds=0.2,
                peak_hip_midpoint_y=0.58,
                valid_frames_percentage=66.67,
            )
        ],
        artifacts=SquatSegmentationArtifacts(
            frame_phases_csv="frame_phases.csv",
            repetitions_csv="repetitions.csv",
            segmentation_plot="segmentation.png",
            summary_json="segmentation.json",
        ),
    )
    report.pose = SquatPoseSummary(
        case_id=report.case_id,
        video_path="video.mp4",
        min_visibility_threshold=0.5,
        total_frames=4,
        processed_frames=4,
        frames_with_pose=4,
        valid_frames=3,
        processed_frames_percentage=100,
        valid_frames_percentage=75,
        mean_detected_keypoints=12,
        artifacts=SquatPoseArtifacts(
            landmarks_csv="landmarks.csv",
            frame_quality_csv="frame_quality.csv",
            overlay_video="overlay.mp4",
            quality_plot="pose_quality.png",
            summary_json="pose_summary.json",
        ),
    )

    explanation = build_case_explanation(report, artifacts, max_frames=3)

    assert explanation.total_source_frames == 4
    assert explanation.frames_sampled is False
    assert explanation.frames[0].frame_index == 0
    assert explanation.frames[-1].frame_index == 3
    assert explanation.frames[-1].pelvis_lateral_shift_pct == 10
    assert explanation.frames[-1].right_knee_medial_deviation_pct == 12
    assert "pose_quality.png" in {
        artifact.filename for artifact in explanation.artifact_downloads
    }
    left_hip = next(
        item
        for item in explanation.landmark_visibility_summaries
        if item.landmark == "left_hip"
    )
    assert left_hip.mean_visibility == 0.7
    assert left_hip.usable_frames_percentage == 66.67
    assert left_hip.availability == "intermitente"
    peak_frame = next(
        frame for frame in explanation.frames if frame.frame_index == 2
    )
    assert peak_frame.landmark_visibility["left_hip"] == 0.4


def _csv(value: str) -> bytes:
    return value.encode("utf-8")
