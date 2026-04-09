
"""Dynamic movement biomechanical metrics for scapulohumeral rhythm analysis."""

from __future__ import annotations

from dataclasses import asdict
from math import atan2, degrees, hypot, nan
from statistics import median
from typing import Any

from biomechanics.models import BiomechanicsMetric


def serialize_metric(metric: BiomechanicsMetric) -> dict[str, Any]:
    """Convert one metric into a JSON-safe payload."""
    payload = asdict(metric)
    if payload["value"] != payload["value"]:
        payload["value"] = None
    payload["status"] = metric.status or ("placeholder" if payload["value"] is None else "computed")
    return payload


def compute_shoulder_abduction_metrics(
    frame_records: list[dict[str, Any]],
    *,
    prior_analysis: dict[str, Any] | None = None,
    include_placeholders: bool = True,
) -> dict[str, Any]:
    """Compute posterior-view shoulder abduction metrics from extracted frame records."""
    if not frame_records:
        raise ValueError("frame_records must include at least one extracted frame.")

    smoothed = _smooth_frame_records(frame_records)
    movement_angles = [record["mean_humeral_abduction"] for record in smoothed]
    onset_position = _detect_movement_start(movement_angles)
    peak_position = max(range(len(smoothed)), key=lambda index: smoothed[index]["mean_humeral_abduction"])
    descent_position = _find_descent_start(movement_angles, peak_position=peak_position, threshold=8.0)
    clip_context = _assess_clip_start(movement_angles, onset_position=onset_position, descent_position=descent_position)
    baseline_context = _assess_baseline_context(movement_angles, onset_position=onset_position, prior_analysis=prior_analysis)

    side_debug: dict[str, dict[str, Any]] = {}
    side_results: dict[str, dict[str, Any]] = {}
    onset_positions: dict[str, dict[str, int]] = {}
    metrics: dict[str, dict[str, Any]] = {}

    for side in ("left", "right"):
        humeral_series = [record[f"humeral_abduction_angle_{side}"] for record in smoothed]
        raw_elevation_series = [record[f"scapular_elevation_dynamic_{side}"] for record in smoothed]
        raw_upward_series = [record[f"scapular_upward_rotation_dynamic_{side}"] for record in smoothed]
        raw_protraction_series = [record[f"scapular_internal_rotation_dynamic_{side}"] for record in smoothed]
        elevation_series, elevation_baseline, elevation_threshold = _movement_delta_series(
            raw_elevation_series,
            onset_position=onset_position,
            peak_position=peak_position,
            minimum_threshold=0.008,
            threshold_ratio=0.18,
        )
        upward_series, upward_baseline, upward_threshold = _movement_delta_series(
            raw_upward_series,
            onset_position=onset_position,
            peak_position=peak_position,
            minimum_threshold=1.0,
            threshold_ratio=0.18,
        )
        protraction_series, protraction_baseline, protraction_threshold = _movement_delta_series(
            raw_protraction_series,
            onset_position=onset_position,
            peak_position=peak_position,
            minimum_threshold=0.01,
            threshold_ratio=0.22,
        )
        winging_series = _dynamic_winging_series(protraction_series, peak_position=peak_position)
        ratio_series = [
            (upward_value / humeral_value) if humeral_value > 1e-6 else None
            for humeral_value, upward_value in zip(humeral_series, upward_series)
        ]

        elevation_onset = _first_elevation_onset(
            elevation_series,
            threshold=elevation_threshold,
            start_index=onset_position,
            stop_index=peak_position,
        )
        upward_onset = _first_upward_rotation_onset(
            upward_series,
            threshold=upward_threshold,
            start_index=onset_position,
            stop_index=peak_position,
        )
        protraction_onset = _first_metric_onset(
            protraction_series,
            threshold=protraction_threshold,
            start_index=onset_position,
            stop_index=peak_position,
        )
        activation_onset = _earliest_not_none(elevation_onset, upward_onset, protraction_onset)
        activation_delay = (activation_onset - onset_position) if activation_onset is not None else None

        peak_humeral = max(humeral_series)
        peak_elevation = max(elevation_series)
        peak_upward = max(upward_series)
        peak_protraction = max(protraction_series)
        peak_winging = max(winging_series) if winging_series else nan

        metrics[f"humeral_abduction_angle_{side}"] = serialize_metric(
            BiomechanicsMetric(
                name=f"humeral_abduction_angle_{side}",
                value=peak_humeral,
                plane="frontal",
                unit="degrees",
                measurement_type="direct",
                priority="P0",
                status="computed",
                confidence=0.88,
                source_of_truth="posterior_video",
                anatomical_directness="direct",
            )
        )
        metrics[f"scapular_elevation_dynamic_{side}"] = serialize_metric(
            BiomechanicsMetric(
                name=f"scapular_elevation_dynamic_{side}",
                value=peak_elevation,
                plane="frontal",
                unit="normalized",
                measurement_type="proxy",
                priority="P0",
                status="computed",
                confidence=0.7,
                proxy_type="posterior_shoulder_girdle_proxy",
                source_of_truth="posterior_video",
                anatomical_directness="indirect",
                quality_notes=["Posterior shoulder-height displacement used as scapular elevation proxy."],
            )
        )
        metrics[f"scapular_upward_rotation_dynamic_{side}"] = serialize_metric(
            BiomechanicsMetric(
                name=f"scapular_upward_rotation_dynamic_{side}",
                value=peak_upward,
                plane="frontal",
                unit="degrees",
                measurement_type="proxy",
                priority="P0",
                status="computed",
                confidence=0.62,
                proxy_type="posterior_shoulder_girdle_proxy",
                source_of_truth="posterior_video",
                anatomical_directness="indirect",
                quality_notes=["Shoulder-to-thorax orientation change used as upward rotation proxy."],
            )
        )
        metrics[f"scapular_internal_rotation_dynamic_{side}"] = serialize_metric(
            BiomechanicsMetric(
                name=f"scapular_internal_rotation_dynamic_{side}",
                value=peak_protraction,
                plane="transverse",
                unit="normalized",
                measurement_type="proxy",
                priority="P1",
                status="computed",
                confidence=0.58,
                proxy_type="posterior_shoulder_girdle_proxy",
                source_of_truth="posterior_video",
                anatomical_directness="indirect",
                quality_notes=["Lateral shoulder drift relative to thoracic midline used as protraction proxy."],
            )
        )
        metrics[f"dynamic_winging_{side}"] = serialize_metric(
            BiomechanicsMetric(
                name=f"dynamic_winging_{side}",
                value=peak_winging if winging_series else nan,
                plane="transverse",
                unit="normalized",
                measurement_type="proxy",
                priority="P1",
                status="low_confidence" if winging_series else ("placeholder" if include_placeholders else "low_confidence"),
                confidence=0.35 if winging_series else 0.2,
                proxy_type="posterior_shoulder_girdle_proxy",
                source_of_truth="posterior_video",
                anatomical_directness="indirect",
                quality_notes=[
                    "Dynamic winging remains an indirect posterior proxy in this iteration.",
                    "Interpretation should be confirmed with dedicated debug review.",
                ],
            )
        )
        metrics[f"scapular_activation_delay_{side}"] = serialize_metric(
            BiomechanicsMetric(
                name=f"scapular_activation_delay_{side}",
                value=float(activation_delay) if activation_delay is not None else nan,
                plane="temporal",
                unit="frames",
                measurement_type="derived",
                priority="P1",
                status="computed" if activation_delay is not None else "low_confidence",
                confidence=0.68 if activation_delay is not None else 0.35,
                source_of_truth="posterior_video",
                quality_notes=([] if activation_delay is not None else ["Scapular activation onset was not robustly detectable in the analyzed ascent window."]),
            )
        )
        metrics[f"elevation_onset_angle_{side}"] = serialize_metric(
            BiomechanicsMetric(
                name=f"elevation_onset_angle_{side}",
                value=humeral_series[elevation_onset] if elevation_onset is not None else nan,
                plane="frontal",
                unit="degrees",
                measurement_type="derived",
                priority="P1",
                status="computed" if elevation_onset is not None else "low_confidence",
                confidence=0.68 if elevation_onset is not None else 0.35,
                source_of_truth="posterior_video",
                quality_notes=([] if elevation_onset is not None else ["Elevation onset did not cross the sustained detection threshold before peak abduction."]),
            )
        )
        metrics[f"upward_rotation_onset_angle_{side}"] = serialize_metric(
            BiomechanicsMetric(
                name=f"upward_rotation_onset_angle_{side}",
                value=humeral_series[upward_onset] if upward_onset is not None else nan,
                plane="frontal",
                unit="degrees",
                measurement_type="derived",
                priority="P1",
                status="computed" if upward_onset is not None else "low_confidence",
                confidence=0.6 if upward_onset is not None else 0.35,
                source_of_truth="posterior_video",
                quality_notes=([] if upward_onset is not None else ["Upward rotation onset did not cross the sustained detection threshold before peak abduction."]),
            )
        )
        _apply_onset_clip_degradation(metrics[f"elevation_onset_angle_{side}"], clip_context=clip_context)
        _apply_onset_clip_degradation(metrics[f"upward_rotation_onset_angle_{side}"], clip_context=clip_context)
        _apply_short_rest_onset_context(
            metrics[f"elevation_onset_angle_{side}"],
            baseline_context=baseline_context,
            clip_context=clip_context,
        )
        _apply_short_rest_onset_context(
            metrics[f"upward_rotation_onset_angle_{side}"],
            baseline_context=baseline_context,
            clip_context=clip_context,
        )
        _apply_elevation_onset_consistency_degradation(
            metrics[f"elevation_onset_angle_{side}"],
            upward_payload=metrics[f"upward_rotation_onset_angle_{side}"],
            peak_humeral=peak_humeral,
            clip_context=clip_context,
        )
        _apply_upward_onset_consistency_degradation(
            metrics[f"upward_rotation_onset_angle_{side}"],
            elevation_payload=metrics[f"elevation_onset_angle_{side}"],
            peak_humeral=peak_humeral,
            clip_context=clip_context,
        )
        metrics[f"scapulohumeral_ratio_{side}"] = serialize_metric(
            BiomechanicsMetric(
                name=f"scapulohumeral_ratio_{side}",
                value=(peak_upward / peak_humeral) if peak_humeral > 1e-6 else nan,
                plane="frontal",
                unit="ratio",
                measurement_type="derived",
                priority="P1",
                status="computed",
                confidence=0.58,
                source_of_truth="posterior_video",
                quality_notes=["Returned as scapular-proxy contribution divided by humeral abduction angle."],
            )
        )

        side_debug[side] = {
            "humeral_abduction_angle": humeral_series,
            "scapular_elevation_dynamic": elevation_series,
            "scapular_upward_rotation_dynamic": upward_series,
            "scapular_internal_rotation_dynamic": protraction_series,
            "dynamic_winging": winging_series,
            "scapulohumeral_ratio": ratio_series,
            "baseline": {
                "elevation": elevation_baseline,
                "upward_rotation": upward_baseline,
                "protraction": protraction_baseline,
            },
            "thresholds": {
                "elevation": elevation_threshold,
                "upward_rotation": upward_threshold,
                "protraction": protraction_threshold,
            },
        }
        side_results[side] = {
            "peak_elevation": peak_elevation,
            "peak_upward": peak_upward,
            "peak_protraction": peak_protraction,
            "peak_winging": peak_winging,
            "peak_humeral": peak_humeral,
        }
        onset_positions[side] = {
            "elevation": elevation_onset,
            "upward_rotation": upward_onset,
            "protraction": protraction_onset,
            "activation": activation_onset,
        }

    dynamic_elevation_asymmetry_series = [
        abs(left_value - right_value)
        for left_value, right_value in zip(
            side_debug["left"]["scapular_elevation_dynamic"],
            side_debug["right"]["scapular_elevation_dynamic"],
        )
    ]
    dynamic_upward_rotation_asymmetry_series = [
        abs(left_value - right_value)
        for left_value, right_value in zip(
            side_debug["left"]["scapular_upward_rotation_dynamic"],
            side_debug["right"]["scapular_upward_rotation_dynamic"],
        )
    ]
    dynamic_protraction_asymmetry_series = [
        abs(left_value - right_value)
        for left_value, right_value in zip(
            side_debug["left"]["scapular_internal_rotation_dynamic"],
            side_debug["right"]["scapular_internal_rotation_dynamic"],
        )
    ]
    dynamic_winging_asymmetry_series = [
        abs(left_value - right_value)
        for left_value, right_value in zip(
            side_debug["left"]["dynamic_winging"],
            side_debug["right"]["dynamic_winging"],
        )
    ]

    metrics["dynamic_elevation_asymmetry"] = serialize_metric(
        BiomechanicsMetric(
            name="dynamic_elevation_asymmetry",
            value=max(dynamic_elevation_asymmetry_series) if dynamic_elevation_asymmetry_series else None,
            plane="frontal",
            unit="normalized",
            measurement_type="derived",
            priority="P0",
            status="computed",
            confidence=0.72,
            source_of_truth="posterior_video",
        )
    )
    metrics["dynamic_upward_rotation_asymmetry"] = serialize_metric(
        BiomechanicsMetric(
            name="dynamic_upward_rotation_asymmetry",
            value=max(dynamic_upward_rotation_asymmetry_series) if dynamic_upward_rotation_asymmetry_series else None,
            plane="frontal",
            unit="degrees",
            measurement_type="derived",
            priority="P0",
            status="computed",
            confidence=0.62,
            source_of_truth="posterior_video",
        )
    )
    metrics["dynamic_protraction_asymmetry"] = serialize_metric(
        BiomechanicsMetric(
            name="dynamic_protraction_asymmetry",
            value=max(dynamic_protraction_asymmetry_series) if dynamic_protraction_asymmetry_series else None,
            plane="transverse",
            unit="normalized",
            measurement_type="derived",
            priority="P1",
            status="computed",
            confidence=0.58,
            source_of_truth="posterior_video",
        )
    )
    metrics["dynamic_winging_asymmetry"] = serialize_metric(
        BiomechanicsMetric(
            name="dynamic_winging_asymmetry",
            value=max(dynamic_winging_asymmetry_series) if dynamic_winging_asymmetry_series else None,
            plane="transverse",
            unit="normalized",
            measurement_type="derived",
            priority="P1",
            status="low_confidence",
            confidence=0.3,
            source_of_truth="posterior_video",
            quality_notes=["Asymmetry derived from low-confidence dynamic winging proxy."],
        )
    )

    baseline_comparison = build_baseline_comparison(metrics, prior_analysis=prior_analysis)
    for name, payload in baseline_comparison["metrics"].items():
        metrics[name] = payload

    phase_info = {
        "status": "completed",
        "movement_start_frame": smoothed[onset_position]["frame_index"],
        "movement_start_position": onset_position,
        "peak_frame": smoothed[peak_position]["frame_index"],
        "peak_position": peak_position,
        "descent_start_frame": smoothed[descent_position]["frame_index"] if descent_position is not None else None,
        "descent_start_position": descent_position,
        "end_frame": smoothed[-1]["frame_index"],
        "phase_ranges": {
            "start": [smoothed[0]["frame_index"], smoothed[onset_position]["frame_index"]],
            "ascent": [smoothed[onset_position]["frame_index"], smoothed[peak_position]["frame_index"]],
            "peak": [smoothed[peak_position]["frame_index"], smoothed[peak_position]["frame_index"]],
            "descent": (
                [smoothed[descent_position]["frame_index"], smoothed[-1]["frame_index"]]
                if descent_position is not None
                else None
            ),
        },
    }
    key_frames = {
        "start_frame": smoothed[0]["frame_index"],
        "movement_start_frame": smoothed[onset_position]["frame_index"],
        "left_onset_frame": smoothed[onset_positions["left"]["elevation"]]["frame_index"] if onset_positions["left"]["elevation"] is not None else None,
        "right_onset_frame": smoothed[onset_positions["right"]["elevation"]]["frame_index"] if onset_positions["right"]["elevation"] is not None else None,
        "left_upward_rotation_onset_frame": smoothed[onset_positions["left"]["upward_rotation"]]["frame_index"] if onset_positions["left"]["upward_rotation"] is not None else None,
        "right_upward_rotation_onset_frame": smoothed[onset_positions["right"]["upward_rotation"]]["frame_index"] if onset_positions["right"]["upward_rotation"] is not None else None,
        "left_activation_onset_frame": smoothed[onset_positions["left"]["activation"]]["frame_index"] if onset_positions["left"]["activation"] is not None else None,
        "right_activation_onset_frame": smoothed[onset_positions["right"]["activation"]]["frame_index"] if onset_positions["right"]["activation"] is not None else None,
        "truncated_clip_frame": smoothed[0]["frame_index"] if clip_context["is_truncated"] else None,
        "peak_frame": smoothed[peak_position]["frame_index"],
        "descent_start_frame": smoothed[descent_position]["frame_index"] if descent_position is not None else None,
        "end_frame": smoothed[-1]["frame_index"],
    }
    time_series = _build_time_series(
        smoothed,
        side_debug=side_debug,
        onset_position=onset_position,
        peak_position=peak_position,
        descent_position=descent_position,
        key_frames=key_frames,
        baseline_comparison=baseline_comparison,
        asymmetry_series={
            "dynamic_elevation_asymmetry": dynamic_elevation_asymmetry_series,
            "dynamic_upward_rotation_asymmetry": dynamic_upward_rotation_asymmetry_series,
            "dynamic_protraction_asymmetry": dynamic_protraction_asymmetry_series,
            "dynamic_winging_asymmetry": dynamic_winging_asymmetry_series,
        },
    )

    metric_debug: dict[str, Any] = {
        "frame_indices": [record["frame_index"] for record in smoothed],
        "series": side_debug,
        "global_series": {
            "dynamic_elevation_asymmetry": dynamic_elevation_asymmetry_series,
            "dynamic_upward_rotation_asymmetry": dynamic_upward_rotation_asymmetry_series,
            "dynamic_protraction_asymmetry": dynamic_protraction_asymmetry_series,
            "dynamic_winging_asymmetry": dynamic_winging_asymmetry_series,
        },
        "movement_start_threshold": {
            "initial_angle": movement_angles[0],
            "movement_start_position": onset_position,
        },
        "clip_context": clip_context,
        "baseline_context": baseline_context,
        "onset_frame_index": smoothed[onset_position]["frame_index"],
        "peak_frame_index": smoothed[peak_position]["frame_index"],
        "descent_frame_index": smoothed[descent_position]["frame_index"] if descent_position is not None else None,
        "movement_phases": phase_info,
        "time_series": time_series,
        "key_frames": key_frames,
        "baseline_comparison": baseline_comparison,
    }

    return {
        "metrics": metrics,
        "movement_phases": phase_info,
        "time_series": time_series,
        "key_frames": key_frames,
        "debug": metric_debug,
        "baseline_comparison": baseline_comparison,
    }


