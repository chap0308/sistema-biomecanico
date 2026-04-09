"""Rule-based dynamic deficiencies for shoulder abduction movement analysis."""

from __future__ import annotations

from typing import Any


def detect_movement_deficiencies(findings: list[dict[str, Any]]) -> dict[str, Any]:
    """Group dynamic findings into cautious movement deficiencies."""
    findings_by_id = {str(item.get("id")): item for item in findings}
    items: list[dict[str, Any]] = []

    early_elevation = [
        findings_by_id[f"early_scapular_elevation_{side}"]
        for side in ("left", "right")
        if f"early_scapular_elevation_{side}" in findings_by_id
    ]
    delayed_activation = [
        findings_by_id[f"delayed_scapular_activation_{side}"]
        for side in ("left", "right")
        if f"delayed_scapular_activation_{side}" in findings_by_id
    ]
    reduced_contribution = [
        findings_by_id[f"reduced_scapular_contribution_{side}"]
        for side in ("left", "right")
        if f"reduced_scapular_contribution_{side}" in findings_by_id
    ]
    winging = [
        findings_by_id[f"possible_dynamic_winging_{side}"]
        for side in ("left", "right")
        if f"possible_dynamic_winging_{side}" in findings_by_id
    ]

    if early_elevation:
        items.append(
            _deficiency(
                deficiency_id="possible_early_upper_trapezius_dominance",
                label="Possible early upper trapezius dominance",
                summary="Early scapular elevation proxy suggests a possible upper-trapezius-dominant pattern during abduction.",
                supporting_findings=early_elevation,
                confidence="low",
            )
        )

    upward_rotation_support = [item for item in [*reduced_contribution] if item is not None]
    if "asymmetric_upward_rotation_pattern" in findings_by_id:
        upward_rotation_support.append(findings_by_id["asymmetric_upward_rotation_pattern"])
    if upward_rotation_support:
        items.append(
            _deficiency(
                deficiency_id="possible_reduced_scapular_upward_rotation",
                label="Possible reduced scapular upward rotation",
                summary="Proxy-based upward rotation findings suggest reduced scapular contribution during shoulder elevation.",
                supporting_findings=upward_rotation_support,
                confidence="low",
            )
        )

    if winging:
        items.append(
            _deficiency(
                deficiency_id="possible_dynamic_winging_pattern",
                label="Possible dynamic winging pattern",
                summary="Low-confidence posterior proxies suggest a possible dynamic winging pattern that should be reviewed frame by frame.",
                supporting_findings=winging,
                confidence="low",
            )
        )

    rhythm_support = []
    for finding_id in ("dynamic_scapular_asymmetry", "scapulohumeral_ratio_asymmetry"):
        if finding_id in findings_by_id:
            rhythm_support.append(findings_by_id[finding_id])
    if rhythm_support:
        items.append(
            _deficiency(
                deficiency_id="possible_asymmetric_scapulohumeral_rhythm",
                label="Possible asymmetric scapulohumeral rhythm",
                summary="The movement shows left-right rhythm asymmetry across scapular proxies and humeral timing.",
                supporting_findings=rhythm_support,
                confidence="medium",
            )
        )

    dyskinesis_support = [*rhythm_support, *delayed_activation, *winging]
    if len(dyskinesis_support) >= 2:
        items.append(
            _deficiency(
                deficiency_id="possible_scapular_dyskinesis",
                label="Possible scapular dyskinesis",
                summary="Combined timing, asymmetry and proxy-control findings are compatible with a possible dyskinesis pattern.",
                supporting_findings=dyskinesis_support,
                confidence="low",
            )
        )

    return {
        "status": "completed",
        "items": sorted(items, key=lambda item: (_severity_rank(item["severity"]), item["id"]), reverse=True),
        "ready": True,
    }


def _deficiency(
    *,
    deficiency_id: str,
    label: str,
    summary: str,
    supporting_findings: list[dict[str, Any]],
    confidence: str,
) -> dict[str, Any]:
    severities = [str(item.get("severity") or "mild") for item in supporting_findings]
    return {
        "id": deficiency_id,
        "label": label,
        "summary": summary,
        "severity": max(severities, key=_severity_rank),
        "confidence": confidence,
        "supporting_findings": [str(item.get("id")) for item in supporting_findings],
        "view": "back",
    }


def _severity_rank(value: str) -> int:
    return {"mild": 1, "moderate": 2, "severe": 3}.get(value, 0)
