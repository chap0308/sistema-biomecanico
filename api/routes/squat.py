"""Local-first API routes for bilateral-squat case analysis."""

from __future__ import annotations

import json
import os
from datetime import datetime
from math import ceil
from pathlib import Path
from typing import Any, Literal

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    Response,
    UploadFile,
    status,
)
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse
from pydantic import ValidationError
from pydantic import BaseModel, Field

from api.auth import SquatUserDependency
from api.schemas.squat_expert import (
    SquatAssignmentCreateRequest,
    SquatAssignmentCreatedResponse,
    SquatCaseAssignmentsResponse,
    SquatEvaluationSavedResponse,
    SquatExpertAssignmentResponse,
    SquatExpertEvaluationRequest,
    SquatExpertProfileResponse,
)
from api.schemas.squat_comparison import SquatManualReferenceRequest
from app.config import get_settings
from src.squat.comparison import (
    CaseComparison,
    DatasetPerformance,
    PatternKey,
    build_stored_case_comparison,
    calculate_dataset_performance,
)
from src.squat.contracts import (
    SquatCaseRecordContract,
    SquatCaseReport,
    SquatManualProtocolReview,
)
from src.squat.models import SquatCaseRecord
from src.squat.exports import (
    build_case_excel,
    build_case_pdf,
    build_technical_data_excel,
)
from src.squat.explanation import (
    SquatCaseExplanation,
    build_case_explanation,
)
from src.squat.service import run_squat_case_analysis
from src.squat.persistence import (
    SquatPersistenceError,
    SquatStoredArtifact,
    SupabaseSquatStore,
)

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


class SquatCaseListItem(BaseModel):
    """Compact case data shown in the paginated web history."""

    case_id: str
    participant_code: str | None = None
    status: str
    protocol_review_status: str | None = None
    created_at: datetime
    updated_at: datetime


class SquatCasePage(BaseModel):
    """Paginated response consumed by the Next.js server component."""

    items: list[SquatCaseListItem]
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total: int = Field(ge=0)
    total_pages: int = Field(ge=0)


@router.get(
    "/squat/cases/{case_id}/comparison",
    response_model=CaseComparison,
    summary="Compare submitted expert judgments with the system",
)
async def get_squat_case_comparison(
    case_id: str,
    current_user: SquatUserDependency,
) -> CaseComparison:
    """Return the four pattern comparisons for the investigator."""
    _require_squat_role(current_user.role, "investigator")
    safe_case_id = _validated_case_id(case_id)
    store = SupabaseSquatStore()
    try:
        payload = await run_in_threadpool(
            store.get_case_comparison_data,
            safe_case_id,
        )
    except SquatPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Squat case was not found.",
        )
    if not _report_has_eligible_repetitions(payload.get("report")):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The case has no valid repetitions available for comparison.",
        )
    return build_stored_case_comparison(payload)


@router.put(
    "/squat/cases/{case_id}/comparison/references/{repetition_index}/{pattern_key}",
    response_model=CaseComparison,
    summary="Record guided expert consensus for one unresolved pattern",
)
async def save_squat_manual_reference(
    case_id: str,
    repetition_index: int,
    pattern_key: PatternKey,
    payload: SquatManualReferenceRequest,
    current_user: SquatUserDependency,
) -> CaseComparison:
    """Persist investigator consensus and return the refreshed comparison."""
    _require_squat_role(current_user.role, "investigator")
    safe_case_id = _validated_case_id(case_id)
    store = SupabaseSquatStore()
    try:
        current_payload = await run_in_threadpool(
            store.get_case_comparison_data,
            safe_case_id,
        )
        if current_payload is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Squat case was not found.",
            )
        unconsolidated_payload = {
            **current_payload,
            "manual_references": [],
        }
        current_comparison = build_stored_case_comparison(
            unconsolidated_payload
        )
        current_pattern = next(
            row
            for row in current_comparison.patterns
            if (
                row.repetition_index == repetition_index
                and row.pattern_key == pattern_key
            )
        )
        if not current_pattern.expert_judgments:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "A final reference requires at least one submitted expert "
                    "judgment."
                ),
            )
        await run_in_threadpool(
            store.save_manual_reference,
            external_case_id=safe_case_id,
            repetition_index=repetition_index,
            pattern_key=pattern_key,
            classification=payload.classification,
            observed_side=payload.observed_side,
            observation=payload.observation,
            resolved_by=current_user.user_id,
        )
        comparison_payload = await run_in_threadpool(
            store.get_case_comparison_data,
            safe_case_id,
        )
    except SquatPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    if comparison_payload is None:  # pragma: no cover - guarded above
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return build_stored_case_comparison(comparison_payload)


