"""Domain models for biomechanical calculations."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class BiomechanicsMetric:
    """Single metric produced by the biomechanics engine."""

    name: str
    value: float
    plane: str
    unit: str
    measurement_type: str
    priority: str = "P0"
    status: str | None = None
    confidence: float | None = None
    confidence_base: str | None = None
    quality_notes: list[str] = field(default_factory=list)
    classification: str | None = None
    flags: list[str] = field(default_factory=list)
    source_of_truth: str | None = None
    calculation_status: str | None = None
    proxy_type: str | None = None
    anatomical_directness: str | None = None


@dataclass(slots=True, frozen=True)
class Point2D:
    """Normalized 2D point in image coordinates (x, y)."""

    x: float
    y: float


@dataclass(slots=True, frozen=True)
class RestingLandmarks:
    """Landmark set required for resting posture biomechanical metrics."""

    nose: Point2D
    left_ear: Point2D
    right_ear: Point2D
    left_shoulder: Point2D
    right_shoulder: Point2D
    left_elbow: Point2D
    right_elbow: Point2D
    left_hip: Point2D
    right_hip: Point2D
    left_knee: Point2D
    right_knee: Point2D
    left_ankle: Point2D
    right_ankle: Point2D

    @classmethod
    def from_mapping(cls, values: dict[str, tuple[float, float]]) -> "RestingLandmarks":
        """Build a typed landmark set from a `(x, y)` mapping."""
        required = (
            "nose",
            "left_ear",
            "right_ear",
            "left_shoulder",
            "right_shoulder",
            "left_elbow",
            "right_elbow",
            "left_hip",
            "right_hip",
            "left_knee",
            "right_knee",
            "left_ankle",
            "right_ankle",
        )
        missing = [name for name in required if name not in values]
        if missing:
            raise ValueError(f"Missing landmarks: {', '.join(missing)}")

        return cls(**{name: Point2D(*values[name]) for name in required})
