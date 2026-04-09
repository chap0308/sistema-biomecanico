"""Resting-posture orchestration pipeline."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isnan
from pathlib import Path
from typing import Any, Sequence

import cv2

from biomechanics.models import BiomechanicsMetric
from biomechanics.resting_metrics import compute_resting_metrics
from detection.deficiencies import detect_rest_deficiencies
from detection.findings import detect_rest_findings
from orchestration.rest_temporal import aggregate_metric_series, sample_video_frames
from orchestration.view_metric_policy import (
    NOT_APPLICABLE_STATUS,
    filter_metrics_for_view,
    normalize_rest_view,
)
from pose.mediapipe_pose import MediaPipePoseExtractor, PoseExtractionError
from pose.schemas import PoseExtractionResult


@dataclass(slots=True)
class RestPipelineResult:
    """Serializable resting-analysis payload prepared for the API layer."""

    analysis_type: str
    status: str
    view: str
    capture_mode: str
    pipeline_version: str
    pose: dict[str, object]
    metrics: dict[str, dict[str, object]]
    findings: dict[str, object]
    deficiencies: dict[str, object]


@dataclass(slots=True)
class RestAnalysisPipeline:
    """Coordinate pose extraction, metric calculation and descriptive grouping layers."""

    pose_extractor: MediaPipePoseExtractor
    pipeline_version: str = "rest-v2"

    def analyze_image_bytes(
        self,
        image_bytes: bytes,
        *,
        view: str = "front",
        include_placeholders: bool = True,
    ) -> RestPipelineResult:
        """Run the full resting-posture pipeline for a single image."""
        normalized_view = normalize_rest_view(view)
        pose_result = self.pose_extractor.extract_from_image_bytes(image_bytes)
        metrics = self._compute_metrics(
            pose_result.resting_landmarks,
            include_placeholders=include_placeholders,
        )
        return self._build_result(
            pose_results=[pose_result],
            metrics=metrics,
            view=normalized_view,
            capture_mode="single_image",
            temporal_metadata=None,
        )

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
        """Run the rest pipeline over a short static video by aggregating sampled frames."""
        normalized_view = normalize_rest_view(view)
        path = Path(video_path)
        frames = sample_video_frames(path, max_frames=max_frames, frame_step=frame_step)
        if not frames:
            raise PoseExtractionError(f"No readable frames were sampled from video: {path}")
        return self.analyze_frame_arrays(
            frames,
            view=normalized_view,
            include_placeholders=include_placeholders,
            capture_mode="static_video",
            aggregation=aggregation,
            reject_outliers=reject_outliers,
        )

    def analyze_frame_arrays(
        self,
        frames: Sequence[Any],
        *,
        view: str = "front",
        include_placeholders: bool = True,
        capture_mode: str = "multi_frame_sequence",
        aggregation: str = "median",
        reject_outliers: bool = True,
    ) -> RestPipelineResult:
        """Run the rest pipeline on multiple in-memory frames and aggregate the metrics."""
        normalized_view = normalize_rest_view(view)
        if not frames:
            raise ValueError("frames must include at least one image.")

        pose_results: list[PoseExtractionResult] = []
        failures = 0
        last_error: Exception | None = None

        for frame in frames:
            try:
                pose_results.append(self._extract_pose_from_frame(frame))
            except PoseExtractionError as exc:
                failures += 1
                last_error = exc

        if not pose_results:
            if last_error is not None:
                raise PoseExtractionError(str(last_error)) from last_error
            raise PoseExtractionError("No valid pose detections were produced from the provided frames.")

        metric_series = [
            self._compute_metrics(result.resting_landmarks, include_placeholders=include_placeholders)
            for result in pose_results
        ]
        metrics = (
            aggregate_metric_series(
                metric_series,
                strategy=aggregation,
                reject_outliers=reject_outliers,
            )
            if len(metric_series) > 1
            else metric_series[0]
        )
        temporal_metadata = {
            "input_frame_count": len(frames),
            "successful_frame_count": len(pose_results),
            "failed_frame_count": failures,
            "aggregation": aggregation,
            "outlier_rejection": reject_outliers,
        }
        return self._build_result(
            pose_results=pose_results,
            metrics=metrics,
            view=normalized_view,
            capture_mode=capture_mode,
            temporal_metadata=temporal_metadata,
        )

    @staticmethod
    def _compute_metrics(
        landmarks: Any,
        *,
        include_placeholders: bool,
    ) -> dict[str, BiomechanicsMetric]:
        return compute_resting_metrics(
            landmarks,
            include_placeholders=include_placeholders,
        )

    def _build_result(
        self,
        *,
        pose_results: Sequence[PoseExtractionResult],
        metrics: dict[str, BiomechanicsMetric],
        view: str,
        capture_mode: str,
        temporal_metadata: dict[str, object] | None,
    ) -> RestPipelineResult:
        serialized_metrics = self._serialize_metrics(metrics, view=view)
        findings = detect_rest_findings(serialized_metrics, view=view)
        deficiencies = detect_rest_deficiencies(findings.items, view=view)
        return RestPipelineResult(
            analysis_type="rest",
            status="success",
            view=view,
            capture_mode=capture_mode,
            pipeline_version=self.pipeline_version,
            pose=self._serialize_pose_metadata(pose_results, temporal_metadata=temporal_metadata),
            metrics=serialized_metrics,
            findings=asdict(findings),
            deficiencies=asdict(deficiencies),
        )

    @staticmethod
    def _serialize_pose_metadata(
        pose_results: Sequence[PoseExtractionResult],
        *,
        temporal_metadata: dict[str, object] | None,
    ) -> dict[str, object]:
        """Convert pose metadata to JSON-safe primitives."""
        metadata = pose_results[0].metadata
        payload: dict[str, object] = {
            "detected": True,
            "detector": metadata.detector,
            "image_width": metadata.image_width,
            "image_height": metadata.image_height,
            "landmark_count": metadata.landmark_count,
            "relevant_landmark_count": metadata.relevant_landmark_count,
            "min_visibility": min(result.metadata.min_visibility for result in pose_results),
        }
        if temporal_metadata is not None:
            payload.update(temporal_metadata)
        return payload

    def _extract_pose_from_frame(self, frame: Any) -> PoseExtractionResult:
        extractor = self.pose_extractor
        if hasattr(extractor, "extract_from_image_array"):
            return extractor.extract_from_image_array(frame)

        ok, encoded = cv2.imencode(".jpg", frame)
        if not ok:
            raise PoseExtractionError("Unable to encode frame for pose extraction.")
        return extractor.extract_from_image_bytes(encoded.tobytes())

    @staticmethod
    def _serialize_metrics(
        metrics: dict[str, BiomechanicsMetric],
        *,
        view: str,
    ) -> dict[str, dict[str, object]]:
        """Convert metric dataclasses to JSON-safe dictionaries with view policy applied."""
        output: dict[str, dict[str, object]] = {}
        for name, (metric, is_applicable) in filter_metrics_for_view(metrics, view=view).items():
            serialized_metric = asdict(metric)
            if not is_applicable:
                output[name] = {
                    **serialized_metric,
                    "value": None,
                    "status": NOT_APPLICABLE_STATUS,
                }
                continue

            metric_value = None if isnan(metric.value) else metric.value
            metric_status = metric.status or ("placeholder" if metric_value is None else "computed")
            output[name] = {
                **serialized_metric,
                "value": metric_value,
                "status": metric_status,
            }
        return output


__all__ = ["RestAnalysisPipeline", "RestPipelineResult"]
