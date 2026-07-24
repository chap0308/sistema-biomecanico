"""Temporal MediaPipe Pose extraction and debug artifacts for squat videos."""

from __future__ import annotations

import csv
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Sequence

import cv2
import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pose.schemas import PoseLandmark
from src.squat.models import SquatPoseArtifacts, SquatPoseSummary
from src.squat.video import probe_video

SQUAT_LANDMARK_INDEXES: dict[str, int] = {
    "nose": 0,
    "left_shoulder": 11,
    "right_shoulder": 12,
    "left_hip": 23,
    "right_hip": 24,
    "left_knee": 25,
    "right_knee": 26,
    "left_ankle": 27,
    "right_ankle": 28,
    "left_heel": 29,
    "right_heel": 30,
    "left_foot_index": 31,
    "right_foot_index": 32,
}

_CORE_REQUIRED = (
    "left_shoulder",
    "right_shoulder",
    "left_hip",
    "right_hip",
    "left_knee",
    "right_knee",
    "left_ankle",
    "right_ankle",
)

_SKELETON_CONNECTIONS = (
    ("left_shoulder", "right_shoulder"),
    ("left_shoulder", "left_hip"),
    ("right_shoulder", "right_hip"),
    ("left_hip", "right_hip"),
    ("left_hip", "left_knee"),
    ("right_hip", "right_knee"),
    ("left_knee", "left_ankle"),
    ("right_knee", "right_ankle"),
    ("left_ankle", "left_heel"),
    ("right_ankle", "right_heel"),
    ("left_heel", "left_foot_index"),
    ("right_heel", "right_foot_index"),
)

_LANDMARK_COLUMNS = (
    "frame_index",
    "timestamp_seconds",
    "landmark",
    "x",
    "y",
    "z",
    "visibility",
    "presence",
)

_QUALITY_COLUMNS = (
    "frame_index",
    "timestamp_seconds",
    "pose_detected",
    "valid_for_analysis",
    "detected_keypoints",
    "minimum_critical_visibility",
    "invalid_reason",
)


@dataclass(slots=True, frozen=True)
class PoseFrameAssessment:
    """Pose and quality decision for one decoded video frame."""

    named_landmarks: dict[str, PoseLandmark]
    all_landmarks: tuple[PoseLandmark, ...]
    pose_detected: bool
    valid_for_analysis: bool
    detected_keypoints: int
    minimum_critical_visibility: float
    invalid_reason: str


def assess_pose_landmarks(
    landmarks: Sequence[Any] | None,
    *,
    min_visibility: float,
) -> PoseFrameAssessment:
    """Convert MediaPipe landmarks and apply the frontal-video validity rule."""
    if not landmarks or len(landmarks) <= max(SQUAT_LANDMARK_INDEXES.values()):
        return PoseFrameAssessment({}, (), False, False, 0, 0.0, "pose_not_detected")

    all_landmarks = tuple(_to_pose_landmark(item) for item in landmarks)
    named = {name: all_landmarks[index] for name, index in SQUAT_LANDMARK_INDEXES.items()}
    detected = sum(point.visibility >= min_visibility for point in named.values())
    minimum_visibility = min(named[name].visibility for name in _CORE_REQUIRED)

    missing_core = [name for name in _CORE_REQUIRED if named[name].visibility < min_visibility]
    distal_left = max(named["left_heel"].visibility, named["left_foot_index"].visibility)
    distal_right = max(named["right_heel"].visibility, named["right_foot_index"].visibility)
    missing_distal = []
    if distal_left < min_visibility:
        missing_distal.append("left_distal_foot")
    if distal_right < min_visibility:
        missing_distal.append("right_distal_foot")

    missing = missing_core + missing_distal
    return PoseFrameAssessment(
        named_landmarks=named,
        all_landmarks=all_landmarks,
        pose_detected=True,
        valid_for_analysis=not missing,
        detected_keypoints=detected,
        minimum_critical_visibility=minimum_visibility,
        invalid_reason=";".join(missing),
    )