@router.get(
    "/squat/comparison/metrics",
    response_model=DatasetPerformance,
    summary="Calculate accumulated expert-system performance metrics",
)
async def get_squat_dataset_metrics(
    current_user: SquatUserDependency,
) -> DatasetPerformance:
    """Return pooled and per-pattern metrics over consolidated cases."""
    _require_squat_role(current_user.role, "investigator")
    try:
        payloads = await run_in_threadpool(
            SupabaseSquatStore().list_comparison_data
        )
    except SquatPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    comparisons = [
        build_stored_case_comparison(payload) for payload in payloads
    ]
    return calculate_dataset_performance(comparisons)


@router.get(
    "/squat/cases/{case_id}/exports/{filename}",
    summary="Export research instruments or the readable case report",
)
async def export_squat_case(
    case_id: str,
    filename: Literal[
        "instruments.xlsx",
        "report.pdf",
        "technical-data.xlsx",
    ],
    current_user: SquatUserDependency,
) -> Response:
    """Generate investigator-only exports from canonical persisted data."""
    _require_squat_role(current_user.role, "investigator")
    safe_case_id = _validated_case_id(case_id)
    store = SupabaseSquatStore()
    try:
        comparison_payload, case_record, case_report, dataset_payloads = (
            await run_in_threadpool(
                _load_export_payload,
                store,
                safe_case_id,
            )
        )
    except SquatPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    if comparison_payload is None or case_record is None or case_report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The completed squat case was not found.",
        )
    if filename == "technical-data.xlsx":
        report_model = SquatCaseReport.model_validate(case_report)
        artifacts: dict[str, bytes] = {}
        case_dir = (_OUTPUT_ROOT / safe_case_id).resolve()
        for artifact_name in _technical_artifact_names(report_model):
            local_path = (case_dir / artifact_name).resolve()
            if local_path.parent == case_dir and local_path.is_file():
                artifacts[artifact_name] = local_path.read_bytes()
                continue
            stored = await run_in_threadpool(
                store.get_case_artifact,
                safe_case_id,
                artifact_name,
            )
            if stored is not None:
                artifacts[artifact_name] = stored.content
        content = await run_in_threadpool(
            build_technical_data_excel,
            artifacts=artifacts,
        )
        media_type = (
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
        return Response(
            content=content,
            media_type=media_type,
            headers={
                "Content-Disposition": (
                    f'attachment; filename="{safe_case_id}-{filename}"'
                ),
                "Content-Length": str(len(content)),
            },
        )

    comparison = build_stored_case_comparison(comparison_payload)
    if comparison.reference_status != "closed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The case must be closed before exporting final results.",
        )
    if not comparison.ready_for_metrics:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Expert references must be consolidated before exporting "
                "the comparative instruments."
            ),
        )
    performance = calculate_dataset_performance(
        [
            build_stored_case_comparison(payload)
            for payload in dataset_payloads
        ]
    )
    if filename == "instruments.xlsx":
        report_model = SquatCaseReport.model_validate(case_report)
        artifacts: dict[str, bytes] = {}
        case_dir = (_OUTPUT_ROOT / safe_case_id).resolve()
        for artifact_name in _explanation_artifact_names(report_model):
            local_path = (case_dir / artifact_name).resolve()
            if local_path.parent == case_dir and local_path.is_file():
                artifacts[artifact_name] = local_path.read_bytes()
                continue
            stored = await run_in_threadpool(
                store.get_case_artifact,
                safe_case_id,
                artifact_name,
            )
            if stored is not None:
                artifacts[artifact_name] = stored.content
        explanation = build_case_explanation(report_model, artifacts)
        content = await run_in_threadpool(
            build_case_excel,
            case_record=case_record,
            case_report=case_report,
            comparison=comparison,
            performance=performance,
            landmark_visibility=[
                item.model_dump(mode="json")
                for item in explanation.landmark_visibility_summaries
            ],
        )
        media_type = (
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    else:
        content = await run_in_threadpool(
            build_case_pdf,
            case_report=case_report,
            comparison=comparison,
            performance=performance,
        )
        media_type = "application/pdf"
    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": (
                f'attachment; filename="{safe_case_id}-{filename}"'
            ),
            "Content-Length": str(len(content)),
        },
    )


