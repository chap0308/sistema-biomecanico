"""Integration pipeline for ISA static reference plus breathing video dynamics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from api.schemas.baseline import UploadedVideo
from api.schemas.image import UploadedStaticImage
from api.schemas.isa import IsaVideoMultipartRequest
from orchestration.breathing_baseline_pipeline import BreathingBaselinePipeline
from orchestration.image_subpipelines.isa_pipeline import IsaPipeline


@dataclass(slots=True)
class IsaVideoPipeline:
    """Coordinate the static ISA image with the breathing video in one endpoint."""

    isa_pipeline: IsaPipeline
    breathing_pipeline: BreathingBaselinePipeline
    pipeline_version: str = "isa-video-v1"

    def analyze(self, request: IsaVideoMultipartRequest) -> dict[str, Any]:
        """Run the static ISA reference plus dynamic breathing analysis."""
        metrics_by_group = self.analyze_components(
            isa_image=request.isa_image,
            breathing_video=request.breathing_video,
            include_placeholders=request.include_placeholders,
            aggregation=request.aggregation,
            frame_step=request.frame_step,
            max_frames=request.max_frames,
            reject_outliers=request.reject_outliers,
        )
        return {
            "analysis_type": "isa_video",
            "status": "success",
            "capture_mode": "multipart_isa_image_plus_breathing_video",
            "pipeline_version": self.pipeline_version,
            "requested_groups": ["isa", "breathing_video"],
            "metrics_by_group": metrics_by_group,
        }

    def analyze_components(
        self,
        *,
        isa_image: UploadedStaticImage,
        breathing_video: UploadedVideo,
        include_placeholders: bool,
        aggregation: str,
        frame_step: int,
        max_frames: int,
        reject_outliers: bool,
    ) -> dict[str, Any]:
        """Compute the reusable ISA and breathing metric groups."""
        isa_result = self.isa_pipeline.analyze(
            {"front_torso": isa_image},
            include_placeholders=include_placeholders,
        )
        breathing_result = self.breathing_pipeline.analyze_video_bytes(
            breathing_video.payload,
            filename=breathing_video.filename,
            include_placeholders=include_placeholders,
            aggregation=aggregation,
            frame_step=frame_step,
            max_frames=max_frames,
            reject_outliers=reject_outliers,
        )
        return {
            "isa": isa_result,
            "breathing": breathing_result,
        }
