"""Typed contracts for the bilateral squat analysis pipeline."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from src.core.ids import stable_id

SquatCaseProfile = Literal["positivo_controlado", "negativo", "no_etiquetado"]
ProtocolReviewStatus = Literal["pendiente", "aceptado", "rechazado"]
RegistrationStatus = Literal["pendiente_revision_protocolo", "listo_para_pose", "rechazado"]

CRITICAL_LANDMARKS: tuple[str, ...] = (
    "left_shoulder",
    "right_shoulder",
    "left_hip",
    "right_hip",
    "left_knee",
    "right_knee",
    "left_ankle",
    "right_ankle",
    "left_heel",
    "right_heel",
    "left_foot_index",
    "right_foot_index",
)

TARGET_FINDINGS: tuple[str, ...] = (
    "inclinacion_lateral_tronco",
    "desplazamiento_lateral_pelvis",
    "valgo_dinamico_visible",
    "asimetria_bilateral_observable",
)


class SquatCaseRecord(BaseModel):
    """Traceable record for one frontal bilateral-squat video."""

    case_id: str
    video_path: str
    participant_code: str | None = None
    profile: SquatCaseProfile = "no_etiquetado"
    intended_findings: list[str] = Field(default_factory=list)
    protocol_review_status: ProtocolReviewStatus = "pendiente"
    exclusion_reason: str | None = None
    view: Literal["anterior"] = "anterior"
    plane: Literal["frontal"] = "frontal"
    load_condition: Literal["sin_carga_externa"] = "sin_carga_externa"

    @field_validator("case_id")
    @classmethod
    def validate_case_id(cls, value: str) -> str:
        """Require a filesystem- and CSV-safe case identifier."""
        normalized = value.strip()
        if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{2,63}", normalized) is None:
            raise ValueError("case_id may only contain letters, numbers, '-' and '_'")
        return normalized

    @field_validator("intended_findings")
    @classmethod
    def validate_intended_findings(cls, values: list[str]) -> list[str]:
        """Reject target labels outside the thesis scope."""
        unknown = sorted(set(values) - set(TARGET_FINDINGS))
        if unknown:
            raise ValueError(f"unsupported intended findings: {', '.join(unknown)}")
        return list(dict.fromkeys(values))

    @field_validator("exclusion_reason")
    @classmethod
    def validate_exclusion_reason(cls, value: str | None) -> str | None:
        """Normalize an optional protocol exclusion reason."""
        return value.strip() or None if value is not None else None

    @model_validator(mode="after")
    def require_rejection_reason(self) -> "SquatCaseRecord":
        """Keep every protocol rejection methodologically traceable."""
        if self.protocol_review_status == "rechazado" and not self.exclusion_reason:
            raise ValueError("exclusion_reason is required when a case is rejected")
        return self


class VideoTechnicalMetadata(BaseModel):
    """Technical properties obtained without biomechanical interpretation."""

    path: str
    suffix: str
    width_px: int = Field(gt=0)
    height_px: int = Field(gt=0)
    fps: float = Field(gt=0)
    frame_count: int = Field(gt=0)
    duration_seconds: float = Field(gt=0)
    first_frame_readable: bool


class SquatRegistrationResult(BaseModel):
    """Baseline output produced before pose extraction starts."""

    schema_version: Literal["1.0"] = "1.0"
    analysis_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    stage: Literal["registro_tecnico"] = "registro_tecnico"
    status: RegistrationStatus
    ready_for_pose: bool
    case: SquatCaseRecord
    video: VideoTechnicalMetadata
    critical_landmarks: list[str] = Field(default_factory=lambda: list(CRITICAL_LANDMARKS))
    target_findings: list[str] = Field(default_factory=lambda: list(TARGET_FINDINGS))
    notes: list[str] = Field(default_factory=list)

    @classmethod
    def from_case(
        cls,
        case: SquatCaseRecord,
        video: VideoTechnicalMetadata,
    ) -> "SquatRegistrationResult":
        """Build a deterministic registration result from a case and video probe."""
        ready_for_pose = case.protocol_review_status == "aceptado"
        if case.protocol_review_status == "rechazado":
            status: RegistrationStatus = "rechazado"
        elif ready_for_pose:
            status = "listo_para_pose"
        else:
            status = "pendiente_revision_protocolo"

        notes = []
        if not ready_for_pose and case.protocol_review_status == "pendiente":
            notes.append(
                "El archivo es legible, pero requiere revisión del protocolo de captura "
                "antes de extraer la pose."
            )
        if case.protocol_review_status == "rechazado" and case.exclusion_reason:
            notes.append(case.exclusion_reason)

        analysis_id = stable_id("squat", f"{case.case_id}:{Path(video.path).resolve()}")
        return cls(
            analysis_id=analysis_id,
            status=status,
            ready_for_pose=ready_for_pose,
            case=case,
            video=video,
            notes=notes,
        )


class SquatPoseArtifacts(BaseModel):
    """Files generated by the temporal pose-extraction stage."""

    landmarks_csv: str
    frame_quality_csv: str
    overlay_video: str
    quality_plot: str
    summary_json: str


class SquatPoseSummary(BaseModel):
    """Aggregate quality indicators for pose extraction from one video."""

    schema_version: Literal["1.0"] = "1.0"
    case_id: str
    stage: Literal["extraccion_pose_2d"] = "extraccion_pose_2d"
    detector: Literal["mediapipe_pose"] = "mediapipe_pose"
    video_path: str
    min_visibility_threshold: float = Field(ge=0.0, le=1.0)
    total_frames: int = Field(ge=0)
    processed_frames: int = Field(ge=0)
    frames_with_pose: int = Field(ge=0)
    valid_frames: int = Field(ge=0)
    processed_frames_percentage: float = Field(ge=0.0, le=100.0)
    valid_frames_percentage: float = Field(ge=0.0, le=100.0)
    mean_detected_keypoints: float = Field(ge=0.0)
    artifacts: SquatPoseArtifacts
