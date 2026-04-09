"""Schemas and multipart parsing helpers for ISA plus breathing video analysis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, Any

from fastapi import File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field

from api.schemas.baseline import UploadedVideo
from api.schemas.image import IsaGroupResponse, ProcessingMetadataResponse, UploadedStaticImage

_VIDEO_CONTENT_TYPES = {"video/mp4", "video/quicktime", "video/x-msvideo", "video/x-matroska", "video/webm"}


@dataclass(slots=True, frozen=True)
class IsaVideoMultipartRequest:
    """Normalized grouped request consumed by the ISA-plus-breathing orchestrator."""

    isa_image: UploadedStaticImage
    breathing_video: UploadedVideo
    include_placeholders: bool = True
    aggregation: str = "median"
    frame_step: int = 5
    max_frames: int = 12
    reject_outliers: bool = True

    @classmethod
    async def as_form(
        cls,
        isa_front_torso: Annotated[UploadFile, File()],
        breathing_video: Annotated[UploadFile, File()],
        include_placeholders: Annotated[bool, Form()] = True,
        aggregation: Annotated[str, Form()] = "median",
        frame_step: Annotated[int, Form()] = 5,
        max_frames: Annotated[int, Form()] = 12,
        reject_outliers: Annotated[bool, Form()] = True,
    ) -> "IsaVideoMultipartRequest":
        """Parse the dedicated ISA multipart contract."""
        if not isa_front_torso.content_type or not isa_front_torso.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Field 'isa_front_torso' must be uploaded as an image.",
            )
        if not breathing_video.content_type or breathing_video.content_type not in _VIDEO_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Field 'breathing_video' must be uploaded as a supported video file.",
            )
        if aggregation not in {"mean", "median"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Field 'aggregation' must be either 'mean' or 'median'.",
            )
        if frame_step <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Field 'frame_step' must be greater than 0.",
            )
        if max_frames <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Field 'max_frames' must be greater than 0.",
            )

        isa_payload = await isa_front_torso.read()
        breathing_payload = await breathing_video.read()
        return cls(
            isa_image=UploadedStaticImage(
                filename=isa_front_torso.filename or "isa_front_torso.jpg",
                content_type=isa_front_torso.content_type,
                payload=isa_payload,
            ),
            breathing_video=UploadedVideo(
                filename=breathing_video.filename or "breathing_video.mp4",
                content_type=breathing_video.content_type,
                payload=breathing_payload,
            ),
            include_placeholders=include_placeholders,
            aggregation=aggregation,
            frame_step=frame_step,
            max_frames=max_frames,
            reject_outliers=reject_outliers,
        )


class BreathingTimeSeriesFrameResponse(BaseModel):
    """One sampled frame used for breathing debug and temporal plotting."""

    frame_index: int
    isa: float | None = None
    rib_flare_score: float | None = None
    left_costal_margin_angle: float | None = None
    right_costal_margin_angle: float | None = None
    costal_projection_index: float | None = None
    lower_thoracic_width_proxy: float | None = None
    upper_abdominal_width_proxy: float | None = None
    lower_thoracic_excursion: float | None = None
    upper_abdominal_excursion: float | None = None
    thoracic_abdominal_dissociation: float | None = None
    landmarks: dict[str, Any] | None = None
    isa_status: str | None = None
    rib_flare_status: str | None = None
    thoracic_abdominal_status: str | None = None
    isa_confidence: float | None = None
    rib_flare_confidence: float | None = None
    thoracic_abdominal_confidence: float | None = None


class BreathingKeyFramesResponse(BaseModel):
    """Key breathing-cycle frames exposed for debugging and overlays."""

    max_inhalation_frame: int | None = None
    max_exhalation_frame: int | None = None
    rib_flare_persistence_frame: int | None = None
    thoracic_abdominal_exhalation_frame: int | None = None


class BreathingGroupResponse(BaseModel):
    """Dedicated breathing output for the ISA video endpoint."""

    status: str
    pose: ProcessingMetadataResponse
    metrics: dict[str, Any]
    signals: dict[str, object]
    time_series: list[BreathingTimeSeriesFrameResponse] = Field(default_factory=list)
    key_frames: BreathingKeyFramesResponse = Field(default_factory=BreathingKeyFramesResponse)


class IsaVideoMetricsGroupsResponse(BaseModel):
    """Container for ISA image plus breathing video metrics."""

    isa: IsaGroupResponse
    breathing: BreathingGroupResponse


class IsaVideoAnalysisResponse(BaseModel):
    """Response payload for `/analyze/video/isa`."""

    analysis_type: str
    status: str
    capture_mode: str
    pipeline_version: str
    requested_groups: list[str]
    metrics_by_group: IsaVideoMetricsGroupsResponse
