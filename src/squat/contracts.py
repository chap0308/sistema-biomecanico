"""Stable JSON contracts for squat-case registration and reporting."""

from __future__ import annotations

from datetime import date, datetime, timezone
import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.squat.models import (
    CRITICAL_LANDMARKS,
    SquatBiomechanicsSummary,
    SquatFindingsSummary,
    SquatPoseSummary,
    SquatQualityGateSummary,
    SquatRegistrationResult,
    SquatSegmentationSummary,
)

LandmarkAvailabilityCode = Literal["B", "I", "D", "O", "N", "C"]
LightingStatus = Literal["adecuada", "regular", "deficiente", "no_verificada"]
BackgroundStatus = Literal["adecuado", "regular", "deficiente", "no_verificado"]
BodyVisibilityStatus = Literal[
    "completa",
    "parcial_utilizable",
    "insuficiente",
    "no_verificada",
]
OcclusionStatus = Literal["ninguna", "leve", "moderada", "severa", "no_verificada"]
SurfaceStatus = Literal["plana", "no_plana", "no_verificable"]
HeelSupportStatus = Literal["no", "si", "no_verificable"]
HeelContactStatus = Literal[
    "continuo",
    "elevacion_breve",
    "elevacion_evidente_o_sostenida",
    "no_verificable",
]
ReportStatus = Literal[
    "registro_pendiente",
    "registro_rechazado",
    "analisis_parcial",
    "no_apto_para_analisis",
    "analisis_completo",
]
CaptureEvent = Literal["inicio_descenso", "maxima_profundidad", "final_ascenso"]


class SquatManualProtocolReview(BaseModel):
    """Manual Instrument 1 fields that cannot be inferred by the pose model."""

    model_config = ConfigDict(extra="forbid")

    record_date: date | None = None
    video_source: str | None = None
    capture_device: str | None = None
    lighting: LightingStatus = "no_verificada"
    background: BackgroundStatus = "no_verificado"
    body_visibility: BodyVisibilityStatus = "no_verificada"
    occlusions: OcclusionStatus = "no_verificada"
    complete_squat_observable: bool | None = None
    surface: SurfaceStatus = "no_verificable"
    external_heel_support: HeelSupportStatus = "no_verificable"
    apparent_heel_contact: HeelContactStatus = "no_verificable"
    support_condition_compliant: bool | None = None
    plantar_support_observation: str | None = None
    landmark_availability: dict[str, LandmarkAvailabilityCode] = Field(
        default_factory=dict
    )
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None

    @field_validator(
        "video_source",
        "capture_device",
        "plantar_support_observation",
        "reviewed_by",
    )
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        """Normalize blank optional text fields."""
        return value.strip() or None if value is not None else None

    @field_validator("landmark_availability")
    @classmethod
    def validate_landmark_names(
        cls,
        values: dict[str, LandmarkAvailabilityCode],
    ) -> dict[str, LandmarkAvailabilityCode]:
        """Restrict availability codes to the thesis landmark set plus nose."""
        allowed = set(CRITICAL_LANDMARKS) | {"nose"}
        unknown = sorted(set(values) - allowed)
        if unknown:
            raise ValueError(
                "unsupported landmark availability keys: " + ", ".join(unknown)
            )
        return values


class SquatCaseRecordContract(BaseModel):
    """Instrument 1 contract persisted before computational analysis."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"] = "1.0"
    contract: Literal["squat_case_record"] = "squat_case_record"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    registration: SquatRegistrationResult
    manual_protocol_review: SquatManualProtocolReview


class SquatEventCapture(BaseModel):
    """One anonymized visual checkpoint for a detected repetition."""

    model_config = ConfigDict(extra="forbid")

    repetition_index: int = Field(ge=1)
    event: CaptureEvent
    frame_index: int = Field(ge=0)
    timestamp_seconds: float = Field(ge=0.0)
    relative_path: str


class SquatArtifactManifest(BaseModel):
    """Portable relative paths exposed to an API or interface."""

    model_config = ConfigDict(extra="forbid")

    overlay_video: str | None = None
    landmarks_csv: str | None = None
    frame_quality_csv: str | None = None
    pose_quality_plot: str | None = None
    frame_phases_csv: str | None = None
    repetitions_csv: str | None = None
    segmentation_plot: str | None = None
    biomechanical_frame_metrics_csv: str | None = None
    biomechanical_repetition_metrics_csv: str | None = None
    biomechanical_metrics_plot: str | None = None
    rule_evidence_csv: str | None = None
    event_captures: list[SquatEventCapture] = Field(default_factory=list)


class SquatCaseReport(BaseModel):
    """Instrument 2-oriented aggregate consumed by API clients."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"] = "1.0"
    contract: Literal["squat_case_report"] = "squat_case_report"
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    case_id: str
    status: ReportStatus
    case_record_path: str
    pose: SquatPoseSummary | None = None
    segmentation: SquatSegmentationSummary | None = None
    quality: SquatQualityGateSummary | None = None
    biomechanics: SquatBiomechanicsSummary | None = None
    findings: SquatFindingsSummary | None = None
    artifacts: SquatArtifactManifest = Field(default_factory=SquatArtifactManifest)
    pipeline_version: str
    notes: list[str] = Field(default_factory=list)


