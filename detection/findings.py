"""Rule-based biomechanical findings for resting-posture analysis."""

from __future__ import annotations

from typing import Any

from detection.models import Finding, FindingsResult
from detection.thresholds import REST_FINDING_THRESHOLDS, ThresholdBand
from orchestration.view_metric_policy import normalize_rest_view

MetricPayload = dict[str, Any]
MetricMap = dict[str, MetricPayload]

_SCAPULAR_FINDING_WEIGHTS = {
    "scapular_elevation_asymmetry": 1.0,
    "scapular_position_asymmetry": 0.9,
    "left_scapular_protraction_bias": 0.5,
    "right_scapular_protraction_bias": 0.5,
    "possible_winging_bias": 0.5,
    "possible_left_winging_bias": 0.5,
    "possible_right_winging_bias": 0.5,
    "scapular_internal_rotation_bias_left": 0.3,
    "scapular_internal_rotation_bias_right": 0.3,
    "scapular_upward_rotation_bias_left": 0.3,
    "scapular_upward_rotation_bias_right": 0.3,
}

_SEVERITY_RANK = {"severe": 3, "moderate": 2, "mild": 1}


def _metric_payload(metrics: MetricMap, name: str) -> MetricPayload | None:
    metric = metrics.get(name)
    return metric if isinstance(metric, dict) else None


def _metric_value(metrics: MetricMap, name: str) -> float | None:
    metric = _metric_payload(metrics, name)
    if metric is None:
        return None
    if metric.get("status") not in {"computed", "low_confidence"}:
        return None
    value = metric.get("value")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _classify_greater(value: float | None, thresholds: ThresholdBand) -> str | None:
    if value is None:
        return None
    if value >= thresholds.severe:
        return "severe"
    if value >= thresholds.moderate:
        return "moderate"
    if value >= thresholds.mild:
        return "mild"
    return None


def _classify_lower(value: float | None, thresholds: ThresholdBand) -> str | None:
    if value is None:
        return None
    if value <= thresholds.severe:
        return "severe"
    if value <= thresholds.moderate:
        return "moderate"
    if value <= thresholds.mild:
        return "mild"
    return None


def _classify_absolute(value: float | None, thresholds: ThresholdBand) -> str | None:
    if value is None:
        return None
    return _classify_greater(abs(value), thresholds)


def _angle_deviation_from_horizontal(value: float | None) -> float | None:
    if value is None:
        return None
    normalized = abs(value) % 180.0
    return min(normalized, abs(180.0 - normalized))


def _confidence_from_numeric(value: float | None) -> str:
    if value is None:
        return "low"
    if value >= 0.8:
        return "high"
    if value >= 0.6:
        return "medium"
    return "low"


def _metric_confidence(metrics: MetricMap, *metric_names: str, fallback: str = "low") -> str:
    confidences: list[float] = []
    for metric_name in metric_names:
        metric = _metric_payload(metrics, metric_name)
        if metric is None:
            continue
        confidence = metric.get("confidence")
        if isinstance(confidence, (int, float)):
            confidences.append(float(confidence))
    if not confidences:
        return fallback
    return _confidence_from_numeric(min(confidences))


def _finding_weight(finding_id: str) -> float | None:
    return _SCAPULAR_FINDING_WEIGHTS.get(finding_id)


def _build_finding(
    *,
    finding_id: str,
    label: str,
    summary: str,
    severity: str,
    confidence: str,
    view: str,
    related_metrics: list[str],
    side: str | None = None,
    weight: float | None = None,
) -> Finding:
    return Finding(
        id=finding_id,
        label=label,
        summary=summary,
        severity=severity,
        confidence=confidence,
        view=view,
        side=side,
        weight=weight,
        related_metrics=related_metrics,
    )


def _append_finding(
    items: list[Finding],
    *,
    finding_id: str,
    label: str,
    summary: str,
    severity: str | None,
    confidence: str,
    view: str,
    related_metrics: list[str],
    side: str | None = None,
    weight: float | None = None,
) -> None:
    if severity is None:
        return
    items.append(
        _build_finding(
            finding_id=finding_id,
            label=label,
            summary=summary,
            severity=severity,
            confidence=confidence,
            view=view,
            related_metrics=related_metrics,
            side=side,
            weight=weight,
        )
    )


def _sort_key(finding: Finding) -> tuple[float, int, str]:
    return (
        float(finding.weight or 0.0),
        _SEVERITY_RANK.get(finding.severity, 0),
        finding.id,
    )


