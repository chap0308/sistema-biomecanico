"""Schemas and multipart parsing helpers for grouped static-image analysis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, Any

from fastapi import File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field


IMAGE_GROUP_FIELD_MAP: dict[str, tuple[str, ...]] = {
    "rest_phase1": ("front", "side", "back"),
    "face": ("front_face",),
    "foot_triptych": ("front", "back", "left_arch", "right_arch"),
    "isa": ("front_torso",),
    "scapula": ("back_upper_body",),
}
"""Canonical multipart field naming convention for `/analyze/image/rest`."""


@dataclass(slots=True, frozen=True)
class UploadedStaticImage:
    """Small immutable representation of one uploaded image."""

    filename: str
    content_type: str
    payload: bytes


@dataclass(slots=True, frozen=True)
class ImageRestMultipartRequest:
    """Normalized grouped request consumed by the image orchestration layer."""

    image_groups: dict[str, dict[str, UploadedStaticImage]]
    include_placeholders: bool = True

    @classmethod
    async def as_form(
        cls,
        include_placeholders: Annotated[bool, Form()] = True,
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
    ) -> "ImageRestMultipartRequest":
        """Parse grouped multipart uploads using explicit field names."""
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

        for group_name, slots in IMAGE_GROUP_FIELD_MAP.items():
            provided_fields = [
                field_name
                for slot in slots
                if (field_name := f"{group_name}_{slot}") in uploads and uploads[field_name] is not None
            ]
            if not provided_fields:
                continue

            missing_fields = [f"{group_name}_{slot}" for slot in slots if uploads[f"{group_name}_{slot}"] is None]
            if missing_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Incomplete image group '{group_name}'. Missing required fields: "
                        f"{', '.join(missing_fields)}."
                    ),
                )

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

        if not image_groups:
            supported_fields = [
                f"{group_name}_{slot}"
                for group_name, slots in IMAGE_GROUP_FIELD_MAP.items()
                for slot in slots
            ]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "At least one complete image group must be provided. "
                    f"Supported multipart fields: {', '.join(supported_fields)}."
                ),
            )

        return cls(image_groups=image_groups, include_placeholders=include_placeholders)


class GroupMetricResponse(BaseModel):
    """Biomechanical metric returned by a grouped static-image pipeline."""

    name: str
    value: float | None
    plane: str
    unit: str
    measurement_type: str
    priority: str
    status: str
    notes: list[str] = Field(default_factory=list)
    confidence: float | None = None
    confidence_base: str | None = None
    quality_notes: list[str] = Field(default_factory=list)
    classification: str | None = None
    flags: list[str] = Field(default_factory=list)
    source_of_truth: str | None = None
    calculation_status: str | None = None
    proxy_type: str | None = None
    anatomical_directness: str | None = None
    landmarks: dict[str, object] | None = None
    frame_index: int | None = None


class ProcessingMetadataResponse(BaseModel):
    """Metadata emitted by the extraction layer for a specific image group."""

    detected: bool = True
    detector: str
    image_width: int
    image_height: int
    landmark_count: int | None = None
    relevant_landmark_count: int | None = None
    min_visibility: float | None = None
    input_frame_count: int | None = None
    successful_frame_count: int | None = None
    failed_frame_count: int | None = None
    aggregation: str | None = None
    outlier_rejection: bool | None = None
    classified_frame_count: int | None = None
    notes: list[str] = Field(default_factory=list)


class PendingBlockResponse(BaseModel):
    """Reserved response block for layers not implemented in this iteration."""

    status: str
    items: list[dict[str, Any]] = Field(default_factory=list)
    ready: bool = False


class RestPhase1ViewResponse(BaseModel):
    """Metrics and pose metadata for one anatomical posture view."""

    pose: ProcessingMetadataResponse
    metrics: dict[str, GroupMetricResponse]


class RestPhase1GroupResponse(BaseModel):
    """Grouped response for the baseline rest posture triad."""

    status: str
    metrics_by_view: dict[str, RestPhase1ViewResponse]
    debug_by_view: dict[str, dict[str, Any]] | None = None


class FaceGroupResponse(BaseModel):
    """Grouped facial analysis output."""

    status: str
    pose: ProcessingMetadataResponse
    metrics: dict[str, GroupMetricResponse]
    debug: dict[str, Any] | None = None


class FootTriptychGroupResponse(BaseModel):
    """Grouped feet output keeping both per-view and aggregate metrics."""

    status: str
    processing_by_view: dict[str, ProcessingMetadataResponse]
    metrics: dict[str, GroupMetricResponse]
    confidence_overall: float | None = None
    foot_triptych_summary: dict[str, Any] | None = None
    debug_by_view: dict[str, dict[str, Any]] | None = None


class IsaGroupResponse(BaseModel):
    """Grouped ISA output."""

    status: str
    pose: ProcessingMetadataResponse
    metrics: dict[str, GroupMetricResponse]


class ScapulaGroupResponse(BaseModel):
    """Grouped static scapular output."""

    status: str
    pose: ProcessingMetadataResponse
    metrics: dict[str, GroupMetricResponse]
    debug: dict[str, Any] | None = None


class ImageRestGroupsResponse(BaseModel):
    """Container for optional grouped image-analysis results."""

    rest_phase1: RestPhase1GroupResponse | None = None
    face: FaceGroupResponse | None = None
    foot_triptych: FootTriptychGroupResponse | None = None
    isa: IsaGroupResponse | None = None
    scapula: ScapulaGroupResponse | None = None


class ImageRestAnalysisResponse(BaseModel):
    """Response payload for `/analyze/image/rest`."""

    analysis_type: str
    status: str
    capture_mode: str
    pipeline_version: str
    requested_groups: list[str]
    groups: ImageRestGroupsResponse
    findings: PendingBlockResponse
    deficiencies: PendingBlockResponse
    triggered_tests: PendingBlockResponse

