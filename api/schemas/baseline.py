"""Schemas and multipart parsing helpers for the rest baseline endpoint."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, Any

from fastapi import File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field

from api.schemas.image import IMAGE_GROUP_FIELD_MAP, UploadedStaticImage

_VIDEO_CONTENT_TYPES = {"video/mp4", "video/quicktime", "video/x-msvideo", "video/x-matroska", "video/webm"}


@dataclass(slots=True, frozen=True)
class UploadedVideo:
    """Small immutable representation of one uploaded video."""

    filename: str
    content_type: str
    payload: bytes


@dataclass(slots=True, frozen=True)
class RestBaselineMultipartRequest:
    """Normalized grouped request consumed by the rest baseline orchestrator."""

    image_groups: dict[str, dict[str, UploadedStaticImage]]
    breathing_video: UploadedVideo
    include_placeholders: bool = True
    aggregation: str = "median"
    frame_step: int = 5
    max_frames: int = 12
    reject_outliers: bool = True

    @classmethod
    async def as_form(
        cls,
        breathing_video: Annotated[UploadFile, File()],
        include_placeholders: Annotated[bool, Form()] = True,
        aggregation: Annotated[str, Form()] = "median",
        frame_step: Annotated[int, Form()] = 5,
        max_frames: Annotated[int, Form()] = 12,
        reject_outliers: Annotated[bool, Form()] = True,
        rest_phase1_front: Annotated[UploadFile | None, File()] = None,
        rest_phase1_side: Annotated[UploadFile | None, File()] = None,
        rest_phase1_back: Annotated[UploadFile | None, File()] = None,
        face_front_face: Annotated[UploadFile | None, File()] = None,
        foot_triptych_front: Annotated[UploadFile | None, File()] = None,
        foot_triptych_back: Annotated[UploadFile | None, File()] = None,
        foot_triptych_left_arch: Annotated[UploadFile | None, File()] = None,
        foot_triptych_right_arch: Annotated[UploadFile | None, File()] = None,
        isa_front_torso: Annotated[UploadFile | None, File()] = None,
        scapula_back_upper_body: Annotated[UploadFile | None, File()] = None,
    ) -> "RestBaselineMultipartRequest":
        """Parse baseline multipart uploads using explicit image-group field names."""
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

        uploads: dict[str, UploadFile | None] = {
            "rest_phase1_front": rest_phase1_front,
            "rest_phase1_side": rest_phase1_side,
            "rest_phase1_back": rest_phase1_back,
            "face_front_face": face_front_face,
            "foot_triptych_front": foot_triptych_front,
            "foot_triptych_back": foot_triptych_back,
            "foot_triptych_left_arch": foot_triptych_left_arch,
            "foot_triptych_right_arch": foot_triptych_right_arch,
            "isa_front_torso": isa_front_torso,
            "scapula_back_upper_body": scapula_back_upper_body,
        }

        image_groups: dict[str, dict[str, UploadedStaticImage]] = {}
        missing_groups: list[str] = []

        for group_name, slots in IMAGE_GROUP_FIELD_MAP.items():
            missing_fields = [f"{group_name}_{slot}" for slot in slots if uploads[f"{group_name}_{slot}"] is None]
            if missing_fields:
                missing_groups.append(group_name)
                continue

            group_payload: dict[str, UploadedStaticImage] = {}
            for slot in slots:
                upload = uploads[f"{group_name}_{slot}"]
                assert upload is not None
                if not upload.content_type or not upload.content_type.startswith("image/"):
                    raise HTTPException(
                        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                        detail=(
                            f"Field '{group_name}_{slot}' must be uploaded as an image. "
                            "Only image/* content types are supported."
                        ),
                    )
                payload = await upload.read()
                group_payload[slot] = UploadedStaticImage(
                    filename=upload.filename or f"{group_name}_{slot}.jpg",
                    content_type=upload.content_type,
                    payload=payload,
                )
            image_groups[group_name] = group_payload

        if missing_groups:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "The baseline endpoint requires all static image groups. "
                    f"Missing groups: {', '.join(missing_groups)}."
                ),
            )

        video_payload = await breathing_video.read()
        return cls(
            image_groups=image_groups,
            breathing_video=UploadedVideo(
                filename=breathing_video.filename or "breathing_video.mp4",
                content_type=breathing_video.content_type,
                payload=video_payload,
            ),
            include_placeholders=include_placeholders,
            aggregation=aggregation,
            frame_step=frame_step,
            max_frames=max_frames,
            reject_outliers=reject_outliers,
        )


class ResultItemsResponse(BaseModel):
    """Generic block used for findings, deficiencies and triggered tests."""

    status: str
    items: list[dict[str, Any]] = Field(default_factory=list)
    ready: bool = True
    baseline_flags: list[str] = Field(default_factory=list)
    severity_score: float | None = None


class RestBaselineAnalysisResponse(BaseModel):
    """Response payload for `/analyze/rest/baseline`."""

    analysis_type: str
    status: str
    capture_mode: str
    pipeline_version: str
    requested_groups: list[str]
    metrics_by_group: dict[str, Any]
    findings_by_group: dict[str, ResultItemsResponse]
    deficiencies_by_group: dict[str, ResultItemsResponse]
    integrated_findings: ResultItemsResponse
    preliminary_deficiencies: ResultItemsResponse
    triggered_tests_next: ResultItemsResponse
    baseline_scapular_state: dict[str, Any] | None = None
    baseline_scapular_asymmetry: dict[str, Any] | None = None
    baseline_scapular_proxy_metrics: dict[str, Any] | None = None
    baseline_scapula_context: dict[str, Any] | None = None
