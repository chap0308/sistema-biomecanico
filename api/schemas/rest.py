"""Schemas for the resting-posture analysis endpoint."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RestMetricResponse(BaseModel):
    """Single biomechanical metric exposed by the rest-analysis API."""

    name: str
    value: float | None
    plane: str
    unit: str
    measurement_type: str
    priority: str
    status: str


class RestPoseResponse(BaseModel):
    """Pose-extraction metadata returned by the rest-analysis API."""

    detected: bool = True
    detector: str
    image_width: int
    image_height: int
    landmark_count: int
    relevant_landmark_count: int
    min_visibility: float
    input_frame_count: int | None = None
    successful_frame_count: int | None = None
    failed_frame_count: int | None = None
    aggregation: str | None = None
    outlier_rejection: bool | None = None


class FindingResponse(BaseModel):
    """Structured biomechanical finding returned by the rest-analysis API."""

    id: str
    label: str
    summary: str
    severity: str
    confidence: str
    view: str
    related_metrics: list[str] = Field(default_factory=list)


class FindingsResponse(BaseModel):
    """Structured findings emitted from the rest-analysis metrics."""

    status: str = Field(description="Current state of the findings layer.")
    items: list[FindingResponse] = Field(default_factory=list)
    ready_for_detection: bool = True


class DeficiencyResponse(BaseModel):
    """High-level biomechanical deficiency grouped from findings."""

    id: str
    label: str
    summary: str
    severity: str
    confidence: str
    supporting_findings: list[str] = Field(default_factory=list)
    view: str


class DeficienciesResponse(BaseModel):
    """Structured deficiencies emitted from grouped findings."""

    status: str = Field(description="Current state of the deficiencies layer.")
    items: list[DeficiencyResponse] = Field(default_factory=list)
    ready_for_recommendations: bool = True


class RestAnalysisResponse(BaseModel):
    """Response payload for rest-oriented image or video analysis."""

    analysis_type: str
    status: str
    view: str
    capture_mode: str
    pipeline_version: str
    pose: RestPoseResponse
    metrics: dict[str, RestMetricResponse]
    findings: FindingsResponse
    deficiencies: DeficienciesResponse
