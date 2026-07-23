"""Technical pipeline for bilateral squat video analysis."""

from src.squat.models import (
    SquatCaseRecord,
    SquatPoseSummary,
    SquatRegistrationResult,
)
from src.squat.pipeline import register_squat_case
from src.squat.pose_video import extract_squat_pose_video

__all__ = [
    "SquatCaseRecord",
    "SquatPoseSummary",
    "SquatRegistrationResult",
    "extract_squat_pose_video",
    "register_squat_case",
]