def build_baseline_comparison(metrics: dict[str, dict[str, Any]], *, prior_analysis: dict[str, Any] | None) -> dict[str, Any]:
    """Compare dynamic movement metrics against optional static baseline context."""
    if not prior_analysis:
        notes = ["No prior_analysis was provided; baseline comparison remains contextual only."]
        return {
            "status": "not_available",
            "notes": notes,
            "metrics": {
                name: _comparison_placeholder(name, notes[0])
                for name in (
                    "baseline_vs_dynamic_elevation_change",
                    "baseline_vs_dynamic_protraction_change",
                    "baseline_vs_dynamic_rotation_change",
                    "baseline_vs_dynamic_winging_change",
                )
            },
        }

    elevation_baseline = _find_metric_value(prior_analysis, "scapular_elevation_difference")
    left_protraction = _find_metric_value(prior_analysis, "scapula_spine_distance_left")
    right_protraction = _find_metric_value(prior_analysis, "scapula_spine_distance_right")
    left_rotation = _find_metric_value(prior_analysis, "scapular_upward_rotation_left")
    right_rotation = _find_metric_value(prior_analysis, "scapular_upward_rotation_right")
    winging_baseline = _find_metric_value(prior_analysis, "winging_index")

    comparison_metrics = {
        "baseline_vs_dynamic_elevation_change": {
            "name": "baseline_vs_dynamic_elevation_change",
            "value": {
                "baseline_asymmetry": elevation_baseline,
                "dynamic_asymmetry": metrics["dynamic_elevation_asymmetry"]["value"],
                "delta": _safe_delta(metrics["dynamic_elevation_asymmetry"]["value"], elevation_baseline),
            },
            "status": "computed" if elevation_baseline is not None else "low_confidence",
            "measurement_type": "baseline_comparison",
            "quality_notes": ["Static scapular elevation asymmetry compared against dynamic posterior asymmetry."],
        },
        "baseline_vs_dynamic_protraction_change": {
            "name": "baseline_vs_dynamic_protraction_change",
            "value": {
                "left": _safe_delta(metrics["scapular_internal_rotation_dynamic_left"]["value"], left_protraction),
                "right": _safe_delta(metrics["scapular_internal_rotation_dynamic_right"]["value"], right_protraction),
            },
            "status": "computed" if left_protraction is not None or right_protraction is not None else "low_confidence",
            "measurement_type": "baseline_comparison",
            "quality_notes": ["Posterior protraction proxy compared against static scapula-spine distance proxies."],
        },
        "baseline_vs_dynamic_rotation_change": {
            "name": "baseline_vs_dynamic_rotation_change",
            "value": {
                "left": _safe_delta(metrics["scapular_upward_rotation_dynamic_left"]["value"], left_rotation),
                "right": _safe_delta(metrics["scapular_upward_rotation_dynamic_right"]["value"], right_rotation),
            },
            "status": "computed" if left_rotation is not None or right_rotation is not None else "low_confidence",
            "measurement_type": "baseline_comparison",
            "quality_notes": ["Dynamic upward rotation proxy compared against static posterior scapular rotation proxies."],
        },
        "baseline_vs_dynamic_winging_change": {
            "name": "baseline_vs_dynamic_winging_change",
            "value": {
                "left": _safe_delta(metrics["dynamic_winging_left"]["value"], winging_baseline),
                "right": _safe_delta(metrics["dynamic_winging_right"]["value"], winging_baseline),
            },
            "status": "computed" if winging_baseline is not None else "low_confidence",
            "measurement_type": "baseline_comparison",
            "quality_notes": ["Dynamic winging proxy compared against static winging proxy."],
        },
    }
    return {
        "status": "completed",
        "notes": ["Prior analysis supplied; dynamic metrics were contrasted against available scapular baseline fields."],
        "metrics": comparison_metrics,
    }


