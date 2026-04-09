"""View-specific applicability rules for resting-posture metrics."""

from __future__ import annotations

from collections.abc import Mapping

from biomechanics.models import BiomechanicsMetric

REST_VIEW_APPLICABLE_PLANES: dict[str, frozenset[str]] = {
    "front": frozenset({"frontal", "transverse"}),
    "side": frozenset({"sagittal"}),
    "back": frozenset({"frontal", "transverse"}),
}

NOT_APPLICABLE_STATUS = "not_applicable_for_view"


def normalize_rest_view(view: str) -> str:
    """Normalize a rest-analysis view string."""
    normalized = view.strip().lower()
    if normalized not in REST_VIEW_APPLICABLE_PLANES:
        valid_views = ", ".join(sorted(REST_VIEW_APPLICABLE_PLANES))
        raise ValueError(f"Unsupported rest-analysis view '{view}'. Expected one of: {valid_views}.")
    return normalized


def is_metric_applicable_for_view(metric: BiomechanicsMetric, *, view: str) -> bool:
    """Return whether a metric should be exposed as applicable for a given view."""
    normalized_view = normalize_rest_view(view)
    return metric.plane in REST_VIEW_APPLICABLE_PLANES[normalized_view]


def filter_metrics_for_view(
    metrics: Mapping[str, BiomechanicsMetric],
    *,
    view: str,
) -> dict[str, tuple[BiomechanicsMetric, bool]]:
    """Return metrics paired with their applicability for the requested view."""
    normalize_rest_view(view)
    return {
        name: (metric, is_metric_applicable_for_view(metric, view=view))
        for name, metric in metrics.items()
    }


__all__ = [
    "NOT_APPLICABLE_STATUS",
    "REST_VIEW_APPLICABLE_PLANES",
    "filter_metrics_for_view",
    "is_metric_applicable_for_view",
    "normalize_rest_view",
]
