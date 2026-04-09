"""Static resting posture metrics aligned with the refined clinical flow.

Only P0 metrics that are realistic with MediaPipe Pose are implemented here.
P1 metrics remain explicit placeholders, while P2 metrics are documented but
kept out of this module's API because they require FaceMesh, foot segmentation,
or a dedicated capture/modeling pipeline.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from math import atan2, degrees, isnan

from biomechanics.geometry import (
    angle_3p_deg,
    euclidean_distance_2d,
    line_angle_to_horizontal_deg,
    line_angle_to_vertical_deg,
    midpoint,
)
from biomechanics.models import BiomechanicsMetric, Point2D, RestingLandmarks
from biomechanics.normalization import normalize_by_reference

MetricFunction = Callable[[RestingLandmarks], float]
MetricSpec = tuple[str, str, str, MetricFunction]


THORACIC_PROXY_LOW_CONFIDENCE_NOTES = [
    "MediaPipe Pose does not expose thoracic vertebral landmarks, so this sagittal metric is only a proxy.",
    "The proxy uses profile-shoulder offset relative to the neck-pelvis axis and should not be interpreted as a vertebral Cobb-like angle.",
]

_SCAPULA_GROUP_A_METRICS = {
    "scapular_elevation_difference",
    "scapular_symmetry_index",
}

_SCAPULA_GROUP_B_METRICS = {
    "scapula_spine_distance_left",
    "scapula_spine_distance_right",
    "scapular_internal_rotation_left",
    "scapular_internal_rotation_right",
    "scapular_upward_rotation_left",
    "scapular_upward_rotation_right",
    "winging_index",
}

_SCAPULA_PROXY_QUALITY_NOTES = [
    "posterior_view_proxy",
    "scapula_not_directly_tracked",
    "acromion_based_estimation",
    "thorax_reference_proxy",
    "interpret_with_caution",
]

_SCAPULA_PROXY_FLAGS = [
    "fragile_scapular_proxy",
    "posterior_proxy_metric",
    "not_direct_scapula_measurement",
]


def _to_tuple(point: Point2D) -> tuple[float, float]:
    return (point.x, point.y)


def _point_above(point: Point2D, delta: float = 1.0) -> Point2D:
    return Point2D(x=point.x, y=point.y - delta)


def _bounded_ratio(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return max(0.0, min(1.0, numerator / denominator))


def _body_reference(landmarks: RestingLandmarks) -> float:
    trunk = euclidean_distance_2d(_to_tuple(neck_center(landmarks)), _to_tuple(pelvis_center(landmarks)))
    shoulder_span = euclidean_distance_2d(_to_tuple(landmarks.left_shoulder), _to_tuple(landmarks.right_shoulder))
    hip_span = euclidean_distance_2d(_to_tuple(landmarks.left_hip), _to_tuple(landmarks.right_hip))
    for candidate in (trunk, shoulder_span, hip_span, 1.0):
        if candidate > 0:
            return candidate
    return 1.0


def _normalize_distance(value: float, landmarks: RestingLandmarks) -> float:
    return normalize_by_reference(value, _body_reference(landmarks))


def _deviation_from_straight(angle: float) -> float:
    return abs(180.0 - angle)


def _deviation_from_horizontal(angle: float) -> float:
    normalized = abs(angle)
    return min(normalized, abs(180.0 - normalized))


def _distance_point_to_line(point: Point2D, line_start: Point2D, line_end: Point2D) -> float:
    x0, y0 = point.x, point.y
    x1, y1 = line_start.x, line_start.y
    x2, y2 = line_end.x, line_end.y
    denominator = euclidean_distance_2d((x1, y1), (x2, y2))
    if denominator == 0:
        return 0.0
    numerator = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
    return numerator / denominator


def _dominant_profile_shoulder(landmarks: RestingLandmarks) -> tuple[Point2D, str, float, float]:
    thorax = thoracic_center(landmarks)
    left_offset = abs(landmarks.left_shoulder.x - thorax.x)
    right_offset = abs(landmarks.right_shoulder.x - thorax.x)
    total = left_offset + right_offset
    dominance = 0.5 if total == 0 else max(left_offset, right_offset) / total
    if left_offset >= right_offset:
        return landmarks.left_shoulder, "left", left_offset, dominance
    return landmarks.right_shoulder, "right", right_offset, dominance


def _thoracic_proxy_assessment(landmarks: RestingLandmarks) -> dict[str, object]:
    neck = neck_center(landmarks)
    pelvis = pelvis_center(landmarks)
    trunk_length = euclidean_distance_2d(_to_tuple(neck), _to_tuple(pelvis))
    shoulder, shoulder_side, shoulder_offset_x, dominance = _dominant_profile_shoulder(landmarks)

    notes = list(THORACIC_PROXY_LOW_CONFIDENCE_NOTES)
    flags = ["fragile_thoracic_proxy"]
    if trunk_length <= 1e-6:
        notes.append("Neck-pelvis trunk axis could not be defined robustly.")
        return {
            "kyphosis_angle": float("nan"),
            "flattening_index": float("nan"),
            "confidence": 0.0,
            "status": "placeholder",
            "quality_notes": notes,
            "flags": flags + ["degenerate_trunk_axis"],
            "calculation_status": "degenerate_trunk_axis",
        }

    shoulder_offset = _distance_point_to_line(shoulder, neck, pelvis)
    normalized_offset = shoulder_offset / trunk_length
    if shoulder_offset_x / trunk_length < 0.015:
        notes.append("The shoulder offset from the trunk axis was too small to support a meaningful thoracic curvature proxy.")
        return {
            "kyphosis_angle": float("nan"),
            "flattening_index": float("nan"),
            "confidence": 0.18,
            "status": "placeholder",
            "quality_notes": notes,
            "flags": flags + ["insufficient_sagittal_signal"],
            "calculation_status": "insufficient_sagittal_signal",
        }
    if dominance < 0.55:
        notes.append("Both shoulders were similarly projected in the lateral capture, so the profile-side proxy is ambiguous.")
        return {
            "kyphosis_angle": float("nan"),
            "flattening_index": float("nan"),
            "confidence": 0.24,
            "status": "placeholder",
            "quality_notes": notes,
            "flags": flags + ["ambiguous_profile_side"],
            "calculation_status": "ambiguous_profile_side",
        }

    proxy_angle = float(degrees(atan2(shoulder_offset, max(trunk_length * 0.35, 1e-6))))
    flattening_index = float(max(0.0, min(1.0, 1.0 - proxy_angle / 40.0)))
    confidence = float(max(0.28, min(0.52, 0.24 + normalized_offset * 2.0)))
    notes.append(f"The proxy is anchored to the {shoulder_side} shoulder because it is the most laterally dominant profile shoulder in the image.")
    if confidence < 0.55:
        notes.append("This value is intentionally marked low-confidence until richer thoracic landmarks are available.")
    return {
        "kyphosis_angle": proxy_angle,
        "flattening_index": flattening_index,
        "confidence": confidence,
        "status": "low_confidence",
        "quality_notes": notes,
        "flags": flags,
        "calculation_status": "proxy_from_profile_shoulder_offset",
    }


def neck_center(landmarks: RestingLandmarks) -> Point2D:
    """Return midpoint between shoulders used as a neck base approximation."""
    return midpoint(landmarks.left_shoulder, landmarks.right_shoulder)


def pelvis_center(landmarks: RestingLandmarks) -> Point2D:
    """Return midpoint between hips."""
    return midpoint(landmarks.left_hip, landmarks.right_hip)


def thoracic_center(landmarks: RestingLandmarks) -> Point2D:
    """Return a thoracic proxy between neck and pelvis centers."""
    return midpoint(neck_center(landmarks), pelvis_center(landmarks))


def ankle_center(landmarks: RestingLandmarks) -> Point2D:
    """Return midpoint between ankles used for support-base references."""
    return midpoint(landmarks.left_ankle, landmarks.right_ankle)


def spine_center(landmarks: RestingLandmarks) -> Point2D:
    """Return trunk center proxy between thorax and pelvis."""
    return midpoint(thoracic_center(landmarks), pelvis_center(landmarks))


def upper_spine_reference(landmarks: RestingLandmarks) -> Point2D:
    """Return the torso midline projected to shoulder level for scapular proxies."""
    neck = neck_center(landmarks)
    pelvis = pelvis_center(landmarks)
    target_y = (landmarks.left_shoulder.y + landmarks.right_shoulder.y) / 2.0
    delta_y = pelvis.y - neck.y
    if abs(delta_y) <= 1e-6:
        return Point2D(x=neck.x, y=target_y)
    ratio = (target_y - neck.y) / delta_y
    return Point2D(x=neck.x + (pelvis.x - neck.x) * ratio, y=target_y)


def _scapular_width_reference(landmarks: RestingLandmarks) -> float:
    shoulder_span = abs(landmarks.right_shoulder.x - landmarks.left_shoulder.x)
    if shoulder_span > 1e-6:
        return shoulder_span
    return max(_body_reference(landmarks), 1e-6)


def _deviation_from_vertical(angle: float) -> float:
    normalized = abs(angle)
    return min(normalized, abs(180.0 - normalized))


def shoulder_height_difference(landmarks: RestingLandmarks) -> float:
    """Frontal plane. Measurement type: direct geometric measurement.

    Technical:
        Normalized vertical difference between left and right shoulder heights.

    Clinical interpretation:
        Higher values suggest unilateral shoulder/scapular elevation or global
        lateral compensation.
    """
    return _normalize_distance(abs(landmarks.left_shoulder.y - landmarks.right_shoulder.y), landmarks)


def scapular_elevation_difference(landmarks: RestingLandmarks) -> float:
    """Frontal plane. Measurement type: biomechanical proxy.

    Technical:
        Normalized difference between the vertical displacement of each shoulder
        relative to the thoracic center. MediaPipe Pose does not see scapulae
        directly, so this estimates scapular elevation asymmetry indirectly.

    Clinical interpretation:
        Higher values suggest asymmetric resting elevation/depression across
        the scapular belt.
    """
    thorax = thoracic_center(landmarks)
    left = abs(landmarks.left_shoulder.y - thorax.y)
    right = abs(landmarks.right_shoulder.y - thorax.y)
    return _normalize_distance(abs(left - right), landmarks)


def scapula_spine_distance_left(landmarks: RestingLandmarks) -> float:
    """Frontal plane. Measurement type: biomechanical proxy.

    Technical:
        Horizontal offset between the left acromion proxy and the projected
        spinal midline at shoulder level, normalized by bi-acromial width.
        This is intentionally crop-stable and avoids using trunk height for a
        left-right scapular spacing proxy.

    Clinical interpretation:
        Larger values suggest greater left resting protraction/abduction bias.
    """
    spine_reference = upper_spine_reference(landmarks)
    return abs(landmarks.left_shoulder.x - spine_reference.x) / _scapular_width_reference(landmarks)


def scapula_spine_distance_right(landmarks: RestingLandmarks) -> float:
    """Frontal plane. Measurement type: biomechanical proxy.

    Technical:
        Right-sided analogue of the crop-stable scapula-spine spacing proxy.

    Clinical interpretation:
        Larger values suggest greater right resting protraction/abduction bias.
    """
    spine_reference = upper_spine_reference(landmarks)
    return abs(landmarks.right_shoulder.x - spine_reference.x) / _scapular_width_reference(landmarks)


def scapular_symmetry_index(landmarks: RestingLandmarks) -> float:
    """Frontal plane. Measurement type: compound index.

    Technical:
        Bounded [0, 1] index averaging left-right asymmetry in scapula-spine
        proxy distance and scapular elevation proxy.

    Clinical interpretation:
        Higher values indicate a more asymmetric resting scapular presentation.
    """
    left_dist = scapula_spine_distance_left(landmarks)
    right_dist = scapula_spine_distance_right(landmarks)
    dist_component = _bounded_ratio(abs(left_dist - right_dist), left_dist + right_dist)

    thorax = thoracic_center(landmarks)
    left_elevation = abs(landmarks.left_shoulder.y - thorax.y)
    right_elevation = abs(landmarks.right_shoulder.y - thorax.y)
    elevation_component = _bounded_ratio(abs(left_elevation - right_elevation), left_elevation + right_elevation)
    return (dist_component + elevation_component) / 2.0


def torso_lateral_tilt(landmarks: RestingLandmarks) -> float:
    """Frontal plane. Measurement type: direct geometric measurement.

    Technical:
        Angle of the thorax-to-pelvis axis relative to vertical.

    Clinical interpretation:
        Larger values indicate lateral torso bias or functional side-bending.
    """
    return line_angle_to_vertical_deg(thoracic_center(landmarks), pelvis_center(landmarks))


def thoracic_kyphosis_angle(landmarks: RestingLandmarks) -> float:
    """Sagittal plane. Measurement type: biomechanical proxy.

    Technical:
        Low-confidence sagittal proxy derived from profile-shoulder offset
        relative to the neck-pelvis axis. This is not a vertebral-angle
        measurement and may be unavailable when the side-view signal is weak.

    Clinical interpretation:
        Higher values suggest greater upper-thorax flexion bias, but only as a
        coarse proxy.
    """
    return float(_thoracic_proxy_assessment(landmarks)["kyphosis_angle"])


def shoulder_protraction_angle_left(landmarks: RestingLandmarks) -> float:
    """Sagittal plane. Measurement type: biomechanical proxy.

    Technical:
        Left ear-shoulder-hip deviation from a stacked alignment. Higher values
        indicate a more flexed/anterior shoulder presentation.

    Clinical interpretation:
        Increased values support a left rounded-shoulder / protraction bias.
    """
    return _deviation_from_straight(angle_3p_deg(landmarks.left_ear, landmarks.left_shoulder, landmarks.left_hip))


def shoulder_protraction_angle_right(landmarks: RestingLandmarks) -> float:
    """Sagittal plane. Measurement type: biomechanical proxy.

    Technical:
        Right ear-shoulder-hip deviation from a stacked alignment.

    Clinical interpretation:
        Increased values support a right rounded-shoulder / protraction bias.
    """
    return _deviation_from_straight(
        angle_3p_deg(landmarks.right_ear, landmarks.right_shoulder, landmarks.right_hip)
    )


def cranio_shoulder_angle(landmarks: RestingLandmarks) -> float:
    """Sagittal plane. Measurement type: biomechanical proxy.

    Technical:
        Mean inclination of each ear-to-shoulder line relative to horizontal.

    Clinical interpretation:
        Lower values usually reflect forward head posture, while higher values
        reflect a more stacked head-over-shoulder relation.
    """
    left = line_angle_to_horizontal_deg(landmarks.left_ear, landmarks.left_shoulder)
    right = line_angle_to_horizontal_deg(landmarks.right_ear, landmarks.right_shoulder)
    return (left + right) / 2.0


def scapular_anterior_tilt_left(landmarks: RestingLandmarks) -> float:
    """Sagittal plane. Measurement type: biomechanical proxy.

    Technical:
        Left thorax-shoulder-hip deviation from a stacked alignment used as an
        anterior tilt surrogate. MediaPipe Pose does not measure scapular tilt
        directly.

    Clinical interpretation:
        Higher values suggest a left anteriorly tilted scapular resting bias.
    """
    return _deviation_from_straight(angle_3p_deg(thoracic_center(landmarks), landmarks.left_shoulder, landmarks.left_hip))


def scapular_anterior_tilt_right(landmarks: RestingLandmarks) -> float:
    """Sagittal plane. Measurement type: biomechanical proxy.

    Technical:
        Right thorax-shoulder-hip deviation from stacked alignment.

    Clinical interpretation:
        Higher values suggest a right anteriorly tilted scapular resting bias.
    """
    return _deviation_from_straight(
        angle_3p_deg(thoracic_center(landmarks), landmarks.right_shoulder, landmarks.right_hip)
    )


def scapular_internal_rotation_left(landmarks: RestingLandmarks) -> float:
    """Transverse plane. Measurement type: biomechanical proxy.

    Technical:
        Deviation of the left scapular proxy vector from a neutral vertical,
        using the projected spinal midline at shoulder height as the origin.
        This remains a fragile posterior-view proxy, not a true axial-rotation
        measurement.

    Clinical interpretation:
        Higher values suggest greater left internal rotation/protraction bias.
    """
    spine_reference = upper_spine_reference(landmarks)
    return _deviation_from_vertical(line_angle_to_vertical_deg(spine_reference, landmarks.left_shoulder))


def scapular_internal_rotation_right(landmarks: RestingLandmarks) -> float:
    """Transverse plane. Measurement type: biomechanical proxy.

    Technical:
        Right-sided analogue of the projected midline-to-acromion internal
        rotation surrogate.

    Clinical interpretation:
        Higher values suggest greater right internal rotation/protraction bias.
    """
    spine_reference = upper_spine_reference(landmarks)
    return _deviation_from_vertical(line_angle_to_vertical_deg(spine_reference, landmarks.right_shoulder))


def scapular_upward_rotation_left(landmarks: RestingLandmarks) -> float:
    """Transverse/frontal plane. Measurement type: biomechanical proxy.

    Technical:
        Absolute deviation of the left projected midline-to-acromion vector from
        a neutral horizontal reference. This yields an interpretable elevation /
        upward-rotation surrogate instead of an opaque absolute quadrant angle.

    Clinical interpretation:
        Larger values suggest a more elevated/upwardly rotated resting posture.
    """
    spine_reference = upper_spine_reference(landmarks)
    return _deviation_from_horizontal(line_angle_to_horizontal_deg(spine_reference, landmarks.left_shoulder))


def scapular_upward_rotation_right(landmarks: RestingLandmarks) -> float:
    """Transverse/frontal plane. Measurement type: biomechanical proxy.

    Technical:
        Right-sided analogue of the horizontal-deviation upward rotation proxy.

    Clinical interpretation:
        Larger values suggest a more elevated/upwardly rotated resting posture.
    """
    spine_reference = upper_spine_reference(landmarks)
    return _deviation_from_horizontal(line_angle_to_horizontal_deg(spine_reference, landmarks.right_shoulder))


def clavicle_orientation(landmarks: RestingLandmarks) -> float:
    """Frontal plane. Measurement type: biomechanical proxy.

    Technical:
        Orientation of the shoulder line relative to horizontal as a clavicular
        belt surrogate.

    Clinical interpretation:
        Larger values indicate a more oblique clavicular/shoulder girdle line.
    """
    return line_angle_to_horizontal_deg(landmarks.left_shoulder, landmarks.right_shoulder)


def winging_index(landmarks: RestingLandmarks) -> float:
    """Frontal/transverse planes. Measurement type: compound index.

    Technical:
        Bounded [0, 1] composite index blending scapula-spine asymmetry,
        internal rotation asymmetry, and upward rotation asymmetry. It is an
        inferred resting winging tendency, not a direct medial-border measure.

    Clinical interpretation:
        Higher values suggest a stronger scapular winging/diskinesis tendency.
    """
    dist_component = _bounded_ratio(
        abs(scapula_spine_distance_left(landmarks) - scapula_spine_distance_right(landmarks)),
        scapula_spine_distance_left(landmarks) + scapula_spine_distance_right(landmarks),
    )
    internal_component = _bounded_ratio(
        abs(scapular_internal_rotation_left(landmarks) - scapular_internal_rotation_right(landmarks)),
        180.0,
    )
    upward_component = _bounded_ratio(
        abs(scapular_upward_rotation_left(landmarks) - scapular_upward_rotation_right(landmarks)),
        180.0,
    )
    return (dist_component + internal_component + upward_component) / 3.0


def pelvic_tilt(landmarks: RestingLandmarks) -> float:
    """Frontal plane. Measurement type: direct geometric measurement.

    Technical:
        Absolute deviation of the left-right hip line from a neutral horizontal.
        This avoids the 0-vs-180 convention mismatch across front and back.

    Clinical interpretation:
        Larger values indicate pelvic hiking/drop asymmetry at rest.
    """
    return _deviation_from_horizontal(line_angle_to_horizontal_deg(landmarks.left_hip, landmarks.right_hip))


def head_tilt_angle(landmarks: RestingLandmarks) -> float:
    """Frontal plane. Measurement type: direct geometric measurement.

    Technical:
        Absolute deviation of the inter-aural line from a neutral horizontal.

    Clinical interpretation:
        Larger values indicate greater lateral head tilt.
    """
    return _deviation_from_horizontal(line_angle_to_horizontal_deg(landmarks.left_ear, landmarks.right_ear))


def forward_center_of_mass_offset(landmarks: RestingLandmarks) -> float:
    """Sagittal plane. Measurement type: biomechanical proxy.

    Technical:
        Normalized horizontal offset between a simple global body-center proxy
        (nose, thorax, pelvis average) and the ankle base of support.

    Clinical interpretation:
        Positive values suggest a globally anterior mass bias.
    """
    global_center_x = (landmarks.nose.x + thoracic_center(landmarks).x + pelvis_center(landmarks).x) / 3.0
    return _normalize_distance(global_center_x - ankle_center(landmarks).x, landmarks)


def pelvic_transverse_rotation(landmarks: RestingLandmarks) -> float:
    """Transverse plane. Measurement type: biomechanical proxy.

    Technical:
        Signed 2D foreshortening proxy in [-1, 1] derived from left/right hip
        widths relative to the pelvis center.

    Clinical interpretation:
        Positive values suggest apparent right pelvic rotation; negative values
        suggest apparent left pelvic rotation.
    """
    pelvis = pelvis_center(landmarks)
    left_width = abs(landmarks.left_hip.x - pelvis.x)
    right_width = abs(landmarks.right_hip.x - pelvis.x)
    total = left_width + right_width
    if total == 0:
        return 0.0
    return (left_width - right_width) / total


def pelvic_ankle_sagittal_offset(landmarks: RestingLandmarks) -> float:
    """Sagittal plane. Measurement type: direct geometric measurement.

    Technical:
        Normalized horizontal distance between the pelvis center and ankle
        center in a lateral capture.

    Clinical interpretation:
        Positive values suggest anterior pelvic drift relative to the support
        base, which may be relevant for swayback/APT differentiation later.
    """
    return _normalize_distance(pelvis_center(landmarks).x - ankle_center(landmarks).x, landmarks)


def thoracic_flattening_index(landmarks: RestingLandmarks) -> float:
    """Sagittal plane. Measurement type: compound index.

    Technical:
        Derived from the same low-confidence thoracic proxy as
        `thoracic_kyphosis_angle`. Lower values indicate more apparent upper
        thorax rounding, while higher values indicate a flatter profile.

    Clinical interpretation:
        Higher values suggest thoracic flattening or a rigidly extended upper
        thorax rather than a normal resting kyphotic contour.
    """
    return float(_thoracic_proxy_assessment(landmarks)["flattening_index"])


def thorax_pelvis_rotation(landmarks: RestingLandmarks) -> float:
    """Transverse plane. Measurement type: placeholder.

    Technical:
        Reserved for a future thorax-versus-pelvis rotation metric. The current
        single-image MediaPipe Pose pipeline does not expose a sufficiently
        reliable thoracic contour or axial-rotation reference to estimate this
        without being misleading.

    Clinical interpretation:
        Intended to support rotational trunk patterning, but still unavailable.

    TODO:
        Revisit only after adding either multi-view capture, stronger thoracic
        landmarks, or a dedicated trunk/rib segmentation strategy.
    """
    _ = landmarks
    return float("nan")


def rib_flare_asymmetry(landmarks: RestingLandmarks) -> float:
    """Sagittal/transverse planes. Measurement type: placeholder.

    Technical:
        Reserved for lower-rib asymmetry analysis. MediaPipe Pose does not
        provide lower-rib landmarks, so a single image is not enough to infer a
        clinically honest rib-flare asymmetry metric here.

    Clinical interpretation:
        Intended to support rib flare interpretation in later versions.

    TODO:
        Revisit after adding dedicated thorax/rib landmarks, finer segmentation,
        or multi-frame / multi-view capture.
    """
    _ = landmarks
    return float("nan")


def _enrich_metric(metric: BiomechanicsMetric, landmarks: RestingLandmarks) -> BiomechanicsMetric:
    if metric.name in {"pelvic_tilt", "head_tilt_angle"}:
        return replace(
            metric,
            calculation_status="deviation_from_horizontal_reference",
            quality_notes=["This angle is normalized as absolute deviation from a level horizontal reference (0 degrees = level)."],
        )

    if metric.name in {"thoracic_kyphosis_angle", "thoracic_flattening_index"}:
        proxy = _thoracic_proxy_assessment(landmarks)
        value_key = "kyphosis_angle" if metric.name == "thoracic_kyphosis_angle" else "flattening_index"
        value = float(proxy[value_key])
        return replace(
            metric,
            value=value,
            priority="P1" if isnan(value) else metric.priority,
            status=str(proxy["status"]),
            confidence=float(proxy["confidence"]),
            quality_notes=list(proxy["quality_notes"]),
            flags=list(proxy["flags"]),
            source_of_truth="side_view_proxy",
            calculation_status=str(proxy["calculation_status"]),
        )

    if metric.name in _SCAPULA_GROUP_A_METRICS:
        calculation_status = (
            "elevation_asymmetry_relative_to_thoracic_center"
            if metric.name == "scapular_elevation_difference"
            else "compound_static_scapular_asymmetry_index"
        )
        quality_note = (
            "This static asymmetry metric is suitable as a baseline reference, but it still reflects shoulder-girdle geometry rather than direct scapular tracking."
        )
        return replace(
            metric,
            confidence_base="medium_high",
            anatomical_directness="indirect",
            source_of_truth="posterior_view_proxy" if metric.name == "scapular_elevation_difference" else (metric.source_of_truth or "compound_proxy_baseline"),
            calculation_status=calculation_status,
            quality_notes=[quality_note],
        )

    if metric.name in {"scapula_spine_distance_left", "scapula_spine_distance_right"}:
        return replace(
            metric,
            confidence_base="low_medium",
            source_of_truth="posterior_view_proxy",
            calculation_status="horizontal_distance_to_projected_spinal_midline",
            proxy_type="posterior_shoulder_girdle",
            anatomical_directness="indirect",
            quality_notes=[
                "This spacing proxy is normalized by shoulder width and referenced to the projected spinal midline at shoulder level.",
                *_SCAPULA_PROXY_QUALITY_NOTES,
            ],
            flags=list(_SCAPULA_PROXY_FLAGS),
        )

    if metric.name in {"scapular_internal_rotation_left", "scapular_internal_rotation_right"}:
        return replace(
            metric,
            confidence_base="low_medium",
            source_of_truth="posterior_view_proxy",
            calculation_status="deviation_from_vertical_midline_reference",
            proxy_type="posterior_shoulder_girdle",
            anatomical_directness="indirect",
            quality_notes=[
                "This is a posterior-view scapular proxy from the projected spinal midline to the acromion, not a direct axial-rotation measurement.",
                *_SCAPULA_PROXY_QUALITY_NOTES,
            ],
            flags=list(_SCAPULA_PROXY_FLAGS),
        )

    if metric.name in {"scapular_upward_rotation_left", "scapular_upward_rotation_right"}:
        return replace(
            metric,
            confidence_base="low_medium",
            source_of_truth="posterior_view_proxy",
            calculation_status="deviation_from_horizontal_midline_reference",
            proxy_type="posterior_shoulder_girdle",
            anatomical_directness="indirect",
            quality_notes=[
                "This is a posterior-view upward rotation proxy expressed as deviation from a level horizontal reference.",
                *_SCAPULA_PROXY_QUALITY_NOTES,
            ],
            flags=list(_SCAPULA_PROXY_FLAGS),
        )

    if metric.name == "winging_index":
        return replace(
            metric,
            confidence_base="low_medium",
            source_of_truth="posterior_view_proxy",
            calculation_status="compound_scapular_asymmetry_proxy",
            proxy_type="posterior_shoulder_girdle",
            anatomical_directness="indirect",
            quality_notes=list(_SCAPULA_PROXY_QUALITY_NOTES),
            flags=list(_SCAPULA_PROXY_FLAGS),
        )

    return metric


# P2 metrics intentionally excluded from the implementation surface:
# - infra_sternal_angle: requires lower-rib landmarks or a dedicated thorax model
# - calcaneal_angle: requires heel/rearfoot-specific landmarks or segmentation
# - arch_height_ratio: requires plantar/foot contour extraction
# - bipupilar_tilt: requires FaceMesh
# - mandibular_lateral_shift: requires FaceMesh
# - first_metatarsal_extension_angle: requires toe-specific tracking
# - midfoot_width_ratio: requires foot segmentation

P0_METRIC_SPECS: dict[str, MetricSpec] = {
    "shoulder_height_difference": ("frontal", "normalized", "direct", shoulder_height_difference),
    "scapular_elevation_difference": ("frontal", "normalized", "proxy", scapular_elevation_difference),
    "scapula_spine_distance_left": ("frontal", "normalized", "proxy", scapula_spine_distance_left),
    "scapula_spine_distance_right": ("frontal", "normalized", "proxy", scapula_spine_distance_right),
    "scapular_symmetry_index": ("frontal", "index", "compound_index", scapular_symmetry_index),
    "torso_lateral_tilt": ("frontal", "degrees", "direct", torso_lateral_tilt),
    "thoracic_kyphosis_angle": ("sagittal", "degrees", "proxy", thoracic_kyphosis_angle),
    "shoulder_protraction_angle_left": ("sagittal", "degrees", "proxy", shoulder_protraction_angle_left),
    "shoulder_protraction_angle_right": ("sagittal", "degrees", "proxy", shoulder_protraction_angle_right),
    "cranio_shoulder_angle": ("sagittal", "degrees", "proxy", cranio_shoulder_angle),
    "scapular_anterior_tilt_left": ("sagittal", "degrees", "proxy", scapular_anterior_tilt_left),
    "scapular_anterior_tilt_right": ("sagittal", "degrees", "proxy", scapular_anterior_tilt_right),
    "scapular_internal_rotation_left": ("transverse", "degrees", "proxy", scapular_internal_rotation_left),
    "scapular_internal_rotation_right": ("transverse", "degrees", "proxy", scapular_internal_rotation_right),
    "scapular_upward_rotation_left": ("transverse", "degrees", "proxy", scapular_upward_rotation_left),
    "scapular_upward_rotation_right": ("transverse", "degrees", "proxy", scapular_upward_rotation_right),
    "clavicle_orientation": ("frontal", "degrees", "proxy", clavicle_orientation),
    "winging_index": ("transverse", "index", "compound_index", winging_index),
    "pelvic_tilt": ("frontal", "degrees", "direct", pelvic_tilt),
    "head_tilt_angle": ("frontal", "degrees", "direct", head_tilt_angle),
    "forward_center_of_mass_offset": ("sagittal", "normalized", "proxy", forward_center_of_mass_offset),
    "pelvic_transverse_rotation": ("transverse", "index", "proxy", pelvic_transverse_rotation),
    "pelvic_ankle_sagittal_offset": ("sagittal", "normalized", "direct", pelvic_ankle_sagittal_offset),
    "thoracic_flattening_index": ("sagittal", "index", "compound_index", thoracic_flattening_index),
}

P1_PLACEHOLDER_SPECS: dict[str, MetricSpec] = {
    "thorax_pelvis_rotation": ("transverse", "placeholder", "placeholder", thorax_pelvis_rotation),
    "rib_flare_asymmetry": ("transverse", "placeholder", "placeholder", rib_flare_asymmetry),
}


def compute_resting_metrics(
    landmarks: RestingLandmarks,
    *,
    include_placeholders: bool = True,
) -> dict[str, BiomechanicsMetric]:
    """Compute the refined resting biomechanical metric set.

    Returns:
        Dictionary keyed by metric name. By default it includes all P0 metrics
        plus P1 placeholders. P2 metrics are intentionally excluded.
    """
    output: dict[str, BiomechanicsMetric] = {}
    all_specs = dict(P0_METRIC_SPECS)
    if include_placeholders:
        all_specs.update(P1_PLACEHOLDER_SPECS)

    for name, (plane, unit, measurement_type, func) in all_specs.items():
        value = func(landmarks)
        metric = BiomechanicsMetric(
            name=name,
            value=value,
            plane=plane,
            unit=unit,
            measurement_type=measurement_type,
            priority="P1" if unit == "placeholder" or isnan(value) else "P0",
        )
        output[name] = _enrich_metric(metric, landmarks)
    return output


__all__ = [
    "P0_METRIC_SPECS",
    "P1_PLACEHOLDER_SPECS",
    "ankle_center",
    "clavicle_orientation",
    "compute_resting_metrics",
    "cranio_shoulder_angle",
    "forward_center_of_mass_offset",
    "head_tilt_angle",
    "neck_center",
    "pelvic_ankle_sagittal_offset",
    "pelvis_center",
    "pelvic_tilt",
    "pelvic_transverse_rotation",
    "rib_flare_asymmetry",
    "scapula_spine_distance_left",
    "scapula_spine_distance_right",
    "scapular_anterior_tilt_left",
    "scapular_anterior_tilt_right",
    "scapular_elevation_difference",
    "scapular_internal_rotation_left",
    "scapular_internal_rotation_right",
    "scapular_symmetry_index",
    "scapular_upward_rotation_left",
    "scapular_upward_rotation_right",
    "shoulder_height_difference",
    "shoulder_protraction_angle_left",
    "shoulder_protraction_angle_right",
    "spine_center",
    "upper_spine_reference",
    "thoracic_center",
    "thoracic_flattening_index",
    "thoracic_kyphosis_angle",
    "thorax_pelvis_rotation",
    "torso_lateral_tilt",
    "winging_index",
]