@router.get(
    "/squat/experts",
    response_model=list[SquatExpertProfileResponse],
    summary="List expert accounts available for case assignment",
)
async def list_squat_experts(
    current_user: SquatUserDependency,
) -> list[SquatExpertProfileResponse]:
    """Return only expert identities needed by the investigator."""
    _require_squat_role(current_user.role, "investigator")
    try:
        rows = await run_in_threadpool(SupabaseSquatStore().list_experts)
    except SquatPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    return [SquatExpertProfileResponse.model_validate(row) for row in rows]


@router.post(
    "/squat/cases/{case_id}/assignments",
    response_model=SquatAssignmentCreatedResponse,
    summary="Assign one completed case to expert evaluators",
)
async def assign_squat_case(
    case_id: str,
    payload: SquatAssignmentCreateRequest,
    current_user: SquatUserDependency,
) -> SquatAssignmentCreatedResponse:
    """Create idempotent expert assignments without exposing system output."""
    _require_squat_role(current_user.role, "investigator")
    safe_case_id = _validated_case_id(case_id)
    try:
        rows = await run_in_threadpool(
            SupabaseSquatStore().assign_case,
            external_case_id=safe_case_id,
            evaluator_ids=payload.evaluator_ids,
            assigned_by=current_user.user_id,
        )
    except SquatPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return SquatAssignmentCreatedResponse(
        case_id=safe_case_id,
        assigned=len(rows),
    )


@router.get(
    "/squat/cases/{case_id}/assignments",
    response_model=SquatCaseAssignmentsResponse,
    summary="List the expert roster assigned to a case",
)
async def list_squat_case_assignments(
    case_id: str,
    current_user: SquatUserDependency,
) -> SquatCaseAssignmentsResponse:
    """Return assignment identities and statuses without response contents."""
    _require_squat_role(current_user.role, "investigator")
    safe_case_id = _validated_case_id(case_id)
    try:
        roster = await run_in_threadpool(
            SupabaseSquatStore().list_case_assignments,
            safe_case_id,
        )
    except SquatPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    if roster is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return SquatCaseAssignmentsResponse.model_validate(roster)


@router.delete(
    "/squat/cases/{case_id}/assignments/{assignment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove an expert and any response from an open case",
)
async def remove_squat_case_assignment(
    case_id: str,
    assignment_id: str,
    current_user: SquatUserDependency,
) -> Response:
    """Cascade-delete one assignment before final-reference review starts."""
    _require_squat_role(current_user.role, "investigator")
    try:
        await run_in_threadpool(
            SupabaseSquatStore().remove_case_assignment,
            external_case_id=_validated_case_id(case_id),
            assignment_id=assignment_id,
        )
    except SquatPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/squat/cases/{case_id}/reference/start",
    response_model=CaseComparison,
    summary="Lock the expert roster and start final-reference review",
)
async def start_squat_final_reference(
    case_id: str,
    current_user: SquatUserDependency,
) -> CaseComparison:
    """Start reference review after every assigned expert has submitted."""
    _require_squat_role(current_user.role, "investigator")
    safe_case_id = _validated_case_id(case_id)
    store = SupabaseSquatStore()
    try:
        current_payload = await run_in_threadpool(
            store.get_case_comparison_data, safe_case_id
        )
        if current_payload is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        if (
            current_payload["assigned_evaluators"] < 1
            or current_payload["submitted_evaluations"]
            != current_payload["assigned_evaluators"]
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Every assigned evaluator must submit an evaluation before "
                    "final-reference review starts."
                ),
            )
        await run_in_threadpool(
            store.set_reference_status,
            external_case_id=safe_case_id,
            expected_status="open",
            next_status="in_progress",
            actor_id=current_user.user_id,
        )
        refreshed = await run_in_threadpool(
            store.get_case_comparison_data, safe_case_id
        )
    except SquatPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc
    return build_stored_case_comparison(refreshed or current_payload)


