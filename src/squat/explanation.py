"""Bounded, typed explanation data derived from canonical squat artifacts."""

from __future__ import annotations

import csv
from io import StringIO
import math
from typing import Literal, Mapping

from pydantic import BaseModel, ConfigDict, Field

from src.squat.contracts import SquatCaseReport
from src.squat.models import (
    SquatRepetition,
    SquatRepetitionMetrics,
    SquatRuleDecision,
)


class SquatExplanationQuality(BaseModel):
    """Pose-quality values needed by the explanatory interface."""

    model_config = ConfigDict(extra="forbid")

    visibility_threshold: float = Field(ge=0.0, le=1.0)
    processed_percentage: float = Field(ge=0.0, le=100.0)
    valid_percentage: float = Field(ge=0.0, le=100.0)
    selected_keypoints: int = Field(ge=0)
    mean_detected_keypoints: float = Field(ge=0.0)
    minimum_observed_visibility: float | None = Field(default=None, ge=0.0, le=1.0)


class SquatExplanationFrame(BaseModel):
    """One sampled frame shared by all synchronized web charts."""

    model_config = ConfigDict(extra="forbid")

    frame_index: int = Field(ge=0)
    timestamp_seconds: float = Field(ge=0.0)
    valid_for_analysis: bool
    detected_keypoints: int | None = Field(default=None, ge=0)
    minimum_critical_visibility: float | None = Field(default=None, ge=0.0, le=1.0)
    hip_midpoint_y: float | None = None
    hip_midpoint_y_smoothed: float | None = None
    repetition_index: int = Field(default=0, ge=0)
    phase: str = "reposo"
    trunk_inclination_deg: float | None = None
    pelvis_lateral_shift_pct: float | None = None
    left_knee_medial_deviation_pct: float | None = None
    right_knee_medial_deviation_pct: float | None = None
    bilateral_alignment_difference_pct: float | None = None


class SquatExplanationLandmark(BaseModel):
    """Normalized pose point used to draw key-frame geometry."""

    model_config = ConfigDict(extra="forbid")

    x: float
    y: float
    visibility: float = Field(ge=0.0, le=1.0)


class SquatExplanationGeometry(BaseModel):
    """Derived points already used by the biomechanical formulas."""

    model_config = ConfigDict(extra="forbid")

    shoulder_midpoint: SquatExplanationLandmark | None = None
    pelvis_midpoint: SquatExplanationLandmark | None = None
    ankle_midpoint: SquatExplanationLandmark | None = None
    left_knee_projection: SquatExplanationLandmark | None = None
    right_knee_projection: SquatExplanationLandmark | None = None


class SquatExplanationKeyFrame(BaseModel):
    """Landmarks retained at one relevant repetition event."""

    model_config = ConfigDict(extra="forbid")

    repetition_index: int = Field(ge=1)
    event: Literal["inicio_descenso", "maxima_profundidad", "final_ascenso"]
    frame_index: int = Field(ge=0)
    timestamp_seconds: float = Field(ge=0.0)
    landmarks: dict[str, SquatExplanationLandmark]
    geometry: SquatExplanationGeometry


class SquatExplanationRepetition(BaseModel):
    """Segmentation, metrics and decisions for one execution."""

    model_config = ConfigDict(extra="forbid")

    segmentation: SquatRepetition
    metrics: SquatRepetitionMetrics | None = None
    decisions: list[SquatRuleDecision] = Field(default_factory=list)


class SquatExplanationArtifact(BaseModel):
    """One canonical artifact that remains available for download."""

    model_config = ConfigDict(extra="forbid")

    kind: str
    filename: str


