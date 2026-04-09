"""Tests for temporal aggregation utilities used by the rest pipeline."""

from __future__ import annotations

from math import isnan

import pytest

from biomechanics.models import BiomechanicsMetric
from orchestration.rest_temporal import aggregate_metric_series


def _metric(value: float) -> BiomechanicsMetric:
    return BiomechanicsMetric(
        name="shoulder_height_difference",
        value=value,
        plane="frontal",
        unit="normalized",
        measurement_type="direct",
    )


def test_aggregate_metric_series_uses_median_and_rejects_simple_outliers() -> None:
    series = [
        {"shoulder_height_difference": _metric(0.10)},
        {"shoulder_height_difference": _metric(0.11)},
        {"shoulder_height_difference": _metric(0.12)},
        {"shoulder_height_difference": _metric(0.90)},
    ]

    aggregated = aggregate_metric_series(series, strategy="median", reject_outliers=True)

    assert aggregated["shoulder_height_difference"].value == 0.11


def test_aggregate_metric_series_can_use_mean_without_outlier_rejection() -> None:
    series = [
        {"shoulder_height_difference": _metric(0.10)},
        {"shoulder_height_difference": _metric(0.14)},
    ]

    aggregated = aggregate_metric_series(series, strategy="mean", reject_outliers=False)

    assert aggregated["shoulder_height_difference"].value == pytest.approx(0.12)


def test_aggregate_metric_series_preserves_placeholder_nan_metrics() -> None:
    nan_metric = BiomechanicsMetric(
        name="thorax_pelvis_rotation",
        value=float("nan"),
        plane="transverse",
        unit="placeholder",
        measurement_type="placeholder",
        priority="P1",
    )
    aggregated = aggregate_metric_series(
        [{"thorax_pelvis_rotation": nan_metric}, {"thorax_pelvis_rotation": nan_metric}],
        strategy="median",
        reject_outliers=True,
    )

    assert isnan(aggregated["thorax_pelvis_rotation"].value)