@router.post(
    "/squat/cases/{case_id}/reference/close",
    response_model=CaseComparison,
    summary="Close a fully consolidated case",
)
async def close_squat_final_reference(
    case_id: str,
    current_user: SquatUserDependency,
) -> CaseComparison:
    """Freeze final references and expose system output to assigned experts."""
    _require_squat_role(current_user.role, "investigator")
    safe_case_id = _validated_case_id(case_id)
    store = SupabaseSquatStore()
    try:
        current_payload = await run_in_threadpool(
            store.get_case_comparison_data, safe_case_id
        )
        if current_payload is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        comparison = build_stored_case_comparison(current_payload)
        if not comparison.ready_for_metrics:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Every repetition and pattern needs a final reference.",
            )
        await run_in_threadpool(
            store.set_reference_status,
            external_case_id=safe_case_id,
            expected_status="in_progress",
            next_status="closed",
            actor_id=current_user.user_id,
        )
        refreshed = await run_in_threadpool(
            store.get_case_comparison_data, safe_case_id
        )
    except SquatPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc
    return build_stored_case_comparison(refreshed or current_payload)


@router.get(
    "/squat/expert/assignments",
    response_model=list[SquatExpertAssignmentResponse],
    summary="List blinded assignments for the current expert",
)
async def list_current_expert_assignments(
    current_user: SquatUserDependency,
) -> list[SquatExpertAssignmentResponse]:
    """Return assignment metadata and only the current expert's own draft."""
    _require_squat_role(current_user.role, "expert")
    try:
        rows = await run_in_threadpool(
            SupabaseSquatStore().list_expert_assignments,
            current_user.user_id,
        )
    except SquatPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    return [
        SquatExpertAssignmentResponse.model_validate(row) for row in rows
    ]


@router.get(
    "/squat/expert/assignments/{assignment_id}",
    response_model=SquatExpertAssignmentResponse,
    summary="Get one blinded assignment for the current expert",
)
async def get_current_expert_assignment(
    assignment_id: str,
    current_user: SquatUserDependency,
) -> SquatExpertAssignmentResponse:
    """Return no report, rule, metric or system classification."""
    _require_squat_role(current_user.role, "expert")
    try:
        row = await run_in_threadpool(
            SupabaseSquatStore().get_expert_assignment,
            assignment_id,
            evaluator_id=current_user.user_id,
        )
    except SquatPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expert assignment was not found.",
        )
    return SquatExpertAssignmentResponse.model_validate(row)


@router.get(
    "/squat/expert/assignments/{assignment_id}/system-results",
    response_model=SquatCaseReport,
    summary="Get system results after the investigator closes the case",
)
async def get_current_expert_system_results(
    assignment_id: str,
    current_user: SquatUserDependency,
) -> SquatCaseReport:
    """Reveal system output only to an assigned expert after final closure."""
    _require_squat_role(current_user.role, "expert")
    store = SupabaseSquatStore()
    try:
        assignment = await run_in_threadpool(
            store.get_expert_assignment,
            assignment_id,
            evaluator_id=current_user.user_id,
        )
        if assignment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        if assignment["reference_status"] != "closed":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="System results remain blinded until the case is closed.",
            )
        report = await run_in_threadpool(
            store.get_case_report, assignment["case_id"]
        )
    except SquatPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return SquatCaseReport.model_validate(report)


@router.put(
    "/squat/expert/assignments/{assignment_id}/evaluation",
    response_model=SquatEvaluationSavedResponse,
    summary="Save or submit the current expert evaluation",
)
async def save_current_expert_evaluation(
    assignment_id: str,
    payload: SquatExpertEvaluationRequest,
    current_user: SquatUserDependency,
) -> SquatEvaluationSavedResponse:
    """Persist Instrument 3 while permanently locking submitted responses."""
    _require_squat_role(current_user.role, "expert")
    try:
        result = await run_in_threadpool(
            SupabaseSquatStore().save_expert_evaluation,
            assignment_id=assignment_id,
            evaluator_id=current_user.user_id,
            status=payload.status,
            general_observation=payload.general_observation,
            items=[item.model_dump(mode="json") for item in payload.items],
        )
    except SquatPersistenceError as exc:
        conflict = "cannot be modified" in str(exc)
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
                if conflict
                else status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=str(exc),
        ) from exc
    return SquatEvaluationSavedResponse.model_validate(result)


