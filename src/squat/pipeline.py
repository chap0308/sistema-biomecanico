"""Initial orchestration for bilateral squat case registration."""

from __future__ import annotations

import json
from pathlib import Path

from src.squat.contracts import (
    SquatManualProtocolReview,
    write_case_record_contract,
)
from src.squat.models import SquatCaseRecord, SquatRegistrationResult
from src.squat.registry import append_case_record
from src.squat.video import probe_video


def register_squat_case(
    case: SquatCaseRecord,
    *,
    registry_path: str | Path,
    output_dir: str | Path,
    manual_review: SquatManualProtocolReview | None = None,
) -> tuple[SquatRegistrationResult, Path]:
    """Inspect, register and persist the baseline result for one squat video."""
    video = probe_video(case.video_path)
    normalized_case = case.model_copy(update={"video_path": video.path})
    result = SquatRegistrationResult.from_case(normalized_case, video)

    append_case_record(registry_path, normalized_case)
    case_output_dir = Path(output_dir) / normalized_case.case_id
    case_output_dir.mkdir(parents=True, exist_ok=True)
    result_path = case_output_dir / "registration.json"
    result_path.write_text(
        json.dumps(result.model_dump(mode="json"), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_case_record_contract(
        result,
        case_output_dir / "case_record.json",
        manual_review=manual_review,
    )
    return result, result_path


__all__ = ["register_squat_case"]
