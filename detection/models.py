"""Shared data models for the detection layer."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Finding:
    """Structured biomechanical finding derived from one or more metrics."""

    id: str
    label: str
    summary: str
    severity: str
    confidence: str
    view: str
    side: str | None = None
    weight: float | None = None
    related_metrics: list[str] = field(default_factory=list)


@dataclass(slots=True)
class FindingsResult:
    """Container for the findings emitted by a detection pass."""

    status: str
    items: list[Finding] = field(default_factory=list)
    ready_for_detection: bool = True