@router.get(
    "/squat/expert/assignments/{assignment_id}/video",
    summary="Stream the clean anonymized review video",
)
async def get_current_expert_review_video(
    assignment_id: str,
    current_user: SquatUserDependency,
    request: Request,
) -> Response:
    """Serve no overlay, landmarks, metrics or system classification."""
    _require_squat_role(current_user.role, "expert")
    store = SupabaseSquatStore()
    try:
        assignment = await run_in_threadpool(
            store.get_expert_assignment,
            assignment_id,
            evaluator_id=current_user.user_id,
        )
        if assignment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expert assignment was not found.",
            )
        case_dir = (_OUTPUT_ROOT / assignment["case_id"]).resolve()
        report_path = case_dir / "case_report.json"
        if report_path.is_file():
            report = SquatCaseReport.model_validate_json(
                report_path.read_text(encoding="utf-8")
            )
            review_name = report.artifacts.review_video
            if review_name:
                review_path = (case_dir / review_name).resolve()
                if review_path.parent == case_dir and review_path.is_file():
                    return FileResponse(review_path)
        stored = await run_in_threadpool(
            store.get_expert_review_artifact,
            assignment_id,
            evaluator_id=current_user.user_id,
            range_header=request.headers.get("range"),
        )
    except SquatPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    if stored is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expert review video was not found.",
        )
    return _stored_artifact_response(stored)


@router.get(
    "/squat/cases",
    response_model=SquatCasePage,
    summary="List persistent squat cases for the investigator",
)
async def list_squat_cases(
    current_user: SquatUserDependency,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    case_status: str | None = Query(default=None, alias="status"),
) -> SquatCasePage:
    """Return a stable server-paginated history from Supabase."""
    if current_user.role != "investigator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the investigator can list squat cases.",
        )
    try:
        result = await run_in_threadpool(
            SupabaseSquatStore().list_cases,
            page=page,
            page_size=page_size,
            status_filter=case_status,
        )
    except SquatPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    return SquatCasePage(
        items=[
            SquatCaseListItem(
                case_id=row["external_case_id"],
                participant_code=row.get("participant_code"),
                status=row["status"],
                protocol_review_status=row.get("protocol_review_status"),
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in result.rows
        ],
        page=page,
        page_size=page_size,
        total=result.total,
        total_pages=ceil(result.total / page_size) if result.total else 0,
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
    participant_age: int | None = Form(default=None),
    participant_sex: str | None = Form(default=None),
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
            participant_age=participant_age,
            participant_sex=participant_sex,
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
        report = await run_in_threadpool(
            run_squat_case_analysis,
            case,
            manual_review=manual_review,
            registry_path=_REGISTRY_PATH,
            output_dir=_OUTPUT_ROOT,
            ruleset_path=_RULESET_PATH,
        )
        if get_settings().squat_persistence_required:
            record_path = _OUTPUT_ROOT / case.case_id / "case_record.json"
            case_record = SquatCaseRecordContract.model_validate_json(
                record_path.read_text(encoding="utf-8")
            )
            await run_in_threadpool(
                SupabaseSquatStore().persist_completed_case,
                created_by=current_user.user_id,
                upload_path=upload_path,
                output_dir=_OUTPUT_ROOT / case.case_id,
                content_type=video.content_type or "video/mp4",
                case_record=case_record,
                report=report,
            )
        return report
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
    except (FileNotFoundError, RuntimeError, SquatPersistenceError) as exc:
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
        if not get_settings().squat_persistence_required:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Squat case report was not found.",
            )
        try:
            stored_report = await run_in_threadpool(
                SupabaseSquatStore().get_case_report,
                safe_case_id,
            )
        except SquatPersistenceError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc
        if stored_report is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Squat case report was not found.",
            )
        return SquatCaseReport.model_validate(stored_report)
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
    "/squat/cases/{case_id}/explanation",
    response_model=SquatCaseExplanation,
    summary="Get bounded evidence for the explanatory case interface",
)
async def get_squat_case_explanation(
    case_id: str,
    current_user: SquatUserDependency,
) -> SquatCaseExplanation:
    """Return chart, table and key-frame data without recomputing metrics."""
    _require_squat_role(current_user.role, "investigator")
    safe_case_id = _validated_case_id(case_id)
    case_dir = (_OUTPUT_ROOT / safe_case_id).resolve()
    report_path = case_dir / "case_report.json"
    if report_path.is_file():
        report = SquatCaseReport.model_validate_json(
            report_path.read_text(encoding="utf-8")
        )
        artifacts = {
            filename: (case_dir / filename).read_bytes()
            for filename in _explanation_artifact_names(report)
            if (case_dir / filename).is_file()
        }
        return build_case_explanation(report, artifacts)

    if not get_settings().squat_persistence_required:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Squat case explanation was not found.",
        )
    store = SupabaseSquatStore()
    try:
        stored_report = await run_in_threadpool(
            store.get_case_report,
            safe_case_id,
        )
        if stored_report is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Squat case explanation was not found.",
            )
        report = SquatCaseReport.model_validate(stored_report)
        artifacts: dict[str, bytes] = {}
        for filename in _explanation_artifact_names(report):
            stored = await run_in_threadpool(
                store.get_case_artifact,
                safe_case_id,
                filename,
            )
            if stored is not None:
                artifacts[filename] = stored.content
        return build_case_explanation(report, artifacts)
    except SquatPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
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
        if not get_settings().squat_persistence_required:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Squat case record was not found.",
            )
        try:
            stored_record = await run_in_threadpool(
                SupabaseSquatStore().get_case_record,
                safe_case_id,
            )
        except SquatPersistenceError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc
        if stored_record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Squat case record was not found.",
            )
        return SquatCaseRecordContract.model_validate(stored_record)
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
    request: Request,
) -> Response:
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
    if report_path.is_file():
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
    if not get_settings().squat_persistence_required:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Squat case asset was not found.",
        )
    try:
        stored = await run_in_threadpool(
            SupabaseSquatStore().get_case_artifact,
            safe_case_id,
            filename,
            range_header=request.headers.get("range"),
        )
    except SquatPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    if stored is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Squat case asset was not found.",
        )
    return _stored_artifact_response(stored)


