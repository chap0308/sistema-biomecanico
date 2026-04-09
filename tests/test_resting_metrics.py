"""Unit tests for resting posture biomechanical metrics."""

from math import isclose, isnan

from biomechanics.models import RestingLandmarks
from biomechanics.resting_metrics import (
    P0_METRIC_SPECS,
    P1_PLACEHOLDER_SPECS,
    clavicle_orientation,
    compute_resting_metrics,
    forward_center_of_mass_offset,
    head_tilt_angle,
    pelvic_tilt,
    pelvic_ankle_sagittal_offset,
    pelvic_transverse_rotation,
    rib_flare_asymmetry,
    scapula_spine_distance_left,
    scapula_spine_distance_right,
    shoulder_height_difference,
    thoracic_flattening_index,
    thoracic_kyphosis_angle,
    thorax_pelvis_rotation,
    torso_lateral_tilt,
    winging_index,
)


def _balanced_landmarks() -> RestingLandmarks:
    return RestingLandmarks.from_mapping(
        {
            "nose": (0.50, 0.15),
            "left_ear": (0.44, 0.20),
            "right_ear": (0.56, 0.20),
            "left_shoulder": (0.42, 0.30),
            "right_shoulder": (0.58, 0.30),
            "left_elbow": (0.38, 0.45),
            "right_elbow": (0.62, 0.45),
            "left_hip": (0.45, 0.55),
            "right_hip": (0.55, 0.55),
            "left_knee": (0.46, 0.75),
            "right_knee": (0.54, 0.75),
            "left_ankle": (0.47, 0.95),
            "right_ankle": (0.53, 0.95),
        }
    )


def _mirrored_back_landmarks() -> RestingLandmarks:
    return RestingLandmarks.from_mapping(
        {
            "nose": (0.50, 0.15),
            "left_ear": (0.56, 0.20),
            "right_ear": (0.44, 0.20),
            "left_shoulder": (0.58, 0.30),
            "right_shoulder": (0.42, 0.30),
            "left_elbow": (0.62, 0.45),
            "right_elbow": (0.38, 0.45),
            "left_hip": (0.55, 0.55),
            "right_hip": (0.45, 0.55),
            "left_knee": (0.54, 0.75),
            "right_knee": (0.46, 0.75),
            "left_ankle": (0.53, 0.95),
            "right_ankle": (0.47, 0.95),
        }
    )


def _side_proxy_landmarks() -> RestingLandmarks:
    return RestingLandmarks.from_mapping(
        {
            "nose": (0.40, 0.15),
            "left_ear": (0.46, 0.12),
            "right_ear": (0.44, 0.12),
            "left_shoulder": (0.61, 0.23),
            "right_shoulder": (0.46, 0.23),
            "left_elbow": (0.50, 0.38),
            "right_elbow": (0.47, 0.38),
            "left_hip": (0.53, 0.48),
            "right_hip": (0.50, 0.48),
            "left_knee": (0.57, 0.68),
            "right_knee": (0.54, 0.68),
            "left_ankle": (0.60, 0.92),
            "right_ankle": (0.58, 0.92),
        }
    )


def test_balanced_posture_core_asymmetry_metrics_near_zero() -> None:
    """Symmetric synthetic posture should have low frontal asymmetry."""
    landmarks = _balanced_landmarks()

    assert shoulder_height_difference(landmarks) == 0.0
    assert isclose(
        scapula_spine_distance_left(landmarks),
        scapula_spine_distance_right(landmarks),
        rel_tol=0.0,
        abs_tol=1e-9,
    )
    assert torso_lateral_tilt(landmarks) == 0.0
    assert clavicle_orientation(landmarks) == 0.0
    assert pelvic_tilt(landmarks) == 0.0
    assert head_tilt_angle(landmarks) == 0.0
    assert isclose(forward_center_of_mass_offset(landmarks), 0.0, rel_tol=0.0, abs_tol=1e-9)
    assert 0.0 <= winging_index(landmarks) <= 1.0


