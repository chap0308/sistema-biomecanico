"""Orchestrator for grouped static-image analysis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from api.schemas.image import ImageRestMultipartRequest
from orchestration.image_subpipelines.face_pipeline import FacePipeline
from orchestration.image_subpipelines.foot_triptych_pipeline import FootTriptychPipeline
from orchestration.image_subpipelines.isa_pipeline import IsaPipeline
from orchestration.image_subpipelines.rest_phase1_pipeline import RestPhase1Pipeline
from orchestration.image_subpipelines.scapula_static_pipeline import ScapulaStaticPipeline


@dataclass(slots=True)
class ImageRestPipeline:
    """Coordinate the grouped static-image subpipelines."""

    rest_phase1_pipeline: RestPhase1Pipeline
    face_pipeline: FacePipeline
    foot_triptych_pipeline: FootTriptychPipeline
    isa_pipeline: IsaPipeline
    scapula_pipeline: ScapulaStaticPipeline
    pipeline_version: str = "image-rest-v1"

    def analyze(self, request: ImageRestMultipartRequest) -> dict[str, Any]:
        """Run only the groups explicitly present in the multipart request."""
        groups: dict[str, Any] = {}

        if "rest_phase1" in request.image_groups:
            groups["rest_phase1"] = self.rest_phase1_pipeline.analyze(
                request.image_groups["rest_phase1"],
                include_placeholders=request.include_placeholders,
            )
        if "face" in request.image_groups:
            groups["face"] = self.face_pipeline.analyze(
                request.image_groups["face"],
                include_placeholders=request.include_placeholders,
            )
        if "foot_triptych" in request.image_groups:
            groups["foot_triptych"] = self.foot_triptych_pipeline.analyze(
                request.image_groups["foot_triptych"],
                include_placeholders=request.include_placeholders,
            )
        if "isa" in request.image_groups:
            groups["isa"] = self.isa_pipeline.analyze(
                request.image_groups["isa"],
                include_placeholders=request.include_placeholders,
            )
        if "scapula" in request.image_groups:
            groups["scapula"] = self.scapula_pipeline.analyze(
                request.image_groups["scapula"],
                include_placeholders=request.include_placeholders,
            )

        pending_block = {
            "status": "pending",
            "items": [],
            "ready": False,
        }
        return {
            "analysis_type": "rest",
            "status": "success",
            "capture_mode": "multipart_image_groups",
            "pipeline_version": self.pipeline_version,
            "requested_groups": list(request.image_groups.keys()),
            "groups": groups,
            "findings": pending_block,
            "deficiencies": pending_block,
            "triggered_tests": pending_block,
        }