def _dominance_votes(metrics: MetricMap, *, delta_distance: float = 0.04, delta_angle: float = 8.0) -> tuple[int, int]:
    left_votes = 0
    right_votes = 0

    left_distance = _metric_value(metrics, "scapula_spine_distance_left")
    right_distance = _metric_value(metrics, "scapula_spine_distance_right")
    if left_distance is not None and right_distance is not None:
        if left_distance - right_distance >= delta_distance:
            left_votes += 1
        elif right_distance - left_distance >= delta_distance:
            right_votes += 1

    left_internal = _metric_value(metrics, "scapular_internal_rotation_left")
    right_internal = _metric_value(metrics, "scapular_internal_rotation_right")
    if left_internal is not None and right_internal is not None:
        if left_internal - right_internal >= delta_angle:
            left_votes += 1
        elif right_internal - left_internal >= delta_angle:
            right_votes += 1

    return left_votes, right_votes


def detect_rest_findings(metrics: MetricMap, *, view: str) -> FindingsResult:
    """Convert serialized resting metrics into structured biomechanical findings."""
    normalized_view = normalize_rest_view(view)
    items: list[Finding] = []

    _append_finding(
        items,
        finding_id="forward_postural_bias",
        label="Forward postural bias",
        summary="Proxy-based lateral finding suggesting a global forward postural tendency.",
        severity=_classify_greater(
            _metric_value(metrics, "forward_center_of_mass_offset"),
            REST_FINDING_THRESHOLDS["forward_postural_bias"],
        ),
        confidence="medium",
        view=normalized_view,
        related_metrics=["forward_center_of_mass_offset"],
    )

    _append_finding(
        items,
        finding_id="thoracic_kyphosis_bias",
        label="Thoracic kyphosis bias",
        summary="Proxy-based sagittal finding suggesting a flexed thoracic resting tendency.",
        severity=_classify_greater(
            _metric_value(metrics, "thoracic_kyphosis_angle"),
            REST_FINDING_THRESHOLDS["thoracic_kyphosis_bias"],
        ),
        confidence="medium",
        view=normalized_view,
        related_metrics=["thoracic_kyphosis_angle"],
    )

    _append_finding(
        items,
        finding_id="thoracic_flattening_bias",
        label="Thoracic flattening bias",
        summary="Compound-index finding suggesting a relatively flattened thoracic profile.",
        severity=_classify_greater(
            _metric_value(metrics, "thoracic_flattening_index"),
            REST_FINDING_THRESHOLDS["thoracic_flattening_bias"],
        ),
        confidence="medium",
        view=normalized_view,
        related_metrics=["thoracic_flattening_index"],
    )

    _append_finding(
        items,
        finding_id="torso_lateral_tilt",
        label="Torso lateral tilt",
        summary="Direct frontal finding showing a visible lateral trunk inclination.",
        severity=_classify_greater(
            _metric_value(metrics, "torso_lateral_tilt"),
            REST_FINDING_THRESHOLDS["torso_lateral_tilt"],
        ),
        confidence="high",
        view=normalized_view,
        related_metrics=["torso_lateral_tilt"],
    )

    _append_finding(
        items,
        finding_id="pelvic_tilt_bias",
        label="Pelvic tilt bias",
        summary="Direct frontal finding suggesting a visible pelvic tilt or pelvic level asymmetry.",
        severity=_classify_greater(
            _angle_deviation_from_horizontal(_metric_value(metrics, "pelvic_tilt")),
            REST_FINDING_THRESHOLDS["pelvic_tilt_bias"],
        ),
        confidence="high",
        view=normalized_view,
        related_metrics=["pelvic_tilt"],
    )

    _append_finding(
        items,
        finding_id="forward_head_posture",
        label="Forward head posture",
        summary="Proxy-based sagittal finding suggesting the head sits anterior to the shoulder complex.",
        severity=_classify_lower(
            _metric_value(metrics, "cranio_shoulder_angle"),
            REST_FINDING_THRESHOLDS["forward_head_posture"],
        ),
        confidence="medium",
        view=normalized_view,
        related_metrics=["cranio_shoulder_angle"],
    )

    _append_finding(
        items,
        finding_id="head_lateral_tilt",
        label="Head lateral tilt",
        summary="Direct frontal finding showing a visible lateral head tilt.",
        severity=_classify_greater(
            _angle_deviation_from_horizontal(_metric_value(metrics, "head_tilt_angle")),
            REST_FINDING_THRESHOLDS["head_lateral_tilt"],
        ),
        confidence="high",
        view=normalized_view,
        related_metrics=["head_tilt_angle"],
    )

    _append_finding(
        items,
        finding_id="shoulder_height_asymmetry",
        label="Shoulder height asymmetry",
        summary="Direct frontal finding showing a visible shoulder height asymmetry.",
        severity=_classify_greater(
            _metric_value(metrics, "shoulder_height_difference"),
            REST_FINDING_THRESHOLDS["shoulder_height_asymmetry"],
        ),
        confidence="high",
        view=normalized_view,
        related_metrics=["shoulder_height_difference"],
    )

    left_protraction = _metric_value(metrics, "shoulder_protraction_angle_left")
    right_protraction = _metric_value(metrics, "shoulder_protraction_angle_right")
    bilateral_protraction_value = min(left_protraction, right_protraction) if left_protraction is not None and right_protraction is not None else None
    _append_finding(
        items,
        finding_id="bilateral_shoulder_protraction",
        label="Bilateral shoulder protraction",
        summary="Proxy-based sagittal finding suggesting both shoulders present a protracted resting tendency.",
        severity=_classify_greater(
            bilateral_protraction_value,
            REST_FINDING_THRESHOLDS["bilateral_shoulder_protraction"],
        ),
        confidence="medium",
        view=normalized_view,
        related_metrics=["shoulder_protraction_angle_left", "shoulder_protraction_angle_right"],
    )

    _append_finding(
        items,
        finding_id="shoulder_protraction_left",
        label="Left shoulder protraction bias",
        summary="Proxy-based sagittal finding suggesting a left-sided protracted shoulder resting tendency.",
        severity=_classify_greater(
            left_protraction,
            REST_FINDING_THRESHOLDS["shoulder_protraction_left"],
        ),
        confidence="medium",
        view=normalized_view,
        related_metrics=["shoulder_protraction_angle_left"],
    )

    _append_finding(
        items,
        finding_id="shoulder_protraction_right",
        label="Right shoulder protraction bias",
        summary="Proxy-based sagittal finding suggesting a right-sided protracted shoulder resting tendency.",
        severity=_classify_greater(
            right_protraction,
            REST_FINDING_THRESHOLDS["shoulder_protraction_right"],
        ),
        confidence="medium",
        view=normalized_view,
        related_metrics=["shoulder_protraction_angle_right"],
    )

    _append_finding(
        items,
        finding_id="scapular_elevation_asymmetry",
        label="Scapular elevation asymmetry",
        summary="Static baseline finding suggesting asymmetric scapular elevation at rest.",
        severity=_classify_greater(
            _metric_value(metrics, "scapular_elevation_difference"),
            REST_FINDING_THRESHOLDS["scapular_elevation_asymmetry"],
        ),
        confidence=_metric_confidence(metrics, "scapular_elevation_difference", fallback="medium"),
        view=normalized_view,
        related_metrics=["scapular_elevation_difference"],
        weight=_finding_weight("scapular_elevation_asymmetry"),
    )

    _append_finding(
        items,
        finding_id="scapular_position_asymmetry",
        label="Scapular position asymmetry",
        summary="Static baseline finding suggesting asymmetric scapular resting position at rest.",
        severity=_classify_greater(
            _metric_value(metrics, "scapular_symmetry_index"),
            REST_FINDING_THRESHOLDS["scapular_position_asymmetry"],
        ),
        confidence=_metric_confidence(metrics, "scapular_symmetry_index", fallback="medium"),
        view=normalized_view,
        related_metrics=["scapular_symmetry_index"],
        weight=_finding_weight("scapular_position_asymmetry"),
    )

    winging_severity = _classify_greater(
        _metric_value(metrics, "winging_index"),
        REST_FINDING_THRESHOLDS["possible_winging_bias"],
    )
    _append_finding(
        items,
        finding_id="possible_winging_bias",
        label="Possible winging bias",
        summary="Proxy-based finding suggesting a possible scapular winging tendency that should be validated with dynamic analysis.",
        severity=winging_severity,
        confidence=_metric_confidence(metrics, "winging_index", fallback="low"),
        view=normalized_view,
        related_metrics=["winging_index"],
        weight=_finding_weight("possible_winging_bias"),
    )

    _append_finding(
        items,
        finding_id="pelvic_forward_backward_bias",
        label="Pelvic forward/backward bias",
        summary=(
            "Direct sagittal finding suggesting an anterior pelvic drift relative to the ankle base."
            if (_metric_value(metrics, "pelvic_ankle_sagittal_offset") or 0.0) > 0
            else "Direct sagittal finding suggesting a posterior pelvic drift relative to the ankle base."
        ),
        severity=_classify_absolute(
            _metric_value(metrics, "pelvic_ankle_sagittal_offset"),
            REST_FINDING_THRESHOLDS["pelvic_forward_backward_bias"],
        ),
        confidence="high",
        view=normalized_view,
        related_metrics=["pelvic_ankle_sagittal_offset"],
    )

    pelvic_transverse_value = _metric_value(metrics, "pelvic_transverse_rotation")
    _append_finding(
        items,
        finding_id="pelvic_transverse_rotation_bias",
        label="Pelvic transverse rotation bias",
        summary=(
            "Proxy-based transverse finding suggesting an apparent right pelvic rotation bias."
            if (pelvic_transverse_value or 0.0) > 0
            else "Proxy-based transverse finding suggesting an apparent left pelvic rotation bias."
        ),
        severity=_classify_absolute(
            pelvic_transverse_value,
            REST_FINDING_THRESHOLDS["pelvic_transverse_rotation_bias"],
        ),
        confidence="medium",
        view=normalized_view,
        related_metrics=["pelvic_transverse_rotation"],
    )

    if normalized_view == "back":
        _append_finding(
            items,
            finding_id="left_scapular_protraction_bias",
            label="Possible left scapular protraction asymmetry",
            summary="Proxy-based posterior finding suggesting possible left scapular protraction asymmetry at rest.",
            severity=_classify_greater(
                _metric_value(metrics, "scapula_spine_distance_left"),
                REST_FINDING_THRESHOLDS["left_scapular_protraction_bias"],
            ),
            confidence=_metric_confidence(metrics, "scapula_spine_distance_left", fallback="low"),
            view=normalized_view,
            related_metrics=["scapula_spine_distance_left"],
            weight=_finding_weight("left_scapular_protraction_bias"),
        )

        _append_finding(
            items,
            finding_id="right_scapular_protraction_bias",
            label="Possible right scapular protraction asymmetry",
            summary="Proxy-based posterior finding suggesting possible right scapular protraction asymmetry at rest.",
            severity=_classify_greater(
                _metric_value(metrics, "scapula_spine_distance_right"),
                REST_FINDING_THRESHOLDS["right_scapular_protraction_bias"],
            ),
            confidence=_metric_confidence(metrics, "scapula_spine_distance_right", fallback="low"),
            view=normalized_view,
            related_metrics=["scapula_spine_distance_right"],
            weight=_finding_weight("right_scapular_protraction_bias"),
        )

        _append_finding(
            items,
            finding_id="scapular_internal_rotation_bias_left",
            label="Left scapular orientation asymmetry (proxy-based)",
            summary="Proxy-based posterior finding suggesting possible left scapular orientation asymmetry at rest.",
            severity=_classify_greater(
                _metric_value(metrics, "scapular_internal_rotation_left"),
                REST_FINDING_THRESHOLDS["scapular_internal_rotation_bias_left"],
            ),
            confidence=_metric_confidence(metrics, "scapular_internal_rotation_left", fallback="low"),
            view=normalized_view,
            related_metrics=["scapular_internal_rotation_left"],
            weight=_finding_weight("scapular_internal_rotation_bias_left"),
        )

        _append_finding(
            items,
            finding_id="scapular_internal_rotation_bias_right",
            label="Right scapular orientation asymmetry (proxy-based)",
            summary="Proxy-based posterior finding suggesting possible right scapular orientation asymmetry at rest.",
            severity=_classify_greater(
                _metric_value(metrics, "scapular_internal_rotation_right"),
                REST_FINDING_THRESHOLDS["scapular_internal_rotation_bias_right"],
            ),
            confidence=_metric_confidence(metrics, "scapular_internal_rotation_right", fallback="low"),
            view=normalized_view,
            related_metrics=["scapular_internal_rotation_right"],
            weight=_finding_weight("scapular_internal_rotation_bias_right"),
        )

        _append_finding(
            items,
            finding_id="scapular_upward_rotation_bias_left",
            label="Left scapular orientation asymmetry (proxy-based)",
            summary="Proxy-based posterior finding suggesting possible left scapular orientation asymmetry at rest.",
            severity=_classify_greater(
                _metric_value(metrics, "scapular_upward_rotation_left"),
                REST_FINDING_THRESHOLDS["scapular_upward_rotation_bias_left"],
            ),
            confidence=_metric_confidence(metrics, "scapular_upward_rotation_left", fallback="low"),
            view=normalized_view,
            related_metrics=["scapular_upward_rotation_left"],
            weight=_finding_weight("scapular_upward_rotation_bias_left"),
        )

        _append_finding(
            items,
            finding_id="scapular_upward_rotation_bias_right",
            label="Right scapular orientation asymmetry (proxy-based)",
            summary="Proxy-based posterior finding suggesting possible right scapular orientation asymmetry at rest.",
            severity=_classify_greater(
                _metric_value(metrics, "scapular_upward_rotation_right"),
                REST_FINDING_THRESHOLDS["scapular_upward_rotation_bias_right"],
            ),
            confidence=_metric_confidence(metrics, "scapular_upward_rotation_right", fallback="low"),
            view=normalized_view,
            related_metrics=["scapular_upward_rotation_right"],
            weight=_finding_weight("scapular_upward_rotation_bias_right"),
        )

        left_votes, right_votes = _dominance_votes(metrics)
        if winging_severity is not None and left_votes >= 2:
            items.append(
                _build_finding(
                    finding_id="possible_left_winging_bias",
                    label="Possible left winging bias",
                    summary="Low-confidence posterior finding suggesting a possible left-sided scapular winging tendency based on multiple proxy asymmetries.",
                    severity=winging_severity,
                    confidence=_metric_confidence(metrics, "winging_index", "scapula_spine_distance_left", "scapular_internal_rotation_left", fallback="low"),
                    view=normalized_view,
                    related_metrics=["winging_index", "scapula_spine_distance_left", "scapular_internal_rotation_left"],
                    weight=_finding_weight("possible_left_winging_bias"),
                )
            )
        if winging_severity is not None and right_votes >= 2:
            items.append(
                _build_finding(
                    finding_id="possible_right_winging_bias",
                    label="Possible right winging bias",
                    summary="Low-confidence posterior finding suggesting a possible right-sided scapular winging tendency based on multiple proxy asymmetries.",
                    severity=winging_severity,
                    confidence=_metric_confidence(metrics, "winging_index", "scapula_spine_distance_right", "scapular_internal_rotation_right", fallback="low"),
                    view=normalized_view,
                    related_metrics=["winging_index", "scapula_spine_distance_right", "scapular_internal_rotation_right"],
                    weight=_finding_weight("possible_right_winging_bias"),
                )
            )

    if normalized_view == "side":
        _append_finding(
            items,
            finding_id="scapular_anterior_tilt_bias_left",
            label="Left scapular anterior tilt bias",
            summary="Low-confidence sagittal proxy suggesting a left-sided anterior scapular tilt tendency from single-image pose data.",
            severity=_classify_greater(
                _metric_value(metrics, "scapular_anterior_tilt_left"),
                REST_FINDING_THRESHOLDS["scapular_anterior_tilt_bias_left"],
            ),
            confidence="low",
            view=normalized_view,
            related_metrics=["scapular_anterior_tilt_left"],
        )

        _append_finding(
            items,
            finding_id="scapular_anterior_tilt_bias_right",
            label="Right scapular anterior tilt bias",
            summary="Low-confidence sagittal proxy suggesting a right-sided anterior scapular tilt tendency from single-image pose data.",
            severity=_classify_greater(
                _metric_value(metrics, "scapular_anterior_tilt_right"),
                REST_FINDING_THRESHOLDS["scapular_anterior_tilt_bias_right"],
            ),
            confidence="low",
            view=normalized_view,
            related_metrics=["scapular_anterior_tilt_right"],
        )

    items.sort(key=_sort_key, reverse=True)
    return FindingsResult(status="completed", items=items, ready_for_detection=True)