def extract_squat_pose_video(
    video_path: str | Path,
    *,
    case_id: str,
    output_dir: str | Path,
    min_visibility: float = 0.5,
    anonymize_face: bool = True,
) -> SquatPoseSummary:
    """Extract pose for every frame and write CSV, overlay, plot and summary artifacts."""
    if not 0.0 <= min_visibility <= 1.0:
        raise ValueError("min_visibility must be between 0 and 1")

    video = probe_video(video_path)
    case_output_dir = Path(output_dir) / case_id
    case_output_dir.mkdir(parents=True, exist_ok=True)
    landmarks_path = case_output_dir / "landmarks.csv"
    quality_path = case_output_dir / "frame_quality.csv"
    overlay_path = case_output_dir / "overlay.mp4"
    review_path = case_output_dir / "review.mp4"
    plot_path = case_output_dir / "pose_quality.png"
    summary_path = case_output_dir / "pose_summary.json"

    capture = cv2.VideoCapture(video.path)
    writer = cv2.VideoWriter(
        str(overlay_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        video.fps,
        (video.width_px, video.height_px),
    )
    review_writer = cv2.VideoWriter(
        str(review_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        video.fps,
        (video.width_px, video.height_px),
    )
    if not capture.isOpened():
        writer.release()
        review_writer.release()
        raise RuntimeError(f"Unable to open squat video for pose extraction: {video.path}")
    if not writer.isOpened():
        capture.release()
        review_writer.release()
        raise RuntimeError(f"Unable to create squat overlay video: {overlay_path}")
    if not review_writer.isOpened():
        capture.release()
        writer.release()
        raise RuntimeError(f"Unable to create squat review video: {review_path}")

    quality_rows: list[dict[str, object]] = []
    processed_frames = 0
    frames_with_pose = 0
    valid_frames = 0
    detected_keypoints_total = 0

    try:
        with landmarks_path.open("w", encoding="utf-8-sig", newline="") as landmark_handle, quality_path.open(
            "w", encoding="utf-8-sig", newline=""
        ) as quality_handle, _create_pose_model() as pose_model:
            landmark_writer = csv.DictWriter(landmark_handle, fieldnames=_LANDMARK_COLUMNS)
            quality_writer = csv.DictWriter(quality_handle, fieldnames=_QUALITY_COLUMNS)
            landmark_writer.writeheader()
            quality_writer.writeheader()

            frame_index = 0
            while True:
                readable, frame_bgr = capture.read()
                if not readable:
                    break
                timestamp_seconds = frame_index / video.fps
                frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
                result = pose_model.process(frame_rgb)
                raw_landmarks = getattr(getattr(result, "pose_landmarks", None), "landmark", None)
                assessment = assess_pose_landmarks(
                    raw_landmarks,
                    min_visibility=min_visibility,
                )

                processed_frames += 1
                frames_with_pose += int(assessment.pose_detected)
                valid_frames += int(assessment.valid_for_analysis)
                detected_keypoints_total += assessment.detected_keypoints

                for name, point in assessment.named_landmarks.items():
                    landmark_writer.writerow(
                        {
                            "frame_index": frame_index,
                            "timestamp_seconds": f"{timestamp_seconds:.6f}",
                            "landmark": name,
                            "x": f"{point.x:.8f}",
                            "y": f"{point.y:.8f}",
                            "z": f"{point.z:.8f}",
                            "visibility": f"{point.visibility:.8f}",
                            "presence": "" if point.presence is None else f"{point.presence:.8f}",
                        }
                    )

                quality_row: dict[str, object] = {
                    "frame_index": frame_index,
                    "timestamp_seconds": f"{timestamp_seconds:.6f}",
                    "pose_detected": assessment.pose_detected,
                    "valid_for_analysis": assessment.valid_for_analysis,
                    "detected_keypoints": assessment.detected_keypoints,
                    "minimum_critical_visibility": f"{assessment.minimum_critical_visibility:.8f}",
                    "invalid_reason": assessment.invalid_reason,
                }
                quality_writer.writerow(quality_row)
                quality_rows.append(quality_row)

                annotated = frame_bgr.copy()
                if anonymize_face:
                    _pixelate_face(annotated, assessment.all_landmarks)
                review_writer.write(annotated)
                _draw_pose_overlay(annotated, assessment, frame_index=frame_index)
                writer.write(annotated)
                frame_index += 1
    finally:
        capture.release()
        writer.release()
        review_writer.release()

    _save_pose_quality_plot(
        quality_rows,
        output_path=plot_path,
        min_visibility=min_visibility,
        case_id=case_id,
    )

    total_frames = video.frame_count
    artifacts = SquatPoseArtifacts(
        landmarks_csv=str(landmarks_path),
        frame_quality_csv=str(quality_path),
        overlay_video=str(overlay_path),
        review_video=str(review_path),
        quality_plot=str(plot_path),
        summary_json=str(summary_path),
    )
    summary = SquatPoseSummary(
        case_id=case_id,
        video_path=video.path,
        min_visibility_threshold=min_visibility,
        total_frames=total_frames,
        processed_frames=processed_frames,
        frames_with_pose=frames_with_pose,
        valid_frames=valid_frames,
        processed_frames_percentage=_percentage(processed_frames, total_frames),
        valid_frames_percentage=_percentage(valid_frames, processed_frames),
        mean_detected_keypoints=(
            detected_keypoints_total / processed_frames if processed_frames else 0.0
        ),
        artifacts=artifacts,
    )
    summary_path.write_text(
        json.dumps(summary.model_dump(mode="json"), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return summary


def _to_pose_landmark(landmark: Any) -> PoseLandmark:
    return PoseLandmark(
        x=float(getattr(landmark, "x", 0.0)),
        y=float(getattr(landmark, "y", 0.0)),
        z=float(getattr(landmark, "z", 0.0)),
        visibility=float(getattr(landmark, "visibility", 0.0)),
        presence=(
            None
            if getattr(landmark, "presence", None) is None
            else float(getattr(landmark, "presence"))
        ),
    )


def _create_pose_model() -> Any:
    try:
        import mediapipe as mp
    except ImportError as exc:
        raise RuntimeError("MediaPipe is required for squat pose extraction") from exc
    return mp.solutions.pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )


def _pixelate_face(image: np.ndarray, landmarks: Sequence[PoseLandmark]) -> None:
    height, width = image.shape[:2]
    face_points = [
        point
        for point in landmarks[:11]
        if point.visibility >= 0.2 and 0.0 <= point.x <= 1.0 and 0.0 <= point.y <= 1.0
    ]
    if face_points:
        xs = [point.x * width for point in face_points]
        ys = [point.y * height for point in face_points]
        face_width = max(20.0, max(xs) - min(xs))
        face_height = max(20.0, max(ys) - min(ys))
        x0 = int(max(0, min(xs) - face_width * 0.45))
        x1 = int(min(width, max(xs) + face_width * 0.45))
        y0 = int(max(0, min(ys) - face_height * 0.75))
        y1 = int(min(height, max(ys) + face_height * 0.8))
    else:
        x0, x1 = int(width * 0.15), int(width * 0.85)
        y0, y1 = 0, int(height * 0.55)
    _pixelate_region(image, x0=x0, y0=y0, x1=x1, y1=y1)


def _pixelate_region(
    image: np.ndarray,
    *,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
) -> None:
    if x1 <= x0 or y1 <= y0:
        return
    region = image[y0:y1, x0:x1]
    if region.size == 0:
        return
    small_width = max(1, (x1 - x0) // 12)
    small_height = max(1, (y1 - y0) // 12)
    reduced = cv2.resize(region, (small_width, small_height), interpolation=cv2.INTER_LINEAR)
    image[y0:y1, x0:x1] = cv2.resize(
        reduced,
        (x1 - x0, y1 - y0),
        interpolation=cv2.INTER_NEAREST,
    )


def _draw_pose_overlay(
    image: np.ndarray,
    assessment: PoseFrameAssessment,
    *,
    frame_index: int,
) -> None:
    height, width = image.shape[:2]
    color = (40, 210, 80) if assessment.valid_for_analysis else (30, 170, 255)
    for start_name, end_name in _SKELETON_CONNECTIONS:
        start = assessment.named_landmarks.get(start_name)
        end = assessment.named_landmarks.get(end_name)
        if start is None or end is None:
            continue
        start_px = (int(round(start.x * width)), int(round(start.y * height)))
        end_px = (int(round(end.x * width)), int(round(end.y * height)))
        cv2.line(image, start_px, end_px, color, 2, cv2.LINE_AA)
    for name, point in assessment.named_landmarks.items():
        point_px = (int(round(point.x * width)), int(round(point.y * height)))
        cv2.circle(image, point_px, 4, color, -1, cv2.LINE_AA)
        if name in {"left_knee", "right_knee", "left_ankle", "right_ankle"}:
            cv2.putText(
                image,
                name.replace("left_", "L ").replace("right_", "R "),
                (point_px[0] + 5, point_px[1] - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.36,
                color,
                1,
                cv2.LINE_AA,
            )
    status = "VALID" if assessment.valid_for_analysis else "REVIEW"
    lines = (
        f"Frame {frame_index} | {status}",
        f"Keypoints: {assessment.detected_keypoints}/{len(SQUAT_LANDMARK_INDEXES)}",
        f"Min visibility: {assessment.minimum_critical_visibility:.2f}",
    )
    panel_height = 68
    overlay = image.copy()
    cv2.rectangle(overlay, (8, 8), (min(width - 8, 285), panel_height + 8), (15, 15, 15), -1)
    cv2.addWeighted(overlay, 0.65, image, 0.35, 0, image)
    for index, line in enumerate(lines):
        cv2.putText(
            image,
            line,
            (16, 28 + index * 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            (245, 245, 245),
            1,
            cv2.LINE_AA,
        )


def _save_pose_quality_plot(
    quality_rows: Sequence[dict[str, object]],
    *,
    output_path: Path,
    min_visibility: float,
    case_id: str,
) -> None:
    frame_indexes = [int(row["frame_index"]) for row in quality_rows]
    visibility = [float(row["minimum_critical_visibility"]) for row in quality_rows]
    detected = [int(row["detected_keypoints"]) for row in quality_rows]
    valid = [bool(row["valid_for_analysis"]) for row in quality_rows]

    figure, axes = plt.subplots(2, 1, figsize=(11, 6), sharex=True, constrained_layout=True)
    axes[0].plot(frame_indexes, visibility, color="#167D8D", linewidth=1.4)
    axes[0].axhline(min_visibility, color="#C2412D", linestyle="--", label="Umbral")
    axes[0].set_ylabel("Visibilidad mínima")
    axes[0].set_ylim(0.0, 1.05)
    axes[0].grid(alpha=0.25)
    axes[0].legend(loc="lower right")

    axes[1].plot(frame_indexes, detected, color="#D88922", linewidth=1.4, label="Puntos detectados")
    invalid_frames = [frame for frame, is_valid in zip(frame_indexes, valid, strict=True) if not is_valid]
    if invalid_frames:
        axes[1].scatter(invalid_frames, [0] * len(invalid_frames), color="#C2412D", s=10, label="No válido")
    axes[1].set_xlabel("Fotograma")
    axes[1].set_ylabel("Puntos clave")
    axes[1].set_ylim(-0.5, len(SQUAT_LANDMARK_INDEXES) + 0.5)
    axes[1].grid(alpha=0.25)
    axes[1].legend(loc="lower right")
    figure.suptitle(f"Calidad de estimación de pose 2D — {case_id}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(figure)


def _percentage(numerator: int, denominator: int) -> float:
    return round((numerator / denominator) * 100.0, 4) if denominator else 0.0


__all__ = [
    "PoseFrameAssessment",
    "SQUAT_LANDMARK_INDEXES",
    "assess_pose_landmarks",
    "extract_squat_pose_video",
]
