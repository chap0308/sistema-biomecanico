"""Automated analytical-quality gate for processed squat videos."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Literal

import pandas as pd

from src.squat.models import (
    SquatPoseSummary,
    SquatQualityCheck,
    SquatQualityGateArtifacts,
    SquatQualityGateSummary,
    SquatSegmentationSummary,
)


@dataclass(slots=True, frozen=True)
class SquatQualityPolicy:
    """Configurable technical thresholds, separate from biomechanical rules."""

    minimum_processed_frames_percentage: float = 99.0
    minimum_video_valid_frames_percentage: float = 90.0
    warning_video_valid_frames_percentage: float = 95.0
    minimum_repetitions: int = 1
    minimum_repetition_valid_frames_percentage: float = 80.0
    warning_repetition_valid_frames_percentage: float = 90.0
    require_valid_peak_depth_frame: bool = True


def evaluate_squat_analysis_quality(
    pose_summary_json: str | Path,
    segmentation_summary_json: str | Path,
    frame_quality_csv: str | Path,
    *,
    case_id: str,
    output_dir: str | Path,
    policy: SquatQualityPolicy | None = None,
) -> SquatQualityGateSummary:
    """Evaluate whether pose and segmentation support formal biomechanical analysis."""
    active_policy = policy or SquatQualityPolicy()
    pose = SquatPoseSummary.model_validate_json(
        Path(pose_summary_json).read_text(encoding="utf-8")
    )
    segmentation = SquatSegmentationSummary.model_validate_json(
        Path(segmentation_summary_json).read_text(encoding="utf-8")
    )
    if pose.case_id != case_id or segmentation.case_id != case_id:
        raise ValueError("case_id must match pose and segmentation summaries")

    quality = pd.read_csv(frame_quality_csv)
    required_columns = {"frame_index", "valid_for_analysis"}
    missing = sorted(required_columns - set(quality.columns))
    if missing:
        raise ValueError(
            "frame quality is missing required columns: " + ", ".join(missing)
        )
    valid_by_frame = {
        int(row.frame_index): _as_bool(row.valid_for_analysis)
        for row in quality.itertuples(index=False)
    }

    checks: list[SquatQualityCheck] = []
    _append_check(
        checks,
        check_id="processed_frames",
        description="Porcentaje de fotogramas procesados correctamente",
        severity="exclusion",
        passed=(
            pose.processed_frames_percentage
            >= active_policy.minimum_processed_frames_percentage
        ),
        observed=f"{pose.processed_frames_percentage:.2f} %",
        requirement=(
            f">= {active_policy.minimum_processed_frames_percentage:.2f} %"
        ),
    )
    _append_check(
        checks,
        check_id="valid_video_frames",
        description="Porcentaje global de fotogramas válidos",
        severity="exclusion",
        passed=(
            pose.valid_frames_percentage
            >= active_policy.minimum_video_valid_frames_percentage
        ),
        observed=f"{pose.valid_frames_percentage:.2f} %",
        requirement=(
            f">= {active_policy.minimum_video_valid_frames_percentage:.2f} %"
        ),
    )
    _append_check(
        checks,
        check_id="valid_video_frames_warning",
        description="Calidad global recomendada de fotogramas válidos",
        severity="warning",
        passed=(
            pose.valid_frames_percentage
            >= active_policy.warning_video_valid_frames_percentage
        ),
        observed=f"{pose.valid_frames_percentage:.2f} %",
        requirement=(
            f">= {active_policy.warning_video_valid_frames_percentage:.2f} %"
        ),
    )
    _append_check(
        checks,
        check_id="repetition_count",
        description="Cantidad de repeticiones completas detectadas",
        severity="exclusion",
        passed=(
            segmentation.repetitions_detected
            >= active_policy.minimum_repetitions
        ),
        observed=str(segmentation.repetitions_detected),
        requirement=f">= {active_policy.minimum_repetitions}",
    )

    eligible_repetition_indexes: list[int] = []
    excluded_repetition_indexes: list[int] = []
    for repetition in segmentation.repetitions:
        repetition_is_valid = (
            repetition.valid_frames_percentage
            >= active_policy.minimum_repetition_valid_frames_percentage
        )
        _append_check(
            checks,
            check_id=f"repetition_{repetition.repetition_index}_valid_frames",
            description=(
                f"Fotogramas válidos de la repetición {repetition.repetition_index}"
            ),
            severity="exclusion",
            passed=repetition_is_valid,
            observed=f"{repetition.valid_frames_percentage:.2f} %",
            requirement=(
                f">= {active_policy.minimum_repetition_valid_frames_percentage:.2f} %"
            ),
        )
        _append_check(
            checks,
            check_id=f"repetition_{repetition.repetition_index}_warning",
            description=(
                f"Calidad recomendada de la repetición {repetition.repetition_index}"
            ),
            severity="warning",
            passed=(
                repetition.valid_frames_percentage
                >= active_policy.warning_repetition_valid_frames_percentage
            ),
            observed=f"{repetition.valid_frames_percentage:.2f} %",
            requirement=(
                f">= {active_policy.warning_repetition_valid_frames_percentage:.2f} %"
            ),
        )
        peak_valid = valid_by_frame.get(repetition.peak_depth_frame, False)
        repetition_is_valid = repetition_is_valid and (
            peak_valid if active_policy.require_valid_peak_depth_frame else True
        )
        _append_check(
            checks,
            check_id=f"repetition_{repetition.repetition_index}_peak_depth",
            description=(
                "Disponibilidad de puntos críticos en máxima profundidad "
                f"de la repetición {repetition.repetition_index}"
            ),
            severity="exclusion",
            passed=(
                peak_valid
                if active_policy.require_valid_peak_depth_frame
                else True
            ),
            observed="válido" if peak_valid else "no válido",
            requirement=(
                "válido"
                if active_policy.require_valid_peak_depth_frame
                else "no obligatorio"
            ),
        )
        (
            eligible_repetition_indexes
            if repetition_is_valid
            else excluded_repetition_indexes
        ).append(repetition.repetition_index)

    global_exclusion_reasons = [
        check.description
        for check in checks
        if (
            check.severity == "exclusion"
            and not check.passed
            and not check.check_id.startswith("repetition_")
        )
    ]
    warnings = [
        check.description
        for check in checks
        if check.severity == "warning" and not check.passed
    ]
    if excluded_repetition_indexes:
        warnings.append(
            "Se excluyeron repeticiones sin evidencia suficiente: "
            + ", ".join(map(str, excluded_repetition_indexes))
        )
    exclusion_reasons = list(global_exclusion_reasons)
    if not eligible_repetition_indexes:
        exclusion_reasons.append(
            "No se detectó ninguna repetición completa con calidad analítica suficiente"
        )
    if exclusion_reasons:
        status = "no_apto_para_analisis"
    elif warnings:
        status = "revision_requerida"
    else:
        status = "apto_para_analisis"

    case_output_dir = Path(output_dir) / case_id
    case_output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = case_output_dir / "quality_gate_summary.json"
    summary = SquatQualityGateSummary(
        case_id=case_id,
        status=status,
        eligible_for_analysis=not exclusion_reasons,
        eligible_repetition_indexes=eligible_repetition_indexes,
        excluded_repetition_indexes=excluded_repetition_indexes,
        checks=checks,
        exclusion_reasons=exclusion_reasons,
        warnings=warnings,
        artifacts=SquatQualityGateArtifacts(summary_json=str(summary_path)),
    )
    summary_path.write_text(
        json.dumps(summary.model_dump(mode="json"), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return summary


def _append_check(
    checks: list[SquatQualityCheck],
    *,
    check_id: str,
    description: str,
    severity: Literal["exclusion", "warning"],
    passed: bool,
    observed: str,
    requirement: str,
) -> None:
    checks.append(
        SquatQualityCheck(
            check_id=check_id,
            description=description,
            severity=severity,
            passed=passed,
            observed=observed,
            requirement=requirement,
        )
    )


def _as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "si", "sí"}


__all__ = [
    "SquatQualityPolicy",
    "evaluate_squat_analysis_quality",
]
