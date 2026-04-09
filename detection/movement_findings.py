"""Rule-based dynamic findings for shoulder abduction movement analysis."""

from __future__ import annotations

from typing import Any


def detect_shoulder_abduction_findings(
    metrics: dict[str, dict[str, Any]],
    *,
    movement_phases: dict[str, Any],
) -> dict[str, Any]:
    """Convert dynamic metrics into cautious descriptive findings."""
    items: list[dict[str, Any]] = []

    for side in ("left", "right"):
        elevation_onset = _metric_value(metrics, f"elevation_onset_angle_{side}")
        elevation_onset_status = _metric_status(metrics, f"elevation_onset_angle_{side}")
        activation_delay = _metric_value(metrics, f"scapular_activation_delay_{side}")
        scap_ratio = _metric_value(metrics, f"scapulohumeral_ratio_{side}")
        winging = _metric_value(metrics, f"dynamic_winging_{side}")

        if elevation_onset is not None and elevation_onset_status != "low_confidence" and elevation_onset <= 25.0:
            items.append(
                _finding(
                    finding_id=f"early_scapular_elevation_{side}",
                    label=f"Early scapular elevation ({side})",
                    summary=f"Posterior proxy suggests scapular elevation begins early on the {side} side during shoulder abduction.",
                    severity=_severity_greater(25.0 - elevation_onset, mild=5.0, moderate=12.0, severe=20.0),
                    confidence="medium",
                    related_metrics=[f"elevation_onset_angle_{side}", f"scapular_elevation_dynamic_{side}"],
                    side=side,
                )
            )

        if activation_delay is not None and activation_delay >= 3.0:
            items.append(
                _finding(
                    finding_id=f"delayed_scapular_activation_{side}",
                    label=f"Delayed scapular activation ({side})",
                    summary=f"Scapular proxy motion starts later than humeral motion on the {side} side.",
                    severity=_severity_greater(activation_delay, mild=3.0, moderate=5.0, severe=7.0),
                    confidence="medium",
                    related_metrics=[f"scapular_activation_delay_{side}", f"elevation_onset_angle_{side}"],
                    side=side,
                )
            )

        if scap_ratio is not None and scap_ratio <= 0.12:
            items.append(
                _finding(
                    finding_id=f"reduced_scapular_contribution_{side}",
                    label=f"Reduced scapular contribution ({side})",
                    summary=f"The scapular proxy contribution appears reduced relative to humeral abduction on the {side} side.",
                    severity=_severity_lower(scap_ratio, mild=0.12, moderate=0.09, severe=0.06),
                    confidence="low",
                    related_metrics=[f"scapulohumeral_ratio_{side}", f"scapular_upward_rotation_dynamic_{side}"],
                    side=side,
                )
            )

        if winging is not None and winging >= 0.03:
            items.append(
                _finding(
                    finding_id=f"possible_dynamic_winging_{side}",
                    label=f"Possible dynamic winging ({side})",
                    summary=f"Low-confidence posterior proxy suggests possible dynamic winging on the {side} side.",
                    severity=_severity_greater(winging, mild=0.03, moderate=0.05, severe=0.08),
                    confidence="low",
                    related_metrics=[f"dynamic_winging_{side}"],
                    side=side,
                )
            )

    elevation_asymmetry = _metric_value(metrics, "dynamic_elevation_asymmetry")
    upward_asymmetry = _metric_value(metrics, "dynamic_upward_rotation_asymmetry")
    protraction_asymmetry = _metric_value(metrics, "dynamic_protraction_asymmetry")
    ratio_left = _metric_value(metrics, "scapulohumeral_ratio_left")
    ratio_right = _metric_value(metrics, "scapulohumeral_ratio_right")

    if any(value is not None and value >= threshold for value, threshold in ((elevation_asymmetry, 0.03), (upward_asymmetry, 6.0), (protraction_asymmetry, 0.03))):
        items.append(
            _finding(
                finding_id="dynamic_scapular_asymmetry",
                label="Dynamic scapular asymmetry",
                summary="Posterior-view proxies suggest a meaningful left-right asymmetry during shoulder abduction.",
                severity=_max_severity(
                    _severity_greater(elevation_asymmetry, mild=0.03, moderate=0.05, severe=0.08),
                    _severity_greater(upward_asymmetry, mild=6.0, moderate=10.0, severe=14.0),
                    _severity_greater(protraction_asymmetry, mild=0.03, moderate=0.05, severe=0.08),
                ),
                confidence="medium",
                related_metrics=[
                    "dynamic_elevation_asymmetry",
                    "dynamic_upward_rotation_asymmetry",
                    "dynamic_protraction_asymmetry",
                ],
            )
        )

    if upward_asymmetry is not None and upward_asymmetry >= 6.0:
        items.append(
            _finding(
                finding_id="asymmetric_upward_rotation_pattern",
                label="Asymmetric upward rotation pattern",
                summary="The upward rotation proxy differs meaningfully between sides during abduction.",
                severity=_severity_greater(upward_asymmetry, mild=6.0, moderate=10.0, severe=14.0),
                confidence="low",
                related_metrics=["dynamic_upward_rotation_asymmetry"],
            )
        )

    if ratio_left is not None and ratio_right is not None and abs(ratio_left - ratio_right) >= 0.08:
        items.append(
            _finding(
                finding_id="scapulohumeral_ratio_asymmetry",
                label="Scapulohumeral ratio asymmetry",
                summary="The scapulohumeral ratio proxy differs between sides across the analyzed movement.",
                severity=_severity_greater(abs(ratio_left - ratio_right), mild=0.08, moderate=0.12, severe=0.18),
                confidence="low",
                related_metrics=["scapulohumeral_ratio_left", "scapulohumeral_ratio_right"],
            )
        )

    return {
        "status": "completed",
        "items": sorted(items, key=lambda item: (_severity_rank(item["severity"]), item["id"]), reverse=True),
        "ready": True,
        "debug": {
            "peak_frame": movement_phases.get("peak_frame"),
            "movement_start_frame": movement_phases.get("movement_start_frame"),
        },
    }


