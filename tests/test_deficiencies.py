"""Unit tests for rule-based resting deficiencies."""

from __future__ import annotations

from detection.deficiencies import detect_rest_deficiencies, detect_scapula_rest_deficiencies
from detection.models import Finding


def _finding(
    finding_id: str,
    *,
    severity: str = "moderate",
    confidence: str = "medium",
    view: str = "front",
) -> Finding:
    return Finding(
        id=finding_id,
        label=finding_id.replace("_", " ").title(),
        summary=f"Synthetic finding for {finding_id}.",
        severity=severity,
        confidence=confidence,
        view=view,
        related_metrics=[finding_id],
    )


def test_detect_rest_deficiencies_groups_forward_findings_into_pattern() -> None:
    """Multiple forward-oriented findings should aggregate into a forward posture pattern."""
    findings = [
        _finding("forward_postural_bias", severity="moderate", view="side"),
        _finding("forward_head_posture", severity="mild", view="side"),
        _finding("bilateral_shoulder_protraction", severity="moderate", view="side"),
    ]

    result = detect_rest_deficiencies(findings, view="side")
    ids = {item.id for item in result.items}
    forward_pattern = next(item for item in result.items if item.id == "forward_posture_pattern")

    assert result.status == "completed"
    assert "forward_posture_pattern" in ids
    assert forward_pattern.supporting_findings == [
        "forward_postural_bias",
        "forward_head_posture",
        "bilateral_shoulder_protraction",
    ]
    assert forward_pattern.view == "side"


def test_detect_rest_deficiencies_can_use_v2_forward_support() -> None:
    """V2 sagittal findings should also support the forward posture grouping."""
    findings = [
        _finding("shoulder_protraction_left", severity="severe", view="side"),
        _finding("pelvic_forward_backward_bias", severity="moderate", view="side"),
    ]

    result = detect_rest_deficiencies(findings, view="side")
    ids = {item.id for item in result.items}

    assert "forward_posture_pattern" in ids


def test_detect_rest_deficiencies_requires_sufficient_support_for_lateral_compensation() -> None:
    """A single frontal finding should not be enough to create a lateral compensation deficiency."""
    findings = [_finding("torso_lateral_tilt", severity="moderate", view="front")]

    result = detect_rest_deficiencies(findings, view="front")
    ids = {item.id for item in result.items}

    assert "lateral_postural_compensation" not in ids


def test_detect_rest_deficiencies_groups_scapular_findings_and_filters_by_view() -> None:
    """Scapular groupings should require corroboration and ignore findings from other views."""
    findings = [
        _finding("possible_left_winging_bias", severity="mild", confidence="low", view="back"),
        _finding("scapular_position_asymmetry", severity="moderate", view="back"),
        _finding("scapular_internal_rotation_bias_left", severity="moderate", view="back"),
        _finding("forward_head_posture", severity="severe", view="side"),
    ]

    result = detect_rest_deficiencies(findings, view="back")
    ids = {item.id for item in result.items}
    winging_pattern = next(item for item in result.items if item.id == "possible_scapular_winging_pattern")

    assert "possible_scapular_winging_pattern" in ids
    assert "forward_posture_pattern" not in ids
    assert winging_pattern.confidence == "low"
    assert winging_pattern.supporting_findings == [
        "possible_left_winging_bias",
        "scapular_position_asymmetry",
        "scapular_internal_rotation_bias_left",
    ]


def test_detect_scapula_rest_deficiencies_maps_findings_to_probabilistic_patterns() -> None:
    findings = [
        Finding(
            id="scapular_elevation_asymmetry",
            label="Asimetria de elevacion escapular",
            summary="Synthetic scapula rest finding.",
            severity="moderate",
            confidence="high",
            view="back",
            side="right",
            weight=1.0,
            related_metrics=["scapular_elevation_difference"],
        ),
        Finding(
            id="possible_scapular_protraction_asymmetry",
            label="Posible asimetria de protraccion escapular",
            summary="Synthetic scapula rest finding.",
            severity="mild",
            confidence="low",
            view="back",
            side="right",
            weight=0.5,
            related_metrics=["scapula_spine_distance_left", "scapula_spine_distance_right"],
        ),
        Finding(
            id="possible_static_winging",
            label="Posible winging escapular en reposo",
            summary="Synthetic scapula rest finding.",
            severity="mild",
            confidence="low",
            view="back",
            weight=0.5,
            related_metrics=["winging_index"],
        ),
    ]

    result = detect_scapula_rest_deficiencies(findings)
    ids = {item.id for item in result.items}
    assert "scapulothoracic_postural_asymmetry" in ids
    assert "possible_upper_trapezius_hyperactivity_right" in ids
    assert "possible_scapular_instability" in ids
    retractor = next(item for item in result.items if item.id == "possible_scapular_retractor_weakness")
    assert retractor.related_findings == ["possible_scapular_protraction_asymmetry"]
