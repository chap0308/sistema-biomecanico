"""Specialized static and thoracic metrics that do not fit the main rest posture module."""

from __future__ import annotations

from dataclasses import dataclass, replace
import math
from typing import Any

from biomechanics.models import BiomechanicsMetric, Point2D, RestingLandmarks
from biomechanics.resting_metrics import compute_resting_metrics
from orchestration.view_metric_policy import filter_metrics_for_view

_SCAPULA_METRIC_NAMES = {
    "scapular_elevation_difference",
    "scapula_spine_distance_left",
    "scapula_spine_distance_right",
    "scapular_symmetry_index",
    "scapular_internal_rotation_left",
    "scapular_internal_rotation_right",
    "scapular_upward_rotation_left",
    "scapular_upward_rotation_right",
    "clavicle_orientation",
    "winging_index",
}

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


@dataclass(slots=True, frozen=True)
class IsaLandmarks:
    """Three landmark proxies used to estimate the infra-sternal angle."""

    left_costal_margin: Point2D
    substernal_vertex: Point2D
    right_costal_margin: Point2D


@dataclass(slots=True)
class IsaMeasurement:
    """Container for a static or framewise ISA estimate."""

    angle_degrees: float | None
    confidence: float
    status: str
    quality_notes: list[str]
    landmarks: IsaLandmarks | None = None
    frame_index: int | None = None


@dataclass(slots=True, frozen=True)
class DynamicIsaMeasurement:
    """Container summarizing a dynamic breathing-cycle ISA estimate."""

    max_inhalation: IsaMeasurement | None
    min_exhalation: IsaMeasurement | None
    dynamic_delta: float | None
    confidence: float
    quality_notes: list[str]
    valid_frame_count: int
    total_frame_count: int


@dataclass(slots=True)
class RibFlareStaticMeasurement:
    """Container for the static rib-flare proxy metrics."""

    rib_flare_presence_score: float | None
    rib_flare_asymmetry: float | None
    left_costal_margin_angle: float | None
    right_costal_margin_angle: float | None
    costal_projection_index: float | None
    confidence: float
    status: str
    quality_notes: list[str]
    landmarks: IsaLandmarks | None = None
    frame_index: int | None = None
    left_openness_score: float | None = None
    right_openness_score: float | None = None


@dataclass(slots=True, frozen=True)
class DynamicRibFlareMeasurement:
    """Container summarizing framewise rib-flare proxy measurements."""

    dynamic_asymmetry: float | None
    excursion_left: float | None
    excursion_right: float | None
    persistence_exhalation: float | None
    thoracic_abdominal_dissociation_score: float | None
    confidence: float
    quality_notes: list[str]
    valid_frame_count: int
    total_frame_count: int
    exhalation_frame_index: int | None = None



@dataclass(slots=True)
class ThoracicAbdominalFrameMeasurement:
    """Per-frame thoracic and upper-abdominal width proxies."""

    thoracic_width_proxy: float | None
    upper_abdominal_width_proxy: float | None
    confidence: float
    status: str
    quality_notes: list[str]
    frame_index: int | None = None


@dataclass(slots=True, frozen=True)
class DynamicThoracicAbdominalMeasurement:
    """Container summarizing thoracic-abdominal coordination over time."""

    dissociation_score: float | None
    phase_offset: float | None
    amplitude_ratio: float | None
    exhalation_mismatch: float | None
    upper_abdominal_excursion: float | None
    lower_thoracic_excursion: float | None
    confidence: float
    quality_notes: list[str]
    valid_frame_count: int
    total_frame_count: int
    exhalation_frame_index: int | None = None


def _clip_confidence(value: float) -> float:
    return max(0.0, min(1.0, value))


def _merge_unique(*groups: list[str]) -> list[str]:
    merged: list[str] = []
    for group in groups:
        for item in group:
            if item not in merged:
                merged.append(item)
    return merged


