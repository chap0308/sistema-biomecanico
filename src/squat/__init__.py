"""Technical pipeline for bilateral squat video analysis."""

from src.squat.biomechanics import calculate_squat_biomechanics
from src.squat.models import (
    SquatBiomechanicsSummary,
    SquatCaseRecord,
    SquatPoseSummary,
    SquatQualityGateSummary,
    SquatRegistrationResult,
    SquatSegmentationSummary,
)
from src.squat.pipeline import register_squat_case
from src.squat.pose_video import extract_squat_pose_video
from src.squat.quality_gate import evaluate_squat_analysis_quality
from src.squat.segmentation import segment_squat_pose_artifacts

__all__ = [
    "SquatBiomechanicsSummary",
    "SquatCaseRecord",
    "SquatPoseSummary",
    "SquatQualityGateSummary",
    "SquatRegistrationResult",
    "SquatSegmentationSummary",
    "calculate_squat_biomechanics",
    "extract_squat_pose_video",
    "evaluate_squat_analysis_quality",
    "register_squat_case",
    "segment_squat_pose_artifacts",
]