def test_compute_resting_metrics_returns_refined_p0_and_p1_only() -> None:
    """Aggregator should expose P0 metrics plus explicit P1 placeholders when P1 is not yet viable."""
    landmarks = _balanced_landmarks()
    output = compute_resting_metrics(landmarks)

    assert len(output) == len(P0_METRIC_SPECS) + len(P1_PLACEHOLDER_SPECS)
    assert set(P0_METRIC_SPECS).issubset(output)
    assert set(P1_PLACEHOLDER_SPECS).issubset(output)
    assert "infra_sternal_angle" not in output
    assert "calcaneal_angle" not in output
    assert output["shoulder_height_difference"].unit == "normalized"
    assert output["thoracic_kyphosis_angle"].unit == "degrees"
    assert output["winging_index"].measurement_type == "compound_index"
    assert output["pelvic_transverse_rotation"].unit == "index"
    assert output["pelvic_ankle_sagittal_offset"].unit == "normalized"
    assert output["thorax_pelvis_rotation"].priority == "P1"
    assert isnan(output["thorax_pelvis_rotation"].value)
    assert isnan(output["rib_flare_asymmetry"].value)


def test_compute_resting_metrics_can_skip_placeholders() -> None:
    """Aggregator should optionally emit only implemented P0 metrics."""
    output = compute_resting_metrics(_balanced_landmarks(), include_placeholders=False)

    assert len(output) == len(P0_METRIC_SPECS)
    assert "thorax_pelvis_rotation" not in output
    assert "rib_flare_asymmetry" not in output


def test_asymmetric_shoulder_changes_height_metric() -> None:
    """Unilateral shoulder elevation should be reflected in the metric."""
    landmarks = RestingLandmarks.from_mapping(
        {
            "nose": (0.50, 0.15),
            "left_ear": (0.44, 0.20),
            "right_ear": (0.56, 0.20),
            "left_shoulder": (0.42, 0.26),
            "right_shoulder": (0.58, 0.30),
            "left_elbow": (0.38, 0.45),
            "right_elbow": (0.62, 0.45),
            "left_hip": (0.45, 0.55),
            "right_hip": (0.55, 0.55),
            "left_knee": (0.46, 0.75),
            "right_knee": (0.54, 0.75),
            "left_ankle": (0.47, 0.95),
            "right_ankle": (0.53, 0.95),
        }
    )

    assert shoulder_height_difference(landmarks) > 0.0


def test_refined_flow_metrics_have_stable_baseline_values() -> None:
    """Balanced synthetic posture should produce near-neutral implemented flow metrics."""
    landmarks = _balanced_landmarks()

    assert isclose(pelvic_transverse_rotation(landmarks), 0.0, rel_tol=0.0, abs_tol=1e-9)
    assert isclose(pelvic_ankle_sagittal_offset(landmarks), 0.0, rel_tol=0.0, abs_tol=1e-9)
    assert isnan(thoracic_kyphosis_angle(landmarks))
    assert isnan(thoracic_flattening_index(landmarks))


def test_p1_placeholders_remain_callable_and_explicit() -> None:
    """P1 metrics should remain callable placeholders returning NaN until richer capture is available."""
    landmarks = _balanced_landmarks()

    assert isnan(thorax_pelvis_rotation(landmarks))
    assert isnan(rib_flare_asymmetry(landmarks))


def test_pelvic_and_head_tilt_use_same_horizontal_deviation_convention_front_and_back() -> None:
    """Mirrored front/back point ordering should not flip between 0 and 180 degree conventions."""
    front = _balanced_landmarks()
    back = _mirrored_back_landmarks()

    assert isclose(pelvic_tilt(front), pelvic_tilt(back), rel_tol=0.0, abs_tol=1e-9)
    assert isclose(head_tilt_angle(front), head_tilt_angle(back), rel_tol=0.0, abs_tol=1e-9)


def test_thoracic_proxy_returns_low_confidence_metadata_instead_of_silent_zero() -> None:
    """Thoracic kyphosis should remain fragile and explicitly marked as such."""
    metrics = compute_resting_metrics(_side_proxy_landmarks(), include_placeholders=False)
    kyphosis = metrics["thoracic_kyphosis_angle"]
    flattening = metrics["thoracic_flattening_index"]

    assert kyphosis.value > 0.0
    assert kyphosis.status == "low_confidence"
    assert kyphosis.confidence is not None
    assert kyphosis.confidence < 0.55
    assert kyphosis.source_of_truth == "side_view_proxy"
    assert kyphosis.calculation_status == "proxy_from_profile_shoulder_offset"
    assert "fragile_thoracic_proxy" in kyphosis.flags
    assert kyphosis.quality_notes
    assert flattening.status == "low_confidence"


