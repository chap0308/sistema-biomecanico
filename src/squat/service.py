"""End-to-end local service used by the CLI and future web interface."""

from __future__ import annotations

from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from src.squat.biomechanics import calculate_squat_biomechanics
from src.squat.contracts import (
    SquatCaseReport,
    SquatManualProtocolReview,
    build_case_report,
    write_case_record_contract,
)
from src.squat.evidence import generate_repetition_event_captures
from src.squat.models import (
    ProtocolReviewStatus,
    SquatBiomechanicsSummary,
    SquatCaseRecord,
    SquatFindingsSummary,
    SquatPoseSummary,
    SquatQualityGateSummary,
    SquatRegistrationResult,
    SquatSegmentationSummary,
)
from src.squat.pipeline import register_squat_case
from src.squat.pose_video import extract_squat_pose_video
from src.squat.quality_gate import evaluate_squat_analysis_quality
from src.squat.rules import classify_squat_findings
from src.squat.segmentation import segment_squat_pose_artifacts
from src.squat.video import probe_video

SummaryT = TypeVar("SummaryT", bound=BaseModel)


def run_squat_case_analysis(
    case: SquatCaseRecord,
    *,
    manual_review: SquatManualProtocolReview | None,
    registry_path: str | Path,
    output_dir: str | Path,
    ruleset_path: str | Path,
    min_visibility: float = 0.5,
    anonymize_face: bool = True,
    pipeline_version: str = "0.1.0",
) -> SquatCaseReport:
    """Run the complete pipeline and return its interface-ready report."""
    output_root = Path(output_dir)
    case_dir = output_root / case.case_id
    registration, _ = register_squat_case(
        case,
        registry_path=registry_path,
        output_dir=output_root,
        manual_review=manual_review,
    )
    case_record_path = case_dir / "case_record.json"
    report_path = case_dir / "case_report.json"
    if not registration.ready_for_pose:
        return build_case_report(
            case_record_path,
            output_path=report_path,
            pipeline_version=pipeline_version,
        )

    pose = extract_squat_pose_video(
        registration.case.video_path,
        case_id=case.case_id,
        output_dir=output_root,
        min_visibility=min_visibility,
        anonymize_face=anonymize_face,
    )
    segmentation = segment_squat_pose_artifacts(
        pose.artifacts.landmarks_csv,
        pose.artifacts.frame_quality_csv,
        case_id=case.case_id,
        output_dir=output_root,
    )
    event_captures = generate_repetition_event_captures(
        pose.artifacts.overlay_video,
        segmentation,
        output_dir=case_dir,
    )
    quality = evaluate_squat_analysis_quality(
        pose.artifacts.summary_json,
        segmentation.artifacts.summary_json,
        pose.artifacts.frame_quality_csv,
        case_id=case.case_id,
        output_dir=output_root,
    )
    if not quality.eligible_for_analysis:
        return build_case_report(
            case_record_path,
            output_path=report_path,
            pose=pose,
            segmentation=segmentation,
            quality=quality,
            event_captures=event_captures,
            pipeline_version=pipeline_version,
        )

    biomechanics = calculate_squat_biomechanics(
        pose.artifacts.landmarks_csv,
        segmentation.artifacts.frame_phases_csv,
        case_id=case.case_id,
        output_dir=output_root,
    )
    findings = classify_squat_findings(
        biomechanics.artifacts.summary_json,
        quality.artifacts.summary_json,
        ruleset_path,
        case_id=case.case_id,
        output_dir=output_root,
    )
    return build_case_report(
        case_record_path,
        output_path=report_path,
        pose=pose,
        segmentation=segmentation,
        quality=quality,
        biomechanics=biomechanics,
        findings=findings,
        event_captures=event_captures,
        pipeline_version=pipeline_version,
    )


def assemble_existing_squat_case(
    case_id: str,
    *,
    case_output_dir: str | Path,
    manual_review: SquatManualProtocolReview | None = None,
    protocol_review_status: ProtocolReviewStatus = "pendiente",
    pipeline_version: str = "0.1.0",
) -> SquatCaseReport:
    """Build contracts and event captures from already generated stage outputs."""
    case_dir = Path(case_output_dir)
    pose = _load_summary(case_dir / "pose_summary.json", SquatPoseSummary)
    segmentation = _load_optional_summary(
        case_dir / "segmentation_summary.json",
        SquatSegmentationSummary,
    )
    quality = _load_optional_summary(
        case_dir / "quality_gate_summary.json",
        SquatQualityGateSummary,
    )
    biomechanics = _load_optional_summary(
        case_dir / "biomechanical_summary.json",
        SquatBiomechanicsSummary,
    )
    findings = _load_optional_summary(
        case_dir / "findings.json",
        SquatFindingsSummary,
    )
    if pose.case_id != case_id:
        raise ValueError("case_id must match the existing pose summary")

    registration_path = case_dir / "registration.json"
    if registration_path.is_file():
        registration = SquatRegistrationResult.model_validate_json(
            registration_path.read_text(encoding="utf-8")
        )
    else:
        case = SquatCaseRecord(
            case_id=case_id,
            video_path=pose.video_path,
            protocol_review_status=protocol_review_status,
        )
        registration = SquatRegistrationResult.from_case(
            case,
            probe_video(pose.video_path),
        )
        registration_path.write_text(
            registration.model_dump_json(indent=2),
            encoding="utf-8",
        )

    case_record_path = case_dir / "case_record.json"
    write_case_record_contract(
        registration,
        case_record_path,
        manual_review=manual_review,
    )
    if not registration.ready_for_pose:
        return build_case_report(
            case_record_path,
            output_path=case_dir / "case_report.json",
            pipeline_version=pipeline_version,
        )
    captures = (
        generate_repetition_event_captures(
            pose.artifacts.overlay_video,
            segmentation,
            output_dir=case_dir,
        )
        if segmentation is not None
        else []
    )
    return build_case_report(
        case_record_path,
        output_path=case_dir / "case_report.json",
        pose=pose,
        segmentation=segmentation,
        quality=quality,
        biomechanics=biomechanics,
        findings=findings,
        event_captures=captures,
        pipeline_version=pipeline_version,
    )


def _load_summary(path: Path, model_type: type[SummaryT]) -> SummaryT:
    if not path.is_file():
        raise FileNotFoundError(f"Required squat summary does not exist: {path}")
    return model_type.model_validate_json(path.read_text(encoding="utf-8"))


def _load_optional_summary(
    path: Path,
    model_type: type[SummaryT],
) -> SummaryT | None:
    return _load_summary(path, model_type) if path.is_file() else None


__all__ = ["assemble_existing_squat_case", "run_squat_case_analysis"]