def _comparison_placeholder(name: str, note: str) -> dict[str, Any]:
    return {
        "name": name,
        "value": None,
        "status": "not_available",
        "measurement_type": "baseline_comparison",
        "quality_notes": [note],
    }


def _find_metric_value(payload: Any, metric_name: str) -> float | None:
    if isinstance(payload, dict):
        if metric_name in payload:
            candidate = payload[metric_name]
            if isinstance(candidate, dict):
                value = candidate.get("value")
                return float(value) if isinstance(value, (int, float)) else None
            if isinstance(candidate, (int, float)):
                return float(candidate)
        for value in payload.values():
            found = _find_metric_value(value, metric_name)
            if found is not None:
                return found
    elif isinstance(payload, list):
        for item in payload:
            found = _find_metric_value(item, metric_name)
            if found is not None:
                return found
    return None


def _safe_delta(dynamic_value: Any, baseline_value: float | None) -> float | None:
    if not isinstance(dynamic_value, (int, float)) or baseline_value is None:
        return None
    return float(dynamic_value) - baseline_value


def _smooth_frame_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    smoothed: list[dict[str, Any]] = []
    series_keys = [
        "humeral_abduction_angle_left",
        "humeral_abduction_angle_right",
        "mean_humeral_abduction",
        "scapular_elevation_dynamic_left",
        "scapular_elevation_dynamic_right",
        "scapular_upward_rotation_dynamic_left",
        "scapular_upward_rotation_dynamic_right",
        "scapular_internal_rotation_dynamic_left",
        "scapular_internal_rotation_dynamic_right",
    ]
    for index, record in enumerate(records):
        smoothed_record = dict(record)
        window = records[max(0, index - 2) : min(len(records), index + 3)]
        for key in series_keys:
            smoothed_record[key] = sum(item[key] for item in window) / len(window)
        smoothed.append(smoothed_record)
    return smoothed


