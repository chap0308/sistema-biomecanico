"""Expert-reference consolidation and technical performance metrics."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable, Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field

PatternKey = Literal[
    "trunk_lateral_inclination",
    "pelvis_lateral_shift",
    "visible_dynamic_valgus",
    "bilateral_asymmetry",
]
ReferenceMethod = Literal[
    "coincidencia_directa",
    "mayoria_absoluta",
    "consenso_guiado",
]

PATTERN_KEYS: tuple[PatternKey, ...] = (
    "trunk_lateral_inclination",
    "pelvis_lateral_shift",
    "visible_dynamic_valgus",
    "bilateral_asymmetry",
)
FINDING_TO_PATTERN: dict[str, PatternKey] = {
    "inclinacion_lateral_tronco": "trunk_lateral_inclination",
    "desplazamiento_lateral_pelvis": "pelvis_lateral_shift",
    "valgo_dinamico_visible": "visible_dynamic_valgus",
    "asimetria_bilateral_observable": "bilateral_asymmetry",
}


class ExpertJudgment(BaseModel):
    """One submitted expert classification."""

    evaluator_id: str
    repetition_index: int = Field(default=1, ge=1)
    pattern_key: PatternKey
    classification: Literal["presente", "ausente", "no_concluyente"]
    observed_side: str | None = None
    confidence: Literal["baja", "media", "alta"] | None = None


class FinalReference(BaseModel):
    """Consolidated expert reference for one pattern."""

    classification: Literal["presente", "ausente", "no_concluyente"]
    observed_side: str | None = None
    method: ReferenceMethod
    observation: str | None = None

    @computed_field
    @property
    def label(self) -> str:
        """Return the canonical categorical label."""
        if self.classification == "presente" and self.observed_side is None:
            return "presente"
        return canonical_label(
            self.classification,
            self.observed_side,
        )


class PatternComparison(BaseModel):
    """Traceable comparison for one case and one independent pattern."""

    model_config = ConfigDict(extra="forbid")

    repetition_index: int = Field(default=1, ge=1)
    pattern_key: PatternKey
    expert_judgments: list[ExpertJudgment]
    reference: FinalReference | None
    reference_status: Literal[
        "consolidada", "consenso_requerido", "evaluaciones_pendientes"
    ]
    system_classification: Literal[
        "presente", "ausente", "no_concluyente"
    ]
    system_side: str | None = None
    system_label: str
    exact_match: bool | None = None
    binary_outcome: Literal["TP", "TN", "FP", "FN"] | None = None


class PerformanceMetrics(BaseModel):
    """Binary detection and categorical agreement metrics."""

    scope: str
    included_pairs: int = Field(ge=0)
    excluded_inconclusive_pairs: int = Field(ge=0)
    true_positive: int = Field(ge=0)
    true_negative: int = Field(ge=0)
    false_positive: int = Field(ge=0)
    false_negative: int = Field(ge=0)
    accuracy: float | None = None
    precision: float | None = None
    sensitivity: float | None = None
    specificity: float | None = None
    f1_score: float | None = None
    exact_agreement: float | None = None
    cohen_kappa: float | None = None


class CaseComparison(BaseModel):
    """Investigator-facing comparison state for one processed case."""

    case_id: str
    assigned_evaluators: int = Field(ge=0)
    submitted_evaluations: int = Field(ge=0)
    reference_status: Literal["open", "in_progress", "closed"] = "open"
    patterns: list[PatternComparison]
    ready_for_metrics: bool


class DatasetPerformance(BaseModel):
    """Performance summary over every currently consolidated case."""

    consolidated_cases: int = Field(ge=0)
    pending_cases: int = Field(ge=0)
    overall: PerformanceMetrics
    by_pattern: list[PerformanceMetrics]


def build_case_comparisons(
    *,
    judgments: Iterable[ExpertJudgment],
    system_decisions: Iterable[dict[str, Any]],
    manual_references: (
        dict[tuple[int, PatternKey] | PatternKey, FinalReference] | None
    ) = None,
) -> list[PatternComparison]:
    """Build independent pattern comparisons for every detected repetition."""
    grouped: dict[tuple[int, PatternKey], list[ExpertJudgment]] = {}
    for judgment in judgments:
        grouped.setdefault(
            (judgment.repetition_index, judgment.pattern_key),
            [],
        ).append(judgment)
    system = _system_outputs(system_decisions)
    normalized_manual_references = {
        (
            key if isinstance(key, tuple) else (1, key)
        ): reference
        for key, reference in (manual_references or {}).items()
    }
    repetition_indexes = sorted(
        {
            repetition_index
            for repetition_index, _ in (
                set(grouped) | set(system) | set(normalized_manual_references)
            )
        }
    ) or [1]

    rows: list[PatternComparison] = []
    for repetition_index in repetition_indexes:
        for pattern_key in PATTERN_KEYS:
            key = (repetition_index, pattern_key)
            pattern_judgments = grouped.get(key, [])
            reference, reference_status = consolidate_reference(
                pattern_key=pattern_key,
                judgments=pattern_judgments,
                manual_reference=normalized_manual_references.get(key),
            )
            system_classification, system_side = system.get(
                key,
                ("no_concluyente", None),
            )
            system_label = canonical_label(
                system_classification,
                system_side,
                pattern_key=pattern_key,
            )
            exact_match: bool | None = None
            outcome: Literal["TP", "TN", "FP", "FN"] | None = None
            if reference and (
                reference.classification != "no_concluyente"
                and system_classification != "no_concluyente"
            ):
                reference_label = canonical_label(
                    reference.classification,
                    reference.observed_side,
                    pattern_key=pattern_key,
                )
                exact_match = reference_label == system_label
                outcome = _binary_outcome(
                    reference.classification,
                    system_classification,
                )
            rows.append(
                PatternComparison(
                    repetition_index=repetition_index,
                    pattern_key=pattern_key,
                    expert_judgments=pattern_judgments,
                    reference=reference,
                    reference_status=reference_status,
                    system_classification=system_classification,
                    system_side=system_side,
                    system_label=system_label,
                    exact_match=exact_match,
                    binary_outcome=outcome,
                )
            )
    return rows


def build_stored_case_comparison(payload: dict[str, Any]) -> CaseComparison:
    """Build a comparison from the persistence-layer aggregate payload."""
    judgments = [
        ExpertJudgment.model_validate(item)
        for item in payload.get("judgments", [])
    ]
    manual_references = {
        (row.get("repetition_index", 1), row["pattern_key"]): FinalReference(
            classification=row["classification"],
            observed_side=row.get("observed_side"),
            method="consenso_guiado",
            observation=row.get("observation"),
        )
        for row in payload.get("manual_references", [])
    }
    report = payload.get("report") or {}
    findings = report.get("findings") or {}
    patterns = build_case_comparisons(
        judgments=judgments,
        system_decisions=findings.get("decisions", []),
        manual_references=manual_references,
    )
    return CaseComparison(
        case_id=payload["case_id"],
        assigned_evaluators=payload.get("assigned_evaluators", 0),
        submitted_evaluations=payload.get("submitted_evaluations", 0),
        reference_status=payload.get("reference_status", "open"),
        patterns=patterns,
        ready_for_metrics=all(
            pattern.reference is not None for pattern in patterns
        ),
    )


def calculate_dataset_performance(
    comparisons: Iterable[CaseComparison],
) -> DatasetPerformance:
    """Calculate pooled and per-pattern metrics for consolidated cases."""
    comparisons = list(comparisons)
    consolidated = [
        comparison
        for comparison in comparisons
        if comparison.ready_for_metrics
    ]
    all_rows = [
        row for comparison in consolidated for row in comparison.patterns
    ]
    by_pattern = [
        calculate_metrics(
            [
                row
                for row in all_rows
                if row.pattern_key == pattern_key
            ],
            scope=pattern_key,
        )
        for pattern_key in PATTERN_KEYS
    ]
    overall = calculate_metrics(all_rows, scope="general")
    pattern_kappas = [
        metric.cohen_kappa
        for metric in by_pattern
        if metric.cohen_kappa is not None
    ]
    overall = overall.model_copy(
        update={
            "cohen_kappa": (
                round(sum(pattern_kappas) / len(pattern_kappas), 4)
                if pattern_kappas
                else None
            )
        }
    )
    return DatasetPerformance(
        consolidated_cases=len(consolidated),
        pending_cases=len(comparisons) - len(consolidated),
        overall=overall,
        by_pattern=by_pattern,
    )


def consolidate_reference(
    *,
    pattern_key: PatternKey,
    judgments: list[ExpertJudgment],
    manual_reference: FinalReference | None,
) -> tuple[
    FinalReference | None,
    Literal["consolidada", "consenso_requerido", "evaluaciones_pendientes"],
]:
    """Apply direct agreement, absolute majority, or recorded consensus."""
    if manual_reference:
        return manual_reference, "consolidada"
    if len(judgments) < 2:
        return None, "evaluaciones_pendientes"

    labels = [
        canonical_label(
            judgment.classification,
            judgment.observed_side,
            pattern_key=pattern_key,
        )
        for judgment in judgments
    ]
    counts = Counter(labels)
    label, count = counts.most_common(1)[0]
    if len(judgments) == 2 and count == 2:
        return _reference_from_label(
            label,
            method="coincidencia_directa",
        ), "consolidada"
    if len(judgments) >= 3 and count > len(judgments) / 2:
        return _reference_from_label(
            label,
            method="mayoria_absoluta",
        ), "consolidada"
    return None, "consenso_requerido"


def calculate_metrics(
    rows: Iterable[PatternComparison],
    *,
    scope: str,
) -> PerformanceMetrics:
    """Calculate binary detection metrics and nominal Cohen's Kappa."""
    included: list[PatternComparison] = []
    excluded = 0
    for row in rows:
        if (
            row.reference is None
            or row.reference.classification == "no_concluyente"
            or row.system_classification == "no_concluyente"
        ):
            excluded += 1
            continue
        included.append(row)

    outcomes = Counter(
        row.binary_outcome for row in included if row.binary_outcome
    )
    tp = outcomes["TP"]
    tn = outcomes["TN"]
    fp = outcomes["FP"]
    fn = outcomes["FN"]
    reference_labels = [
        canonical_label(
            row.reference.classification,
            row.reference.observed_side,
            pattern_key=row.pattern_key,
        )
        for row in included
        if row.reference
    ]
    system_labels = [row.system_label for row in included]
    exact_matches = sum(
        reference == system
        for reference, system in zip(
            reference_labels,
            system_labels,
            strict=True,
        )
    )
    return PerformanceMetrics(
        scope=scope,
        included_pairs=len(included),
        excluded_inconclusive_pairs=excluded,
        true_positive=tp,
        true_negative=tn,
        false_positive=fp,
        false_negative=fn,
        accuracy=_ratio(tp + tn, len(included)),
        precision=_ratio(tp, tp + fp),
        sensitivity=_ratio(tp, tp + fn),
        specificity=_ratio(tn, tn + fp),
        f1_score=_ratio(2 * tp, 2 * tp + fp + fn),
        exact_agreement=_ratio(exact_matches, len(included)),
        cohen_kappa=_cohen_kappa(reference_labels, system_labels),
    )