def _scapula_rest_side_from_group(group_payload: dict[str, Any] | None) -> str | None:
    if not isinstance(group_payload, dict):
        return None
    debug_payload = group_payload.get("debug")
    if not isinstance(debug_payload, dict):
        return None
    landmarks = debug_payload.get("landmarks")
    if not isinstance(landmarks, dict):
        return None
    left_shoulder = landmarks.get("left_shoulder")
    right_shoulder = landmarks.get("right_shoulder")
    if not isinstance(left_shoulder, dict) or not isinstance(right_shoulder, dict):
        return None
    left_y = left_shoulder.get("y")
    right_y = right_shoulder.get("y")
    if not isinstance(left_y, (int, float)) or not isinstance(right_y, (int, float)):
        return None
    if abs(float(left_y) - float(right_y)) < 1e-3:
        return None
    return "left" if float(left_y) < float(right_y) else "right"


def detect_scapula_rest_findings(group_payload: dict[str, Any]) -> FindingsResult:
    """Generate scapula-rest findings for the dedicated baseline scapular group."""
    metrics = group_payload.get("metrics", {}) if isinstance(group_payload, dict) else {}
    if not isinstance(metrics, dict):
        metrics = {}

    items: list[Finding] = []
    elevated_side = _scapula_rest_side_from_group(group_payload)

    elevation_value = _metric_value(metrics, "scapular_elevation_difference")
    elevation_severity = _classify_greater(
        elevation_value,
        REST_FINDING_THRESHOLDS["scapular_elevation_asymmetry"],
    )
    if elevation_value is not None and elevation_value > 0.03 and elevation_severity is not None:
        side_text = f" with the {elevated_side} side resting higher" if elevated_side in {"left", "right"} else ""
        _append_finding(
            items,
            finding_id="scapular_elevation_asymmetry",
            label="Asimetria de elevacion escapular",
            summary=f"El baseline estatico muestra una asimetria de elevacion escapular{side_text}.",
            severity=elevation_severity,
            confidence=_metric_confidence(metrics, "scapular_elevation_difference", fallback="medium"),
            view="back",
            related_metrics=["scapular_elevation_difference"],
            side=elevated_side,
            weight=1.0,
        )
    else:
        items.append(
            _build_finding(
                finding_id="static_scapular_symmetry",
                label="Simetria escapular estatica",
                summary="Las metricas robustas no muestran una asimetria clara de elevacion escapular en reposo.",
                severity="mild",
                confidence=_metric_confidence(metrics, "scapular_elevation_difference", "scapular_symmetry_index", fallback="medium"),
                view="back",
                related_metrics=["scapular_elevation_difference", "scapular_symmetry_index"],
                weight=0.0,
            )
        )

    geometry_value = _metric_value(metrics, "scapular_symmetry_index")
    geometry_severity = _classify_greater(
        geometry_value,
        ThresholdBand(mild=0.05, moderate=0.10, severe=0.18),
    )
    if geometry_value is not None and geometry_value > 0.05 and geometry_severity is not None:
        _append_finding(
            items,
            finding_id="scapular_geometric_asymmetry",
            label="Asimetria geometrica escapular",
            summary="El indice de simetria sugiere un desequilibrio escapulotoracico global en reposo.",
            severity=geometry_severity,
            confidence=_metric_confidence(metrics, "scapular_symmetry_index", fallback="medium"),
            view="back",
            related_metrics=["scapular_symmetry_index"],
            weight=0.9,
        )

    left_distance = _metric_value(metrics, "scapula_spine_distance_left")
    right_distance = _metric_value(metrics, "scapula_spine_distance_right")
    if left_distance is not None and right_distance is not None:
        distance_delta = abs(right_distance - left_distance)
        protraction_side = "right" if right_distance > left_distance else "left" if left_distance > right_distance else "none"
        protraction_severity = _classify_greater(distance_delta, ThresholdBand(mild=0.10, moderate=0.16, severe=0.24))
        if distance_delta > 0.10 and protraction_severity is not None:
            _append_finding(
                items,
                finding_id="possible_scapular_protraction_asymmetry",
                label="Posible asimetria de protraccion escapular",
                summary=f"La diferencia de distancia a la linea media sugiere una posible protraccion escapular {protraction_side} (proxy-based).",
                severity=protraction_severity,
                confidence=_metric_confidence(metrics, "scapula_spine_distance_left", "scapula_spine_distance_right", fallback="low"),
                view="back",
                related_metrics=["scapula_spine_distance_left", "scapula_spine_distance_right"],
                side=protraction_side if protraction_side != "none" else None,
                weight=0.5,
            )

    internal_threshold = 60.0
    for side in ("left", "right"):
        metric_name = f"scapular_internal_rotation_{side}"
        value = _metric_value(metrics, metric_name)
        severity = _classify_greater(value, ThresholdBand(mild=60.0, moderate=70.0, severe=80.0))
        if value is not None and value > internal_threshold and severity is not None:
            _append_finding(
                items,
                finding_id=f"possible_internal_rotation_increase_{side}",
                label="Posible rotacion interna escapular aumentada",
                summary=f"La orientacion posterior sugiere una posible rotacion interna escapular aumentada en el lado {side} (proxy-based).",
                severity=severity,
                confidence=_metric_confidence(metrics, metric_name, fallback="low"),
                view="back",
                related_metrics=[metric_name],
                side=side,
                weight=0.3,
            )

    winging_value = _metric_value(metrics, "winging_index")
    winging_severity = _classify_greater(winging_value, ThresholdBand(mild=0.20, moderate=0.30, severe=0.45))
    if winging_value is not None and winging_value > 0.20 and winging_severity is not None:
        _append_finding(
            items,
            finding_id="possible_static_winging",
            label="Posible winging escapular en reposo",
            summary="El indice de winging sugiere una posible prominencia escapular estatica en reposo (proxy-based).",
            severity=winging_severity,
            confidence=_metric_confidence(metrics, "winging_index", fallback="low"),
            view="back",
            related_metrics=["winging_index"],
            weight=0.5,
        )
    else:
        items.append(
            _build_finding(
                finding_id="no_static_winging",
                label="Ausencia de winging estatico",
                summary="El baseline no muestra una senal relevante de winging escapular estatico.",
                severity="mild",
                confidence=_metric_confidence(metrics, "winging_index", fallback="medium"),
                view="back",
                related_metrics=["winging_index"],
                weight=0.0,
            )
        )

    left_upward = _metric_value(metrics, "scapular_upward_rotation_left")
    right_upward = _metric_value(metrics, "scapular_upward_rotation_right")
    if left_upward is not None and right_upward is not None:
        upward_delta = abs(left_upward - right_upward)
        upward_side = "left" if left_upward > right_upward else "right" if right_upward > left_upward else None
        upward_severity = _classify_greater(upward_delta, ThresholdBand(mild=5.0, moderate=10.0, severe=20.0))
        if upward_delta > 5.0 and upward_severity is not None:
            _append_finding(
                items,
                finding_id="scapular_upward_rotation_asymmetry",
                label="Asimetria de rotacion superior escapular",
                summary="La diferencia angular entre lados sugiere una asimetria de rotacion superior escapular (proxy-based).",
                severity=upward_severity,
                confidence=_metric_confidence(metrics, "scapular_upward_rotation_left", "scapular_upward_rotation_right", fallback="low"),
                view="back",
                related_metrics=["scapular_upward_rotation_left", "scapular_upward_rotation_right"],
                side=upward_side,
                weight=0.3,
            )
        else:
            items.append(
                _build_finding(
                    finding_id="leveled_scapular_orientation",
                    label="Orientacion escapular nivelada",
                    summary="La orientacion escapular posterior se mantiene relativamente nivelada entre ambos lados en este baseline.",
                    severity="mild",
                    confidence=_metric_confidence(metrics, "scapular_upward_rotation_left", "scapular_upward_rotation_right", fallback="medium"),
                    view="back",
                    related_metrics=["scapular_upward_rotation_left", "scapular_upward_rotation_right"],
                    weight=0.0,
                )
            )

    items.sort(key=_sort_key, reverse=True)
    return FindingsResult(status="completed", items=items, ready_for_detection=True)