def write_case_record_contract(
    registration: SquatRegistrationResult,
    output_path: str | Path,
    *,
    manual_review: SquatManualProtocolReview | None = None,
) -> SquatCaseRecordContract:
    """Validate and persist the aggregate Instrument 1 contract."""
    contract = SquatCaseRecordContract(
        registration=registration,
        manual_protocol_review=manual_review or SquatManualProtocolReview(),
    )
    _write_model_json(contract, output_path)
    return contract


def build_case_report(
    case_record_json: str | Path,
    *,
    output_path: str | Path,
    pose: SquatPoseSummary | None = None,
    segmentation: SquatSegmentationSummary | None = None,
    quality: SquatQualityGateSummary | None = None,
    biomechanics: SquatBiomechanicsSummary | None = None,
    findings: SquatFindingsSummary | None = None,
    event_captures: list[SquatEventCapture] | None = None,
    pipeline_version: str = "0.1.0",
) -> SquatCaseReport:
    """Assemble validated stage summaries without recomputing their values."""
    record_path = Path(case_record_json)
    record = SquatCaseRecordContract.model_validate_json(
        record_path.read_text(encoding="utf-8")
    )
    case_id = record.registration.case.case_id
    _require_matching_case_ids(
        case_id,
        pose=pose,
        segmentation=segmentation,
        quality=quality,
        biomechanics=biomechanics,
        findings=findings,
    )
    pose = _portable_pose(pose)
    segmentation = _portable_segmentation(segmentation)
    quality = _portable_quality(quality)
    biomechanics = _portable_biomechanics(biomechanics)
    findings = _portable_findings(findings)

    status, notes = _report_status(
        record,
        pose=pose,
        segmentation=segmentation,
        quality=quality,
        biomechanics=biomechanics,
        findings=findings,
    )
    manifest = _artifact_manifest(
        pose=pose,
        segmentation=segmentation,
        biomechanics=biomechanics,
        findings=findings,
        event_captures=event_captures or [],
    )
    report = SquatCaseReport(
        case_id=case_id,
        status=status,
        case_record_path=record_path.name,
        pose=pose,
        segmentation=segmentation,
        quality=quality,
        biomechanics=biomechanics,
        findings=findings,
        artifacts=manifest,
        pipeline_version=pipeline_version,
        notes=notes,
    )
    _write_model_json(report, output_path)
    return report