def _stored_artifact_response(stored: SquatStoredArtifact) -> Response:
    headers = {
        "Accept-Ranges": stored.accept_ranges or "bytes",
        "Content-Length": str(len(stored.content)),
    }
    if stored.content_range:
        headers["Content-Range"] = stored.content_range
    return Response(
        content=stored.content,
        status_code=stored.status_code,
        media_type=stored.mime_type,
        headers=headers,
    )


def _require_squat_role(current_role: str, expected_role: str) -> None:
    if current_role != expected_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"This operation requires the {expected_role} role.",
        )


def _report_has_eligible_repetitions(
    report: dict[str, Any] | None,
) -> bool:
    if not report:
        return False
    quality = report.get("quality")
    if quality is not None:
        indexes = quality.get("eligible_repetition_indexes") or []
        if indexes:
            return True
        if not quality.get("eligible_for_analysis"):
            return False
        return bool((report.get("findings") or {}).get("decisions"))
    segmentation = report.get("segmentation") or {}
    findings = report.get("findings") or {}
    return bool(
        segmentation.get("repetitions") or findings.get("decisions")
    )


def _load_export_payload(
    store: SupabaseSquatStore,
    case_id: str,
) -> tuple[
    dict[str, Any] | None,
    dict[str, Any] | None,
    dict[str, Any] | None,
    list[dict[str, Any]],
]:
    """Load all canonical inputs needed by one export request."""
    return (
        store.get_case_comparison_data(case_id),
        store.get_case_record(case_id),
        store.get_case_report(case_id),
        store.list_comparison_data(),
    )


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


def _explanation_artifact_names(report: SquatCaseReport) -> list[str]:
    """Return only canonical tables consumed by the explanation builder."""
    names = (
        report.artifacts.frame_quality_csv,
        report.artifacts.frame_phases_csv,
        report.artifacts.biomechanical_frame_metrics_csv,
        report.artifacts.landmarks_csv,
    )
    return [name for name in names if name]


def _technical_artifact_names(report: SquatCaseReport) -> list[str]:
    """Return canonical CSV files included in the readable technical workbook."""
    names = (
        report.artifacts.landmarks_csv,
        report.artifacts.frame_quality_csv,
        report.artifacts.frame_phases_csv,
        report.artifacts.repetitions_csv,
        report.artifacts.biomechanical_frame_metrics_csv,
        report.artifacts.biomechanical_repetition_metrics_csv,
        report.artifacts.rule_evidence_csv,
    )
    return [name for name in names if name]


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
