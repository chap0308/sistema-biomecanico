"""Local-first API routes for bilateral-squat case analysis."""

from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse
from pydantic import ValidationError

from api.auth import SquatUserDependency
from src.squat.contracts import (
    SquatCaseRecordContract,
    SquatCaseReport,
    SquatManualProtocolReview,
)
from src.squat.models import SquatCaseRecord
from src.squat.service import run_squat_case_analysis

router = APIRouter()

_VIDEO_CONTENT_TYPES = {
    "video/mp4",
    "video/quicktime",
    "video/x-msvideo",
    "video/x-matroska",
    "video/webm",
}
_DATA_ROOT = Path(
    os.getenv("SQUAT_DATA_ROOT", "data/sentadilla_bilateral")
)
_OUTPUT_ROOT = _DATA_ROOT / "outputs"
_UPLOAD_ROOT = _DATA_ROOT / "uploads"
_REGISTRY_PATH = _DATA_ROOT / "metadata" / "casos.csv"
_RULESET_PATH = Path(
    os.getenv(
        "SQUAT_RULESET_PATH",
        "config/squat/ruleset_v0_1_provisional.json",
    )
)


@router.post(
    "/squat/cases",
    response_model=SquatCaseReport,
    summary="Register and analyze one frontal bilateral-squat video",
)
async def analyze_squat_case(
    current_user: SquatUserDependency,
    video: UploadFile = File(...),
    case_id: str = Form(...),
    participant_code: str | None = Form(default=None),
    profile: str = Form(default="no_etiquetado"),
    protocol_review_status: str = Form(default="aceptado"),
    exclusion_reason: str | None = Form(default=None),
    intended_findings_json: str = Form(default="[]"),
    manual_review_json: str = Form(default="{}"),
) -> SquatCaseReport:
    """Receive a video plus Instrument 1 data and return the aggregate report."""
    if current_user.role != "investigator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the investigator can register squat cases.",
        )
    _validate_video_upload(video)
    try:
        intended_findings = json.loads(intended_findings_json)
        manual_review = SquatManualProtocolReview.model_validate_json(
            manual_review_json
        )
        case = SquatCaseRecord(
            case_id=case_id,
            video_path="pending-upload",
            participant_code=participant_code,
            profile=profile,
            intended_findings=intended_findings,
            protocol_review_status=protocol_review_status,
            exclusion_reason=exclusion_reason,
        )
    except (json.JSONDecodeError, ValidationError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    suffix = Path(video.filename or "upload.mp4").suffix.lower() or ".mp4"
    _UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    upload_path = _UPLOAD_ROOT / f"{case.case_id}{suffix}"
    if upload_path.exists() or (_OUTPUT_ROOT / case.case_id).exists():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"case_id already exists: {case.case_id}",
        )
    await _persist_upload(video, upload_path)
    case = case.model_copy(update={"video_path": str(upload_path)})

    try:
        return await run_in_threadpool(
            run_squat_case_analysis,
            case,
            manual_review=manual_review,
            registry_path=_REGISTRY_PATH,
            output_dir=_OUTPUT_ROOT,
            ruleset_path=_RULESET_PATH,
        )
    except ValueError as exc:
        if "case_id already exists" in str(exc):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(exc),
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except (FileNotFoundError, RuntimeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.get(
    "/squat/cases/{case_id}",
    response_model=SquatCaseReport,
    summary="Get the aggregate report for one analyzed case",
)
async def get_squat_case_report(
    case_id: str,
    current_user: SquatUserDependency,
) -> SquatCaseReport:
    """Load a previously generated report without recomputing the analysis."""
    if current_user.role != "investigator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System results are restricted to the investigator.",
        )
    safe_case_id = _validated_case_id(case_id)
    report_path = _OUTPUT_ROOT / safe_case_id / "case_report.json"
    if not report_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Squat case report was not found.",
        )
    try:
        return SquatCaseReport.model_validate_json(
            report_path.read_text(encoding="utf-8")
        )
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stored squat case report is invalid.",
        ) from exc


@router.get(
    "/squat/cases/{case_id}/record",
    response_model=SquatCaseRecordContract,
    summary="Get the Instrument 1 record for one case",
)
async def get_squat_case_record(
    case_id: str,
    current_user: SquatUserDependency,
) -> SquatCaseRecordContract:
    """Load manual and technical registration fields through a typed endpoint."""
    if current_user.role != "investigator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Technical case records are restricted to the investigator.",
        )
    safe_case_id = _validated_case_id(case_id)
    record_path = _OUTPUT_ROOT / safe_case_id / "case_record.json"
    if not record_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Squat case record was not found.",
        )
    try:
        return SquatCaseRecordContract.model_validate_json(
            record_path.read_text(encoding="utf-8")
        )
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stored squat case record is invalid.",
        ) from exc


@router.get(
    "/squat/cases/{case_id}/assets/{filename}",
    response_class=FileResponse,
    summary="Get one report artifact using its manifest filename",
)
async def get_squat_case_asset(
    case_id: str,
    filename: str,
    current_user: SquatUserDependency,
) -> FileResponse:
    """Serve direct case artifacts without exposing arbitrary filesystem paths."""
    if current_user.role != "investigator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System artifacts are restricted to the investigator.",
        )
    safe_case_id = _validated_case_id(case_id)
    if Path(filename).name != filename:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Squat case asset was not found.",
        )
    case_dir = (_OUTPUT_ROOT / safe_case_id).resolve()
    artifact = (case_dir / filename).resolve()
    report_path = case_dir / "case_report.json"
    if not report_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Squat case report was not found.",
        )
    report = SquatCaseReport.model_validate_json(
        report_path.read_text(encoding="utf-8")
    )
    if (
        artifact.parent != case_dir
        or filename not in _allowed_asset_names(report)
        or not artifact.is_file()
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Squat case asset was not found.",
        )
    return FileResponse(artifact)


def _validate_video_upload(video: UploadFile) -> None:
    if not video.content_type or video.content_type not in _VIDEO_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only supported video uploads can be analyzed.",
        )


async def _persist_upload(video: UploadFile, destination: Path) -> None:
    temporary = destination.with_suffix(destination.suffix + ".part")
    try:
        with temporary.open("wb") as handle:
            while chunk := await video.read(1024 * 1024):
                handle.write(chunk)
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)


def _validated_case_id(case_id: str) -> str:
    try:
        return SquatCaseRecord(
            case_id=case_id,
            video_path="validation-only",
        ).case_id
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid squat case identifier.",
        ) from exc


def _allowed_asset_names(report: SquatCaseReport) -> set[str]:
    payload = report.artifacts.model_dump(mode="json")
    captures = payload.pop("event_captures", [])
    names = {value for value in payload.values() if isinstance(value, str)}
    names.update(
        capture["relative_path"]
        for capture in captures
        if isinstance(capture.get("relative_path"), str)
    )
    return names


__all__ = ["router"]
