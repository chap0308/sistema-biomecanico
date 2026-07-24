"""Technical pipeline for bilateral squat video analysis."""

from src.squat.biomechanics import calculate_squat_biomechanics
from src.squat.contracts import (
    SquatCaseRecordContract,
    SquatCaseReport,
    SquatManualProtocolReview,
    build_case_report,
    export_contract_schemas,
)
from src.squat.evidence import generate_repetition_event_captures
from src.squat.models import (
    SquatBiomechanicsSummary,
    SquatCaseRecord,
    SquatFindingsSummary,
    SquatPoseSummary,
    SquatQualityGateSummary,
    SquatRegistrationResult,
    SquatSegmentationSummary,
)
from src.squat.pipeline import register_squat_case
from src.squat.pose_video import extract_squat_pose_video
from src.squat.quality_gate import evaluate_squat_analysis_quality
from src.squat.rules import classify_squat_findings
from src.squat.segmentation import segment_squat_pose_artifacts
from src.squat.service import assemble_existing_squat_case, run_squat_case_analysis

__all__ = [
    "SquatBiomechanicsSummary",
    "SquatCaseRecord",
    "SquatCaseRecordContract",
    "SquatCaseReport",
    "SquatFindingsSummary",
    "SquatPoseSummary",
    "SquatQualityGateSummary",
    "SquatRegistrationResult",
    "SquatSegmentationSummary",
    "SquatManualProtocolReview",
    "build_case_report",
    "assemble_existing_squat_case",
    "calculate_squat_biomechanics",
    "classify_squat_findings",
    "extract_squat_pose_video",
    "export_contract_schemas",
    "generate_repetition_event_captures",
    "evaluate_squat_analysis_quality",
    "register_squat_case",
    "run_squat_case_analysis",
    "segment_squat_pose_artifacts",
]