def _assess_clip_start(
    values: list[float],
    *,
    onset_position: int,
    descent_position: int | None,
) -> dict[str, Any]:
    initial_angle = values[0] if values else 0.0
    initial_phase = _phase_label(0, initial_angle, onset_position=onset_position, descent_position=descent_position)
    is_truncated = onset_position == 0 and (initial_angle >= 25.0 or initial_phase in {"phase_2", "phase_3", "descent"})
    flags = ["truncated_clip", "late_clip_start", "onset_not_fully_observed"] if is_truncated else []
    notes = []
    if is_truncated:
        notes = [
            "Clip starts with movement already in progress.",
            "Reported onset values reflect the first detectable onset within the available clip, not the true biomechanical onset.",
        ]
    return {
        "is_truncated": is_truncated,
        "initial_angle": initial_angle,
        "initial_phase": initial_phase,
        "flags": flags,
        "quality_notes": notes,
        "calculation_status": "first_detectable_within_clip" if is_truncated else None,
    }


def _assess_baseline_context(
    values: list[float],
    *,
    onset_position: int,
    prior_analysis: dict[str, Any] | None,
) -> dict[str, Any]:
    rest_frame_count = max(0, onset_position)
    short_rest = 0 < rest_frame_count < 5
    brief_rest = 0 < rest_frame_count < 3
    notes: list[str] = []
    flags: list[str] = []
    if short_rest:
        notes.append("Visible dynamic rest before abduction is brief, so onset detection relies on a limited baseline window.")
        flags.append("short_dynamic_rest")
    if prior_analysis is not None:
        notes.append("Prior static scapular baseline was available as contextual support for interpreting onset confidence.")
        flags.append("prior_static_baseline_available")
    return {
        "rest_frame_count": rest_frame_count,
        "is_short_rest": short_rest,
        "is_brief_rest": brief_rest,
        "has_prior_analysis": prior_analysis is not None,
        "flags": flags,
        "quality_notes": notes,
    }


