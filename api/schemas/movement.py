"""Schemas and multipart parsing helpers for movement video analysis."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Annotated, Any

from fastapi import File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field

from api.schemas.baseline import UploadedVideo

_VIDEO_CONTENT_TYPES = {"video/mp4", "video/quicktime", "video/x-msvideo", "video/x-matroska", "video/webm"}
_SUPPORTED_MOVEMENT_TYPES = {"shoulder_abduction"}


@dataclass(slots=True, frozen=True)
class MovementVideoMultipartRequest:
    """Normalized request consumed by the movement video pipeline."""

    movement_type: str
    video_back: UploadedVideo
    video_front: UploadedVideo | None = None
    prior_analysis: dict[str, Any] | None = None
    include_placeholders: bool = True
    aggregation: str = "median"
    frame_step: int = 2
    max_frames: int = 60
    reject_outliers: bool = True

    @classmethod
    async def as_form(
        cls,
        movement_type: Annotated[str, Form()],
        video_back: Annotated[UploadFile, File()],
        video_front: Annotated[UploadFile | None, File()] = None,
        prior_analysis: Annotated[str | None, Form()] = None,
        include_placeholders: Annotated[bool, Form()] = True,
        aggregation: Annotated[str, Form()] = "median",
        frame_step: Annotated[int, Form()] = 2,
        max_frames: Annotated[int, Form()] = 60,
        reject_outliers: Annotated[bool, Form()] = True,
    ) -> "MovementVideoMultipartRequest":
        """Parse multipart uploads for the dedicated movement endpoint."""
        normalized_movement_type = movement_type.strip().lower()
        if normalized_movement_type not in _SUPPORTED_MOVEMENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Unsupported movement_type '{movement_type}'. "
                    f"Expected one of: {', '.join(sorted(_SUPPORTED_MOVEMENT_TYPES))}."
                ),
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

        for field_name, upload in (("video_back", video_back), ("video_front", video_front)):
            if upload is None:
                continue
            if not upload.content_type or upload.content_type not in _VIDEO_CONTENT_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail=f"Field '{field_name}' must be uploaded as a supported video file.",
                )

        parsed_prior_analysis: dict[str, Any] | None = None
        if prior_analysis:
            try:
                candidate = json.loads(prior_analysis)
            except json.JSONDecodeError as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Field 'prior_analysis' must contain valid JSON when provided.",
                ) from exc
            if not isinstance(candidate, dict):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Field 'prior_analysis' must decode to a JSON object.",
                )
            parsed_prior_analysis = candidate

        back_payload = await video_back.read()
        front_payload = await video_front.read() if video_front is not None else None
        return cls(
            movement_type=normalized_movement_type,
            video_back=UploadedVideo(
                filename=video_back.filename or "movement_back.mp4",
                content_type=video_back.content_type,
                payload=back_payload,
            ),
            video_front=(
                UploadedVideo(
                    filename=video_front.filename or "movement_front.mp4",
                    content_type=video_front.content_type,
                    payload=front_payload or b"",
                )
                if video_front is not None
                else None
            ),
            prior_analysis=parsed_prior_analysis,
            include_placeholders=include_placeholders,
            aggregation=aggregation,
            frame_step=frame_step,
            max_frames=max_frames,
            reject_outliers=reject_outliers,
        )


class MovementResultItemsResponse(BaseModel):
    """Generic result block used by movement findings and deficiencies."""

    status: str
    items: list[dict[str, Any]] = Field(default_factory=list)
    ready: bool = True


class MovementAnalysisResponse(BaseModel):
    """Response payload for `/analyze/video/movement`."""

    analysis_type: str
    status: str
    movement_type: str
    capture_mode: str
    pipeline_version: str
    views: dict[str, Any]
    movement_phases: dict[str, Any]
    metrics: dict[str, Any]
    findings: MovementResultItemsResponse
    deficiencies: MovementResultItemsResponse
    baseline_comparison: dict[str, Any]
    quality: dict[str, Any]
