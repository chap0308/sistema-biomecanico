"""Temporal sampling and aggregation helpers for resting-posture analysis."""

from __future__ import annotations

from dataclasses import replace
from math import isnan
from pathlib import Path
from statistics import mean, median
from typing import Literal

import cv2
import numpy as np

from biomechanics.models import BiomechanicsMetric

AggregationStrategy = Literal["mean", "median"]


def sample_video_frames(
    video_path: Path,
    *,
    max_frames: int = 9,
    frame_step: int = 5,
) -> list[np.ndarray]:
    """Sample a bounded set of frames from a short static video."""
    return [frame for _, frame in sample_indexed_video_frames(video_path, max_frames=max_frames, frame_step=frame_step)]



def sample_indexed_video_frames(
    video_path: Path,
    *,
    max_frames: int = 9,
    frame_step: int = 5,
) -> list[tuple[int, np.ndarray]]:
    """Sample frames while preserving the original video frame indices."""
    if max_frames <= 0:
        raise ValueError("max_frames must be greater than 0.")
    if frame_step <= 0:
        raise ValueError("frame_step must be greater than 0.")
    if not video_path.is_file():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise ValueError(f"Unable to open video file: {video_path}")

    try:
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        sampled_indices = _build_sample_indices(
            frame_count=frame_count,
            max_frames=max_frames,
            frame_step=frame_step,
        )
        frames: list[tuple[int, np.ndarray]] = []

        if sampled_indices:
            for frame_index in sampled_indices:
                capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
                ok, frame = capture.read()
                if ok and frame is not None:
                    frames.append((frame_index, frame))
            if frames:
                return frames

        capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
        frame_index = 0
        while len(frames) < max_frames:
            ok, frame = capture.read()
            if not ok or frame is None:
                break
            if frame_index % frame_step == 0:
                frames.append((frame_index, frame))
            frame_index += 1
        return frames
    finally:
        capture.release()



def aggregate_metric_series(
    metric_series: list[dict[str, BiomechanicsMetric]],
    *,
    strategy: AggregationStrategy = "median",
    reject_outliers: bool = True,
) -> dict[str, BiomechanicsMetric]:
    """Aggregate per-frame metrics into a single stable metric set."""
    if not metric_series:
        raise ValueError("metric_series must include at least one frame.")
    if strategy not in {"mean", "median"}:
        raise ValueError(f"Unsupported aggregation strategy '{strategy}'. Expected 'mean' or 'median'.")

    aggregated: dict[str, BiomechanicsMetric] = {}
    metric_names = metric_series[0].keys()
    for name in metric_names:
        template = metric_series[0][name]
        values = [frame_metrics[name].value for frame_metrics in metric_series if name in frame_metrics]
        valid_values = [value for value in values if not isnan(value)]
        if valid_values:
            filtered_values = _reject_outliers(valid_values) if reject_outliers else valid_values
            if not filtered_values:
                filtered_values = valid_values
            aggregated[name] = replace(
                template,
                value=_aggregate_values(filtered_values, strategy=strategy),
            )
            continue

        aggregated[name] = template
    return aggregated



def _build_sample_indices(
    *,
    frame_count: int,
    max_frames: int,
    frame_step: int,
) -> list[int]:
    """Pick evenly distributed indices when the video length is known."""
    if frame_count <= 0:
        return []
    if frame_count <= max_frames:
        return list(range(frame_count))

    stepped_indices = list(range(0, frame_count, frame_step))
    if len(stepped_indices) <= max_frames:
        return stepped_indices

    linspace = np.linspace(0, len(stepped_indices) - 1, num=max_frames, dtype=int)
    return [stepped_indices[index] for index in linspace.tolist()]



def _aggregate_values(values: list[float], *, strategy: AggregationStrategy) -> float:
    if strategy == "mean":
        return float(mean(values))
    return float(median(values))



def _reject_outliers(values: list[float]) -> list[float]:
    """Filter simple outliers using an IQR band when enough samples exist."""
    if len(values) < 4:
        return values

    sorted_values = sorted(values)
    q1 = float(np.percentile(sorted_values, 25))
    q3 = float(np.percentile(sorted_values, 75))
    iqr = q3 - q1
    if iqr == 0:
        return values

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return [value for value in values if lower <= value <= upper]


__all__ = ["aggregate_metric_series", "sample_indexed_video_frames", "sample_video_frames"]
