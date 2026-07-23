"""Technical pipeline for bilateral squat video analysis."""

from src.squat.models import (
    SquatCaseRecord,
    SquatPoseSummary,
    SquatRegistrationResult,
    SquatSegmentationSummary,
)
from src.squat.pipeline import register_squat_case
from src.squat.pose_video import extract_squat_pose_video
from src.squat.segmentation import segment_squat_pose_artifacts

__all__ = [
    "SquatCaseRecord",
    "SquatPoseSummary",
    "SquatRegistrationResult",
    "SquatSegmentationSummary",
    "extract_squat_pose_video",
    "register_squat_case",
    "segment_squat_pose_artifacts",
]
