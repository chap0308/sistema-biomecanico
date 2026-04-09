"""Plotting helpers for ISA, breathing and grouped static-image debug artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

_TIME_SERIES_COLUMNS = [
    "frame_index",
    "isa",
    "rib_flare_score",
    "left_costal_margin_angle",
    "right_costal_margin_angle",
    "costal_projection_index",
    "lower_thoracic_width_proxy",
    "upper_abdominal_width_proxy",
    "lower_thoracic_excursion",
    "upper_abdominal_excursion",
    "thoracic_abdominal_dissociation",
    "isa_status",
    "rib_flare_status",
    "thoracic_abdominal_status",
    "isa_confidence",
    "rib_flare_confidence",
    "thoracic_abdominal_confidence",
]

_MOVEMENT_TIME_SERIES_COLUMNS = [
    "frame_index",
    "humeral_abduction_angle_left",
    "humeral_abduction_angle_right",
    "scapular_elevation_dynamic_left",
    "scapular_elevation_dynamic_right",
    "scapular_upward_rotation_dynamic_left",
    "scapular_upward_rotation_dynamic_right",
    "scapular_internal_rotation_dynamic_left",
    "scapular_internal_rotation_dynamic_right",
    "dynamic_winging_left",
    "dynamic_winging_right",
]


def time_series_to_dataframe(time_series: list[dict[str, Any]]) -> pd.DataFrame:
    """Convert breathing time-series JSON into a stable DataFrame."""
    rows: list[dict[str, Any]] = []
    for item in time_series:
        row = {key: item.get(key) for key in _TIME_SERIES_COLUMNS}
        rows.append(row)
    dataframe = pd.DataFrame(rows)
    if dataframe.empty:
        return pd.DataFrame(columns=_TIME_SERIES_COLUMNS)
    dataframe = dataframe.sort_values("frame_index").reset_index(drop=True)
    return dataframe


def save_time_series_csv(time_series: list[dict[str, Any]], output_path: Path) -> pd.DataFrame:
    """Persist the breathing time series as CSV."""
    dataframe = time_series_to_dataframe(time_series)
    dataframe.to_csv(output_path, index=False)
    return dataframe


def movement_debug_to_dataframe(debug_payload: dict[str, Any]) -> pd.DataFrame:
    """Convert movement debug series into a stable frame-by-frame DataFrame."""
    frame_indices = debug_payload.get("frame_indices", []) if isinstance(debug_payload, dict) else []
    series = debug_payload.get("series", {}) if isinstance(debug_payload, dict) else {}
    left_series = series.get("left", {}) if isinstance(series, dict) else {}
    right_series = series.get("right", {}) if isinstance(series, dict) else {}

    rows: list[dict[str, Any]] = []
    for index, frame_index in enumerate(frame_indices):
        rows.append(
            {
                "frame_index": frame_index,
                "humeral_abduction_angle_left": _series_value(left_series, "humeral_abduction_angle", index),
                "humeral_abduction_angle_right": _series_value(right_series, "humeral_abduction_angle", index),
                "scapular_elevation_dynamic_left": _series_value(left_series, "scapular_elevation_dynamic", index),
                "scapular_elevation_dynamic_right": _series_value(right_series, "scapular_elevation_dynamic", index),
                "scapular_upward_rotation_dynamic_left": _series_value(left_series, "scapular_upward_rotation_dynamic", index),
                "scapular_upward_rotation_dynamic_right": _series_value(right_series, "scapular_upward_rotation_dynamic", index),
                "scapular_internal_rotation_dynamic_left": _series_value(left_series, "scapular_internal_rotation_dynamic", index),
                "scapular_internal_rotation_dynamic_right": _series_value(right_series, "scapular_internal_rotation_dynamic", index),
                "dynamic_winging_left": _series_value(left_series, "dynamic_winging", index),
                "dynamic_winging_right": _series_value(right_series, "dynamic_winging", index),
            }
        )
    dataframe = pd.DataFrame(rows)
    if dataframe.empty:
        return pd.DataFrame(columns=_MOVEMENT_TIME_SERIES_COLUMNS)
    return dataframe.sort_values("frame_index").reset_index(drop=True)


def save_movement_time_series_csv(debug_payload: dict[str, Any], output_path: Path) -> pd.DataFrame:
    """Persist movement debug series as CSV."""
    dataframe = movement_debug_to_dataframe(debug_payload)
    dataframe.to_csv(output_path, index=False)
    return dataframe


def save_group_metrics_csvs(groups: dict[str, Any], output_dir: Path) -> list[Path]:
    """Persist summary CSVs for grouped static-image analysis."""
    output_dir.mkdir(parents=True, exist_ok=True)
    saved_paths: list[Path] = []

    rest_group = groups.get("rest_phase1") if isinstance(groups, dict) else None
    if isinstance(rest_group, dict):
        dataframe = rest_phase1_metrics_to_dataframe(rest_group)
        if not dataframe.empty:
            path = output_dir / "rest_phase1_metrics.csv"
            dataframe.to_csv(path, index=False)
            saved_paths.append(path)

    face_group = groups.get("face") if isinstance(groups, dict) else None
    if isinstance(face_group, dict):
        dataframe = single_group_metrics_to_dataframe(face_group)
        if not dataframe.empty:
            path = output_dir / "face_metrics.csv"
            dataframe.to_csv(path, index=False)
            saved_paths.append(path)

    foot_group = groups.get("foot_triptych") if isinstance(groups, dict) else None
    if isinstance(foot_group, dict):
        dataframe = single_group_metrics_to_dataframe(foot_group)
        if not dataframe.empty:
            path = output_dir / "foot_triptych_metrics.csv"
            dataframe.to_csv(path, index=False)
            saved_paths.append(path)

    scapula_group = groups.get("scapula") if isinstance(groups, dict) else None
    if isinstance(scapula_group, dict):
        dataframe = single_group_metrics_to_dataframe(scapula_group)
        if not dataframe.empty:
            path = output_dir / "scapula_metrics.csv"
            dataframe.to_csv(path, index=False)
            saved_paths.append(path)

    return saved_paths


def save_static_debug_plots(groups: dict[str, Any], output_dir: Path) -> list[Path]:
    """Generate comparative plots for grouped static-image analysis."""
    output_dir.mkdir(parents=True, exist_ok=True)
    saved_paths: list[Path] = []

    rest_group = groups.get("rest_phase1") if isinstance(groups, dict) else None
    if isinstance(rest_group, dict):
        dataframe = rest_phase1_metrics_to_dataframe(rest_group)
        if not dataframe.empty:
            for metric_name in ["shoulder_height_difference", "torso_lateral_tilt", "pelvic_tilt", "head_tilt_angle"]:
                paths = _save_bar_plot(
                    dataframe,
                    x="view",
                    y=metric_name,
                    title=f"Rest Phase 1: {metric_name}",
                    ylabel=metric_name,
                    output_path=output_dir / f"rest_phase1_{metric_name}.png",
                )
                saved_paths.extend(paths)

    foot_group = groups.get("foot_triptych") if isinstance(groups, dict) else None
    if isinstance(foot_group, dict):
        dataframe = single_group_metrics_to_dataframe(foot_group)
        if not dataframe.empty:
            saved_paths.extend(
                _save_subset_bar_plot(
                    dataframe,
                    metric_names=["foot_progression_angle_left", "foot_progression_angle_right"],
                    title="Foot progression left/right",
                    ylabel="Degrees",
                    output_path=output_dir / "foot_progression_comparison.png",
                )
            )
            saved_paths.extend(
                _save_subset_bar_plot(
                    dataframe,
                    metric_names=["calcaneal_angle_left", "calcaneal_angle_right"],
                    title="Calcaneal angle left/right",
                    ylabel="Degrees",
                    output_path=output_dir / "calcaneal_comparison.png",
                )
            )
            saved_paths.extend(
                _save_subset_bar_plot(
                    dataframe,
                    metric_names=["arch_height_ratio_left", "arch_height_ratio_right"],
                    title="Arch height ratio left/right",
                    ylabel="Ratio",
                    output_path=output_dir / "arch_height_comparison.png",
                )
            )

    scapula_group = groups.get("scapula") if isinstance(groups, dict) else None
    if isinstance(scapula_group, dict):
        dataframe = single_group_metrics_to_dataframe(scapula_group)
        if not dataframe.empty:
            saved_paths.extend(
                _save_subset_bar_plot(
                    dataframe,
                    metric_names=["scapula_spine_distance_left", "scapula_spine_distance_right"],
                    title="Scapula-spine distance left/right",
                    ylabel="Normalized",
                    output_path=output_dir / "scapula_spine_distance_comparison.png",
                )
            )
            saved_paths.extend(
                _save_subset_bar_plot(
                    dataframe,
                    metric_names=["scapular_internal_rotation_left", "scapular_internal_rotation_right"],
                    title="Scapular internal rotation left/right",
                    ylabel="Degrees",
                    output_path=output_dir / "scapular_internal_rotation_comparison.png",
                )
            )
            saved_paths.extend(
                _save_subset_bar_plot(
                    dataframe,
                    metric_names=["scapular_upward_rotation_left", "scapular_upward_rotation_right"],
                    title="Scapular upward rotation left/right",
                    ylabel="Degrees",
                    output_path=output_dir / "scapular_upward_rotation_comparison.png",
                )
            )

    return saved_paths


def rest_phase1_metrics_to_dataframe(group_payload: dict[str, Any]) -> pd.DataFrame:
    """Flatten rest_phase1 grouped metrics into one row per view."""
    rows: list[dict[str, Any]] = []
    metrics_by_view = group_payload.get("metrics_by_view", {}) if isinstance(group_payload, dict) else {}
    for view_name, view_payload in metrics_by_view.items():
        row: dict[str, Any] = {"view": view_name}
        metrics = view_payload.get("metrics", {}) if isinstance(view_payload, dict) else {}
        for metric_name, metric_payload in metrics.items():
            if isinstance(metric_payload, dict):
                row[metric_name] = metric_payload.get("value")
        rows.append(row)
    return pd.DataFrame(rows)


def single_group_metrics_to_dataframe(group_payload: dict[str, Any]) -> pd.DataFrame:
    """Flatten a single static group metrics block into a tabular summary."""
    metrics = group_payload.get("metrics", {}) if isinstance(group_payload, dict) else {}
    rows: list[dict[str, Any]] = []
    for metric_name, metric_payload in metrics.items():
        if not isinstance(metric_payload, dict):
            continue
        rows.append(
            {
                "metric": metric_name,
                "value": metric_payload.get("value"),
                "plane": metric_payload.get("plane"),
                "unit": metric_payload.get("unit"),
                "measurement_type": metric_payload.get("measurement_type"),
                "status": metric_payload.get("status"),
                "priority": metric_payload.get("priority"),
            }
        )
    return pd.DataFrame(rows)


def save_debug_plots(dataframe: pd.DataFrame, output_dir: Path) -> list[Path]:
    """Generate the main debug plots from sampled breathing metrics."""
    output_dir.mkdir(parents=True, exist_ok=True)
    saved_paths: list[Path] = []

    saved_paths.extend(
        _save_line_plot(
            dataframe,
            x="frame_index",
            y_columns=["isa"],
            title="ISA vs Frame",
            ylabel="Degrees",
            output_path=output_dir / "isa_plot.png",
        )
    )
    saved_paths.extend(
        _save_line_plot(
            dataframe,
            x="frame_index",
            y_columns=["rib_flare_score"],
            title="Rib Flare Score vs Frame",
            ylabel="Score",
            output_path=output_dir / "rib_flare_plot.png",
        )
    )
    saved_paths.extend(
        _save_line_plot(
            dataframe,
            x="frame_index",
            y_columns=["left_costal_margin_angle", "right_costal_margin_angle"],
            title="Left vs Right Costal Margin Angle",
            ylabel="Degrees",
            output_path=output_dir / "costal_margin_angles_plot.png",
        )
    )
    saved_paths.extend(
        _save_line_plot(
            dataframe,
            x="frame_index",
            y_columns=["costal_projection_index"],
            title="Costal Projection Index vs Frame",
            ylabel="Index",
            output_path=output_dir / "costal_projection_plot.png",
        )
    )
    saved_paths.extend(
        _save_line_plot(
            dataframe,
            x="frame_index",
            y_columns=["thoracic_abdominal_dissociation"],
            title="Thoracic-Abdominal Dissociation vs Frame",
            ylabel="Index",
            output_path=output_dir / "thoracic_abdominal_dissociation_plot.png",
        )
    )
    saved_paths.extend(
        _save_line_plot(
            dataframe,
            x="frame_index",
            y_columns=["upper_abdominal_excursion", "lower_thoracic_excursion"],
            title="Upper Abdominal vs Lower Thoracic Excursion",
            ylabel="Normalized Excursion",
            output_path=output_dir / "thoracic_excursion_plot.png",
        )
    )
    return saved_paths


def save_movement_debug_plots(dataframe: pd.DataFrame, output_dir: Path) -> list[Path]:
    """Generate the main debug plots from movement frame series."""
    output_dir.mkdir(parents=True, exist_ok=True)
    saved_paths: list[Path] = []

    saved_paths.extend(
        _save_line_plot(
            dataframe,
            x="frame_index",
            y_columns=["humeral_abduction_angle_left", "humeral_abduction_angle_right"],
            title="Humeral Abduction Angle",
            ylabel="Degrees",
            output_path=output_dir / "movement_humeral_abduction_plot.png",
        )
    )
    saved_paths.extend(
        _save_line_plot(
            dataframe,
            x="frame_index",
            y_columns=["scapular_elevation_dynamic_left", "scapular_elevation_dynamic_right"],
            title="Scapular Elevation Proxy",
            ylabel="Normalized",
            output_path=output_dir / "movement_scapular_elevation_plot.png",
        )
    )
    saved_paths.extend(
        _save_line_plot(
            dataframe,
            x="frame_index",
            y_columns=["scapular_upward_rotation_dynamic_left", "scapular_upward_rotation_dynamic_right"],
            title="Scapular Upward Rotation Proxy",
            ylabel="Degrees",
            output_path=output_dir / "movement_upward_rotation_plot.png",
        )
    )
    saved_paths.extend(
        _save_line_plot(
            dataframe,
            x="frame_index",
            y_columns=["scapular_internal_rotation_dynamic_left", "scapular_internal_rotation_dynamic_right"],
            title="Scapular Internal Rotation / Protraction Proxy",
            ylabel="Normalized",
            output_path=output_dir / "movement_protraction_plot.png",
        )
    )
    saved_paths.extend(
        _save_line_plot(
            dataframe,
            x="frame_index",
            y_columns=["dynamic_winging_left", "dynamic_winging_right"],
            title="Dynamic Winging Proxy",
            ylabel="Normalized",
            output_path=output_dir / "movement_winging_plot.png",
        )
    )
    return saved_paths


def _save_line_plot(
    dataframe: pd.DataFrame,
    *,
    x: str,
    y_columns: list[str],
    title: str,
    ylabel: str,
    output_path: Path,
) -> list[Path]:
    available_columns = [column for column in y_columns if column in dataframe.columns and dataframe[column].notna().any()]
    if dataframe.empty or x not in dataframe.columns or not available_columns:
        return []

    figure, axis = plt.subplots(figsize=(10, 5))
    for column in available_columns:
        axis.plot(dataframe[x], dataframe[column], marker="o", linewidth=2, label=column)
    for frame_value, label, color in _movement_plot_events(dataframe, x):
        axis.axvline(frame_value, color=color, linestyle="--", alpha=0.45, linewidth=1.5)
        axis.text(frame_value, axis.get_ylim()[1], label, rotation=90, va="top", ha="right", fontsize=8, color=color)
    axis.set_title(title)
    axis.set_xlabel("Frame Index")
    axis.set_ylabel(ylabel)
    axis.grid(True, alpha=0.3)
    if len(available_columns) > 1:
        axis.legend()
    figure.tight_layout()
    figure.savefig(output_path, dpi=160)
    plt.close(figure)
    return [output_path]


def _movement_plot_events(dataframe: pd.DataFrame, x: str) -> list[tuple[float, str, str]]:
    if "phase_event" not in dataframe.columns or x not in dataframe.columns:
        return []
    labels = {
        "movement_start": ("start", "#6a4c93"),
        "truncated_clip": ("late start", "#c1121f"),
        "left_onset": ("L onset", "#2a9d8f"),
        "right_onset": ("R onset", "#e76f51"),
        "peak_abduction": ("peak", "#264653"),
        "descent_start": ("descent", "#f4a261"),
    }
    events: list[tuple[float, str, str]] = []
    for _, row in dataframe.iterrows():
        raw_value = row.get("phase_event")
        if not isinstance(raw_value, str) or not raw_value:
            continue
        frame_value = row.get(x)
        if frame_value is None:
            continue
        for event_name in raw_value.split("|"):
            if event_name in labels:
                label, color = labels[event_name]
                events.append((float(frame_value), label, color))
    deduped: list[tuple[float, str, str]] = []
    seen: set[tuple[float, str]] = set()
    for frame_value, label, color in events:
        key = (frame_value, label)
        if key in seen:
            continue
        seen.add(key)
        deduped.append((frame_value, label, color))
    return deduped


def _save_bar_plot(
    dataframe: pd.DataFrame,
    *,
    x: str,
    y: str,
    title: str,
    ylabel: str,
    output_path: Path,
) -> list[Path]:
    if dataframe.empty or x not in dataframe.columns or y not in dataframe.columns or not dataframe[y].notna().any():
        return []
    figure, axis = plt.subplots(figsize=(8, 4.5))
    axis.bar(dataframe[x], dataframe[y], color="#2E86AB")
    axis.set_title(title)
    axis.set_xlabel(x)
    axis.set_ylabel(ylabel)
    axis.grid(True, axis="y", alpha=0.25)
    figure.tight_layout()
    figure.savefig(output_path, dpi=160)
    plt.close(figure)
    return [output_path]


def _series_value(series_by_name: dict[str, Any], name: str, index: int) -> Any:
    values = series_by_name.get(name, []) if isinstance(series_by_name, dict) else []
    if not isinstance(values, list) or index >= len(values):
        return None
    return values[index]


def _save_subset_bar_plot(
    dataframe: pd.DataFrame,
    *,
    metric_names: list[str],
    title: str,
    ylabel: str,
    output_path: Path,
) -> list[Path]:
    available = [name for name in metric_names if name in dataframe.columns and dataframe[name].notna().any()]
    if dataframe.empty or not available:
        return []

    subset = dataframe[["metric", "value"]].copy() if "metric" in dataframe.columns and "value" in dataframe.columns else None
    if subset is not None:
        metric_map = {str(row["metric"]): row["value"] for _, row in subset.iterrows()}
        values = [metric_map.get(name) for name in metric_names]
        if not any(value is not None for value in values):
            return []
        figure, axis = plt.subplots(figsize=(8, 4.5))
        axis.bar(metric_names, values, color=["#2E86AB", "#F18F01", "#6AB187", "#C73E1D"][: len(metric_names)])
        axis.set_title(title)
        axis.set_ylabel(ylabel)
        axis.grid(True, axis="y", alpha=0.25)
        figure.tight_layout()
        figure.savefig(output_path, dpi=160)
        plt.close(figure)
        return [output_path]
    return []

_MOVEMENT_TIME_SERIES_COLUMNS = [
    "frame_index",
    "phase",
    "phase_event",
    "min_visibility",
    "humeral_abduction_angle_left",
    "humeral_abduction_angle_right",
    "mean_humeral_abduction",
    "scapular_elevation_dynamic_left",
    "scapular_elevation_dynamic_right",
    "dynamic_elevation_asymmetry",
    "scapular_upward_rotation_dynamic_left",
    "scapular_upward_rotation_dynamic_right",
    "dynamic_upward_rotation_asymmetry",
    "scapular_internal_rotation_dynamic_left",
    "scapular_internal_rotation_dynamic_right",
    "dynamic_protraction_asymmetry",
    "dynamic_winging_left",
    "dynamic_winging_right",
    "dynamic_winging_asymmetry",
    "scapulohumeral_ratio_left",
    "scapulohumeral_ratio_right",
    "baseline_elevation_asymmetry",
    "baseline_vs_dynamic_elevation_delta",
    "baseline_rotation_left",
    "baseline_rotation_right",
    "baseline_vs_dynamic_rotation_delta_left",
    "baseline_vs_dynamic_rotation_delta_right",
    "baseline_protraction_left",
    "baseline_protraction_right",
    "baseline_vs_dynamic_protraction_delta_left",
    "baseline_vs_dynamic_protraction_delta_right",
    "baseline_winging_left",
    "baseline_winging_right",
    "baseline_vs_dynamic_winging_delta_left",
    "baseline_vs_dynamic_winging_delta_right",
]


def movement_debug_to_dataframe(debug_payload: dict[str, Any]) -> pd.DataFrame:
    """Convert movement debug series into a stable frame-by-frame DataFrame."""
    time_series = debug_payload.get("time_series", []) if isinstance(debug_payload, dict) else []
    if isinstance(time_series, list) and time_series:
        rows: list[dict[str, Any]] = []
        for item in time_series:
            rows.append({key: item.get(key) for key in _MOVEMENT_TIME_SERIES_COLUMNS})
        dataframe = pd.DataFrame(rows)
        if dataframe.empty:
            return pd.DataFrame(columns=_MOVEMENT_TIME_SERIES_COLUMNS)
        return dataframe.sort_values("frame_index").reset_index(drop=True)

    frame_indices = debug_payload.get("frame_indices", []) if isinstance(debug_payload, dict) else []
    series = debug_payload.get("series", {}) if isinstance(debug_payload, dict) else {}
    global_series = debug_payload.get("global_series", {}) if isinstance(debug_payload, dict) else {}
    left_series = series.get("left", {}) if isinstance(series, dict) else {}
    right_series = series.get("right", {}) if isinstance(series, dict) else {}

    rows: list[dict[str, Any]] = []
    for index, frame_index in enumerate(frame_indices):
        rows.append(
            {
                "frame_index": frame_index,
                "humeral_abduction_angle_left": _series_value(left_series, "humeral_abduction_angle", index),
                "humeral_abduction_angle_right": _series_value(right_series, "humeral_abduction_angle", index),
                "scapular_elevation_dynamic_left": _series_value(left_series, "scapular_elevation_dynamic", index),
                "scapular_elevation_dynamic_right": _series_value(right_series, "scapular_elevation_dynamic", index),
                "dynamic_elevation_asymmetry": _series_value(global_series, "dynamic_elevation_asymmetry", index),
                "scapular_upward_rotation_dynamic_left": _series_value(left_series, "scapular_upward_rotation_dynamic", index),
                "scapular_upward_rotation_dynamic_right": _series_value(right_series, "scapular_upward_rotation_dynamic", index),
                "dynamic_upward_rotation_asymmetry": _series_value(global_series, "dynamic_upward_rotation_asymmetry", index),
                "scapular_internal_rotation_dynamic_left": _series_value(left_series, "scapular_internal_rotation_dynamic", index),
                "scapular_internal_rotation_dynamic_right": _series_value(right_series, "scapular_internal_rotation_dynamic", index),
                "dynamic_protraction_asymmetry": _series_value(global_series, "dynamic_protraction_asymmetry", index),
                "dynamic_winging_left": _series_value(left_series, "dynamic_winging", index),
                "dynamic_winging_right": _series_value(right_series, "dynamic_winging", index),
                "dynamic_winging_asymmetry": _series_value(global_series, "dynamic_winging_asymmetry", index),
                "scapulohumeral_ratio_left": _series_value(left_series, "scapulohumeral_ratio", index),
                "scapulohumeral_ratio_right": _series_value(right_series, "scapulohumeral_ratio", index),
            }
        )
    dataframe = pd.DataFrame(rows)
    if dataframe.empty:
        return pd.DataFrame(columns=_MOVEMENT_TIME_SERIES_COLUMNS)
    return dataframe.sort_values("frame_index").reset_index(drop=True)


def save_movement_time_series_csv(debug_payload: dict[str, Any], output_path: Path) -> pd.DataFrame:
    """Persist movement debug series as CSV."""
    dataframe = movement_debug_to_dataframe(debug_payload)
    dataframe.to_csv(output_path, index=False)
    return dataframe


def save_movement_phases_csv(debug_payload: dict[str, Any], output_path: Path) -> pd.DataFrame:
    """Persist movement phase labels as a compact CSV."""
    dataframe = movement_debug_to_dataframe(debug_payload)
    phase_columns = [column for column in ["frame_index", "phase", "phase_event"] if column in dataframe.columns]
    phase_dataframe = dataframe[phase_columns].copy() if phase_columns else pd.DataFrame(columns=["frame_index", "phase", "phase_event"])
    phase_dataframe.to_csv(output_path, index=False)
    return phase_dataframe


def save_movement_debug_plots(dataframe: pd.DataFrame, output_dir: Path) -> list[Path]:
    """Generate the main debug plots from movement frame series."""
    output_dir.mkdir(parents=True, exist_ok=True)
    saved_paths: list[Path] = []

    saved_paths.extend(_save_line_plot(dataframe, x="frame_index", y_columns=["humeral_abduction_angle_left", "humeral_abduction_angle_right"], title="Humeral Abduction Angle", ylabel="Degrees", output_path=output_dir / "movement_humeral_abduction_plot.png"))
    saved_paths.extend(_save_line_plot(dataframe, x="frame_index", y_columns=["scapular_elevation_dynamic_left", "scapular_elevation_dynamic_right"], title="Scapular Elevation Proxy", ylabel="Normalized", output_path=output_dir / "movement_scapular_elevation_plot.png"))
    saved_paths.extend(_save_line_plot(dataframe, x="frame_index", y_columns=["dynamic_elevation_asymmetry"], title="Dynamic Elevation Asymmetry", ylabel="Normalized", output_path=output_dir / "movement_dynamic_elevation_asymmetry_plot.png"))
    saved_paths.extend(_save_line_plot(dataframe, x="frame_index", y_columns=["scapular_upward_rotation_dynamic_left", "scapular_upward_rotation_dynamic_right"], title="Scapular Upward Rotation Proxy", ylabel="Degrees", output_path=output_dir / "movement_upward_rotation_plot.png"))
    saved_paths.extend(_save_line_plot(dataframe, x="frame_index", y_columns=["dynamic_upward_rotation_asymmetry"], title="Dynamic Upward Rotation Asymmetry", ylabel="Degrees", output_path=output_dir / "movement_dynamic_upward_rotation_asymmetry_plot.png"))
    saved_paths.extend(_save_line_plot(dataframe, x="frame_index", y_columns=["scapular_internal_rotation_dynamic_left", "scapular_internal_rotation_dynamic_right"], title="Scapular Internal Rotation / Protraction Proxy", ylabel="Normalized", output_path=output_dir / "movement_protraction_plot.png"))
    saved_paths.extend(_save_line_plot(dataframe, x="frame_index", y_columns=["dynamic_winging_left", "dynamic_winging_right"], title="Dynamic Winging Proxy", ylabel="Normalized", output_path=output_dir / "movement_winging_plot.png"))
    saved_paths.extend(_save_line_plot(dataframe, x="frame_index", y_columns=["scapulohumeral_ratio_left", "scapulohumeral_ratio_right"], title="Scapulohumeral Ratio", ylabel="Ratio", output_path=output_dir / "movement_scapulohumeral_ratio_plot.png"))
    saved_paths.extend(_save_line_plot(dataframe, x="frame_index", y_columns=["baseline_vs_dynamic_elevation_delta"], title="Baseline vs Dynamic Elevation Delta", ylabel="Normalized", output_path=output_dir / "movement_baseline_vs_dynamic_elevation_plot.png"))
    saved_paths.extend(_save_line_plot(dataframe, x="frame_index", y_columns=["baseline_vs_dynamic_rotation_delta_left", "baseline_vs_dynamic_rotation_delta_right"], title="Baseline vs Dynamic Rotation Delta", ylabel="Degrees", output_path=output_dir / "movement_baseline_vs_dynamic_rotation_plot.png"))
    saved_paths.extend(_save_line_plot(dataframe, x="frame_index", y_columns=["baseline_vs_dynamic_protraction_delta_left", "baseline_vs_dynamic_protraction_delta_right"], title="Baseline vs Dynamic Protraction Delta", ylabel="Normalized", output_path=output_dir / "movement_baseline_vs_dynamic_protraction_plot.png"))
    saved_paths.extend(_save_line_plot(dataframe, x="frame_index", y_columns=["baseline_vs_dynamic_winging_delta_left", "baseline_vs_dynamic_winging_delta_right"], title="Baseline vs Dynamic Winging Delta", ylabel="Normalized", output_path=output_dir / "movement_baseline_vs_dynamic_winging_plot.png"))
    return saved_paths
