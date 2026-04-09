"""Video pipeline for a single rotating rest video covering phase-1 views."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from orchestration.image_subpipelines.rest_phase1_pipeline import select_rest_phase1_metrics
from orchestration.rest_pipeline import RestAnalysisPipeline
from orchestration.rest_temporal import sample_video_frames
from pose.mediapipe_pose import PoseExtractionError

_SIDE_SPAN_THRESHOLD = 0.16


@dataclass(slots=True)
class VideoRestPipeline:
    """Extract front, side and back phase-1 metrics from a single rotating video."""

    rest_pipeline: RestAnalysisPipeline
    pipeline_version: str = "video-rest-v1"

    def analyze_video_path(
        self,
        video_path: str | Path,
        *,
        include_placeholders: bool = True,
        max_frames: int = 18,
        frame_step: int = 10,
        aggregation: str = "median",
        reject_outliers: bool = True,
    ) -> dict[str, Any]:
        """Sample one video, classify frames by view, and aggregate phase-1 metrics."""
        frames = sample_video_frames(Path(video_path), max_frames=max_frames, frame_step=frame_step)
        if not frames:
            raise PoseExtractionError(f"No readable frames were sampled from video: {video_path}")
        return self.analyze_frame_arrays(
            frames,
            include_placeholders=include_placeholders,
            aggregation=aggregation,
            reject_outliers=reject_outliers,
        )

    def analyze_frame_arrays(
        self,
        frames: list[np.ndarray],
        *,
        include_placeholders: bool = True,
        aggregation: str = "median",
        reject_outliers: bool = True,
    ) -> dict[str, Any]:
        """Run the multiview phase-1 analysis from in-memory frames."""
        if not frames:
            raise ValueError("frames must include at least one image.")

        frames_by_view: dict[str, list[np.ndarray]] = {"front": [], "side": [], "back": []}
        failures = 0
        last_error: Exception | None = None

        for frame in frames:
            try:
                pose_result = self.rest_pipeline.pose_extractor.extract_from_image_array(frame)
            except PoseExtractionError as exc:
                failures += 1
                last_error = exc
                continue
            view = self._classify_view(pose_result.named_landmarks)
            frames_by_view[view].append(frame)

        if all(not classified_frames for classified_frames in frames_by_view.values()):
            if last_error is not None:
                raise PoseExtractionError(str(last_error)) from last_error
            raise PoseExtractionError("No valid pose detections were produced from the provided frames.")

        missing_views = [view for view, classified_frames in frames_by_view.items() if not classified_frames]
        if missing_views:
            raise ValueError(
                "The rotating rest video did not provide enough frames for all phase-1 views. "
                f"Missing views: {', '.join(missing_views)}."
            )

        metrics_by_view: dict[str, dict[str, object]] = {}
        for view in ("front", "side", "back"):
            result = self.rest_pipeline.analyze_frame_arrays(
                frames_by_view[view],
                view=view,
                include_placeholders=include_placeholders,
                capture_mode="single_video_multiview",
                aggregation=aggregation,
                reject_outliers=reject_outliers,
            )
            pose = dict(result.pose)
            pose["classified_frame_count"] = len(frames_by_view[view])
            metrics_by_view[view] = {
                "pose": pose,
                "metrics": select_rest_phase1_metrics(view, result.metrics),
            }

        pending_block = {"status": "pending", "items": [], "ready": False}
        return {
            "analysis_type": "rest",
            "status": "success",
            "capture_mode": "single_video_multiview",
            "pipeline_version": self.pipeline_version,
            "requested_groups": ["rest_phase1"],
            "groups": {
                "rest_phase1": {
                    "status": "success",
                    "metrics_by_view": metrics_by_view,
                }
            },
            "findings": pending_block,
            "deficiencies": pending_block,
            "triggered_tests": pending_block,
        }

    @staticmethod
    def _classify_view(named_landmarks: dict[str, Any]) -> str:
        """Classify a frame as front, side or back using shoulder orientation."""
        left_shoulder = named_landmarks["left_shoulder"]
        right_shoulder = named_landmarks["right_shoulder"]
        shoulder_delta = float(left_shoulder.x - right_shoulder.x)
        shoulder_span = abs(shoulder_delta)
        if shoulder_span < _SIDE_SPAN_THRESHOLD:
            return "side"
        return "front" if shoulder_delta > 0 else "back"