def _detect_movement_start(values: list[float]) -> int:
    baseline_window = values[: min(3, len(values))]
    baseline = min(baseline_window) if baseline_window else 0.0
    if baseline >= 20.0:
        return 0
    for index in range(max(0, len(baseline_window) - 1), len(values)):
        current = values[index]
        next_value = values[min(index + 1, len(values) - 1)]
        if current - baseline >= 10.0 and next_value - baseline >= 8.0:
            return _refine_movement_start(values, detected_index=index, baseline=baseline)
    return 0


def _refine_movement_start(values: list[float], *, detected_index: int, baseline: float) -> int:
    search_start = max(1, detected_index - 2)
    local_floor = max(2.0, (values[detected_index] - baseline) * 0.3)
    for index in range(detected_index - 1, search_start - 1, -1):
        previous_value = values[index - 1] if index > 0 else values[index]
        current_value = values[index]
        next_value = values[index + 1]
        is_local_minimum = current_value <= previous_value + 1.0 and current_value <= next_value + 1.0
        rise_from_minimum = values[detected_index] - current_value
        if is_local_minimum and rise_from_minimum >= local_floor:
            return index
    return detected_index

def _find_descent_start(values: list[float], *, peak_position: int, threshold: float) -> int | None:
    peak_value = values[peak_position]
    for index in range(peak_position + 1, len(values)):
        if peak_value - values[index] >= threshold:
            return index
    return None


