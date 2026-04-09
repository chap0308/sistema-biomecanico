"""Rule-based grouping of resting findings into higher-level deficiencies."""

from __future__ import annotations

from collections.abc import Sequence

from detection.deficiency_models import DeficienciesResult, Deficiency
from detection.models import Finding
from orchestration.view_metric_policy import normalize_rest_view

_SEVERITY_ORDER = {"mild": 1, "moderate": 2, "severe": 3}
_CONFIDENCE_ORDER = {"low": 1, "medium": 2, "high": 3}


def _finding_by_id(findings: Sequence[Finding], *, view: str) -> dict[str, Finding]:
    return {finding.id: finding for finding in findings if finding.view == view}


def _max_severity(findings: Sequence[Finding]) -> str:
    return max(findings, key=lambda finding: _SEVERITY_ORDER.get(finding.severity, 0)).severity


def _max_confidence(findings: Sequence[Finding]) -> str:
    return max(findings, key=lambda finding: _CONFIDENCE_ORDER.get(finding.confidence, 0)).confidence


def _build_deficiency(
    *,
    deficiency_id: str,
    label: str,
    summary: str,
    supporting_findings: Sequence[Finding],
    view: str,
    confidence: str | None = None,
    weight: float | None = None,
) -> Deficiency:
    related_findings = [finding.id for finding in supporting_findings]
    return Deficiency(
        id=deficiency_id,
        label=label,
        summary=summary,
        severity=_max_severity(supporting_findings),
        confidence=confidence or _max_confidence(supporting_findings),
        supporting_findings=related_findings,
        related_findings=related_findings,
        weight=weight,
        view=view,
    )


def detect_rest_deficiencies(findings: Sequence[Finding], *, view: str) -> DeficienciesResult:
    """Group rest-analysis findings into high-level biomechanical deficiencies."""
    normalized_view = normalize_rest_view(view)
    findings_by_id = _finding_by_id(findings, view=normalized_view)
    items: list[Deficiency] = []

    shoulder_asymmetry = findings_by_id.get("shoulder_height_asymmetry")
    if shoulder_asymmetry is not None:
        items.append(
            _build_deficiency(
                deficiency_id="postural_shoulder_asymmetry",
                label="Postural shoulder asymmetry",
                summary="High-level postural asymmetry centered on the shoulder line at rest.",
                supporting_findings=[shoulder_asymmetry],
                view=normalized_view,
            )
        )

    scapular_support = [
        findings_by_id[finding_id]
        for finding_id in (
            "shoulder_height_asymmetry",
            "scapular_elevation_asymmetry",
            "scapular_position_asymmetry",
            "left_scapular_protraction_bias",
            "right_scapular_protraction_bias",
            "scapular_internal_rotation_bias_left",
            "scapular_internal_rotation_bias_right",
        )
        if finding_id in findings_by_id
    ]
    if len(scapular_support) >= 2:
        items.append(
            _build_deficiency(
                deficiency_id="scapular_resting_asymmetry",
                label="Scapular resting asymmetry",
                summary="Combined shoulder-scapular findings suggest an asymmetric resting scapulothoracic presentation.",
                supporting_findings=scapular_support,
                view=normalized_view,
            )
        )

    forward_support = [
        findings_by_id[finding_id]
        for finding_id in (
            "forward_postural_bias",
            "forward_head_posture",
            "bilateral_shoulder_protraction",
            "shoulder_protraction_left",
            "shoulder_protraction_right",
            "pelvic_forward_backward_bias",
        )
        if finding_id in findings_by_id
    ]
    if len(forward_support) >= 2:
        items.append(
            _build_deficiency(
                deficiency_id="forward_posture_pattern",
                label="Forward posture pattern",
                summary="Multiple sagittal findings support a forward-oriented resting posture pattern.",
                supporting_findings=forward_support,
                view=normalized_view,
            )
        )

    thoracic_support = [
        findings_by_id[finding_id]
        for finding_id in ("thoracic_kyphosis_bias", "thoracic_flattening_bias")
        if finding_id in findings_by_id
    ]
    if thoracic_support:
        items.append(
            _build_deficiency(
                deficiency_id="thoracic_posture_pattern",
                label="Thoracic posture pattern",
                summary="Resting thoracic findings suggest a meaningful thoracic posture bias that warrants interpretation with context.",
                supporting_findings=thoracic_support,
                view=normalized_view,
            )
        )

    lateral_support = [
        findings_by_id[finding_id]
        for finding_id in ("torso_lateral_tilt", "pelvic_tilt_bias", "head_lateral_tilt")
        if finding_id in findings_by_id
    ]
    if len(lateral_support) >= 2:
        items.append(
            _build_deficiency(
                deficiency_id="lateral_postural_compensation",
                label="Lateral postural compensation",
                summary="Multi-segment frontal findings suggest a lateral compensatory resting pattern.",
                supporting_findings=lateral_support,
                view=normalized_view,
            )
        )

    winging_support = [
        findings_by_id[finding_id]
        for finding_id in (
            "possible_winging_bias",
            "possible_left_winging_bias",
            "possible_right_winging_bias",
            "scapular_position_asymmetry",
            "scapular_elevation_asymmetry",
            "scapular_internal_rotation_bias_left",
            "scapular_internal_rotation_bias_right",
        )
        if finding_id in findings_by_id
    ]
    has_winging_signal = any(
        finding_id in findings_by_id
        for finding_id in ("possible_winging_bias", "possible_left_winging_bias", "possible_right_winging_bias")
    )
    if has_winging_signal and len(winging_support) >= 2:
        items.append(
            _build_deficiency(
                deficiency_id="possible_scapular_winging_pattern",
                label="Possible scapular winging pattern",
                summary="Winging-related findings suggest a possible resting scapular prominence pattern that should be validated dynamically.",
                supporting_findings=winging_support,
                view=normalized_view,
                confidence="low",
            )
        )

    return DeficienciesResult(status="completed", items=items, ready_for_recommendations=True)


