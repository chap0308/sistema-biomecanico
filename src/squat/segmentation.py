"""Interpretable temporal segmentation for frontal bilateral-squat videos."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Sequence

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.squat.models import (
    SquatRepetition,
    SquatSegmentationArtifacts,
    SquatSegmentationSummary,
)

_LANDMARK_REQUIRED_COLUMNS = {
    "frame_index",
    "timestamp_seconds",
    "landmark",
    "y",
}
_QUALITY_REQUIRED_COLUMNS = {"frame_index", "valid_for_analysis"}


@dataclass(slots=True, frozen=True)
class DetectedRepetition:
    """Frame indexes delimiting one squat repetition."""

    start_frame: int
    peak_depth_frame: int
    end_frame: int


def detect_squat_repetitions(
    hip_midpoint_y: Sequence[float],
    *,
    fps: float,
    smoothing_seconds: float = 0.2,
    peak_window_seconds: float = 3.0,
    minimum_peak_distance_seconds: float = 2.0,
    maximum_repetition_seconds: float = 10.0,
) -> tuple[np.ndarray, list[DetectedRepetition]]:
    """Detect repetitions from the downward displacement of the hip midpoint."""
    if fps <= 0:
        raise ValueError("fps must be greater than zero")
    signal = np.asarray(hip_midpoint_y, dtype=float)
    if signal.ndim != 1 or signal.size < 3:
        raise ValueError("hip_midpoint_y must be a one-dimensional signal")
    if not np.isfinite(signal).any():
        raise ValueError("hip_midpoint_y must contain at least one finite value")

    interpolated = (
        pd.Series(signal)
        .interpolate(limit_direction="both")
        .ffill()
        .bfill()
    )
    smoothing_window = max(3, int(round(fps * smoothing_seconds)))
    smoothed = (
        interpolated.rolling(smoothing_window, center=True, min_periods=1)
        .median()
        .rolling(smoothing_window, center=True, min_periods=1)
        .mean()
        .to_numpy(dtype=float)
    )

    signal_range = float(np.quantile(smoothed, 0.95) - np.quantile(smoothed, 0.05))
    if signal_range < 0.04:
        return smoothed, []

    peak_window = max(2, int(round(fps * peak_window_seconds)))
    minimum_peak_distance = max(1, int(round(fps * minimum_peak_distance_seconds)))
    minimum_prominence = max(0.03, signal_range * 0.18)
    candidates = _peak_candidates(
        smoothed,
        window=peak_window,
        minimum_prominence=minimum_prominence,
    )
    peaks = _suppress_nearby_peaks(
        candidates,
        signal=smoothed,
        minimum_distance=minimum_peak_distance,
    )

    maximum_repetition_frames = max(3, int(round(fps * maximum_repetition_seconds)))
    repetitions = [
        _repetition_around_peak(
            smoothed,
            peaks=peaks,
            peak_position=position,
            maximum_repetition_frames=maximum_repetition_frames,
        )
        for position in range(len(peaks))
    ]
    return smoothed, repetitions


def segment_squat_pose_artifacts(
    landmarks_csv: str | Path,
    frame_quality_csv: str | Path,
    *,
    case_id: str,
    output_dir: str | Path,
) -> SquatSegmentationSummary:
    """Segment pose artifacts and export per-frame and per-repetition evidence."""
    landmarks_path = Path(landmarks_csv)
    quality_path = Path(frame_quality_csv)
    landmarks = pd.read_csv(landmarks_path)
    quality = pd.read_csv(quality_path)
    _require_columns(landmarks, _LANDMARK_REQUIRED_COLUMNS, source=landmarks_path)
    _require_columns(quality, _QUALITY_REQUIRED_COLUMNS, source=quality_path)

    hips = landmarks[landmarks["landmark"].isin(("left_hip", "right_hip"))]
    hip_signal = (
        hips.pivot_table(
            index="frame_index",
            columns="landmark",
            values="y",
            aggfunc="mean",
        )
        .reindex(columns=["left_hip", "right_hip"])
        .mean(axis=1)
        .sort_index()
    )
    timestamps = (
        landmarks.groupby("frame_index")["timestamp_seconds"]
        .first()
        .reindex(hip_signal.index)
        .astype(float)
    )
    fps = _infer_fps(timestamps.to_numpy(dtype=float))
    smoothed, detected = detect_squat_repetitions(hip_signal.to_numpy(), fps=fps)

    quality_by_frame = (
        quality.set_index("frame_index")["valid_for_analysis"]
        .map(_as_bool)
        .reindex(hip_signal.index, fill_value=False)
    )
    phases = np.full(len(hip_signal), "reposo", dtype=object)
    repetition_numbers = np.zeros(len(hip_signal), dtype=int)
    repetitions: list[SquatRepetition] = []

    for repetition_index, repetition in enumerate(detected, start=1):
        start_position = repetition.start_frame
        peak_position = repetition.peak_depth_frame
        end_position = repetition.end_frame
        phases[start_position:peak_position] = "descenso"
        phases[peak_position] = "maxima_profundidad"
        phases[peak_position + 1 : end_position] = "ascenso"
        phases[end_position] = "cierre"
        repetition_numbers[start_position : end_position + 1] = repetition_index

        frame_slice = quality_by_frame.iloc[start_position : end_position + 1]
        start_seconds = float(timestamps.iloc[start_position])
        peak_seconds = float(timestamps.iloc[peak_position])
        end_seconds = float(timestamps.iloc[end_position])
        repetitions.append(
            SquatRepetition(
                repetition_index=repetition_index,
                start_frame=int(hip_signal.index[start_position]),
                peak_depth_frame=int(hip_signal.index[peak_position]),
                end_frame=int(hip_signal.index[end_position]),
                start_seconds=start_seconds,
                peak_depth_seconds=peak_seconds,
                end_seconds=end_seconds,
                descent_duration_seconds=round(peak_seconds - start_seconds, 4),
                ascent_duration_seconds=round(end_seconds - peak_seconds, 4),
                total_duration_seconds=round(end_seconds - start_seconds, 4),
                peak_hip_midpoint_y=round(float(smoothed[peak_position]), 8),
                valid_frames_percentage=round(float(frame_slice.mean()) * 100.0, 4),
            )
        )

    case_output_dir = Path(output_dir) / case_id
    case_output_dir.mkdir(parents=True, exist_ok=True)
    phases_path = case_output_dir / "frame_phases.csv"
    repetitions_path = case_output_dir / "repetitions.csv"
    plot_path = case_output_dir / "segmentation.png"
    summary_path = case_output_dir / "segmentation_summary.json"

    frame_table = pd.DataFrame(
        {
            "frame_index": hip_signal.index.astype(int),
            "timestamp_seconds": timestamps.to_numpy(dtype=float),
            "hip_midpoint_y": hip_signal.to_numpy(dtype=float),
            "hip_midpoint_y_smoothed": smoothed,
            "valid_for_analysis": quality_by_frame.to_numpy(dtype=bool),
            "repetition_index": repetition_numbers,
            "phase": phases,
        }
    )
    frame_table.to_csv(phases_path, index=False, encoding="utf-8-sig")
    pd.DataFrame(
        [item.model_dump() for item in repetitions],
        columns=list(SquatRepetition.model_fields),
    ).to_csv(repetitions_path, index=False, encoding="utf-8-sig")
    _save_segmentation_plot(
        frame_table,
        repetitions,
        output_path=plot_path,
        case_id=case_id,
    )

    artifacts = SquatSegmentationArtifacts(
        frame_phases_csv=str(phases_path),
        repetitions_csv=str(repetitions_path),
        segmentation_plot=str(plot_path),
        summary_json=str(summary_path),
    )
    summary = SquatSegmentationSummary(
        case_id=case_id,
        landmarks_csv=str(landmarks_path),
        frame_quality_csv=str(quality_path),
        fps=fps,
        total_frames=len(frame_table),
        repetitions_detected=len(repetitions),
        repetitions=repetitions,
        artifacts=artifacts,
    )
    summary_path.write_text(
        json.dumps(summary.model_dump(mode="json"), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return summary


def _peak_candidates(
    signal: np.ndarray,
    *,
    window: int,
    minimum_prominence: float,
) -> list[int]:
    candidates: list[int] = []
    for index in range(1, len(signal) - 1):
        if not (signal[index] >= signal[index - 1] and signal[index] > signal[index + 1]):
            continue
        left = signal[max(0, index - window) : index]
        right = signal[index + 1 : min(len(signal), index + window + 1)]
        prominence = signal[index] - max(float(left.min()), float(right.min()))
        if prominence >= minimum_prominence:
            candidates.append(index)
    return candidates


def _suppress_nearby_peaks(
    candidates: Sequence[int],
    *,
    signal: np.ndarray,
    minimum_distance: int,
) -> list[int]:
    selected: list[int] = []
    for candidate in sorted(candidates, key=lambda index: signal[index], reverse=True):
        if all(abs(candidate - existing) >= minimum_distance for existing in selected):
            selected.append(candidate)
    return sorted(selected)


def _repetition_around_peak(
    signal: np.ndarray,
    *,
    peaks: Sequence[int],
    peak_position: int,
    maximum_repetition_frames: int,
) -> DetectedRepetition:
    peak = peaks[peak_position]
    left_search_start = (
        peaks[peak_position - 1] + 1
        if peak_position > 0
        else max(0, peak - maximum_repetition_frames)
    )
    right_search_end = (
        peaks[peak_position + 1]
        if peak_position + 1 < len(peaks)
        else min(len(signal) - 1, peak + maximum_repetition_frames)
    )
    left_valley = left_search_start + int(np.argmin(signal[left_search_start : peak + 1]))
    right_valley = peak + int(np.argmin(signal[peak : right_search_end + 1]))

    left_level = signal[left_valley] + 0.15 * (signal[peak] - signal[left_valley])
    right_level = signal[right_valley] + 0.15 * (signal[peak] - signal[right_valley])
    left_candidates = np.flatnonzero(signal[left_valley : peak + 1] <= left_level)
    right_candidates = np.flatnonzero(signal[peak : right_valley + 1] <= right_level)
    start = left_valley + int(left_candidates[-1]) if left_candidates.size else left_valley
    end = peak + int(right_candidates[0]) if right_candidates.size else right_valley
    return DetectedRepetition(start, peak, end)


def _infer_fps(timestamps: np.ndarray) -> float:
    differences = np.diff(timestamps)
    positive = differences[differences > 0]
    if not positive.size:
        raise ValueError("Unable to infer fps from frame timestamps")
    return round(float(1.0 / np.median(positive)), 6)


def _require_columns(
    table: pd.DataFrame,
    required: set[str],
    *,
    source: Path,
) -> None:
    missing = sorted(required - set(table.columns))
    if missing:
        raise ValueError(f"{source} is missing required columns: {', '.join(missing)}")


def _as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "si", "sí"}


def _save_segmentation_plot(
    frame_table: pd.DataFrame,
    repetitions: Sequence[SquatRepetition],
    *,
    output_path: Path,
    case_id: str,
) -> None:
    figure, axis = plt.subplots(figsize=(12, 5), constrained_layout=True)
    axis.plot(
        frame_table["timestamp_seconds"],
        frame_table["hip_midpoint_y_smoothed"],
        color="#176B87",
        linewidth=1.6,
        label="Centro de caderas suavizado",
    )
    for repetition in repetitions:
        axis.axvspan(
            repetition.start_seconds,
            repetition.end_seconds,
            color="#F4A261",
            alpha=0.16,
        )
        axis.scatter(
            repetition.peak_depth_seconds,
            repetition.peak_hip_midpoint_y,
            color="#C23B22",
            s=34,
            zorder=3,
        )
        axis.annotate(
            f"R{repetition.repetition_index}",
            (repetition.peak_depth_seconds, repetition.peak_hip_midpoint_y),
            xytext=(0, 8),
            textcoords="offset points",
            ha="center",
        )
    axis.invert_yaxis()
    axis.set_xlabel("Tiempo (s)")
    axis.set_ylabel("Posición vertical normalizada")
    axis.set_title(f"Segmentación temporal de sentadilla - {case_id}")
    axis.grid(alpha=0.25)
    axis.legend(loc="upper right")
    figure.savefig(output_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(figure)


__all__ = [
    "DetectedRepetition",
    "detect_squat_repetitions",
    "segment_squat_pose_artifacts",
]
