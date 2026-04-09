"""Threshold utilities for rule-based findings generation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ThresholdBand:
    """Three-band threshold set for mild, moderate and severe findings."""

    mild: float
    moderate: float
    severe: float


REST_FINDING_THRESHOLDS: dict[str, ThresholdBand] = {
    "forward_postural_bias": ThresholdBand(mild=0.08, moderate=0.16, severe=0.24),
    "thoracic_kyphosis_bias": ThresholdBand(mild=8.0, moderate=16.0, severe=24.0),
    "thoracic_flattening_bias": ThresholdBand(mild=0.96, moderate=0.98, severe=0.995),
    "torso_lateral_tilt": ThresholdBand(mild=2.0, moderate=5.0, severe=8.0),
    "pelvic_tilt_bias": ThresholdBand(mild=3.0, moderate=6.0, severe=10.0),
    "forward_head_posture": ThresholdBand(mild=60.0, moderate=50.0, severe=40.0),
    "head_lateral_tilt": ThresholdBand(mild=3.0, moderate=6.0, severe=10.0),
    "shoulder_height_asymmetry": ThresholdBand(mild=0.02, moderate=0.05, severe=0.08),
    "bilateral_shoulder_protraction": ThresholdBand(mild=12.0, moderate=20.0, severe=30.0),
    "shoulder_protraction_left": ThresholdBand(mild=24.0, moderate=32.0, severe=40.0),
    "shoulder_protraction_right": ThresholdBand(mild=24.0, moderate=32.0, severe=40.0),
    "scapular_elevation_asymmetry": ThresholdBand(mild=0.02, moderate=0.05, severe=0.08),
    "scapular_position_asymmetry": ThresholdBand(mild=0.08, moderate=0.16, severe=0.24),
    "left_scapular_protraction_bias": ThresholdBand(mild=0.38, moderate=0.46, severe=0.54),
    "right_scapular_protraction_bias": ThresholdBand(mild=0.38, moderate=0.46, severe=0.54),
    "possible_winging_bias": ThresholdBand(mild=0.15, moderate=0.30, severe=0.45),
    "scapular_internal_rotation_bias_left": ThresholdBand(mild=42.0, moderate=55.0, severe=70.0),
    "scapular_internal_rotation_bias_right": ThresholdBand(mild=42.0, moderate=55.0, severe=70.0),
    "scapular_upward_rotation_bias_left": ThresholdBand(mild=15.0, moderate=24.0, severe=34.0),
    "scapular_upward_rotation_bias_right": ThresholdBand(mild=15.0, moderate=24.0, severe=34.0),
    "scapular_anterior_tilt_bias_left": ThresholdBand(mild=158.0, moderate=166.0, severe=172.0),
    "scapular_anterior_tilt_bias_right": ThresholdBand(mild=158.0, moderate=166.0, severe=172.0),
    "pelvic_forward_backward_bias": ThresholdBand(mild=0.05, moderate=0.12, severe=0.20),
    "pelvic_transverse_rotation_bias": ThresholdBand(mild=0.08, moderate=0.16, severe=0.24),
}