def _scapula_capture_context(pose_result: object | None) -> dict[str, object]:
    notes = [
        'Static scapula metrics use posterior MediaPipe pose proxies rather than direct scapular landmarks.',
    ]
    flags = ['scapular_proxy_fragile']
    penalties = {
        'low_visibility': False,
        'poor_scapula_visibility': False,
        'wide_crop': False,
        'full_body_crop': False,
        'torso_rotation': False,
        'not_squared': False,
    }
    if pose_result is None:
        notes.append('Pose extraction metadata was unavailable, so scapular confidence could not be conditioned on capture quality.')
        flags.append('missing_pose_result')
        penalties['poor_scapula_visibility'] = True
        return {'notes': notes, 'flags': flags, 'penalties': penalties}

    named_landmarks = getattr(pose_result, 'named_landmarks', None)
    if not named_landmarks:
        notes.append('Named pose landmarks were unavailable for scapular confidence assessment.')
        flags.append('missing_named_landmarks')
        penalties['poor_scapula_visibility'] = True
        return {'notes': notes, 'flags': flags, 'penalties': penalties}

    left_shoulder = named_landmarks.get('left_shoulder')
    right_shoulder = named_landmarks.get('right_shoulder')
    left_hip = named_landmarks.get('left_hip')
    right_hip = named_landmarks.get('right_hip')
    if any(point is None for point in (left_shoulder, right_shoulder, left_hip, right_hip)):
        notes.append('Posterior anchor landmarks were incomplete, reducing scapular proxy reliability.')
        flags.append('incomplete_posterior_anchors')
        penalties['poor_scapula_visibility'] = True
        return {'notes': notes, 'flags': flags, 'penalties': penalties}

    shoulder_visibility = min(
        float(getattr(left_shoulder, 'visibility', 0.0) or 0.0),
        float(getattr(right_shoulder, 'visibility', 0.0) or 0.0),
    )
    hip_visibility = min(
        float(getattr(left_hip, 'visibility', 0.0) or 0.0),
        float(getattr(right_hip, 'visibility', 0.0) or 0.0),
    )
    if min(shoulder_visibility, hip_visibility) < 0.70:
        penalties['low_visibility'] = True
        notes.append('Posterior shoulder or hip landmarks were detected with limited visibility.')
        flags.append('low_visibility_posterior_anchors')
    if shoulder_visibility < 0.58:
        penalties['poor_scapula_visibility'] = True
        notes.append('Scapular region visibility appears limited; acromial proxies may reflect loose clothing or poor posterior contour definition.')
        flags.append('scapulae_poorly_visible')
        flags.append('possible_loose_clothing')

    shoulder_span = abs(float(left_shoulder.x) - float(right_shoulder.x))
    if shoulder_span < 0.22:
        penalties['full_body_crop'] = True
        notes.append('Full body crop reduces scapular precision because the shoulder span is small in the image.')
        flags.append('full_body_crop_reduces_scapular_precision')
    elif shoulder_span < 0.30:
        penalties['wide_crop'] = True
        notes.append('The posterior crop is wider than ideal, so scapular proxies are less stable than in a torso-focused capture.')
        flags.append('wide_crop_reduces_precision')

    shoulder_tilt = abs(
        math.degrees(
            math.atan2(
                float(right_shoulder.y) - float(left_shoulder.y),
                float(right_shoulder.x) - float(left_shoulder.x) + 1e-6,
            )
        )
    )
    if shoulder_tilt > 5.0:
        penalties['not_squared'] = True
        notes.append('Shoulders are not fully squared to the camera, which biases posterior scapular comparisons.')
        flags.append('shoulders_not_fully_squared')

    shoulder_depth_delta = abs(
        float(getattr(left_shoulder, 'z', 0.0) or 0.0) - float(getattr(right_shoulder, 'z', 0.0) or 0.0)
    )
    if shoulder_depth_delta > 0.10:
        penalties['torso_rotation'] = True
        notes.append('Posterior shoulder depth asymmetry suggests torso rotation during capture.')
        flags.append('torso_rotation_suspected')

    return {'notes': notes, 'flags': flags, 'penalties': penalties}


def _scapula_metric_confidence(metric_name: str, context: dict[str, object]) -> tuple[float, str, str]:
    penalties = context['penalties']
    assert isinstance(penalties, dict)
    is_group_b = metric_name in _SCAPULA_GROUP_B_METRICS
    confidence = 0.78 if metric_name in _SCAPULA_GROUP_A_METRICS else 0.52 if is_group_b else 0.62
    confidence_base = 'medium_high' if metric_name in _SCAPULA_GROUP_A_METRICS else 'low_medium'

    if penalties.get('low_visibility'):
        confidence -= 0.10 if metric_name in _SCAPULA_GROUP_A_METRICS else 0.14
    if penalties.get('poor_scapula_visibility'):
        confidence -= 0.04 if metric_name in _SCAPULA_GROUP_A_METRICS else 0.18
    if penalties.get('wide_crop'):
        confidence -= 0.05 if metric_name in _SCAPULA_GROUP_A_METRICS else 0.10
    if penalties.get('full_body_crop'):
        confidence -= 0.10 if metric_name in _SCAPULA_GROUP_A_METRICS else 0.16
    if penalties.get('not_squared'):
        confidence -= 0.08 if metric_name in _SCAPULA_GROUP_A_METRICS else 0.12
    if penalties.get('torso_rotation'):
        confidence -= 0.08 if metric_name in _SCAPULA_GROUP_A_METRICS else 0.14

    confidence = _clip_confidence(confidence)
    threshold = 0.62 if metric_name in _SCAPULA_GROUP_A_METRICS else 0.50
    status = 'computed' if confidence >= threshold else 'low_confidence'
    return confidence, status, confidence_base


def _scapula_metric_notes(metric_name: str) -> list[str]:
    if metric_name == 'scapular_elevation_difference':
        return ['Resting scapular elevation asymmetry is relatively robust for static baseline use, although it still represents shoulder-girdle geometry rather than direct scapular tracking.']
    if metric_name == 'scapular_symmetry_index':
        return ['Scapular symmetry index is suitable as a static baseline asymmetry summary, but it still inherits indirect inputs from shoulder-girdle geometry.']
    if metric_name.startswith('scapular_internal_rotation'):
        return ['Internal rotation is a posterior 2D proxy based on acromial position relative to the projected spinal midline, not a true axial scapular rotation measurement.']
    if metric_name.startswith('scapular_upward_rotation'):
        return ['Upward rotation is reported as deviation from a level horizontal reference at shoulder height to keep the angle clinically interpretable in 2D.']
    if metric_name.startswith('scapula_spine_distance'):
        return ['Scapula-spine distance is normalized by shoulder width to reduce sensitivity to torso-only versus full-body crop differences.']
    if metric_name == 'winging_index':
        return ['Winging index is a compound asymmetry proxy and should be treated as exploratory until direct scapular contour cues are available.']
    return []


def _enrich_scapula_metrics(
    metrics: dict[str, BiomechanicsMetric],
    pose_result: object | None,
) -> dict[str, BiomechanicsMetric]:
    context = _scapula_capture_context(pose_result)
    capture_notes = list(context['notes'])
    capture_flags = list(context['flags'])
    enriched: dict[str, BiomechanicsMetric] = {}
    for name, metric in metrics.items():
        confidence, status, confidence_base = _scapula_metric_confidence(name, context)
        proxy_notes = _SCAPULA_PROXY_QUALITY_NOTES if name in _SCAPULA_GROUP_B_METRICS else []
        proxy_flags = _SCAPULA_PROXY_FLAGS if name in _SCAPULA_GROUP_B_METRICS else []
        quality_notes = _merge_unique(list(metric.quality_notes), capture_notes, proxy_notes, _scapula_metric_notes(name))
        flags = _merge_unique(list(metric.flags), capture_flags, proxy_flags)
        enriched[name] = replace(
            metric,
            confidence=confidence,
            confidence_base=confidence_base,
            status=status,
            quality_notes=quality_notes,
            flags=flags,
            source_of_truth=metric.source_of_truth or 'posterior_view_proxy',
            proxy_type='posterior_shoulder_girdle' if name in _SCAPULA_GROUP_B_METRICS else metric.proxy_type,
            anatomical_directness='indirect' if name in _SCAPULA_GROUP_B_METRICS else (metric.anatomical_directness or 'indirect'),
        )
    return enriched


