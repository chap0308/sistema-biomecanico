"""Shared data models for high-level deficiency grouping."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Deficiency:
    """High-level biomechanical deficiency grouped from multiple findings."""

    id: str
    label: str
    summary: str
    severity: str
    confidence: str
    supporting_findings: list[str] = field(default_factory=list)
    related_findings: list[str] = field(default_factory=list)
    weight: float | None = None
    view: str = "front"


@dataclass(slots=True)
class DeficienciesResult:
    """Container for grouped biomechanical deficiencies."""

    status: str
    items: list[Deficiency] = field(default_factory=list)
    ready_for_recommendations: bool = True
