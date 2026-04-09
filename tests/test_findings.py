"""Unit tests for rule-based resting findings."""

from __future__ import annotations

from detection.findings import detect_rest_findings, detect_scapula_rest_findings


def _metric(
    name: str,
    value: float | None,
    *,
    status: str = "computed",
    plane: str = "frontal",
    unit: str = "degrees",
    measurement_type: str = "direct",
    priority: str = "P0",
    confidence: float | None = None,
) -> dict[str, object]:
    payload = {
        "name": name,
        "value": value,
        "plane": plane,
        "unit": unit,
        "measurement_type": measurement_type,
        "priority": priority,
        "status": status,
    }
    if confidence is not None:
        payload["confidence"] = confidence
    return payload


def test_detect_rest_findings_generates_basic_sagittal_findings() -> None:
    """Side-view metrics should generate both v1 and v2 sagittal findings when supported."""
    metrics = {
        "forward_center_of_mass_offset": _metric(
            "forward_center_of_mass_offset",
            0.20,
            plane="sagittal",
            unit="normalized",
            measurement_type="proxy",
        ),
        "thoracic_kyphosis_angle": _metric(
            "thoracic_kyphosis_angle",
            18.0,
            plane="sagittal",
            measurement_type="proxy",
        ),
        "thoracic_flattening_index": _metric(
            "thoracic_flattening_index",
            0.99,
            plane="sagittal",
            unit="index",
            measurement_type="compound_index",
        ),
        "cranio_shoulder_angle": _metric(
            "cranio_shoulder_angle",
            45.0,
            plane="sagittal",
            measurement_type="proxy",
        ),
        "shoulder_protraction_angle_left": _metric(
            "shoulder_protraction_angle_left",
            35.0,
            plane="sagittal",
            measurement_type="proxy",
        ),
        "shoulder_protraction_angle_right": _metric(
            "shoulder_protraction_angle_right",
            28.0,
            plane="sagittal",
            measurement_type="proxy",
        ),
        "scapular_anterior_tilt_left": _metric(
            "scapular_anterior_tilt_left",
            168.0,
            plane="sagittal",
            measurement_type="proxy",
        ),
        "scapular_anterior_tilt_right": _metric(
            "scapular_anterior_tilt_right",
            150.0,
            plane="sagittal",
            measurement_type="proxy",
        ),
        "pelvic_ankle_sagittal_offset": _metric(
            "pelvic_ankle_sagittal_offset",
            0.14,
            plane="sagittal",
            unit="normalized",
            measurement_type="direct",
        ),
        "shoulder_height_difference": _metric(
            "shoulder_height_difference",
            None,
            status="not_applicable_for_view",
            plane="frontal",
            unit="normalized",
        ),
    }

    result = detect_rest_findings(metrics, view="side")
    ids = {item.id for item in result.items}

    assert result.status == "completed"
    assert {
        "forward_postural_bias",
        "thoracic_kyphosis_bias",
        "thoracic_flattening_bias",
        "forward_head_posture",
        "bilateral_shoulder_protraction",
        "shoulder_protraction_left",
        "shoulder_protraction_right",
        "pelvic_forward_backward_bias",
        "scapular_anterior_tilt_bias_left",
    }.issubset(ids)
    assert "shoulder_height_asymmetry" not in ids
    assert "scapular_anterior_tilt_bias_right" not in ids