def compute_scapula_static_metrics(
    landmarks: RestingLandmarks,
    *,
    pose_result: object | None = None,
    include_placeholders: bool = True,
) -> dict[str, BiomechanicsMetric]:
    """Return the scapula-focused subset of the resting metrics for a back image."""
    metrics = compute_resting_metrics(landmarks, include_placeholders=include_placeholders)
    filtered = filter_metrics_for_view(metrics, view='back')
    scapula_metrics = {
        name: metric
        for name, (metric, is_applicable) in filtered.items()
        if is_applicable and name in _SCAPULA_METRIC_NAMES
    }
    return _enrich_scapula_metrics(scapula_metrics, pose_result)

def compute_infrasternal_angle(left_point: Point2D, substernal_vertex: Point2D, right_point: Point2D) -> float:
    """Compute the infra-sternal angle in degrees from three 2D points."""
    left_vector = (left_point.x - substernal_vertex.x, left_point.y - substernal_vertex.y)
    right_vector = (right_point.x - substernal_vertex.x, right_point.y - substernal_vertex.y)
    left_norm = math.hypot(*left_vector)
    right_norm = math.hypot(*right_vector)
    if left_norm == 0 or right_norm == 0:
        raise ValueError("Infra-sternal angle requires non-zero vectors on both sides.")

    dot = left_vector[0] * right_vector[0] + left_vector[1] * right_vector[1]
    cosine = max(-1.0, min(1.0, dot / (left_norm * right_norm)))
    return math.degrees(math.acos(cosine))


def compute_costal_margin_angle(*, substernal_vertex: Point2D, costal_margin: Point2D) -> float:
    """Return the margin orientation relative to the horizontal in degrees.

    Lower values mean a more horizontal margin, which is treated only as a flare proxy.
    """
    dx = costal_margin.x - substernal_vertex.x
    dy = costal_margin.y - substernal_vertex.y
    angle = abs(math.degrees(math.atan2(dy, dx)))
    return 180.0 - angle if angle > 90.0 else angle


def compute_costal_projection_index(
    *,
    left_point: Point2D,
    right_point: Point2D,
    substernal_vertex: Point2D,
    torso_width: float,
) -> float:
    """Compute a frontal projection proxy from bilateral costal spread.

    This is a 2D frontal breadth proxy, not true anterior depth.
    """
    if torso_width <= 0:
        raise ValueError("torso_width must be greater than 0.")
    lateral_span = abs(right_point.x - left_point.x)
    vertex_offset = (abs(left_point.x - substernal_vertex.x) + abs(right_point.x - substernal_vertex.x)) / 2.0
    return (0.65 * lateral_span + 0.35 * vertex_offset) / torso_width


def compute_rib_flare_score(
    *,
    left_costal_margin_angle: float,
    right_costal_margin_angle: float,
    costal_projection_index: float,
    isa_angle: float | None,
) -> tuple[float, float, float]:
    """Combine frontal openness proxies into a conservative rib-flare presence score."""
    left_openness = _clip01((58.0 - left_costal_margin_angle) / 30.0)
    right_openness = _clip01((58.0 - right_costal_margin_angle) / 30.0)
    projection_proxy = _clip01((costal_projection_index - 0.42) / 0.26)
    isa_support = _clip01(((isa_angle or 90.0) - 88.0) / 36.0)
    score = _clip01(0.40 * ((left_openness + right_openness) / 2.0) + 0.35 * projection_proxy + 0.25 * isa_support)
    return score, left_openness, right_openness