def canonical_label(
    classification: str,
    observed_side: str | None,
    *,
    pattern_key: PatternKey | None = None,
) -> str:
    """Normalize expert and system outputs into comparable labels."""
    if classification != "presente":
        return classification
    if pattern_key == "bilateral_asymmetry":
        return "presente"
    side = {
        "predominio_izquierdo": "izquierda",
        "predominio_derecho": "derecha",
    }.get(observed_side or "", observed_side)
    return f"presente_{side}" if side else "presente_sin_direccion"


def _system_outputs(
    decisions: Iterable[dict[str, Any]],
) -> dict[tuple[int, PatternKey], tuple[str, str | None]]:
    outputs: dict[tuple[int, PatternKey], tuple[str, str | None]] = {}
    for decision in decisions:
        pattern = FINDING_TO_PATTERN.get(str(decision.get("finding")))
        if pattern:
            outputs[(int(decision.get("repetition_index", 1)), pattern)] = (
                str(decision.get("status", "no_concluyente")),
                decision.get("direction"),
            )
    return outputs


def _reference_from_label(
    label: str,
    *,
    method: ReferenceMethod,
) -> FinalReference:
    if label.startswith("presente_"):
        return FinalReference(
            classification="presente",
            observed_side=label.removeprefix("presente_"),
            method=method,
        )
    return FinalReference(
        classification=label,
        method=method,
    )


