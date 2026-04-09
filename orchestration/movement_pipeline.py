"""Movement-analysis orchestration pipeline."""

from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any, Sequence

from api.schemas.movement import MovementVideoMultipartRequest
from biomechanics.movement_metrics import (
    angle_between_vectors,
    compute_shoulder_abduction_metrics,
    point_distance,
)
from detection.movement_deficiencies import detect_movement_deficiencies
from detection.movement_findings import detect_shoulder_abduction_findings
from orchestration.rest_temporal import sample_indexed_video_frames
from pose.mediapipe_pose import PoseExtractionError

_REQUIRED_LANDMARKS = (
    "left_shoulder",
    "right_shoulder",
    "left_elbow",
    "right_elbow",
    "left_hip",
    "right_hip",
)


@dataclass(slots=True)
class MovementAnalysisPipeline:
    """Coordinate pose extraction, dynamic metrics and cautious movement findings."""

    pose_extractor: Any
    pipeline_version: str = "movement-v1"

    def analyze(self, request: MovementVideoMultipartRequest) -> dict[str, Any]:
        """Run the dedicated movement contract from uploaded videos."""
        temp_parent = Path.cwd() / ".tmp" / "movement_uploads"
        temp_parent.mkdir(parents=True, exist_ok=True)
        temp_root = Path(tempfile.mkdtemp(prefix="movement-", dir=str(temp_parent)))
        try:
            back_path = temp_root / Path(request.video_back.filename).name
            back_path.write_bytes(request.video_back.payload)
            front_path: Path | None = None
            if request.video_front is not None:
                front_path = temp_root / Path(request.video_front.filename).name
                front_path.write_bytes(request.video_front.payload)
            return self.analyze_video_paths(
                back_path,
                movement_type=request.movement_type,
                front_video_path=front_path,
                prior_analysis=request.prior_analysis,
                include_placeholders=request.include_placeholders,
                aggregation=request.aggregation,
                frame_step=request.frame_step,
                max_frames=request.max_frames,
                reject_outliers=request.reject_outliers,
            )
        finally:
            shutil.rmtree(temp_root, ignore_errors=True)

    def analyze_video_paths(
        self,
        back_video_path: str | Path,
        *,
        movement_type: str,
        front_video_path: str | Path | None = None,
        prior_analysis: dict[str, Any] | None = None,
        include_placeholders: bool = True,
        aggregation: str = "median",
        frame_step: int = 2,
        max_frames: int = 60,
        reject_outliers: bool = True,
    ) -> dict[str, Any]:
        """Run movement analysis from persisted video paths."""
        if movement_type != "shoulder_abduction":
            raise ValueError("Only movement_type='shoulder_abduction' is implemented in this iteration.")
        indexed_frames = sample_indexed_video_frames(Path(back_video_path), max_frames=max_frames, frame_step=frame_step)
        if not indexed_frames:
            raise PoseExtractionError(f"No readable frames were sampled from video: {back_video_path}")
        return self.analyze_indexed_frames(
            indexed_frames,
            movement_type=movement_type,
            front_video_path=front_video_path,
            prior_analysis=prior_analysis,
            include_placeholders=include_placeholders,
            aggregation=aggregation,
            reject_outliers=reject_outliers,
        )

    def analyze_indexed_frames(
        self,
        indexed_frames: Sequence[tuple[int, Any]],
        *,
        movement_type: str,
        front_video_path: str | Path | None = None,
        prior_analysis: dict[str, Any] | None = None,
        include_placeholders: bool = True,
        aggregation: str = "median",
        reject_outliers: bool = True,
    ) -> dict[str, Any]:
        """Run movement analysis on sampled in-memory frames for testing and orchestration."""
        if movement_type != "shoulder_abduction":
            raise ValueError("Only movement_type='shoulder_abduction' is implemented in this iteration.")
        if not indexed_frames:
            raise ValueError("indexed_frames must include at least one frame.")

        frame_records: list[dict[str, Any]] = []
        failed_frames = 0
        visibility_scores: list[float] = []
        quality_notes: list[str] = []
        last_error: Exception | None = None

        for frame_index, frame in indexed_frames:
            try:
                pose_result = self.pose_extractor.extract_from_image_array(frame)
                record = self._frame_record(frame_index, pose_result.named_landmarks)
            except Exception as exc:  # pragma: no cover - exercised via integration path
                failed_frames += 1
                last_error = exc
                continue
            if record is None:
                failed_frames += 1
                continue
            frame_records.append(record)
            visibility_scores.append(record["min_visibility"])

        if not frame_records:
            if last_error is not None:
                raise PoseExtractionError(str(last_error)) from last_error
            raise PoseExtractionError("No valid posterior pose detections were produced from the movement video.")

        if failed_frames:
            quality_notes.append(f"{failed_frames} sampled frames were skipped because key landmarks were missing or low visibility.")
        if front_video_path is not None:
            quality_notes.append("Front video was received but not processed in this first posterior-view iteration.")
        if prior_analysis is None:
            quality_notes.append("No prior_analysis was provided; baseline comparison is limited.")

        movement_output = compute_shoulder_abduction_metrics(
            frame_records,
            prior_analysis=prior_analysis,
            include_placeholders=include_placeholders,
        )
        findings = detect_shoulder_abduction_findings(
            movement_output["metrics"],
            movement_phases=movement_output["movement_phases"],
        )
        deficiencies = detect_movement_deficiencies(findings["items"])

        views = {
            "back": {
                "status": "processed",
                "role": "primary",
                "pose": {
                    "detected": True,
                    "detector": "mediapipe_pose",
                    "input_frame_count": len(indexed_frames),
                    "successful_frame_count": len(frame_records),
                    "failed_frame_count": failed_frames,
                    "aggregation": aggregation,
                    "outlier_rejection": reject_outliers,
                    "min_visibility": min(visibility_scores) if visibility_scores else None,
                    "mean_visibility": mean(visibility_scores) if visibility_scores else None,
                },
                "frame_indices": [record["frame_index"] for record in frame_records],
                "quality_notes": quality_notes,
            },
            "front": self._front_view_payload(front_video_path),
        }

        return {
            "analysis_type": "movement",
            "status": "success",
            "movement_type": movement_type,
            "capture_mode": "multipart_video_views",
            "pipeline_version": self.pipeline_version,
            "views": views,
            "movement_phases": movement_output["movement_phases"],
            "time_series": movement_output["time_series"],
            "key_frames": movement_output["key_frames"],
            "metrics": movement_output["metrics"],
            "findings": findings,
            "deficiencies": deficiencies,
            "baseline_comparison": movement_output["baseline_comparison"],
            "quality": {
                "status": "completed",
                "confidence": min(visibility_scores) if visibility_scores else None,
                "quality_notes": quality_notes,
                "debug": movement_output["debug"],
            },
        }

    def _frame_record(self, frame_index: int, named_landmarks: dict[str, Any]) -> dict[str, Any] | None:
        if any(landmark_name not in named_landmarks for landmark_name in _REQUIRED_LANDMARKS):
            return None
        min_visibility = min(float(named_landmarks[name].visibility) for name in _REQUIRED_LANDMARKS)
        if min_visibility < 0.35:
            return None

        left_shoulder = named_landmarks["left_shoulder"]
        right_shoulder = named_landmarks["right_shoulder"]
        left_elbow = named_landmarks["left_elbow"]
        right_elbow = named_landmarks["right_elbow"]
        left_hip = named_landmarks["left_hip"]
        right_hip = named_landmarks["right_hip"]
        left_wrist = named_landmarks.get("left_wrist")
        right_wrist = named_landmarks.get("right_wrist")

        mid_shoulder = ((left_shoulder.x + right_shoulder.x) / 2.0, (left_shoulder.y + right_shoulder.y) / 2.0)
        mid_hip = ((left_hip.x + right_hip.x) / 2.0, (left_hip.y + right_hip.y) / 2.0)
        torso_axis = (mid_shoulder[0] - mid_hip[0], mid_shoulder[1] - mid_hip[1])
        torso_length = max(point_distance(mid_shoulder, mid_hip), 1e-6)

        humeral_left = self._humeral_abduction_angle(left_shoulder, left_elbow, torso_axis)
        humeral_right = self._humeral_abduction_angle(right_shoulder, right_elbow, torso_axis)
        left_elevation = self._shoulder_elevation_proxy(left_shoulder, left_hip, torso_length)
        right_elevation = self._shoulder_elevation_proxy(right_shoulder, right_hip, torso_length)
        left_upward = self._upward_rotation_proxy(left_shoulder, mid_hip)
        right_upward = self._upward_rotation_proxy(right_shoulder, mid_hip)
        left_protraction = self._lateral_shoulder_offset(left_shoulder, left_hip, torso_length, side="left")
        right_protraction = self._lateral_shoulder_offset(right_shoulder, right_hip, torso_length, side="right")

        return {
            "frame_index": frame_index,
            "min_visibility": min_visibility,
            "humeral_abduction_angle_left": humeral_left,
            "humeral_abduction_angle_right": humeral_right,
            "mean_humeral_abduction": (humeral_left + humeral_right) / 2.0,
            "scapular_elevation_dynamic_left": left_elevation,
            "scapular_elevation_dynamic_right": right_elevation,
            "scapular_upward_rotation_dynamic_left": left_upward,
            "scapular_upward_rotation_dynamic_right": right_upward,
            "scapular_internal_rotation_dynamic_left": left_protraction,
            "scapular_internal_rotation_dynamic_right": right_protraction,
            "landmarks": {
                "left_shoulder": self._serialize_landmark(left_shoulder),
                "right_shoulder": self._serialize_landmark(right_shoulder),
                "left_elbow": self._serialize_landmark(left_elbow),
                "right_elbow": self._serialize_landmark(right_elbow),
                "left_wrist": self._serialize_landmark(left_wrist),
                "right_wrist": self._serialize_landmark(right_wrist),
                "left_hip": self._serialize_landmark(left_hip),
                "right_hip": self._serialize_landmark(right_hip),
                "mid_shoulder": self._serialize_point(mid_shoulder),
                "mid_hip": self._serialize_point(mid_hip),
            },
            "reference_lines": [
                self._line("torso_axis", mid_hip, mid_shoulder),
                self._line("biacromial_line", (left_shoulder.x, left_shoulder.y), (right_shoulder.x, right_shoulder.y)),
                self._line("humerus_axis_left", (left_shoulder.x, left_shoulder.y), (left_elbow.x, left_elbow.y)),
                self._line("humerus_axis_right", (right_shoulder.x, right_shoulder.y), (right_elbow.x, right_elbow.y)),
                self._line("thoracic_midline", mid_shoulder, mid_hip),
            ],
        }

    @staticmethod
    def _humeral_abduction_angle(shoulder: Any, elbow: Any, torso_axis: tuple[float, float]) -> float:
        humerus_axis = (elbow.x - shoulder.x, elbow.y - shoulder.y)
        return max(0.0, 180.0 - angle_between_vectors(humerus_axis, torso_axis))

    @staticmethod
    def _upward_rotation_proxy(shoulder: Any, mid_hip: tuple[float, float]) -> float:
        shoulder_to_trunk = (mid_hip[0] - shoulder.x, mid_hip[1] - shoulder.y)
        return angle_between_vectors(shoulder_to_trunk, (1.0, 0.0))

    @staticmethod
    def _shoulder_elevation_proxy(
        shoulder: Any,
        hip: Any,
        torso_length: float,
    ) -> float:
        return (hip.y - shoulder.y) / torso_length

    @staticmethod
    def _lateral_shoulder_offset(
        shoulder: Any,
        hip: Any,
        torso_length: float,
        *,
        side: str,
    ) -> float:
        if side == "left":
            return (hip.x - shoulder.x) / torso_length
        return (shoulder.x - hip.x) / torso_length

    @staticmethod
    def _front_view_payload(front_video_path: str | Path | None) -> dict[str, Any]:
        if front_video_path is None:
            return {
                "status": "not_provided",
                "role": "optional",
                "quality_notes": [],
            }
        return {
            "status": "received_not_processed_in_iteration",
            "role": "optional",
            "quality_notes": ["Front-view implementation was intentionally deferred for this first delivery."],
        }

    @staticmethod
    def _serialize_landmark(landmark: Any | None) -> dict[str, float] | None:
        if landmark is None:
            return None
        return {
            "x": float(landmark.x),
            "y": float(landmark.y),
            "visibility": float(getattr(landmark, "visibility", 0.0)),
        }

    @staticmethod
    def _serialize_point(point: tuple[float, float]) -> dict[str, float]:
        return {
            "x": float(point[0]),
            "y": float(point[1]),
        }

    @classmethod
    def _line(
        cls,
        label: str,
        start: tuple[float, float],
        end: tuple[float, float],
    ) -> dict[str, Any]:
        return {
            "label": label,
            "start": cls._serialize_point(start),
            "end": cls._serialize_point(end),
        }