def _dynamic_winging_series(protraction_series: list[float], *, peak_position: int) -> list[float]:
    baseline = median(protraction_series[: min(3, len(protraction_series))])
    output: list[float] = []
    for index, value in enumerate(protraction_series):
        if index >= peak_position:
            output.append(max(0.0, value - baseline))
        else:
            output.append(max(0.0, (value - baseline) * 0.5))
    return output


def _movement_delta_series(
    values: list[float],
    *,
    onset_position: int,
    peak_position: int,
    minimum_threshold: float,
    threshold_ratio: float,
) -> tuple[list[float], float, float]:
    baseline = median(values[: min(3, len(values))])
    ascent_window = values[onset_position : peak_position + 1] if peak_position >= onset_position else values
    if not ascent_window:
        ascent_window = values
    candidates = [value - baseline for value in ascent_window]
    positive_peak = max(candidates) if candidates else 0.0
    negative_peak = abs(min(candidates)) if candidates else 0.0
    if negative_peak > positive_peak * 1.1:
        series = [max(0.0, baseline - value) for value in values]
        amplitude = negative_peak
    else:
        positive_series = [max(0.0, value - baseline) for value in values]
        amplitude = max(positive_series) if positive_series else 0.0
        if amplitude < (minimum_threshold * 0.8):
            series = [abs(value - baseline) for value in values]
            amplitude = max(series) if series else 0.0
        else:
            series = positive_series
    threshold = max(minimum_threshold, amplitude * threshold_ratio)
    return series, baseline, threshold


def _first_metric_onset(
    values: list[float],
    *,
    threshold: float,
    start_index: int,
    stop_index: int,
) -> int | None:
    if not values:
        return None
    capped_stop = min(stop_index, len(values) - 1)
    for index in range(start_index, capped_stop + 1):
        current = values[index]
        next_value = values[min(index + 1, capped_stop)]
        prev_value = values[index - 1] if index > 0 else current
        if current >= threshold and (next_value >= threshold * 0.85 or prev_value >= threshold * 0.85):
            return index
    return None


def _first_elevation_onset(
    values: list[float],
    *,
    threshold: float,
    start_index: int,
    stop_index: int,
) -> int | None:
    return _first_proxy_onset(
        values,
        threshold=threshold,
        start_index=start_index,
        stop_index=stop_index,
        lookback=8,
        local_floor=max(0.0015, threshold * 0.35),
    )


def _first_upward_rotation_onset(
    values: list[float],
    *,
    threshold: float,
    start_index: int,
    stop_index: int,
) -> int | None:
    return _first_proxy_onset(
        values,
        threshold=threshold,
        start_index=start_index,
        stop_index=stop_index,
        lookback=12,
        local_floor=max(0.25, threshold * 0.35),
    )


def _first_proxy_onset(
    values: list[float],
    *,
    threshold: float,
    start_index: int,
    stop_index: int,
    lookback: int,
    local_floor: float,
) -> int | None:
    crossing = _first_metric_onset(
        values,
        threshold=threshold,
        start_index=start_index,
        stop_index=stop_index,
    )
    if crossing is None:
        return None
    search_start = max(start_index + 1, crossing - lookback)
    for index in range(crossing - 1, search_start - 1, -1):
        previous_value = values[index - 1] if index - 1 >= start_index else values[index]
        current_value = values[index]
        next_value = values[index + 1]
        is_local_minimum = current_value <= previous_value + (local_floor * 0.25) and current_value <= next_value + (local_floor * 0.25)
        rise_from_minimum = values[crossing] - current_value
        if is_local_minimum and rise_from_minimum >= local_floor:
            return index
    return crossing


def _earliest_not_none(*values: int | None) -> int | None:
    available = [value for value in values if value is not None]
    return min(available) if available else None


def _apply_onset_clip_degradation(metric_payload: dict[str, Any], *, clip_context: dict[str, Any]) -> None:
    if not clip_context.get("is_truncated"):
        return
    value = metric_payload.get("value") if isinstance(metric_payload, dict) else None
    if value is None:
        return
    existing_notes = list(metric_payload.get("quality_notes") or [])
    for note in clip_context.get("quality_notes", []):
        if note not in existing_notes:
            existing_notes.append(note)
    existing_flags = list(metric_payload.get("flags") or [])
    for flag in clip_context.get("flags", []):
        if flag not in existing_flags:
            existing_flags.append(flag)
    metric_payload["status"] = "low_confidence"
    metric_payload["confidence"] = min(float(metric_payload.get("confidence") or 1.0), 0.35)
    metric_payload["quality_notes"] = existing_notes
    metric_payload["flags"] = existing_flags
    metric_payload["calculation_status"] = clip_context.get("calculation_status")


def _apply_short_rest_onset_context(
    metric_payload: dict[str, Any],
    *,
    baseline_context: dict[str, Any],
    clip_context: dict[str, Any],
) -> None:
    if clip_context.get("is_truncated") or not baseline_context.get("is_short_rest"):
        return
    value = metric_payload.get("value") if isinstance(metric_payload, dict) else None
    if value is None:
        return
    existing_notes = list(metric_payload.get("quality_notes") or [])
    for note in baseline_context.get("quality_notes", []):
        if note not in existing_notes:
            existing_notes.append(note)
    existing_flags = list(metric_payload.get("flags") or [])
    for flag in baseline_context.get("flags", []):
        if flag not in existing_flags:
            existing_flags.append(flag)
    if baseline_context.get("has_prior_analysis"):
        metric_payload["confidence"] = min(float(metric_payload.get("confidence") or 1.0), 0.58)
    elif baseline_context.get("is_brief_rest"):
        metric_payload["confidence"] = min(float(metric_payload.get("confidence") or 1.0), 0.5)
    else:
        metric_payload["confidence"] = min(float(metric_payload.get("confidence") or 1.0), 0.55)
    metric_payload["quality_notes"] = existing_notes
    metric_payload["flags"] = existing_flags


