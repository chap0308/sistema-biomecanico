"""Biomechanical proxy variables derived from frontal 2D squat landmarks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.squat.models import (
    SquatBiomechanicsArtifacts,
    SquatBiomechanicsSummary,
    SquatRepetitionMetrics,
)

_REQUIRED_LANDMARKS = (
    "left_shoulder",
    "right_shoulder",
    "left_hip",
    "right_hip",
    "left_knee",
    "right_knee",
    "left_ankle",
    "right_ankle",
)
_LANDMARK_COLUMNS = {"frame_index", "landmark", "x", "y"}
_PHASE_COLUMNS = {
    "frame_index",
    "timestamp_seconds",
    "valid_for_analysis",
    "repetition_index",
    "phase",
}
_METRIC_COLUMNS = (
    "trunk_inclination_deg",
    "pelvis_lateral_shift_pct",
    "left_knee_medial_deviation_pct",
    "right_knee_medial_deviation_pct",
    "bilateral_alignment_difference_pct",
)


def calculate_biomechanical_frame_metrics(
    landmarks: pd.DataFrame,
    frame_phases: pd.DataFrame,
) -> tuple[pd.DataFrame, float]:
    """Calculate frame-level proxy variables without applying decision rules."""
    _require_columns(landmarks, _LANDMARK_COLUMNS, source="landmarks")
    _require_columns(frame_phases, _PHASE_COLUMNS, source="frame phases")
    available = set(landmarks["landmark"].unique())
    missing_landmarks = sorted(set(_REQUIRED_LANDMARKS) - available)
    if missing_landmarks:
        raise ValueError(
            "landmarks are missing required points: " + ", ".join(missing_landmarks)
        )

    coordinates = landmarks.pivot_table(
        index="frame_index",
        columns="landmark",
        values=["x", "y"],
        aggfunc="mean",
    )
    phases = frame_phases.set_index("frame_index").sort_index()
    coordinates = coordinates.reindex(phases.index)

    shoulder_mid_x = _midpoint(
        coordinates[("x", "left_shoulder")],
        coordinates[("x", "right_shoulder")],
    )
    shoulder_mid_y = _midpoint(
        coordinates[("y", "left_shoulder")],
        coordinates[("y", "right_shoulder")],
    )
    pelvis_mid_x = _midpoint(
        coordinates[("x", "left_hip")],
        coordinates[("x", "right_hip")],
    )
    pelvis_mid_y = _midpoint(
        coordinates[("y", "left_hip")],
        coordinates[("y", "right_hip")],
    )
    ankle_mid_x = _midpoint(
        coordinates[("x", "left_ankle")],
        coordinates[("x", "right_ankle")],
    )
    shoulder_width = (
        coordinates[("x", "left_shoulder")]
        - coordinates[("x", "right_shoulder")]
    ).abs()

    valid = phases["valid_for_analysis"].map(_as_bool)
    initial_reference = (phases["repetition_index"] == 0) & valid
    if not initial_reference.any():
        initial_reference = valid
    initial_shoulder_width = float(shoulder_width[initial_reference].median())
    if not np.isfinite(initial_shoulder_width) or initial_shoulder_width <= 1e-6:
        raise ValueError("Unable to establish a valid initial shoulder-width reference")

    pelvis_over_support = pelvis_mid_x - ankle_mid_x
    initial_pelvis_offset = float(pelvis_over_support[initial_reference].median())
    trunk_dx = shoulder_mid_x - pelvis_mid_x
    trunk_upward_dy = pelvis_mid_y - shoulder_mid_y
    trunk_inclination = np.degrees(np.arctan2(trunk_dx, trunk_upward_dy))
    pelvis_shift = (
        (pelvis_over_support - initial_pelvis_offset)
        / initial_shoulder_width
        * 100.0
    )
    left_knee_deviation = _knee_medial_deviation(
        coordinates,
        side="left",
        normalization_width=initial_shoulder_width,
    )
    right_knee_deviation = _knee_medial_deviation(
        coordinates,
        side="right",
        normalization_width=initial_shoulder_width,
    )
    bilateral_difference = (left_knee_deviation - right_knee_deviation).abs()

    metrics = phases.reset_index()[
        [
            "frame_index",
            "timestamp_seconds",
            "valid_for_analysis",
            "repetition_index",
            "phase",
        ]
    ].copy()
    metrics["trunk_inclination_deg"] = trunk_inclination.to_numpy(dtype=float)
    metrics["pelvis_lateral_shift_pct"] = pelvis_shift.to_numpy(dtype=float)
    metrics["left_knee_medial_deviation_pct"] = left_knee_deviation.to_numpy(dtype=float)
    metrics["right_knee_medial_deviation_pct"] = right_knee_deviation.to_numpy(dtype=float)
    metrics["bilateral_alignment_difference_pct"] = bilateral_difference.to_numpy(
        dtype=float
    )
    metrics.loc[~valid.to_numpy(dtype=bool), list(_METRIC_COLUMNS)] = np.nan
    return metrics, initial_shoulder_width


def calculate_squat_biomechanics(
    landmarks_csv: str | Path,
    frame_phases_csv: str | Path,
    *,
    case_id: str,
    output_dir: str | Path,
) -> SquatBiomechanicsSummary:
    """Calculate and export frame and repetition biomechanical variables."""
    landmarks_path = Path(landmarks_csv)
    phases_path = Path(frame_phases_csv)
    landmarks = pd.read_csv(landmarks_path)
    phases = pd.read_csv(phases_path)
    frame_metrics, shoulder_width = calculate_biomechanical_frame_metrics(
        landmarks,
        phases,
    )
    repetitions = _summarize_repetitions(frame_metrics)

    case_output_dir = Path(output_dir) / case_id
    case_output_dir.mkdir(parents=True, exist_ok=True)
    frame_metrics_path = case_output_dir / "biomechanical_frame_metrics.csv"
    repetition_metrics_path = case_output_dir / "biomechanical_repetition_metrics.csv"
    plot_path = case_output_dir / "biomechanical_metrics.png"
    summary_path = case_output_dir / "biomechanical_summary.json"

    frame_metrics.to_csv(frame_metrics_path, index=False, encoding="utf-8-sig")
    pd.DataFrame(
        [item.model_dump() for item in repetitions],
        columns=list(SquatRepetitionMetrics.model_fields),
    ).to_csv(repetition_metrics_path, index=False, encoding="utf-8-sig")
    _save_metrics_plot(
        frame_metrics,
        output_path=plot_path,
        case_id=case_id,
    )

    artifacts = SquatBiomechanicsArtifacts(
        frame_metrics_csv=str(frame_metrics_path),
        repetition_metrics_csv=str(repetition_metrics_path),
        metrics_plot=str(plot_path),
        summary_json=str(summary_path),
    )
    summary = SquatBiomechanicsSummary(
        case_id=case_id,
        landmarks_csv=str(landmarks_path),
        frame_phases_csv=str(phases_path),
        initial_shoulder_width=shoulder_width,
        valid_metric_frames=int(
            frame_metrics[list(_METRIC_COLUMNS)].notna().all(axis=1).sum()
        ),
        total_frames=len(frame_metrics),
        repetitions=repetitions,
        conventions=[
            "Vista anterior: el signo positivo horizontal representa el lado anatomico izquierdo.",
            "La inclinacion del tronco es positiva hacia la izquierda y negativa hacia la derecha.",
            "El desplazamiento pelvico se mide respecto al centro de los tobillos y se corrige con el reposo inicial.",
            "La desviacion de rodilla es positiva en direccion medial y negativa en direccion lateral.",
            "Las distancias se normalizan por el ancho inicial de hombros y se expresan como porcentaje.",
        ],
        artifacts=artifacts,
    )
    summary_path.write_text(
        json.dumps(summary.model_dump(mode="json"), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return summary


def _knee_medial_deviation(
    coordinates: pd.DataFrame,
    *,
    side: str,
    normalization_width: float,
) -> pd.Series:
    hip_x = coordinates[("x", f"{side}_hip")]
    hip_y = coordinates[("y", f"{side}_hip")]
    knee_x = coordinates[("x", f"{side}_knee")]
    knee_y = coordinates[("y", f"{side}_knee")]
    ankle_x = coordinates[("x", f"{side}_ankle")]
    ankle_y = coordinates[("y", f"{side}_ankle")]
    vertical_span = ankle_y - hip_y
    interpolation = (knee_y - hip_y) / vertical_span.replace(0.0, np.nan)
    expected_knee_x = hip_x + interpolation * (ankle_x - hip_x)
    image_deviation = knee_x - expected_knee_x
    medial_sign = -1.0 if side == "left" else 1.0
    return image_deviation * medial_sign / normalization_width * 100.0


def _summarize_repetitions(
    frame_metrics: pd.DataFrame,
) -> list[SquatRepetitionMetrics]:
    summaries: list[SquatRepetitionMetrics] = []
    repetition_ids = sorted(
        int(value)
        for value in frame_metrics["repetition_index"].unique()
        if int(value) > 0
    )
    for repetition_index in repetition_ids:
        repetition = frame_metrics[
            frame_metrics["repetition_index"] == repetition_index
        ]
        peak_rows = repetition[repetition["phase"] == "maxima_profundidad"]
        if peak_rows.empty:
            continue
        peak = peak_rows.iloc[0]
        trunk_frame, trunk_max = _absolute_extreme(
            repetition,
            "trunk_inclination_deg",
        )
        pelvis_frame, pelvis_max = _absolute_extreme(
            repetition,
            "pelvis_lateral_shift_pct",
        )
        summaries.append(
            SquatRepetitionMetrics(
                repetition_index=repetition_index,
                peak_depth_frame=int(peak["frame_index"]),
                valid_frames_percentage=round(
                    float(repetition[list(_METRIC_COLUMNS)].notna().all(axis=1).mean())
                    * 100.0,
                    4,
                ),
                trunk_inclination_at_peak_deg=_optional_round(
                    peak["trunk_inclination_deg"]
                ),
                trunk_max_abs_deg=_optional_round(trunk_max),
                trunk_max_abs_frame=trunk_frame,
                pelvis_shift_at_peak_pct=_optional_round(
                    peak["pelvis_lateral_shift_pct"]
                ),
                pelvis_max_abs_shift_pct=_optional_round(pelvis_max),
                pelvis_max_abs_frame=pelvis_frame,
                left_knee_medial_deviation_at_peak_pct=_optional_round(
                    peak["left_knee_medial_deviation_pct"]
                ),
                right_knee_medial_deviation_at_peak_pct=_optional_round(
                    peak["right_knee_medial_deviation_pct"]
                ),
                left_knee_max_medial_deviation_pct=_maximum(
                    repetition["left_knee_medial_deviation_pct"]
                ),
                right_knee_max_medial_deviation_pct=_maximum(
                    repetition["right_knee_medial_deviation_pct"]
                ),
                bilateral_alignment_difference_at_peak_pct=_optional_round(
                    peak["bilateral_alignment_difference_pct"]
                ),
                bilateral_max_alignment_difference_pct=_maximum(
                    repetition["bilateral_alignment_difference_pct"]
                ),
            )
        )
    return summaries


def _absolute_extreme(
    table: pd.DataFrame,
    column: str,
) -> tuple[int | None, float | None]:
    valid = table.dropna(subset=[column])
    if valid.empty:
        return None, None
    index = valid[column].abs().idxmax()
    return int(valid.loc[index, "frame_index"]), abs(float(valid.loc[index, column]))


def _maximum(series: pd.Series) -> float | None:
    valid = series.dropna()
    return _optional_round(valid.max()) if not valid.empty else None


def _optional_round(value: object) -> float | None:
    if value is None:
        return None
    numeric = float(value)
    return round(numeric, 6) if np.isfinite(numeric) else None


def _midpoint(first: pd.Series, second: pd.Series) -> pd.Series:
    return (first + second) / 2.0


def _require_columns(
    table: pd.DataFrame,
    required: set[str],
    *,
    source: str,
) -> None:
    missing = sorted(required - set(table.columns))
    if missing:
        raise ValueError(f"{source} are missing required columns: {', '.join(missing)}")


def _as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "si", "sí"}


def _save_metrics_plot(
    frame_metrics: pd.DataFrame,
    *,
    output_path: Path,
    case_id: str,
) -> None:
    time = frame_metrics["timestamp_seconds"]
    figure, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True, constrained_layout=True)
    axes[0].plot(time, frame_metrics["trunk_inclination_deg"], color="#176B87")
    axes[0].set_ylabel("Tronco (°)")
    axes[1].plot(time, frame_metrics["pelvis_lateral_shift_pct"], color="#D97706")
    axes[1].set_ylabel("Pelvis (%)")
    axes[2].plot(
        time,
        frame_metrics["left_knee_medial_deviation_pct"],
        label="Izquierda",
        color="#B42318",
    )
    axes[2].plot(
        time,
        frame_metrics["right_knee_medial_deviation_pct"],
        label="Derecha",
        color="#2563EB",
    )
    axes[2].set_ylabel("Rodilla medial (%)")
    axes[2].legend(loc="upper right")
    axes[3].plot(
        time,
        frame_metrics["bilateral_alignment_difference_pct"],
        color="#6B4FA1",
    )
    axes[3].set_ylabel("Diferencia (%)")
    axes[3].set_xlabel("Tiempo (s)")
    for axis in axes:
        axis.axhline(0.0, color="#6B7280", linewidth=0.8, alpha=0.5)
        axis.grid(alpha=0.25)
    figure.suptitle(f"Variables biomecánicas observables - {case_id}")
    figure.savefig(output_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(figure)


__all__ = [
    "calculate_biomechanical_frame_metrics",
    "calculate_squat_biomechanics",
]