def _finding(
    *,
    finding_id: str,
    label: str,
    summary: str,
    severity: str | None,
    confidence: str,
    related_metrics: list[str],
    side: str | None = None,
) -> dict[str, Any]:
    return {
        "id": finding_id,
        "label": label,
        "summary": summary,
        "severity": severity or "mild",
        "confidence": confidence,
        "view": "back",
        "side": side,
        "related_metrics": related_metrics,
    }


def _metric_value(metrics: dict[str, dict[str, Any]], name: str) -> float | None:
    payload = metrics.get(name)
    if not isinstance(payload, dict):
        return None
    value = payload.get("value")
    return float(value) if isinstance(value, (int, float)) else None


def _metric_status(metrics: dict[str, dict[str, Any]], name: str) -> str | None:
    payload = metrics.get(name)
    if not isinstance(payload, dict):
        return None
    status = payload.get("status")
    return str(status) if isinstance(status, str) else None


def _severity_greater(value: float | None, *, mild: float, moderate: float, severe: float) -> str | None:
    if value is None:
        return None
    if value >= severe:
        return "severe"
    if value >= moderate:
        return "moderate"
    if value >= mild:
        return "mild"
    return None


def _severity_lower(value: float | None, *, mild: float, moderate: float, severe: float) -> str | None:
    if value is None:
        return None
    if value <= severe:
        return "severe"
    if value <= moderate:
        return "moderate"
    if value <= mild:
        return "mild"
    return None


def _severity_rank(value: str) -> int:
    return {"mild": 1, "moderate": 2, "severe": 3}.get(value, 0)


def _max_severity(*values: str | None) -> str:
    return max((value or "mild" for value in values), key=_severity_rank)