def _binary_outcome(
    reference: str,
    system: str,
) -> Literal["TP", "TN", "FP", "FN"]:
    reference_positive = reference == "presente"
    system_positive = system == "presente"
    if reference_positive and system_positive:
        return "TP"
    if not reference_positive and not system_positive:
        return "TN"
    return "FP" if system_positive else "FN"


def _ratio(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 4) if denominator else None


def _cohen_kappa(
    reference_labels: list[str],
    system_labels: list[str],
) -> float | None:
    if not reference_labels:
        return None
    total = len(reference_labels)
    observed = sum(
        reference == system
        for reference, system in zip(
            reference_labels,
            system_labels,
            strict=True,
        )
    ) / total
    reference_counts = Counter(reference_labels)
    system_counts = Counter(system_labels)
    labels = set(reference_counts) | set(system_counts)
    expected = sum(
        (reference_counts[label] / total) * (system_counts[label] / total)
        for label in labels
    )
    if expected == 1.0:
        return None
    return round((observed - expected) / (1.0 - expected), 4)


__all__ = [
    "ExpertJudgment",
    "CaseComparison",
    "DatasetPerformance",
    "FinalReference",
    "PATTERN_KEYS",
    "PatternComparison",
    "PatternKey",
    "PerformanceMetrics",
    "build_case_comparisons",
    "build_stored_case_comparison",
    "calculate_dataset_performance",
    "calculate_metrics",
    "canonical_label",
    "consolidate_reference",
]