def _apply_elevation_onset_consistency_degradation(
    metric_payload: dict[str, Any],
    *,
    upward_payload: dict[str, Any],
    peak_humeral: float,
    clip_context: dict[str, Any],
) -> None:
    if clip_context.get("is_truncated"):
        return
    elevation_value = metric_payload.get("value") if isinstance(metric_payload, dict) else None
    upward_value = upward_payload.get("value") if isinstance(upward_payload, dict) else None
    if not isinstance(elevation_value, (int, float)) or not isinstance(upward_value, (int, float)):
        return
    if metric_payload.get("status") == "low_confidence":
        return
    lag = float(elevation_value) - float(upward_value)
    late_relative_to_peak = float(elevation_value) >= max(85.0, peak_humeral * 0.55)
    if lag < 35.0 or not late_relative_to_peak:
        return
    existing_notes = list(metric_payload.get("quality_notes") or [])
    note = "Elevation proxy onset lagged markedly behind upward rotation onset, suggesting threshold-limited or visibility-limited elevation detection rather than a clean biomechanical delay."
    if note not in existing_notes:
        existing_notes.append(note)
    existing_flags = list(metric_payload.get("flags") or [])
    for flag in ("late_proxy_onset", "elevation_onset_inconsistent"):
        if flag not in existing_flags:
            existing_flags.append(flag)
    metric_payload["status"] = "low_confidence"
    metric_payload["confidence"] = min(float(metric_payload.get("confidence") or 1.0), 0.45)
    metric_payload["quality_notes"] = existing_notes
    metric_payload["flags"] = existing_flags
    metric_payload["calculation_status"] = "threshold_limited_proxy_onset"


def _apply_upward_onset_consistency_degradation(
    metric_payload: dict[str, Any],
    *,
    elevation_payload: dict[str, Any],
    peak_humeral: float,
    clip_context: dict[str, Any],
) -> None:
    if clip_context.get("is_truncated"):
        return
    upward_value = metric_payload.get("value") if isinstance(metric_payload, dict) else None
    elevation_value = elevation_payload.get("value") if isinstance(elevation_payload, dict) else None
    if not isinstance(upward_value, (int, float)) or not isinstance(elevation_value, (int, float)):
        return
    if metric_payload.get("status") == "low_confidence":
        return
    lag = float(upward_value) - float(elevation_value)
    late_relative_to_peak = float(upward_value) >= max(85.0, peak_humeral * 0.58)
    if lag < 35.0 or not late_relative_to_peak:
        return
    existing_notes = list(metric_payload.get("quality_notes") or [])
    note = "Upward rotation proxy onset lagged markedly behind elevation onset, suggesting threshold-limited or visibility-limited detection rather than a clean biomechanical delay."
    if note not in existing_notes:
        existing_notes.append(note)
    existing_flags = list(metric_payload.get("flags") or [])
    for flag in ("late_proxy_onset", "upward_rotation_onset_inconsistent"):
        if flag not in existing_flags:
            existing_flags.append(flag)
    metric_payload["status"] = "low_confidence"
    metric_payload["confidence"] = min(float(metric_payload.get("confidence") or 1.0), 0.45)
    metric_payload["quality_notes"] = existing_notes
    metric_payload["flags"] = existing_flags
    metric_payload["calculation_status"] = "threshold_limited_proxy_onset"