def test_detect_rest_findings_generates_back_lateralized_scapular_findings() -> None:
    """Back view should emit side-specific scapular findings only when proxy support is strong enough."""
    metrics = {
        "scapula_spine_distance_left": _metric(
            "scapula_spine_distance_left",
            0.50,
            plane="frontal",
            unit="normalized",
            measurement_type="proxy",
        ),
        "scapula_spine_distance_right": _metric(
            "scapula_spine_distance_right",
            0.30,
            plane="frontal",
            unit="normalized",
            measurement_type="proxy",
        ),
        "scapular_internal_rotation_left": _metric(
            "scapular_internal_rotation_left",
            60.0,
            plane="transverse",
            measurement_type="proxy",
        ),
        "scapular_internal_rotation_right": _metric(
            "scapular_internal_rotation_right",
            38.0,
            plane="transverse",
            measurement_type="proxy",
        ),
        "scapular_upward_rotation_left": _metric(
            "scapular_upward_rotation_left",
            150.0,
            plane="transverse",
            measurement_type="proxy",
        ),
        "scapular_upward_rotation_right": _metric(
            "scapular_upward_rotation_right",
            60.0,
            plane="transverse",
            measurement_type="proxy",
        ),
        "winging_index": _metric(
            "winging_index",
            0.34,
            plane="transverse",
            unit="index",
            measurement_type="compound_index",
        ),
        "scapular_position_asymmetry": _metric(
            "scapular_position_asymmetry",
            0.20,
            plane="frontal",
            unit="index",
            measurement_type="compound_index",
        ),
    }

    result = detect_rest_findings(metrics, view="back")
    ids = {item.id for item in result.items}

    assert {
        "left_scapular_protraction_bias",
        "scapular_internal_rotation_bias_left",
        "scapular_upward_rotation_bias_left",
        "possible_left_winging_bias",
        "possible_winging_bias",
    }.issubset(ids)
    assert "right_scapular_protraction_bias" not in ids
    assert "possible_right_winging_bias" not in ids

    left_protraction = next(item for item in result.items if item.id == "left_scapular_protraction_bias")
    elevation = next(item for item in result.items if item.id == "scapular_elevation_asymmetry") if "scapular_elevation_asymmetry" in ids else None
    assert left_protraction.label == "Possible left scapular protraction asymmetry"
    assert "possible left scapular protraction asymmetry" in left_protraction.summary.lower()
    assert left_protraction.weight == 0.5
    if elevation is not None:
        assert elevation.weight == 1.0


def test_detect_rest_findings_respects_metric_applicability_and_view_specific_lateralization() -> None:
    """Front view should ignore back-only lateralized scapular findings even with transverse metrics present."""
    metrics = {
        "scapula_spine_distance_left": _metric(
            "scapula_spine_distance_left",
            0.50,
            plane="frontal",
            unit="normalized",
            measurement_type="proxy",
        ),
        "scapula_spine_distance_right": _metric(
            "scapula_spine_distance_right",
            0.30,
            plane="frontal",
            unit="normalized",
            measurement_type="proxy",
        ),
        "scapular_internal_rotation_left": _metric(
            "scapular_internal_rotation_left",
            60.0,
            plane="transverse",
            measurement_type="proxy",
        ),
        "scapular_internal_rotation_right": _metric(
            "scapular_internal_rotation_right",
            38.0,
            plane="transverse",
            measurement_type="proxy",
        ),
        "winging_index": _metric(
            "winging_index",
            0.34,
            plane="transverse",
            unit="index",
            measurement_type="compound_index",
        ),
        "shoulder_height_difference": _metric(
            "shoulder_height_difference",
            0.06,
            plane="frontal",
            unit="normalized",
        ),
    }

    result = detect_rest_findings(metrics, view="front")
    ids = {item.id for item in result.items}

    assert "possible_winging_bias" in ids
    assert "left_scapular_protraction_bias" not in ids
    assert "possible_left_winging_bias" not in ids
    assert "scapular_internal_rotation_bias_left" not in ids


def test_detect_rest_findings_emits_pelvic_transverse_rotation_bias_when_supported() -> None:
    """Front/back-compatible transverse pelvic bias should be emitted only above threshold."""
    metrics = {
        "pelvic_transverse_rotation": _metric(
            "pelvic_transverse_rotation",
            0.18,
            plane="transverse",
            unit="index",
            measurement_type="proxy",
        )
    }

    result = detect_rest_findings(metrics, view="back")
    pelvic_rotation = next(item for item in result.items if item.id == "pelvic_transverse_rotation_bias")

    assert pelvic_rotation.severity == "moderate"
    assert pelvic_rotation.confidence == "medium"
    assert pelvic_rotation.related_metrics == ["pelvic_transverse_rotation"]