class SquatCaseExplanation(BaseModel):
    """Investigator-only data contract for explaining one analyzed case."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"] = "1.0"
    contract: Literal["squat_case_explanation"] = "squat_case_explanation"
    case_id: str
    pipeline_version: str
    ruleset_version: str | None = None
    quality: SquatExplanationQuality | None = None
    normalization_reference: Literal["initial_shoulder_width"] | None = None
    normalization_value: float | None = None
    total_source_frames: int = Field(ge=0)
    frames_sampled: bool
    frames: list[SquatExplanationFrame] = Field(default_factory=list)
    repetitions: list[SquatExplanationRepetition] = Field(default_factory=list)
    key_frames: list[SquatExplanationKeyFrame] = Field(default_factory=list)
    artifact_downloads: list[SquatExplanationArtifact] = Field(default_factory=list)


def build_case_explanation(
    report: SquatCaseReport,
    artifacts: Mapping[str, bytes],
    *,
    max_frames: int = 900,
) -> SquatCaseExplanation:
    """Build presentation data without changing or recalculating analysis results."""
    if max_frames < 3:
        raise ValueError("max_frames must be at least 3")

    quality_rows = _read_csv(artifacts, report.artifacts.frame_quality_csv)
    phase_rows = _read_csv(artifacts, report.artifacts.frame_phases_csv)
    metric_rows = _read_csv(
        artifacts,
        report.artifacts.biomechanical_frame_metrics_csv,
    )
    frame_indexes = sorted(
        {
            frame_index
            for rows in (quality_rows, phase_rows, metric_rows)
            for row in rows
            if (frame_index := _integer(row.get("frame_index"))) is not None
        }
    )
    rows_by_source = [
        {_integer(row.get("frame_index")): row for row in rows}
        for rows in (quality_rows, phase_rows, metric_rows)
    ]
    retained_indexes = _retained_frame_indexes(
        frame_indexes,
        report=report,
        max_frames=max_frames,
    )
    frames = [
        _explanation_frame(
            frame_index,
            quality=rows_by_source[0].get(frame_index, {}),
            phase=rows_by_source[1].get(frame_index, {}),
            metrics=rows_by_source[2].get(frame_index, {}),
        )
        for frame_index in retained_indexes
    ]
    repetitions = _explanation_repetitions(report)
    return SquatCaseExplanation(
        case_id=report.case_id,
        pipeline_version=report.pipeline_version,
        ruleset_version=(
            report.findings.ruleset_version if report.findings else None
        ),
        quality=_quality_summary(report, quality_rows),
        normalization_reference=(
            report.biomechanics.normalization_reference
            if report.biomechanics
            else None
        ),
        normalization_value=(
            report.biomechanics.initial_shoulder_width
            if report.biomechanics
            else None
        ),
        total_source_frames=len(frame_indexes),
        frames_sampled=len(retained_indexes) < len(frame_indexes),
        frames=frames,
        repetitions=repetitions,
        key_frames=_key_frame_geometry(report, artifacts),
        artifact_downloads=_artifact_downloads(report),
    )


def _read_csv(
    artifacts: Mapping[str, bytes],
    filename: str | None,
) -> list[dict[str, str]]:
    if not filename or filename not in artifacts:
        return []
    text = artifacts[filename].decode("utf-8-sig")
    return list(csv.DictReader(StringIO(text)))


def _retained_frame_indexes(
    frame_indexes: list[int],
    *,
    report: SquatCaseReport,
    max_frames: int,
) -> list[int]:
    if len(frame_indexes) <= max_frames:
        return frame_indexes
    mandatory = {frame_indexes[0], frame_indexes[-1]}
    if report.segmentation:
        for repetition in report.segmentation.repetitions:
            mandatory.update(
                {
                    repetition.start_frame,
                    repetition.peak_depth_frame,
                    repetition.end_frame,
                }
            )
    stride = max(1, math.ceil(len(frame_indexes) / max_frames))
    selected = mandatory | set(frame_indexes[::stride])
    if len(selected) > max_frames:
        optional = sorted(selected - mandatory)
        available = max(0, max_frames - len(mandatory))
        optional_stride = max(1, math.ceil(len(optional) / max(1, available)))
        selected = mandatory | set(optional[::optional_stride][:available])
    return sorted(selected)


def _explanation_frame(
    frame_index: int,
    *,
    quality: Mapping[str, str],
    phase: Mapping[str, str],
    metrics: Mapping[str, str],
) -> SquatExplanationFrame:
    timestamp = (
        _number(phase.get("timestamp_seconds"))
        or _number(quality.get("timestamp_seconds"))
        or _number(metrics.get("timestamp_seconds"))
        or 0.0
    )
    return SquatExplanationFrame(
        frame_index=frame_index,
        timestamp_seconds=timestamp,
        valid_for_analysis=_boolean(
            phase.get("valid_for_analysis")
            or quality.get("valid_for_analysis")
            or metrics.get("valid_for_analysis")
        ),
        detected_keypoints=_integer(quality.get("detected_keypoints")),
        minimum_critical_visibility=_number(
            quality.get("minimum_critical_visibility")
        ),
        hip_midpoint_y=_number(phase.get("hip_midpoint_y")),
        hip_midpoint_y_smoothed=_number(
            phase.get("hip_midpoint_y_smoothed")
        ),
        repetition_index=_integer(phase.get("repetition_index")) or 0,
        phase=phase.get("phase") or "reposo",
        trunk_inclination_deg=_number(
            metrics.get("trunk_inclination_deg")
        ),
        pelvis_lateral_shift_pct=_number(
            metrics.get("pelvis_lateral_shift_pct")
        ),
        left_knee_medial_deviation_pct=_number(
            metrics.get("left_knee_medial_deviation_pct")
        ),
        right_knee_medial_deviation_pct=_number(
            metrics.get("right_knee_medial_deviation_pct")
        ),
        bilateral_alignment_difference_pct=_number(
            metrics.get("bilateral_alignment_difference_pct")
        ),
    )


def _quality_summary(
    report: SquatCaseReport,
    rows: list[dict[str, str]],
) -> SquatExplanationQuality | None:
    if not report.pose:
        return None
    observed = [
        value
        for row in rows
        if (
            value := _number(row.get("minimum_critical_visibility"))
        )
        is not None
    ]
    detected_counts = [
        count
        for row in rows
        if (count := _integer(row.get("detected_keypoints"))) is not None
    ]
    return SquatExplanationQuality(
        visibility_threshold=report.pose.min_visibility_threshold,
        processed_percentage=report.pose.processed_frames_percentage,
        valid_percentage=report.pose.valid_frames_percentage,
        selected_keypoints=max(detected_counts, default=0),
        mean_detected_keypoints=report.pose.mean_detected_keypoints,
        minimum_observed_visibility=min(observed) if observed else None,
    )


def _explanation_repetitions(
    report: SquatCaseReport,
) -> list[SquatExplanationRepetition]:
    if not report.segmentation:
        return []
    metrics = {
        item.repetition_index: item
        for item in (
            report.biomechanics.repetitions if report.biomechanics else []
        )
    }
    decisions: dict[int, list[SquatRuleDecision]] = {}
    for decision in report.findings.decisions if report.findings else []:
        decisions.setdefault(decision.repetition_index, []).append(decision)
    return [
        SquatExplanationRepetition(
            segmentation=repetition,
            metrics=metrics.get(repetition.repetition_index),
            decisions=decisions.get(repetition.repetition_index, []),
        )
        for repetition in report.segmentation.repetitions
    ]


def _key_frame_geometry(
    report: SquatCaseReport,
    artifacts: Mapping[str, bytes],
) -> list[SquatExplanationKeyFrame]:
    rows = _read_csv(artifacts, report.artifacts.landmarks_csv)
    if not report.segmentation or not rows:
        return []
    events: dict[int, tuple[int, str, float]] = {}
    for repetition in report.segmentation.repetitions:
        events[repetition.start_frame] = (
            repetition.repetition_index,
            "inicio_descenso",
            repetition.start_seconds,
        )
        events[repetition.peak_depth_frame] = (
            repetition.repetition_index,
            "maxima_profundidad",
            repetition.peak_depth_seconds,
        )
        events[repetition.end_frame] = (
            repetition.repetition_index,
            "final_ascenso",
            repetition.end_seconds,
        )
    points: dict[int, dict[str, SquatExplanationLandmark]] = {}
    for row in rows:
        frame_index = _integer(row.get("frame_index"))
        name = row.get("landmark")
        if frame_index not in events or not name:
            continue
        x = _number(row.get("x"))
        y = _number(row.get("y"))
        visibility = _number(row.get("visibility"))
        if x is None or y is None or visibility is None:
            continue
        points.setdefault(frame_index, {})[name] = SquatExplanationLandmark(
            x=x,
            y=y,
            visibility=visibility,
        )
    return [
        SquatExplanationKeyFrame(
            repetition_index=events[frame_index][0],
            event=events[frame_index][1],  # type: ignore[arg-type]
            frame_index=frame_index,
            timestamp_seconds=events[frame_index][2],
            landmarks=landmarks,
            geometry=_derived_geometry(landmarks),
        )
        for frame_index, landmarks in sorted(points.items())
    ]


def _derived_geometry(
    landmarks: Mapping[str, SquatExplanationLandmark],
) -> SquatExplanationGeometry:
    return SquatExplanationGeometry(
        shoulder_midpoint=_midpoint(
            landmarks.get("left_shoulder"),
            landmarks.get("right_shoulder"),
        ),
        pelvis_midpoint=_midpoint(
            landmarks.get("left_hip"),
            landmarks.get("right_hip"),
        ),
        ankle_midpoint=_midpoint(
            landmarks.get("left_ankle"),
            landmarks.get("right_ankle"),
        ),
        left_knee_projection=_knee_projection(landmarks, side="left"),
        right_knee_projection=_knee_projection(landmarks, side="right"),
    )


def _midpoint(
    first: SquatExplanationLandmark | None,
    second: SquatExplanationLandmark | None,
) -> SquatExplanationLandmark | None:
    if first is None or second is None:
        return None
    return SquatExplanationLandmark(
        x=(first.x + second.x) / 2.0,
        y=(first.y + second.y) / 2.0,
        visibility=min(first.visibility, second.visibility),
    )


def _knee_projection(
    landmarks: Mapping[str, SquatExplanationLandmark],
    *,
    side: str,
) -> SquatExplanationLandmark | None:
    hip = landmarks.get(f"{side}_hip")
    knee = landmarks.get(f"{side}_knee")
    ankle = landmarks.get(f"{side}_ankle")
    if hip is None or knee is None or ankle is None:
        return None
    vertical_span = ankle.y - hip.y
    if abs(vertical_span) <= 1e-9:
        return None
    interpolation = (knee.y - hip.y) / vertical_span
    return SquatExplanationLandmark(
        x=hip.x + interpolation * (ankle.x - hip.x),
        y=knee.y,
        visibility=min(hip.visibility, knee.visibility, ankle.visibility),
    )


def _artifact_downloads(
    report: SquatCaseReport,
) -> list[SquatExplanationArtifact]:
    payload = report.artifacts.model_dump(mode="json")
    payload.pop("event_captures", None)
    return [
        SquatExplanationArtifact(kind=kind, filename=filename)
        for kind, filename in payload.items()
        if isinstance(filename, str)
    ]


def _number(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def _integer(value: str | None) -> int | None:
    number = _number(value)
    return int(number) if number is not None else None


def _boolean(value: str | None) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "si", "sí"}


__all__ = [
    "SquatCaseExplanation",
    "SquatExplanationFrame",
    "build_case_explanation",
]
