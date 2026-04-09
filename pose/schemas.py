"""Schemas for pose extraction and internal landmark exchange."""

from __future__ import annotations

from dataclasses import dataclass

from biomechanics.models import RestingLandmarks


@dataclass(slots=True, frozen=True)
class PoseLandmark:
    """Single normalized body landmark extracted from a pose model."""

    x: float
    y: float
    z: float
    visibility: float
    presence: float | None = None


@dataclass(slots=True, frozen=True)
class PoseExtractionMetadata:
    """Metadata describing a pose-extraction pass over one image."""

    detector: str
    image_width: int
    image_height: int
    landmark_count: int
    relevant_landmark_count: int
    min_visibility: float


@dataclass(slots=True, frozen=True)
class PoseExtractionResult:
    """Pose extraction result mapped to the internal resting-landmarks model."""

    named_landmarks: dict[str, PoseLandmark]
    resting_landmarks: RestingLandmarks
    metadata: PoseExtractionMetadata
