"""Tests for foot-triptych biomechanical findings fed from geometric classifications."""

from __future__ import annotations

from detection.findings import detect_foot_triptych_findings


def _metric(value, *, classification, confidence=0.85, status="computed"):
    return {
        "name": "metric",
        "value": value,
        "status": status,
        "confidence": confidence,
        "classification": classification,
        "flags": [],
    }


def test_detect_foot_triptych_findings_maps_classification_to_biomechanical_findings() -> None:
    metrics = {
        "calcaneal_angle_left": _metric(9.4, classification="valgus_mild"),
        "calcaneal_angle_right": _metric(-6.2, classification="varus"),
        "foot_progression_angle_right": _metric(-12.8, classification="toe_in"),
        "foot_progression_angle_left": _metric(-2.0, classification="neutral"),
        "arch_height_ratio_left": _metric(0.08, classification="normal_arch"),
        "arch_height_ratio_right": _metric(0.05, classification="normal_arch"),
    }

    findings = detect_foot_triptych_findings(metrics)
    finding_ids = {item.id for item in findings.items}

    assert findings.status == "completed"
    assert "rearfoot_pronation_left" in finding_ids
    assert "rearfoot_asymmetry" in finding_ids
    assert "right_toe_in_pattern" in finding_ids
    assert "arch_height_asymmetry" in finding_ids
