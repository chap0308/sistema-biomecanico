"""Versioned interpretable rules for frontal bilateral-squat findings."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from statistics import median
from typing import Iterable

from src.squat.models import (
    RuleDecisionStatus,
    SquatBiomechanicsSummary,
    SquatFindingsArtifacts,
    SquatFindingsSummary,
    SquatQualityGateSummary,
    SquatRuleDecision,
    SquatRuleSet,
    SquatRuleThreshold,
)

REQUIRED_RULES: tuple[str, ...] = (
    "inclinacion_lateral_tronco",
    "desplazamiento_lateral_pelvis",
    "valgo_dinamico_visible",
    "asimetria_bilateral_observable",
)


def load_squat_ruleset(path: str | Path) -> SquatRuleSet:
    """Load and validate a versioned squat ruleset."""
    ruleset_path = Path(path)
    ruleset = SquatRuleSet.model_validate_json(
        ruleset_path.read_text(encoding="utf-8")
    )
    missing = sorted(set(REQUIRED_RULES) - set(ruleset.rules))
    if missing:
        raise ValueError("ruleset is missing required rules: " + ", ".join(missing))
    return ruleset


def classify_squat_findings(
    biomechanics_summary_json: str | Path,
    quality_summary_json: str | Path,
    ruleset_path: str | Path,
    *,
    case_id: str,
    output_dir: str | Path,
) -> SquatFindingsSummary:
    """Apply provisional rules without consuming intended or expert labels."""
    biomechanics = SquatBiomechanicsSummary.model_validate_json(
        Path(biomechanics_summary_json).read_text(encoding="utf-8")
    )
    quality = SquatQualityGateSummary.model_validate_json(
        Path(quality_summary_json).read_text(encoding="utf-8")
    )
    if biomechanics.case_id != case_id or quality.case_id != case_id:
        raise ValueError("case_id must match biomechanics and quality summaries")
    if not quality.eligible_for_analysis:
        raise ValueError("quality gate rejected the case for biomechanical analysis")

    ruleset = load_squat_ruleset(ruleset_path)
    eligible_indexes = set(
        quality.eligible_repetition_indexes
        or [repetition.repetition_index for repetition in biomechanics.repetitions]
    )
    decisions: list[SquatRuleDecision] = []
    for repetition in biomechanics.repetitions:
        if repetition.repetition_index not in eligible_indexes:
            continue
        decisions.extend(
            [
                _signed_rule_decision(
                    repetition_index=repetition.repetition_index,
                    finding="inclinacion_lateral_tronco",
                    values=[repetition.trunk_inclination_at_peak_deg],
                    threshold=ruleset.rules["inclinacion_lateral_tronco"],
                    positive_direction="izquierda",
                    negative_direction="derecha",
                ),
                _signed_rule_decision(
                    repetition_index=repetition.repetition_index,
                    finding="desplazamiento_lateral_pelvis",
                    values=[repetition.pelvis_shift_at_peak_pct],
                    threshold=ruleset.rules["desplazamiento_lateral_pelvis"],
                    positive_direction="izquierda",
                    negative_direction="derecha",
                ),
                _valgus_decision(
                    repetition_index=repetition.repetition_index,
                    left_values=[
                        repetition.left_knee_medial_deviation_at_peak_pct
                    ],
                    right_values=[
                        repetition.right_knee_medial_deviation_at_peak_pct
                    ],
                    threshold=ruleset.rules["valgo_dinamico_visible"],
                ),
                _asymmetry_decision(
                    repetition_index=repetition.repetition_index,
                    difference_values=[
                        repetition.bilateral_alignment_difference_at_peak_pct
                    ],
                    left_values=[
                        repetition.left_knee_medial_deviation_at_peak_pct
                    ],
                    right_values=[
                        repetition.right_knee_medial_deviation_at_peak_pct
                    ],
                    threshold=ruleset.rules[
                        "asimetria_bilateral_observable"
                    ],
                ),
            ]
        )

    case_output_dir = Path(output_dir) / case_id
    case_output_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = case_output_dir / "rule_evidence.csv"
    findings_path = case_output_dir / "findings.json"
    _write_rule_evidence(evidence_path, decisions)

    notes = [
        "Los umbrales son provisionales y no constituyen puntos de corte clínicos.",
        "La clasificación no utiliza la etiqueta prevista ni la referencia experta.",
    ]
    if quality.status == "revision_requerida":
        notes.append(
            "El control de calidad permitió el análisis, pero solicitó revisión técnica."
        )
    summary = SquatFindingsSummary(
        case_id=case_id,
        ruleset_version=ruleset.ruleset_version,
        ruleset_status=ruleset.status,
        quality_gate_status=quality.status,
        decisions=decisions,
        detected_findings=[
            f"repeticion_{decision.repetition_index}:{decision.finding}"
            for decision in decisions
            if decision.status == "presente"
        ],
        inconclusive_findings=[
            f"repeticion_{decision.repetition_index}:{decision.finding}"
            for decision in decisions
            if decision.status == "no_concluyente"
        ],
        notes=notes,
        artifacts=SquatFindingsArtifacts(
            rule_evidence_csv=str(evidence_path),
            findings_json=str(findings_path),
        ),
    )
    findings_path.write_text(
        json.dumps(summary.model_dump(mode="json"), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return summary


def _signed_rule_decision(
    *,
    repetition_index: int,
    finding: str,
    values: list[float | None],
    threshold: SquatRuleThreshold,
    positive_direction: str,
    negative_direction: str,
) -> SquatRuleDecision:
    states = [_classify_magnitude(value, threshold) for value in values]
    positive_present = sum(
        state == "presente" and value is not None and value > 0.0
        for state, value in zip(states, values, strict=False)
    )
    negative_present = sum(
        state == "presente" and value is not None and value < 0.0
        for state, value in zip(states, values, strict=False)
    )
    if positive_present:
        status: RuleDecisionStatus = "presente"
        direction = positive_direction
    elif negative_present:
        status = "presente"
        direction = negative_direction
    elif "ausente" in states:
        status = "ausente"
        direction = None
    else:
        status = "no_concluyente"
        direction = None
    aggregate = _finite_median(values)
    return SquatRuleDecision(
        repetition_index=repetition_index,
        finding=finding,
        status=status,
        direction=direction,
        metric=threshold.metric,
        unit=threshold.unit,
        aggregate_value=_rounded(aggregate),
        repetition_values=[_rounded(value) for value in values],
        repetition_states=states,
        absent_max=threshold.absent_max,
        present_min=threshold.present_min,
        rationale=(
            f"Se clasifica exclusivamente la repetición {repetition_index} "
            f"mediante la magnitud de {threshold.metric}. El signo determina "
            "la dirección anatómica."
        ),
    )


def _valgus_decision(
    *,
    repetition_index: int,
    left_values: list[float | None],
    right_values: list[float | None],
    threshold: SquatRuleThreshold,
) -> SquatRuleDecision:
    left_states = [_classify_positive(value, threshold) for value in left_values]
    right_states = [_classify_positive(value, threshold) for value in right_values]
    left_status = _single_repetition_state(left_states)
    right_status = _single_repetition_state(right_states)
    if left_status == "presente" and right_status == "presente":
        status: RuleDecisionStatus = "presente"
        direction = "bilateral"
    elif left_status == "presente":
        status = "presente"
        direction = "izquierda"
    elif right_status == "presente":
        status = "presente"
        direction = "derecha"
    elif left_status == "ausente" and right_status == "ausente":
        status = "ausente"
        direction = None
    else:
        status = "no_concluyente"
        direction = None

    left_median = _finite_median(left_values)
    right_median = _finite_median(right_values)
    aggregate_candidates = [
        value for value in (left_median, right_median) if value is not None
    ]
    aggregate = max(aggregate_candidates) if aggregate_candidates else None
    combined_values = []
    for left, right in zip(left_values, right_values, strict=False):
        finite_values = _finite_values((left, right))
        combined_values.append(max(finite_values) if finite_values else None)
    combined_states = [
        _combine_side_states(left, right)
        for left, right in zip(left_states, right_states, strict=False)
    ]
    return SquatRuleDecision(
        repetition_index=repetition_index,
        finding="valgo_dinamico_visible",
        status=status,
        direction=direction,
        metric=threshold.metric,
        unit=threshold.unit,
        aggregate_value=_rounded(aggregate),
        repetition_values=[_rounded(value) for value in combined_values],
        repetition_states=combined_states,
        absent_max=threshold.absent_max,
        present_min=threshold.present_min,
        rationale=(
            "Cada rodilla se evalúa por separado. Solo una desviación medial "
            "positiva puede activar la regla; una desviación lateral no se "
            "convierte en valgo por usar su valor absoluto."
        ),
    )


def _asymmetry_decision(
    *,
    repetition_index: int,
    difference_values: list[float | None],
    left_values: list[float | None],
    right_values: list[float | None],
    threshold: SquatRuleThreshold,
) -> SquatRuleDecision:
    states = [_classify_magnitude(value, threshold) for value in difference_values]
    status = _single_repetition_state(states)
    aggregate = _finite_median(difference_values)
    left_median = _finite_median(left_values)
    right_median = _finite_median(right_values)
    direction = None
    if status == "presente" and left_median is not None and right_median is not None:
        direction = (
            "predominio_izquierdo"
            if left_median > right_median
            else "predominio_derecho"
        )
    return SquatRuleDecision(
        repetition_index=repetition_index,
        finding="asimetria_bilateral_observable",
        status=status,
        direction=direction,
        metric=threshold.metric,
        unit=threshold.unit,
        aggregate_value=_rounded(aggregate),
        repetition_values=[_rounded(value) for value in difference_values],
        repetition_states=states,
        absent_max=threshold.absent_max,
        present_min=threshold.present_min,
        rationale=(
            "Se evalúa la diferencia absoluta entre las alineaciones de ambas "
            f"rodillas en la repetición {repetition_index}."
        ),
    )


def _classify_magnitude(
    value: float | None,
    threshold: SquatRuleThreshold,
) -> RuleDecisionStatus:
    if value is None or not math.isfinite(value):
        return "no_concluyente"
    magnitude = abs(value)
    if magnitude <= threshold.absent_max:
        return "ausente"
    if magnitude >= threshold.present_min:
        return "presente"
    return "no_concluyente"


def _classify_positive(
    value: float | None,
    threshold: SquatRuleThreshold,
) -> RuleDecisionStatus:
    if value is None or not math.isfinite(value):
        return "no_concluyente"
    if value <= threshold.absent_max:
        return "ausente"
    if value >= threshold.present_min:
        return "presente"
    return "no_concluyente"


def _single_repetition_state(
    states: list[RuleDecisionStatus],
) -> RuleDecisionStatus:
    if len(states) == 1:
        return states[0]
    return "no_concluyente"


def _combine_side_states(
    left: RuleDecisionStatus,
    right: RuleDecisionStatus,
) -> RuleDecisionStatus:
    if "presente" in (left, right):
        return "presente"
    if left == right == "ausente":
        return "ausente"
    return "no_concluyente"


def _finite_values(values: Iterable[float | None]) -> list[float]:
    return [
        float(value)
        for value in values
        if value is not None and math.isfinite(value)
    ]


def _finite_median(values: Iterable[float | None]) -> float | None:
    finite = _finite_values(values)
    return median(finite) if finite else None


def _rounded(value: float | None) -> float | None:
    return round(value, 6) if value is not None and math.isfinite(value) else None


def _write_rule_evidence(
    path: Path,
    decisions: list[SquatRuleDecision],
) -> None:
    fieldnames = (
        "repetition_index",
        "finding",
        "status",
        "direction",
        "metric",
        "unit",
        "aggregate_value",
        "repetition_values",
        "repetition_states",
        "absent_max",
        "present_min",
        "ruleset_rationale",
    )
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for decision in decisions:
            writer.writerow(
                {
                    "repetition_index": decision.repetition_index,
                    "finding": decision.finding,
                    "status": decision.status,
                    "direction": decision.direction or "",
                    "metric": decision.metric,
                    "unit": decision.unit,
                    "aggregate_value": decision.aggregate_value,
                    "repetition_values": json.dumps(decision.repetition_values),
                    "repetition_states": json.dumps(decision.repetition_states),
                    "absent_max": decision.absent_max,
                    "present_min": decision.present_min,
                    "ruleset_rationale": decision.rationale,
                }
            )


__all__ = [
    "classify_squat_findings",
    "load_squat_ruleset",
]