def compute_rib_flare_dynamic_metrics(
    frame_measurements: list[RibFlareStaticMeasurement],
    *,
    total_frame_count: int,
    reject_outliers: bool,
) -> DynamicRibFlareMeasurement:
    """Summarize framewise rib-flare proxy measurements across the breathing video."""
    valid_measurements = [
        measurement
        for measurement in frame_measurements
        if measurement.rib_flare_presence_score is not None and measurement.status != "placeholder"
    ]
    quality_notes = [
        "Dynamic rib flare uses framewise frontal proxies of costal openness and spread; treat it as a controlled prototype signal.",
    ]
    if not valid_measurements:
        quality_notes.append("No frame produced enough costal-margin evidence for dynamic rib-flare metrics.")
        return DynamicRibFlareMeasurement(
            dynamic_asymmetry=None,
            excursion_left=None,
            excursion_right=None,
            persistence_exhalation=None,
            thoracic_abdominal_dissociation_score=None,
            confidence=0.0,
            quality_notes=quality_notes,
            valid_frame_count=0,
            total_frame_count=total_frame_count,
            exhalation_frame_index=None,
        )

    filtered_measurements = _reject_rib_flare_outliers(valid_measurements) if reject_outliers else valid_measurements
    if not filtered_measurements:
        filtered_measurements = valid_measurements

    left_scores = [float(item.left_openness_score or 0.0) for item in filtered_measurements]
    right_scores = [float(item.right_openness_score or 0.0) for item in filtered_measurements]
    presence_scores = [float(item.rib_flare_presence_score or 0.0) for item in filtered_measurements]
    exhalation_measurement = min(filtered_measurements, key=lambda item: float(item.rib_flare_presence_score or math.inf))

    dynamic_asymmetry = abs(sum(left_scores) / len(left_scores) - sum(right_scores) / len(right_scores))
    excursion_left = max(left_scores) - min(left_scores)
    excursion_right = max(right_scores) - min(right_scores)
    persistence_exhalation = float(exhalation_measurement.rib_flare_presence_score or 0.0)
    valid_ratio = len(filtered_measurements) / max(total_frame_count, 1)
    mean_confidence = sum(item.confidence for item in filtered_measurements) / max(len(filtered_measurements), 1)
    confidence = min(0.78, _clip01(0.65 * mean_confidence + 0.35 * valid_ratio))

    if len(filtered_measurements) < max(3, total_frame_count // 3):
        quality_notes.append("Only a limited subset of frames produced usable rib-flare measurements.")
    if persistence_exhalation > 0.55:
        quality_notes.append("The frontal flare proxy remained elevated even in the least-flared sampled frame.")
    if confidence < 0.55:
        quality_notes.append("Dynamic rib-flare confidence is limited by weak or inconsistent contour evidence.")
    quality_notes.append(
        "Thoracic-abdominal dissociation should be interpreted separately from rib flare even when both use the same breathing video."
    )

    return DynamicRibFlareMeasurement(
        dynamic_asymmetry=float(dynamic_asymmetry),
        excursion_left=float(excursion_left),
        excursion_right=float(excursion_right),
        persistence_exhalation=float(persistence_exhalation),
        thoracic_abdominal_dissociation_score=None,
        confidence=float(confidence),
        quality_notes=quality_notes,
        valid_frame_count=len(filtered_measurements),
        total_frame_count=total_frame_count,
        exhalation_frame_index=exhalation_measurement.frame_index,
    )


def compute_infra_sternal_angle_placeholder(name: str = "infra_sternal_angle") -> BiomechanicsMetric:
    """Return an explicit placeholder when ISA cannot be estimated honestly."""
    return BiomechanicsMetric(
        name=name,
        value=float("nan"),
        plane="frontal",
        unit="degrees",
        measurement_type="placeholder",
        priority="P1",
    )


def estimate_static_infrasternal_angle(
    image_bgr: Any,
    *,
    pose_result: object | None = None,
) -> IsaMeasurement:
    """Estimate the static infra-sternal angle from a frontal torso image."""
    analysis = _analyze_static_thoracic_geometry(image_bgr, pose_result=pose_result)
    return analysis["isa"]


def estimate_static_rib_flare(
    image_bgr: Any,
    *,
    pose_result: object | None = None,
) -> RibFlareStaticMeasurement:
    """Estimate static rib-flare proxy metrics from a frontal torso image."""
    analysis = _analyze_static_thoracic_geometry(image_bgr, pose_result=pose_result)
    return analysis["rib_flare"]


def estimate_thoracic_abdominal_frame(
    image_bgr: Any,
    *,
    pose_result: object | None = None,
    isa_measurement: IsaMeasurement | None = None,
) -> ThoracicAbdominalFrameMeasurement:
    """Estimate one frame of thoracic and upper-abdominal width proxies."""
    import cv2

    height, width = image_bgr.shape[:2]
    quality_notes = [
        "Thoracic-abdominal proxy uses horizontal body-width profiles from lower thorax and upper abdomen; treat it as a controlled prototype signal.",
    ]
    roi = _build_torso_roi(pose_result, width=width, height=height)
    if roi is None:
        quality_notes.append("Torso ROI could not be localized robustly.")
        return ThoracicAbdominalFrameMeasurement(None, None, 0.0, "placeholder", quality_notes)

    center_x, shoulder_y, hip_y, torso_width = roi
    torso_height = hip_y - shoulder_y
    if torso_height <= 40 or torso_width <= 40:
        quality_notes.append("Torso ROI was too small for a thoracic-abdominal estimate.")
        return ThoracicAbdominalFrameMeasurement(None, None, 0.0, "placeholder", quality_notes)

    if isa_measurement is None:
        isa_measurement = estimate_static_infrasternal_angle(image_bgr, pose_result=pose_result)
    if isa_measurement.landmarks is None:
        quality_notes.append("Substernal reference was unavailable, so thoracic-abdominal widths could not be localized.")
        return ThoracicAbdominalFrameMeasurement(None, None, 0.0, "placeholder", quality_notes)

    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    substernal_y = isa_measurement.landmarks.substernal_vertex.y * height
    thoracic_y = substernal_y + 0.02 * torso_height
    abdominal_y = substernal_y + 0.18 * torso_height

    thoracic_width = _estimate_body_width_proxy(
        gray,
        center_x=center_x,
        y=thoracic_y,
        torso_width=torso_width,
    )
    abdominal_width = _estimate_body_width_proxy(
        gray,
        center_x=center_x,
        y=abdominal_y,
        torso_width=torso_width,
    )
    if thoracic_width is None or abdominal_width is None:
        quality_notes.append("Thoracic or upper-abdominal body boundaries were not detected robustly enough.")
        return ThoracicAbdominalFrameMeasurement(None, None, 0.0, "placeholder", quality_notes)

    confidence = min(
        0.72,
        _clip01(
            0.35 * isa_measurement.confidence
            + 0.30 * _clip01(thoracic_width["score"] / 40.0)
            + 0.30 * _clip01(abdominal_width["score"] / 40.0)
            + 0.05
        ),
    )
    if confidence < 0.55:
        quality_notes.append("Thoracic-abdominal boundary contrast was limited, so this frame is low-confidence.")

    return ThoracicAbdominalFrameMeasurement(
        thoracic_width_proxy=float(thoracic_width["width"]),
        upper_abdominal_width_proxy=float(abdominal_width["width"]),
        confidence=float(confidence),
        status="computed" if confidence >= 0.55 else "low_confidence",
        quality_notes=quality_notes,
    )


def compute_thoracic_abdominal_dynamic_metrics(
    frame_measurements: list[ThoracicAbdominalFrameMeasurement],
    *,
    total_frame_count: int,
    reject_outliers: bool,
) -> DynamicThoracicAbdominalMeasurement:
    """Summarize thoracic and abdominal width proxies across the breathing cycle."""
    valid_measurements = [
        measurement
        for measurement in frame_measurements
        if measurement.thoracic_width_proxy is not None and measurement.upper_abdominal_width_proxy is not None
    ]
    quality_notes = [
        "Thoracic-abdominal dissociation is derived from the temporal relationship between lower-thoracic and upper-abdominal width proxies.",
    ]
    if not valid_measurements:
        quality_notes.append("No frame produced enough thoracic and upper-abdominal contour evidence.")
        return DynamicThoracicAbdominalMeasurement(
            None,
            None,
            None,
            None,
            None,
            None,
            0.0,
            quality_notes,
            0,
            total_frame_count,
            None,
        )

    filtered = _reject_thoracic_abdominal_outliers(valid_measurements) if reject_outliers else valid_measurements
    if not filtered:
        filtered = valid_measurements

    thoracic = [float(item.thoracic_width_proxy or 0.0) for item in filtered]
    abdominal = [float(item.upper_abdominal_width_proxy or 0.0) for item in filtered]
    thoracic_excursion = max(thoracic) - min(thoracic)
    abdominal_excursion = max(abdominal) - min(abdominal)
    amplitude_ratio = thoracic_excursion / max(abdominal_excursion, 1e-6)
    thoracic_peak_index = thoracic.index(max(thoracic))
    abdominal_peak_index = abdominal.index(max(abdominal))
    phase_offset = abs(thoracic_peak_index - abdominal_peak_index) / max(len(filtered) - 1, 1)
    exhalation_index = thoracic.index(min(thoracic))
    exhalation_mismatch = abs(thoracic[exhalation_index] - abdominal[exhalation_index])
    amplitude_imbalance = abs(math.log(max(amplitude_ratio, 1e-6))) / math.log(3.0)
    dissociation_score = _clip01(0.40 * _clip01(amplitude_imbalance) + 0.35 * phase_offset + 0.25 * _clip01(exhalation_mismatch / 0.22))
    mean_confidence = sum(item.confidence for item in filtered) / max(len(filtered), 1)
    valid_ratio = len(filtered) / max(total_frame_count, 1)
    confidence = min(0.76, _clip01(0.65 * mean_confidence + 0.35 * valid_ratio))

    if len(filtered) < max(3, total_frame_count // 3):
        quality_notes.append("Only a limited subset of frames produced usable thoracic-abdominal estimates.")
    if phase_offset > 0.25:
        quality_notes.append("Thoracic and abdominal proxy peaks were temporally separated.")
    if amplitude_ratio > 1.4:
        quality_notes.append("Thoracic excursion exceeded upper-abdominal excursion noticeably.")
    elif amplitude_ratio < 0.7:
        quality_notes.append("Upper-abdominal excursion exceeded thoracic excursion noticeably.")
    if exhalation_mismatch > 0.12:
        quality_notes.append("Thoracic and abdominal proxy widths remained mismatched near exhalation.")
    if confidence < 0.55:
        quality_notes.append("Thoracic-abdominal confidence is limited by weak or inconsistent contour evidence.")

    return DynamicThoracicAbdominalMeasurement(
        dissociation_score=float(dissociation_score),
        phase_offset=float(phase_offset),
        amplitude_ratio=float(amplitude_ratio),
        exhalation_mismatch=float(exhalation_mismatch),
        upper_abdominal_excursion=float(abdominal_excursion),
        lower_thoracic_excursion=float(thoracic_excursion),
        confidence=float(confidence),
        quality_notes=quality_notes,
        valid_frame_count=len(filtered),
        total_frame_count=total_frame_count,
        exhalation_frame_index=filtered[exhalation_index].frame_index,
    )


def summarize_dynamic_infrasternal_angle(
    frame_measurements: list[IsaMeasurement],
    *,
    total_frame_count: int,
    reject_outliers: bool,
) -> DynamicIsaMeasurement:
    """Summarize framewise ISA estimates into inhalation/exhalation extrema."""
    valid_measurements = [
        measurement
        for measurement in frame_measurements
        if measurement.angle_degrees is not None and measurement.status != "placeholder"
    ]
    quality_notes = [
        "Dynamic ISA uses the same edge-based thoracic heuristic frame by frame and summarizes its extrema over time.",
    ]
    if not valid_measurements:
        quality_notes.append("No frame produced enough rib-margin evidence for a dynamic ISA estimate.")
        return DynamicIsaMeasurement(
            max_inhalation=None,
            min_exhalation=None,
            dynamic_delta=None,
            confidence=0.0,
            quality_notes=quality_notes,
            valid_frame_count=0,
            total_frame_count=total_frame_count,
        )

    filtered_measurements = _reject_measurement_outliers(valid_measurements) if reject_outliers else valid_measurements
    if not filtered_measurements:
        filtered_measurements = valid_measurements

    max_measurement = max(filtered_measurements, key=lambda item: float(item.angle_degrees or -math.inf))
    min_measurement = min(filtered_measurements, key=lambda item: float(item.angle_degrees or math.inf))
    dynamic_delta = float(max_measurement.angle_degrees or 0.0) - float(min_measurement.angle_degrees or 0.0)
    valid_ratio = len(filtered_measurements) / max(total_frame_count, 1)
    mean_confidence = sum(item.confidence for item in filtered_measurements) / max(len(filtered_measurements), 1)
    confidence = min(0.80, _clip01(0.65 * mean_confidence + 0.35 * valid_ratio))

    if len(filtered_measurements) < max(3, total_frame_count // 3):
        quality_notes.append("Only a limited subset of frames produced usable ISA estimates.")
    if dynamic_delta < 6.0:
        quality_notes.append("Observed ISA excursion across sampled frames was small.")
    if confidence < 0.55:
        quality_notes.append("Dynamic ISA confidence is limited by weak or inconsistent framewise edge evidence.")

    return DynamicIsaMeasurement(
        max_inhalation=max_measurement,
        min_exhalation=min_measurement,
        dynamic_delta=float(dynamic_delta),
        confidence=float(confidence),
        quality_notes=quality_notes,
        valid_frame_count=len(filtered_measurements),
        total_frame_count=total_frame_count,
    )


def _analyze_static_thoracic_geometry(
    image_bgr: Any,
    *,
    pose_result: object | None = None,
) -> dict[str, object]:
    import cv2

    height, width = image_bgr.shape[:2]
    shared_notes = [
        "Prototype thoracic estimate based on lower-rib contour evidence inside a torso ROI; not on rib landmarks from Pose.",
    ]

    roi = _build_torso_roi(pose_result, width=width, height=height)
    if roi is None:
        shared_notes.append("Torso ROI could not be localized robustly.")
        return {
            "isa": IsaMeasurement(None, 0.0, "placeholder", list(shared_notes)),
            "rib_flare": RibFlareStaticMeasurement(
                None,
                None,
                None,
                None,
                None,
                0.0,
                "placeholder",
                list(shared_notes),
            ),
        }

    center_x, shoulder_y, hip_y, torso_width = roi
    torso_height = hip_y - shoulder_y
    if torso_height <= 40 or torso_width <= 40:
        shared_notes.append("Torso ROI was too small for stable thoracic specialty metrics.")
        return {
            "isa": IsaMeasurement(None, 0.0, "placeholder", list(shared_notes)),
            "rib_flare": RibFlareStaticMeasurement(
                None,
                None,
                None,
                None,
                None,
                0.0,
                "placeholder",
                list(shared_notes),
            ),
        }

    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
    blurred = cv2.GaussianBlur(clahe, (5, 5), 0)
    gradient_map = _gradient_magnitude_map(blurred)
    candidate = _search_best_isa_candidate(
        gradient_map,
        center_x=center_x,
        shoulder_y=shoulder_y,
        hip_y=hip_y,
        torso_width=torso_width,
        width=width,
        height=height,
    )
    if candidate is None:
        shared_notes.append("The lower costal-margin rays were not detected robustly enough.")
        return {
            "isa": IsaMeasurement(None, 0.0, "placeholder", list(shared_notes)),
            "rib_flare": RibFlareStaticMeasurement(
                None,
                None,
                None,
                None,
                None,
                0.0,
                "placeholder",
                list(shared_notes),
            ),
        }

    landmarks = IsaLandmarks(
        left_costal_margin=_pixel_to_normalized(candidate["left_point"], width=width, height=height),
        substernal_vertex=_pixel_to_normalized(candidate["vertex"], width=width, height=height),
        right_costal_margin=_pixel_to_normalized(candidate["right_point"], width=width, height=height),
    )
    isa_angle = compute_infrasternal_angle(
        landmarks.left_costal_margin,
        landmarks.substernal_vertex,
        landmarks.right_costal_margin,
    )
    edge_confidence = _clip01((candidate["left_score"] + candidate["right_score"]) / 180.0)
    symmetry_confidence = _clip01(1.0 - candidate["symmetry_penalty"])
    angle_confidence = 1.0 if 55.0 <= isa_angle <= 140.0 else 0.55 if 40.0 <= isa_angle <= 155.0 else 0.2
    pose_confidence = 1.0 if pose_result is not None else 0.7
    isa_confidence = min(
        0.85,
        _clip01(
            0.45 * edge_confidence + 0.25 * symmetry_confidence + 0.20 * angle_confidence + 0.10 * pose_confidence
        ),
    )

    isa_notes = list(shared_notes)
    if pose_result is None:
        isa_notes.append("Pose ROI fallback was used because pose landmarks were unavailable.")
    if candidate["symmetry_penalty"] > 0.30:
        isa_notes.append("Left/right rib-ray lengths were asymmetric; treat the estimate with caution.")
    if candidate["left_score"] < 35.0 or candidate["right_score"] < 35.0:
        isa_notes.append("One side of the lower thorax had weak edge contrast.")
    if isa_confidence < 0.55:
        isa_notes.append("Edge evidence was weak or inconsistent, so the ISA is marked low-confidence.")
    isa_status = "computed" if isa_confidence >= 0.55 else "low_confidence"

    left_angle = compute_costal_margin_angle(
        substernal_vertex=landmarks.substernal_vertex,
        costal_margin=landmarks.left_costal_margin,
    )
    right_angle = compute_costal_margin_angle(
        substernal_vertex=landmarks.substernal_vertex,
        costal_margin=landmarks.right_costal_margin,
    )
    projection_index = compute_costal_projection_index(
        left_point=landmarks.left_costal_margin,
        right_point=landmarks.right_costal_margin,
        substernal_vertex=landmarks.substernal_vertex,
        torso_width=max(torso_width / width, 1e-6),
    )
    rib_flare_score, left_openness, right_openness = compute_rib_flare_score(
        left_costal_margin_angle=left_angle,
        right_costal_margin_angle=right_angle,
        costal_projection_index=projection_index,
        isa_angle=isa_angle,
    )
    rib_flare_asymmetry = abs(left_angle - right_angle)
    rib_confidence = min(0.75, _clip01(0.45 * edge_confidence + 0.25 * symmetry_confidence + 0.30 * (1.0 - rib_flare_asymmetry / 45.0)))
    rib_notes = list(shared_notes)
    rib_notes.append(
        "Static rib flare is a frontal proxy built from margin orientation and bilateral costal spread; it is not a direct depth measurement."
    )
    if rib_flare_asymmetry > 12.0:
        rib_notes.append("Left/right costal-margin orientations were asymmetric.")
    if projection_index < 0.38:
        rib_notes.append("Frontal costal spread was limited, reducing the confidence of a flare interpretation.")
    if rib_confidence < 0.55:
        rib_notes.append("Contour evidence was limited, so the rib-flare metrics are marked low-confidence.")
    rib_status = "computed" if rib_confidence >= 0.55 else "low_confidence"

    return {
        "isa": IsaMeasurement(
            angle_degrees=float(isa_angle),
            confidence=float(isa_confidence),
            status=isa_status,
            quality_notes=isa_notes,
            landmarks=landmarks,
        ),
        "rib_flare": RibFlareStaticMeasurement(
            rib_flare_presence_score=float(rib_flare_score),
            rib_flare_asymmetry=float(rib_flare_asymmetry),
            left_costal_margin_angle=float(left_angle),
            right_costal_margin_angle=float(right_angle),
            costal_projection_index=float(projection_index),
            confidence=float(rib_confidence),
            status=rib_status,
            quality_notes=rib_notes,
            landmarks=landmarks,
            left_openness_score=float(left_openness),
            right_openness_score=float(right_openness),
        ),
    }


def _build_torso_roi(pose_result: object | None, *, width: int, height: int) -> tuple[float, float, float, float] | None:
    if pose_result is None:
        center_x = width / 2.0
        shoulder_y = height * 0.26
        hip_y = height * 0.78
        torso_width = width * 0.36
        return center_x, shoulder_y, hip_y, torso_width

    named_landmarks = getattr(pose_result, "named_landmarks", None)
    if not named_landmarks:
        return None
    required = ("left_shoulder", "right_shoulder", "left_hip", "right_hip")
    if any(name not in named_landmarks for name in required):
        return None

    shoulder_points = [named_landmarks["left_shoulder"], named_landmarks["right_shoulder"]]
    hip_points = [named_landmarks["left_hip"], named_landmarks["right_hip"]]
    center_x = width * sum(point.x for point in shoulder_points) / 2.0
    shoulder_y = height * sum(point.y for point in shoulder_points) / 2.0
    hip_y = height * sum(point.y for point in hip_points) / 2.0
    torso_width = width * max(
        abs(named_landmarks["left_shoulder"].x - named_landmarks["right_shoulder"].x),
        abs(named_landmarks["left_hip"].x - named_landmarks["right_hip"].x),
    )
    return center_x, shoulder_y, hip_y, torso_width


def _gradient_magnitude_map(gray_image: Any) -> Any:
    import cv2

    gradient_x = cv2.Sobel(gray_image, cv2.CV_32F, 1, 0, ksize=3)
    gradient_y = cv2.Sobel(gray_image, cv2.CV_32F, 0, 1, ksize=3)
    return cv2.GaussianBlur(cv2.magnitude(gradient_x, gradient_y), (5, 5), 0)


def _search_best_isa_candidate(
    gradient_map: Any,
    *,
    center_x: float,
    shoulder_y: float,
    hip_y: float,
    torso_width: float,
    width: int,
    height: int,
) -> dict[str, Any] | None:
    import numpy as np

    torso_height = hip_y - shoulder_y
    x_offsets = np.linspace(-0.08 * torso_width, 0.08 * torso_width, 9)
    vertex_y_values = np.linspace(shoulder_y + 0.18 * torso_height, shoulder_y + 0.42 * torso_height, 10)
    ray_lengths = np.linspace(0.16 * torso_height, 0.34 * torso_height, 6)
    best_candidate: dict[str, Any] | None = None

    for vertex_y in vertex_y_values:
        for vertex_x in center_x + x_offsets:
            for ray_length in ray_lengths:
                left_candidate = _best_ray(
                    gradient_map,
                    origin=(vertex_x, vertex_y),
                    angle_range=np.linspace(115.0, 160.0, 19),
                    length=ray_length,
                    width=width,
                    height=height,
                )
                right_candidate = _best_ray(
                    gradient_map,
                    origin=(vertex_x, vertex_y),
                    angle_range=np.linspace(20.0, 65.0, 19),
                    length=ray_length,
                    width=width,
                    height=height,
                )
                if left_candidate is None or right_candidate is None:
                    continue

                symmetry_penalty = abs(left_candidate["length"] - right_candidate["length"]) / max(
                    1.0,
                    (left_candidate["length"] + right_candidate["length"]) / 2.0,
                )
                score = left_candidate["score"] + right_candidate["score"] - 30.0 * symmetry_penalty
                if best_candidate is None or score > float(best_candidate["score"]):
                    best_candidate = {
                        "score": float(score),
                        "vertex": (float(vertex_x), float(vertex_y)),
                        "left_point": left_candidate["endpoint"],
                        "right_point": right_candidate["endpoint"],
                        "left_score": float(left_candidate["score"]),
                        "right_score": float(right_candidate["score"]),
                        "left_raw_angle": float(left_candidate["angle_deg"]),
                        "right_raw_angle": float(right_candidate["angle_deg"]),
                        "left_length": float(left_candidate["length"]),
                        "right_length": float(right_candidate["length"]),
                        "symmetry_penalty": float(symmetry_penalty),
                    }

    return best_candidate


def _best_ray(
    gradient_map: Any,
    *,
    origin: tuple[float, float],
    angle_range: Any,
    length: float,
    width: int,
    height: int,
) -> dict[str, Any] | None:
    best: dict[str, Any] | None = None
    for angle_deg in angle_range:
        sampled = _sample_ray(
            gradient_map,
            origin=origin,
            angle_deg=float(angle_deg),
            length=length,
            width=width,
            height=height,
        )
        if sampled is None:
            continue
        if best is None or float(sampled["score"]) > float(best["score"]):
            best = sampled
    return best


def _sample_ray(
    gradient_map: Any,
    *,
    origin: tuple[float, float],
    angle_deg: float,
    length: float,
    width: int,
    height: int,
) -> dict[str, Any] | None:
    import numpy as np

    theta = math.radians(angle_deg)
    samples: list[float] = []
    endpoint: tuple[int, int] | None = None
    for fraction in np.linspace(0.15, 1.0, 24):
        x = origin[0] + math.cos(theta) * length * float(fraction)
        y = origin[1] + math.sin(theta) * length * float(fraction)
        pixel_x = int(round(x))
        pixel_y = int(round(y))
        if pixel_x < 0 or pixel_y < 0 or pixel_x >= width or pixel_y >= height:
            return None
        samples.append(float(gradient_map[pixel_y, pixel_x]))
        endpoint = (pixel_x, pixel_y)

    if endpoint is None:
        return None
    strongest = sorted(samples)[-10:]
    return {
        "score": float(sum(strongest) / max(len(strongest), 1)),
        "endpoint": endpoint,
        "length": float(length),
        "angle_deg": float(angle_deg),
    }


def _pixel_to_normalized(point: tuple[float, float], *, width: int, height: int) -> Point2D:
    return Point2D(x=float(point[0]) / float(width), y=float(point[1]) / float(height))


def _estimate_body_width_proxy(
    gray_image: Any,
    *,
    center_x: float,
    y: float,
    torso_width: float,
) -> dict[str, float] | None:
    import numpy as np

    image_height, image_width = gray_image.shape[:2]
    pixel_y = int(round(y))
    if pixel_y < 1 or pixel_y >= image_height - 1:
        return None

    band = gray_image[max(0, pixel_y - 1):min(image_height, pixel_y + 2), :].mean(axis=0)
    gradient = np.abs(np.gradient(band.astype(float)))
    left_expected = int(center_x - 0.5 * torso_width)
    right_expected = int(center_x + 0.5 * torso_width)
    search_half_width = int(max(10.0, 0.22 * torso_width))
    left_start = max(1, left_expected - search_half_width)
    left_end = min(image_width - 2, left_expected + search_half_width)
    right_start = max(1, right_expected - search_half_width)
    right_end = min(image_width - 2, right_expected + search_half_width)
    if left_end <= left_start or right_end <= right_start:
        return None

    left_index = left_start + int(np.argmax(gradient[left_start:left_end]))
    right_index = right_start + int(np.argmax(gradient[right_start:right_end]))
    if right_index <= left_index:
        return None

    score = float((gradient[left_index] + gradient[right_index]) / 2.0)
    return {
        "width": float((right_index - left_index) / max(torso_width, 1.0)),
        "score": score,
    }


def _clip01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _reject_measurement_outliers(measurements: list[IsaMeasurement]) -> list[IsaMeasurement]:
    import numpy as np

    if len(measurements) < 4:
        return measurements
    values = sorted(float(item.angle_degrees or 0.0) for item in measurements)
    q1 = float(np.percentile(values, 25))
    q3 = float(np.percentile(values, 75))
    iqr = q3 - q1
    if iqr == 0:
        return measurements
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return [
        measurement
        for measurement in measurements
        if measurement.angle_degrees is not None and lower <= float(measurement.angle_degrees) <= upper
    ]


def _reject_rib_flare_outliers(measurements: list[RibFlareStaticMeasurement]) -> list[RibFlareStaticMeasurement]:
    import numpy as np

    if len(measurements) < 4:
        return measurements
    values = sorted(float(item.rib_flare_presence_score or 0.0) for item in measurements)
    q1 = float(np.percentile(values, 25))
    q3 = float(np.percentile(values, 75))
    iqr = q3 - q1
    if iqr == 0:
        return measurements
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return [
        measurement
        for measurement in measurements
        if measurement.rib_flare_presence_score is not None and lower <= float(measurement.rib_flare_presence_score) <= upper
    ]


def _reject_thoracic_abdominal_outliers(
    measurements: list[ThoracicAbdominalFrameMeasurement],
) -> list[ThoracicAbdominalFrameMeasurement]:
    import numpy as np

    if len(measurements) < 4:
        return measurements
    widths = [float(item.thoracic_width_proxy or 0.0) for item in measurements]
    q1 = float(np.percentile(widths, 25))
    q3 = float(np.percentile(widths, 75))
    iqr = q3 - q1
    if iqr == 0:
        return measurements
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return [
        item
        for item in measurements
        if item.thoracic_width_proxy is not None and lower <= float(item.thoracic_width_proxy) <= upper
    ]


__all__ = [
    "DynamicIsaMeasurement",
    "DynamicRibFlareMeasurement",
    "DynamicThoracicAbdominalMeasurement",
    "IsaLandmarks",
    "IsaMeasurement",
    "RibFlareStaticMeasurement",
    "ThoracicAbdominalFrameMeasurement",
    "compute_costal_margin_angle",
    "compute_costal_projection_index",
    "compute_infra_sternal_angle_placeholder",
    "compute_infrasternal_angle",
    "compute_rib_flare_dynamic_metrics",
    "compute_rib_flare_score",
    "compute_scapula_static_metrics",
    "compute_thoracic_abdominal_dynamic_metrics",
    "estimate_static_infrasternal_angle",
    "estimate_static_rib_flare",
    "estimate_thoracic_abdominal_frame",
    "summarize_dynamic_infrasternal_angle",
]