def _build_time_series(
    records: list[dict[str, Any]],
    *,
    side_debug: dict[str, dict[str, Any]],
    onset_position: int,
    peak_position: int,
    descent_position: int | None,
    key_frames: dict[str, int | None],
    baseline_comparison: dict[str, Any],
    asymmetry_series: dict[str, list[float]],
) -> list[dict[str, Any]]:
    baseline_metrics = baseline_comparison.get("metrics", {}) if isinstance(baseline_comparison, dict) else {}
    elevation_baseline = _nested_value(baseline_metrics, "baseline_vs_dynamic_elevation_change", "baseline_asymmetry")
    rotation_left_baseline = _find_metric_value(baseline_metrics.get("baseline_vs_dynamic_rotation_change", {}), "left")
    rotation_right_baseline = _find_metric_value(baseline_metrics.get("baseline_vs_dynamic_rotation_change", {}), "right")
    protraction_left_baseline = _find_metric_value(baseline_metrics.get("baseline_vs_dynamic_protraction_change", {}), "left")
    protraction_right_baseline = _find_metric_value(baseline_metrics.get("baseline_vs_dynamic_protraction_change", {}), "right")
    winging_left_baseline = _find_metric_value(baseline_metrics.get("baseline_vs_dynamic_winging_change", {}), "left")
    winging_right_baseline = _find_metric_value(baseline_metrics.get("baseline_vs_dynamic_winging_change", {}), "right")

    rows: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        frame_index = record["frame_index"]
        dynamic_elevation_asymmetry = asymmetry_series["dynamic_elevation_asymmetry"][index]
        dynamic_rotation_asymmetry = asymmetry_series["dynamic_upward_rotation_asymmetry"][index]
        dynamic_protraction_asymmetry = asymmetry_series["dynamic_protraction_asymmetry"][index]
        dynamic_winging_asymmetry = asymmetry_series["dynamic_winging_asymmetry"][index]
        events = _movement_event_labels(frame_index, key_frames)
        row = {
            "frame_index": frame_index,
            "phase": _phase_label(index, record["mean_humeral_abduction"], onset_position=onset_position, descent_position=descent_position),
            "phase_event": "|".join(events) if events else None,
            "min_visibility": record.get("min_visibility"),
            "humeral_abduction_angle_left": side_debug["left"]["humeral_abduction_angle"][index],
            "humeral_abduction_angle_right": side_debug["right"]["humeral_abduction_angle"][index],
            "mean_humeral_abduction": record["mean_humeral_abduction"],
            "scapular_elevation_dynamic_left": side_debug["left"]["scapular_elevation_dynamic"][index],
            "scapular_elevation_dynamic_right": side_debug["right"]["scapular_elevation_dynamic"][index],
            "dynamic_elevation_asymmetry": dynamic_elevation_asymmetry,
            "scapular_upward_rotation_dynamic_left": side_debug["left"]["scapular_upward_rotation_dynamic"][index],
            "scapular_upward_rotation_dynamic_right": side_debug["right"]["scapular_upward_rotation_dynamic"][index],
            "dynamic_upward_rotation_asymmetry": dynamic_rotation_asymmetry,
            "scapular_internal_rotation_dynamic_left": side_debug["left"]["scapular_internal_rotation_dynamic"][index],
            "scapular_internal_rotation_dynamic_right": side_debug["right"]["scapular_internal_rotation_dynamic"][index],
            "dynamic_protraction_asymmetry": dynamic_protraction_asymmetry,
            "dynamic_winging_left": side_debug["left"]["dynamic_winging"][index],
            "dynamic_winging_right": side_debug["right"]["dynamic_winging"][index],
            "dynamic_winging_asymmetry": dynamic_winging_asymmetry,
            "scapulohumeral_ratio_left": side_debug["left"]["scapulohumeral_ratio"][index],
            "scapulohumeral_ratio_right": side_debug["right"]["scapulohumeral_ratio"][index],
            "baseline_elevation_asymmetry": elevation_baseline,
            "baseline_vs_dynamic_elevation_delta": _safe_delta(dynamic_elevation_asymmetry, elevation_baseline),
            "baseline_rotation_left": rotation_left_baseline,
            "baseline_rotation_right": rotation_right_baseline,
            "baseline_vs_dynamic_rotation_delta_left": _safe_delta(side_debug["left"]["scapular_upward_rotation_dynamic"][index], rotation_left_baseline),
            "baseline_vs_dynamic_rotation_delta_right": _safe_delta(side_debug["right"]["scapular_upward_rotation_dynamic"][index], rotation_right_baseline),
            "baseline_protraction_left": protraction_left_baseline,
            "baseline_protraction_right": protraction_right_baseline,
            "baseline_vs_dynamic_protraction_delta_left": _safe_delta(side_debug["left"]["scapular_internal_rotation_dynamic"][index], protraction_left_baseline),
            "baseline_vs_dynamic_protraction_delta_right": _safe_delta(side_debug["right"]["scapular_internal_rotation_dynamic"][index], protraction_right_baseline),
            "baseline_winging_left": winging_left_baseline,
            "baseline_winging_right": winging_right_baseline,
            "baseline_vs_dynamic_winging_delta_left": _safe_delta(side_debug["left"]["dynamic_winging"][index], winging_left_baseline),
            "baseline_vs_dynamic_winging_delta_right": _safe_delta(side_debug["right"]["dynamic_winging"][index], winging_right_baseline),
            "landmarks": record.get("landmarks"),
            "reference_lines": record.get("reference_lines"),
            "key_frame_labels": events,
            "is_peak_frame": index == peak_position,
        }
        rows.append(row)
    return rows


def _phase_label(index: int, humeral_angle: float, *, onset_position: int, descent_position: int | None) -> str:
    if index < onset_position:
        return "start"
    if descent_position is not None and index >= descent_position:
        return "descent"
    if humeral_angle < 30.0:
        return "phase_1"
    if humeral_angle < 90.0:
        return "phase_2"
    return "phase_3"


def _movement_event_labels(frame_index: int, key_frames: dict[str, int | None]) -> list[str]:
    labels: list[str] = []
    if frame_index == key_frames.get("movement_start_frame"):
        labels.append("movement_start")
    if frame_index == key_frames.get("truncated_clip_frame"):
        labels.append("truncated_clip")
    if frame_index == key_frames.get("left_onset_frame"):
        labels.append("left_onset")
    if frame_index == key_frames.get("right_onset_frame"):
        labels.append("right_onset")
    if frame_index == key_frames.get("peak_frame"):
        labels.append("peak_abduction")
    if frame_index == key_frames.get("descent_start_frame"):
        labels.append("descent_start")
    return labels


def _nested_value(metrics: dict[str, Any], metric_name: str, nested_key: str, *, default: Any = None) -> Any:
    metric = metrics.get(metric_name, {}) if isinstance(metrics, dict) else {}
    value = metric.get("value") if isinstance(metric, dict) else None
    if not isinstance(value, dict):
        return default
    return value.get(nested_key, default)


def point_distance(point_a: tuple[float, float], point_b: tuple[float, float]) -> float:
    return hypot(point_a[0] - point_b[0], point_a[1] - point_b[1])


def angle_between_vectors(vector_a: tuple[float, float], vector_b: tuple[float, float]) -> float:
    angle_a = atan2(vector_a[1], vector_a[0])
    angle_b = atan2(vector_b[1], vector_b[0])
    value = abs(degrees(angle_a - angle_b)) % 360.0
    return min(value, 360.0 - value)