__all__ = ["detect_rest_findings", "detect_scapula_rest_findings", "detect_foot_triptych_findings"]


def detect_foot_triptych_findings(metrics: MetricMap) -> FindingsResult:
    """Convert foot-triptych metrics plus geometric classifications into biomechanical findings."""
    items: list[Finding] = []

    def classification(name: str) -> str | None:
        metric = metrics.get(name)
        if not isinstance(metric, dict):
            return None
        status = metric.get("status")
        if status not in {"computed", "low_confidence"}:
            return None
        value = metric.get("classification")
        return str(value) if isinstance(value, str) and value else None

    def metric_confidence(name: str) -> str:
        metric = metrics.get(name)
        if not isinstance(metric, dict):
            return "low"
        confidence = metric.get("confidence")
        return _confidence_from_numeric(float(confidence)) if isinstance(confidence, (int, float)) else "low"

    left_calc = classification("calcaneal_angle_left")
    right_calc = classification("calcaneal_angle_right")
    left_prog = classification("foot_progression_angle_left")
    right_prog = classification("foot_progression_angle_right")
    left_arch = classification("arch_height_ratio_left")
    right_arch = classification("arch_height_ratio_right")
    left_arch_value = _metric_value(metrics, "arch_height_ratio_left")
    right_arch_value = _metric_value(metrics, "arch_height_ratio_right")
    left_calc_value = _metric_value(metrics, "calcaneal_angle_left")
    right_calc_value = _metric_value(metrics, "calcaneal_angle_right")

    if left_calc and left_calc.startswith("valgus"):
        items.append(
            _build_finding(
                finding_id="rearfoot_pronation_left",
                label="Left rearfoot pronation pattern",
                summary="Rearfoot geometry suggests a left-sided pronation / valgus tendency.",
                severity="moderate" if left_calc in {"valgus_moderate", "valgus_severe"} else "mild",
                confidence=metric_confidence("calcaneal_angle_left"),
                view="back",
                related_metrics=["calcaneal_angle_left"],
            )
        )
    if right_calc and right_calc.startswith("valgus"):
        items.append(
            _build_finding(
                finding_id="rearfoot_pronation_right",
                label="Right rearfoot pronation pattern",
                summary="Rearfoot geometry suggests a right-sided pronation / valgus tendency.",
                severity="moderate" if right_calc in {"valgus_moderate", "valgus_severe"} else "mild",
                confidence=metric_confidence("calcaneal_angle_right"),
                view="back",
                related_metrics=["calcaneal_angle_right"],
            )
        )
    if left_calc_value is not None and right_calc_value is not None and abs(left_calc_value - right_calc_value) >= 5.0:
        items.append(
            _build_finding(
                finding_id="rearfoot_asymmetry",
                label="Rearfoot asymmetry",
                summary="Rearfoot alignment differs meaningfully between left and right sides.",
                severity="moderate" if abs(left_calc_value - right_calc_value) >= 10.0 else "mild",
                confidence=_confidence_from_numeric(
                    min(
                        float(metrics.get("calcaneal_angle_left", {}).get("confidence") or 0.0),
                        float(metrics.get("calcaneal_angle_right", {}).get("confidence") or 0.0),
                    )
                ),
                view="back",
                related_metrics=["calcaneal_angle_left", "calcaneal_angle_right"],
            )
        )

    for side in ("left", "right"):
        prog_class = classification(f"foot_progression_angle_{side}")
        if prog_class == "toe_in":
            items.append(
                _build_finding(
                    finding_id=f"{side}_toe_in_pattern",
                    label=f"{side.capitalize()} toe-in pattern",
                    summary=f"Foot progression geometry suggests a {side}-sided toe-in tendency.",
                    severity="moderate",
                    confidence=metric_confidence(f"foot_progression_angle_{side}"),
                    view="front",
                    related_metrics=[f"foot_progression_angle_{side}"],
                )
            )
        elif prog_class == "toe_out":
            items.append(
                _build_finding(
                    finding_id=f"external_rotation_foot_{side}",
                    label=f"{side.capitalize()} toe-out pattern",
                    summary=f"Foot progression geometry suggests a {side}-sided toe-out tendency.",
                    severity="moderate",
                    confidence=metric_confidence(f"foot_progression_angle_{side}"),
                    view="front",
                    related_metrics=[f"foot_progression_angle_{side}"],
                )
            )

    for side in ("left", "right"):
        arch_class = classification(f"arch_height_ratio_{side}")
        if arch_class == "low_arch":
            items.append(
                _build_finding(
                    finding_id=f"medial_arch_collapse_{side}",
                    label=f"{side.capitalize()} low arch pattern",
                    summary=f"Arch-height geometry suggests a lower medial arch on the {side} side.",
                    severity="moderate",
                    confidence=metric_confidence(f"arch_height_ratio_{side}"),
                    view=f"{side}_arch",
                    related_metrics=[f"arch_height_ratio_{side}"],
                )
            )
    if left_arch_value is not None and right_arch_value is not None and abs(left_arch_value - right_arch_value) >= 0.02:
        items.append(
            _build_finding(
                finding_id="arch_height_asymmetry",
                label="Arch height asymmetry",
                summary="Arch-height geometry differs meaningfully between left and right sides.",
                severity="moderate" if abs(left_arch_value - right_arch_value) >= 0.04 else "mild",
                confidence=_confidence_from_numeric(
                    min(
                        float(metrics.get("arch_height_ratio_left", {}).get("confidence") or 0.0),
                        float(metrics.get("arch_height_ratio_right", {}).get("confidence") or 0.0),
                    )
                ),
                view="front",
                related_metrics=["arch_height_ratio_left", "arch_height_ratio_right"],
            )
        )

    return FindingsResult(status="completed", items=items, ready_for_detection=True)