def export_contract_schemas(output_dir: str | Path) -> tuple[Path, Path]:
    """Export reproducible JSON Schemas for frontend and API development."""
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    record_path = directory / "squat_case_record.schema.json"
    report_path = directory / "squat_case_report.schema.json"
    record_path.write_text(
        json.dumps(
            SquatCaseRecordContract.model_json_schema(),
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    report_path.write_text(
        json.dumps(
            SquatCaseReport.model_json_schema(),
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return record_path, report_path


def _report_status(
    record: SquatCaseRecordContract,
    *,
    pose: SquatPoseSummary | None,
    segmentation: SquatSegmentationSummary | None,
    quality: SquatQualityGateSummary | None,
    biomechanics: SquatBiomechanicsSummary | None,
    findings: SquatFindingsSummary | None,
) -> tuple[ReportStatus, list[str]]:
    registration = record.registration
    if registration.status == "pendiente_revision_protocolo":
        return "registro_pendiente", [
            "El caso requiere revisión manual del protocolo antes del análisis."
        ]
    if registration.status == "rechazado":
        return "registro_rechazado", list(registration.notes)
    if quality is not None and not quality.eligible_for_analysis:
        return "no_apto_para_analisis", list(quality.exclusion_reasons)
    if all(
        value is not None
        for value in (pose, segmentation, quality, biomechanics, findings)
    ):
        return "analisis_completo", [
            "Los umbrales biomecánicos son provisionales y no son puntos de corte clínicos."
        ]
    return "analisis_parcial", [
        "El reporte conserva únicamente las etapas disponibles del pipeline."
    ]


def _artifact_manifest(
    *,
    pose: SquatPoseSummary | None,
    segmentation: SquatSegmentationSummary | None,
    biomechanics: SquatBiomechanicsSummary | None,
    findings: SquatFindingsSummary | None,
    event_captures: list[SquatEventCapture],
) -> SquatArtifactManifest:
    return SquatArtifactManifest(
        overlay_video=_name(pose.artifacts.overlay_video) if pose else None,
        landmarks_csv=_name(pose.artifacts.landmarks_csv) if pose else None,
        frame_quality_csv=_name(pose.artifacts.frame_quality_csv) if pose else None,
        pose_quality_plot=_name(pose.artifacts.quality_plot) if pose else None,
        frame_phases_csv=(
            _name(segmentation.artifacts.frame_phases_csv) if segmentation else None
        ),
        repetitions_csv=(
            _name(segmentation.artifacts.repetitions_csv) if segmentation else None
        ),
        segmentation_plot=(
            _name(segmentation.artifacts.segmentation_plot) if segmentation else None
        ),
        biomechanical_frame_metrics_csv=(
            _name(biomechanics.artifacts.frame_metrics_csv)
            if biomechanics
            else None
        ),
        biomechanical_repetition_metrics_csv=(
            _name(biomechanics.artifacts.repetition_metrics_csv)
            if biomechanics
            else None
        ),
        biomechanical_metrics_plot=(
            _name(biomechanics.artifacts.metrics_plot) if biomechanics else None
        ),
        rule_evidence_csv=(
            _name(findings.artifacts.rule_evidence_csv) if findings else None
        ),
        event_captures=event_captures,
    )


def _require_matching_case_ids(
    case_id: str,
    **summaries: BaseModel | None,
) -> None:
    mismatched = [
        name
        for name, summary in summaries.items()
        if summary is not None and getattr(summary, "case_id", None) != case_id
    ]
    if mismatched:
        raise ValueError(
            "case_id does not match aggregate summaries: " + ", ".join(mismatched)
        )


def _name(path: str) -> str:
    return Path(path).name


def _portable_pose(summary: SquatPoseSummary | None) -> SquatPoseSummary | None:
    if summary is None:
        return None
    return summary.model_copy(
        update={
            "video_path": _name(summary.video_path),
            "artifacts": summary.artifacts.model_copy(
                update={
                    "landmarks_csv": _name(summary.artifacts.landmarks_csv),
                    "frame_quality_csv": _name(
                        summary.artifacts.frame_quality_csv
                    ),
                    "overlay_video": _name(summary.artifacts.overlay_video),
                    "quality_plot": _name(summary.artifacts.quality_plot),
                    "summary_json": _name(summary.artifacts.summary_json),
                }
            ),
        }
    )


def _portable_segmentation(
    summary: SquatSegmentationSummary | None,
) -> SquatSegmentationSummary | None:
    if summary is None:
        return None
    return summary.model_copy(
        update={
            "landmarks_csv": _name(summary.landmarks_csv),
            "frame_quality_csv": _name(summary.frame_quality_csv),
            "artifacts": summary.artifacts.model_copy(
                update={
                    "frame_phases_csv": _name(
                        summary.artifacts.frame_phases_csv
                    ),
                    "repetitions_csv": _name(
                        summary.artifacts.repetitions_csv
                    ),
                    "segmentation_plot": _name(
                        summary.artifacts.segmentation_plot
                    ),
                    "summary_json": _name(summary.artifacts.summary_json),
                }
            ),
        }
    )


def _portable_quality(
    summary: SquatQualityGateSummary | None,
) -> SquatQualityGateSummary | None:
    if summary is None:
        return None
    return summary.model_copy(
        update={
            "artifacts": summary.artifacts.model_copy(
                update={"summary_json": _name(summary.artifacts.summary_json)}
            )
        }
    )


def _portable_biomechanics(
    summary: SquatBiomechanicsSummary | None,
) -> SquatBiomechanicsSummary | None:
    if summary is None:
        return None
    return summary.model_copy(
        update={
            "landmarks_csv": _name(summary.landmarks_csv),
            "frame_phases_csv": _name(summary.frame_phases_csv),
            "artifacts": summary.artifacts.model_copy(
                update={
                    "frame_metrics_csv": _name(
                        summary.artifacts.frame_metrics_csv
                    ),
                    "repetition_metrics_csv": _name(
                        summary.artifacts.repetition_metrics_csv
                    ),
                    "metrics_plot": _name(summary.artifacts.metrics_plot),
                    "summary_json": _name(summary.artifacts.summary_json),
                }
            ),
        }
    )


def _portable_findings(
    summary: SquatFindingsSummary | None,
) -> SquatFindingsSummary | None:
    if summary is None:
        return None
    return summary.model_copy(
        update={
            "artifacts": summary.artifacts.model_copy(
                update={
                    "rule_evidence_csv": _name(
                        summary.artifacts.rule_evidence_csv
                    ),
                    "findings_json": _name(summary.artifacts.findings_json),
                }
            )
        }
    )


def _write_model_json(model: BaseModel, output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(model.model_dump(mode="json"), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


__all__ = [
    "SquatArtifactManifest",
    "SquatCaseRecordContract",
    "SquatCaseReport",
    "SquatEventCapture",
    "SquatManualProtocolReview",
    "build_case_report",
    "export_contract_schemas",
    "write_case_record_contract",
]