def detect_scapula_rest_deficiencies(findings: Sequence[Finding]) -> DeficienciesResult:
    """Group scapula-rest findings into cautious scapulothoracic deficiency patterns."""
    findings_by_id = {finding.id: finding for finding in findings}
    items: list[Deficiency] = []

    elevation = findings_by_id.get("scapular_elevation_asymmetry")
    geometry = findings_by_id.get("scapular_geometric_asymmetry")
    protraction = findings_by_id.get("possible_scapular_protraction_asymmetry")
    winging = findings_by_id.get("possible_static_winging")
    rotation = findings_by_id.get("scapular_upward_rotation_asymmetry")
    internal_rotation_findings = [
        finding
        for finding_id, finding in findings_by_id.items()
        if finding_id.startswith("possible_internal_rotation_increase_")
    ]

    if elevation is not None or geometry is not None:
        support = [finding for finding in (elevation, geometry) if finding is not None]
        items.append(
            _build_deficiency(
                deficiency_id="scapulothoracic_postural_asymmetry",
                label="Scapulothoracic postural asymmetry",
                summary="Findings suggest a possible asymmetric resting scapulothoracic posture that should be tracked during dynamic analysis.",
                supporting_findings=support,
                view="back",
                weight=0.9,
            )
        )

    if elevation is not None and elevation.side in {"left", "right"}:
        elevated_side = elevation.side
        opposite_side = "left" if elevated_side == "right" else "right"
        items.append(
            _build_deficiency(
                deficiency_id=f"possible_upper_trapezius_hyperactivity_{elevated_side}",
                label=f"Possible upper trapezius hyperactivity ({elevated_side})",
                summary=f"The elevated resting scapular side is compatible with a possible upper trapezius dominance on the {elevated_side} side.",
                supporting_findings=[elevation],
                view="back",
                weight=0.6,
            )
        )
        items.append(
            _build_deficiency(
                deficiency_id=f"possible_scapular_depressor_weakness_{opposite_side}",
                label=f"Possible scapular depressor weakness ({opposite_side})",
                summary=f"The resting height difference is compatible with possible reduced scapular depression capacity on the {opposite_side} side.",
                supporting_findings=[elevation],
                view="back",
                weight=0.6,
            )
        )

    protraction_support = [finding for finding in [protraction, *internal_rotation_findings] if finding is not None]
    if protraction_support:
        items.append(
            _build_deficiency(
                deficiency_id="possible_scapular_protraction_bias",
                label="Possible scapular protraction bias",
                summary="Proxy-based findings suggest a possible resting protraction bias of the posterior shoulder girdle.",
                supporting_findings=protraction_support,
                view="back",
                confidence="low",
                weight=0.5,
            )
        )
        items.append(
            _build_deficiency(
                deficiency_id="possible_scapular_retractor_weakness",
                label="Possible scapular retractor weakness",
                summary="The proxy-based protraction pattern is compatible with possible reduced scapular retractor support at rest.",
                supporting_findings=protraction_support,
                view="back",
                confidence="low",
                weight=0.4,
            )
        )

    if winging is not None:
        items.append(
            _build_deficiency(
                deficiency_id="possible_scapular_instability",
                label="Possible scapular instability",
                summary="The resting proxy pattern suggests possible scapular instability that should be confirmed during loaded or dynamic movement.",
                supporting_findings=[winging],
                view="back",
                confidence="low",
                weight=0.5,
            )
        )
        items.append(
            _build_deficiency(
                deficiency_id="possible_serratus_or_lower_trapezius_weakness",
                label="Possible serratus anterior or lower trapezius weakness",
                summary="The winging-related resting proxy is compatible with possible serratus anterior or lower trapezius weakness, pending dynamic confirmation.",
                supporting_findings=[winging],
                view="back",
                confidence="low",
                weight=0.4,
            )
        )

    if rotation is not None:
        items.append(
            _build_deficiency(
                deficiency_id="possible_scapular_dyskinesis",
                label="Possible scapular dyskinesis",
                summary="Rotation asymmetry at rest suggests a possible scapular control pattern that may behave as dyskinesis during movement.",
                supporting_findings=[rotation],
                view="back",
                confidence="low",
                weight=0.4,
            )
        )
        items.append(
            _build_deficiency(
                deficiency_id="possible_altered_scapulohumeral_rhythm",
                label="Possible altered scapulohumeral rhythm",
                summary="The static rotation asymmetry is compatible with a possible altered scapulohumeral rhythm that should be validated in video.",
                supporting_findings=[rotation],
                view="back",
                confidence="low",
                weight=0.4,
            )
        )

    items.sort(key=lambda item: (float(item.weight or 0.0), _SEVERITY_ORDER.get(item.severity, 0), item.id), reverse=True)
    return DeficienciesResult(status="completed", items=items, ready_for_recommendations=True)


__all__ = ["detect_rest_deficiencies", "detect_scapula_rest_deficiencies"]