def test_detect_rest_findings_uses_metric_confidence_and_accepts_low_confidence_proxy_metrics() -> None:
    metrics = {
        "scapular_elevation_difference": _metric(
            "scapular_elevation_difference",
            0.06,
            plane="frontal",
            unit="normalized",
            measurement_type="proxy",
            confidence=0.82,
        ),
        "scapular_symmetry_index": _metric(
            "scapular_symmetry_index",
            0.18,
            plane="frontal",
            unit="index",
            measurement_type="compound_index",
            confidence=0.76,
        ),
        "scapula_spine_distance_left": _metric(
            "scapula_spine_distance_left",
            0.50,
            plane="frontal",
            unit="normalized",
            measurement_type="proxy",
            status="low_confidence",
            confidence=0.42,
        ),
        "scapula_spine_distance_right": _metric(
            "scapula_spine_distance_right",
            0.31,
            plane="frontal",
            unit="normalized",
            measurement_type="proxy",
            status="low_confidence",
            confidence=0.41,
        ),
        "winging_index": _metric(
            "winging_index",
            0.22,
            plane="transverse",
            unit="index",
            measurement_type="compound_index",
            status="low_confidence",
            confidence=0.40,
        ),
    }

    result = detect_rest_findings(metrics, view="back")
    by_id = {item.id: item for item in result.items}

    assert by_id["scapular_elevation_asymmetry"].confidence == "high"
    assert by_id["left_scapular_protraction_bias"].confidence == "low"
    assert by_id["possible_winging_bias"].confidence == "low"


def test_detect_scapula_rest_findings_builds_prudent_baseline_findings() -> None:
    group_payload = {
        "metrics": {
            "scapular_elevation_difference": _metric("scapular_elevation_difference", 0.04, plane="frontal", unit="normalized", measurement_type="proxy", confidence=0.82),
            "scapular_symmetry_index": _metric("scapular_symmetry_index", 0.08, plane="frontal", unit="index", measurement_type="compound_index", confidence=0.76),
            "scapula_spine_distance_left": _metric("scapula_spine_distance_left", 0.32, plane="frontal", unit="normalized", measurement_type="proxy", confidence=0.46),
            "scapula_spine_distance_right": _metric("scapula_spine_distance_right", 0.46, plane="frontal", unit="normalized", measurement_type="proxy", confidence=0.44),
            "scapular_internal_rotation_left": _metric("scapular_internal_rotation_left", 48.0, plane="transverse", measurement_type="proxy", confidence=0.44),
            "scapular_internal_rotation_right": _metric("scapular_internal_rotation_right", 68.0, plane="transverse", measurement_type="proxy", confidence=0.43),
            "scapular_upward_rotation_left": _metric("scapular_upward_rotation_left", 12.0, plane="transverse", measurement_type="proxy", confidence=0.42),
            "scapular_upward_rotation_right": _metric("scapular_upward_rotation_right", 20.0, plane="transverse", measurement_type="proxy", confidence=0.41),
            "winging_index": _metric("winging_index", 0.24, plane="transverse", unit="index", measurement_type="compound_index", confidence=0.40),
        },
        "debug": {
            "landmarks": {
                "left_shoulder": {"y": 0.31},
                "right_shoulder": {"y": 0.27},
            }
        },
    }

    result = detect_scapula_rest_findings(group_payload)
    by_id = {item.id: item for item in result.items}

    assert by_id["scapular_elevation_asymmetry"].side == "right"
    assert by_id["possible_scapular_protraction_asymmetry"].side == "right"
    assert by_id["possible_static_winging"].confidence == "low"
    assert by_id["scapular_upward_rotation_asymmetry"].weight == 0.3
