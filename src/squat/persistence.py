"""Supabase persistence for web-managed bilateral-squat cases."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import mimetypes
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests

from app.config import Settings, get_settings
from src.squat.contracts import SquatCaseRecordContract, SquatCaseReport


class SquatPersistenceError(RuntimeError):
    """Raised when Supabase rejects a case persistence operation."""


def _normalize_expert_observed_side(value: str | None) -> str | None:
    """Map legacy predominance labels to the current expert contract."""
    return {
        "predominio_izquierdo": "izquierda",
        "predominio_derecho": "derecha",
    }.get(value or "", value)


@dataclass(slots=True, frozen=True)
class SquatCasePageData:
    """One page returned by PostgREST plus its exact total."""

    rows: list[dict[str, Any]]
    total: int


@dataclass(slots=True, frozen=True)
class SquatStoredArtifact:
    """Private artifact downloaded from Supabase Storage."""

    content: bytes
    mime_type: str
    status_code: int
    content_range: str | None = None
    accept_ranges: str | None = None


class SupabaseSquatStore:
    """Small service-role client for private squat records and files."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.url = self.settings.supabase_url.rstrip("/")
        self.service_key = (
            self.settings.supabase_secret_key
            or self.settings.supabase_service_key
        )

    @property
    def is_configured(self) -> bool:
        """Return whether service-role persistence can be used."""
        return bool(self.url and self.service_key)

    def persist_completed_case(
        self,
        *,
        created_by: str,
        upload_path: Path,
        output_dir: Path,
        content_type: str,
        case_record: SquatCaseRecordContract,
        report: SquatCaseReport,
    ) -> None:
        """Store one completed case plus its declared private artifacts."""
        self._require_configuration()
        external_case_id = report.case_id
        object_path = f"{external_case_id}/original{upload_path.suffix.lower()}"
        self._upload_private_file(
            bucket="squat-inputs",
            object_path=object_path,
            local_path=upload_path,
            content_type=content_type,
        )
        case_row = self._insert(
            "squat_cases",
            {
                "external_case_id": external_case_id,
                "created_by": created_by,
                "participant_code": case_record.registration.case.participant_code,
                "profile": case_record.registration.case.profile,
                "status": _database_status(report.status),
                "protocol_review_status": (
                    case_record.registration.case.protocol_review_status
                ),
                "exclusion_reason": (
                    case_record.registration.case.exclusion_reason
                ),
                "original_object_path": object_path,
                "instrument_1": case_record.model_dump(mode="json"),
            },
        )
        run_row = self._insert(
            "squat_analysis_runs",
            {
                "case_id": case_row["case_id"],
                "status": _run_status(report.status),
                "pipeline_version": report.pipeline_version,
                "ruleset_version": (
                    report.findings.ruleset_version if report.findings else None
                ),
                "report": report.model_dump(mode="json"),
                "started_at": report.generated_at.isoformat(),
                "completed_at": report.generated_at.isoformat(),
            },
        )
        for artifact_kind, filename, metadata in _report_artifacts(report):
            local_path = output_dir / filename
            if not local_path.is_file():
                continue
            artifact_path = f"{external_case_id}/{filename}"
            mime_type = (
                mimetypes.guess_type(filename)[0]
                or "application/octet-stream"
            )
            self._upload_private_file(
                bucket="squat-artifacts",
                object_path=artifact_path,
                local_path=local_path,
                content_type=mime_type,
            )
            self._insert(
                "squat_artifacts",
                {
                    "run_id": run_row["run_id"],
                    "artifact_kind": artifact_kind,
                    "object_path": artifact_path,
                    "mime_type": mime_type,
                    "metadata": metadata,
                },
            )

    def list_cases(
        self,
        *,
        page: int,
        page_size: int,
        status_filter: str | None = None,
    ) -> SquatCasePageData:
        """Return a stable newest-first page for the investigator history."""
        self._require_configuration()
        offset = (page - 1) * page_size
        params: list[tuple[str, str]] = [
            (
                "select",
                "external_case_id,participant_code,status,"
                "protocol_review_status,created_at,updated_at",
            ),
            ("order", "created_at.desc"),
            ("limit", str(page_size)),
            ("offset", str(offset)),
        ]
        if status_filter:
            params.append(("status", f"eq.{status_filter}"))
        response = requests.get(
            f"{self.url}/rest/v1/squat_cases",
            params=params,
            headers={
                **self._headers(),
                "Prefer": "count=exact",
                "Range-Unit": "items",
            },
            timeout=30,
        )
        if response.status_code != 200:
            raise SquatPersistenceError(
                f"Failed to list squat cases: {response.status_code} "
                f"{response.text}"
            )
        content_range = response.headers.get("content-range", "*/0")
        total_text = content_range.rsplit("/", maxsplit=1)[-1]
        total = int(total_text) if total_text.isdigit() else 0
        return SquatCasePageData(rows=response.json(), total=total)

    def get_case_report(self, external_case_id: str) -> dict[str, Any] | None:
        """Load the newest persisted aggregate report for one external case."""
        case_rows = self._select(
            "squat_cases",
            params={
                "select": "case_id,reference_status",
                "external_case_id": f"eq.{external_case_id}",
                "limit": "1",
            },
        )
        if not case_rows:
            return None
        run_rows = self._select(
            "squat_analysis_runs",
            params={
                "select": "report",
                "case_id": f"eq.{case_rows[0]['case_id']}",
                "order": "created_at.desc",
                "limit": "1",
            },
        )
        return run_rows[0]["report"] if run_rows else None

    def get_case_record(self, external_case_id: str) -> dict[str, Any] | None:
        """Load the persisted Instrument 1 contract for one external case."""
        rows = self._select(
            "squat_cases",
            params={
                "select": "instrument_1",
                "external_case_id": f"eq.{external_case_id}",
                "limit": "1",
            },
        )
        return rows[0]["instrument_1"] if rows else None

    def get_case_artifact(
        self,
        external_case_id: str,
        filename: str,
        *,
        range_header: str | None = None,
    ) -> SquatStoredArtifact | None:
        """Download one artifact previously declared by the aggregate report."""
        case_rows = self._select(
            "squat_cases",
            params={
                "select": "case_id",
                "external_case_id": f"eq.{external_case_id}",
                "limit": "1",
            },
        )
        if not case_rows:
            return None
        run_rows = self._select(
            "squat_analysis_runs",
            params={
                "select": "run_id",
                "case_id": f"eq.{case_rows[0]['case_id']}",
                "order": "created_at.desc",
                "limit": "1",
            },
        )
        if not run_rows:
            return None
        object_path = f"{external_case_id}/{filename}"
        artifact_rows = self._select(
            "squat_artifacts",
            params={
                "select": "object_path,mime_type",
                "run_id": f"eq.{run_rows[0]['run_id']}",
                "object_path": f"eq.{object_path}",
                "limit": "1",
            },
        )
        if not artifact_rows:
            return None
        headers = self._headers()
        if range_header:
            headers["Range"] = range_header
        response = requests.get(
            f"{self.url}/storage/v1/object/authenticated/"
            f"squat-artifacts/{quote(object_path, safe='/')}",
            headers=headers,
            timeout=120,
        )
        if response.status_code == 404:
            return None
        if response.status_code not in {200, 206}:
            raise SquatPersistenceError(
                f"Failed to read squat artifact: {response.status_code} "
                f"{response.text}"
            )
        return SquatStoredArtifact(
            content=response.content,
            mime_type=(
                artifact_rows[0].get("mime_type")
                or response.headers.get("content-type")
                or "application/octet-stream"
            ),
            status_code=response.status_code,
            content_range=response.headers.get("content-range"),
            accept_ranges=response.headers.get("accept-ranges"),
        )

    def list_experts(self) -> list[dict[str, Any]]:
        """Return active expert profiles available for assignment."""
        return self._select(
            "profiles",
            params={
                "select": "user_id,email,display_name",
                "squat_role": "eq.expert",
                "order": "display_name.asc",
            },
        )

    def assign_case(
        self,
        *,
        external_case_id: str,
        evaluator_ids: list[str],
        assigned_by: str,
    ) -> list[dict[str, Any]]:
        """Assign one completed case to one or more expert evaluators."""
        case_rows = self._select(
            "squat_cases",
            params={
                "select": "case_id,status,reference_status",
                "external_case_id": f"eq.{external_case_id}",
                "limit": "1",
            },
        )
        if not case_rows:
            raise SquatPersistenceError("Squat case was not found.")
        if case_rows[0]["status"] != "completed":
            raise SquatPersistenceError(
                "Only completed squat cases can be assigned."
            )
        if case_rows[0].get("reference_status", "open") != "open":
            raise SquatPersistenceError(
                "Evaluator assignments are locked after final-reference review starts."
            )
        current_assignments = self._select(
            "squat_expert_assignments",
            params={
                "select": "evaluator_id",
                "case_id": f"eq.{case_rows[0]['case_id']}",
            },
        )
        current_ids = {row["evaluator_id"] for row in current_assignments}
        requested_new_ids = set(evaluator_ids) - current_ids
        if len(current_ids | requested_new_ids) > 3:
            raise SquatPersistenceError(
                "A case can have at most three expert evaluators."
            )
        for evaluator_id in evaluator_ids:
            expert_rows = self._select(
                "profiles",
                params={
                    "select": "user_id",
                    "user_id": f"eq.{evaluator_id}",
                    "squat_role": "eq.expert",
                    "limit": "1",
                },
            )
            if not expert_rows:
                raise SquatPersistenceError(
                    f"Evaluator {evaluator_id} is not an expert account."
                )
        return self._upsert_many(
            "squat_expert_assignments",
            [
                {
                    "case_id": case_rows[0]["case_id"],
                    "evaluator_id": evaluator_id,
                    "assigned_by": assigned_by,
                    "status": "pending",
                }
                for evaluator_id in evaluator_ids
            ],
            on_conflict="case_id,evaluator_id",
            ignore_duplicates=True,
        )

    def list_case_assignments(
        self,
        external_case_id: str,
    ) -> dict[str, Any] | None:
        """Return the investigator roster without expert response contents."""
        case_rows = self._select(
            "squat_cases",
            params={
                "select": "case_id,reference_status",
                "external_case_id": f"eq.{external_case_id}",
                "limit": "1",
            },
        )
        if not case_rows:
            return None
        case = case_rows[0]
        assignments = self._select(
            "squat_expert_assignments",
            params={
                "select": "assignment_id,evaluator_id,status",
                "case_id": f"eq.{case['case_id']}",
                "order": "created_at.asc",
            },
        )
        profiles = {
            row["user_id"]: row
            for row in self._select(
                "profiles",
                params={
                    "select": "user_id,email,display_name",
                    "squat_role": "eq.expert",
                },
            )
        }
        return {
            "case_id": external_case_id,
            "reference_status": case.get("reference_status", "open"),
            "assignments": [
                {
                    **assignment,
                    "email": profiles.get(
                        assignment["evaluator_id"], {}
                    ).get("email"),
                    "display_name": profiles.get(
                        assignment["evaluator_id"], {}
                    ).get("display_name"),
                    "has_response": assignment["status"] != "pending",
                }
                for assignment in assignments
            ],
        }

    def remove_case_assignment(
        self,
        *,
        external_case_id: str,
        assignment_id: str,
    ) -> None:
        """Remove one evaluator while the case roster remains open."""
        roster = self.list_case_assignments(external_case_id)
        if roster is None:
            raise SquatPersistenceError("Squat case was not found.")
        if roster["reference_status"] != "open":
            raise SquatPersistenceError(
                "Evaluator assignments are locked after final-reference review starts."
            )
        assignment = next(
            (
                row
                for row in roster["assignments"]
                if row["assignment_id"] == assignment_id
            ),
            None,
        )
        if assignment is None:
            raise SquatPersistenceError("Expert assignment was not found.")
        self._delete(
            "squat_expert_assignments",
            filters={"assignment_id": f"eq.{assignment_id}"},
        )

    def set_reference_status(
        self,
        *,
        external_case_id: str,
        expected_status: str,
        next_status: str,
        actor_id: str,
    ) -> dict[str, Any]:
        """Advance the irreversible final-reference lifecycle."""
        case_rows = self._select(
            "squat_cases",
            params={
                "select": "case_id,reference_status",
                "external_case_id": f"eq.{external_case_id}",
                "limit": "1",
            },
        )
        if not case_rows:
            raise SquatPersistenceError("Squat case was not found.")
        current = case_rows[0].get("reference_status", "open")
        if current != expected_status:
            raise SquatPersistenceError(
                f"Case reference status is {current}, expected {expected_status}."
            )
        payload: dict[str, Any] = {"reference_status": next_status}
        if next_status == "in_progress":
            payload.update(
                {
                    "reference_started_at": datetime.now(timezone.utc).isoformat(),
                    "reference_started_by": actor_id,
                }
            )
        elif next_status == "closed":
            payload.update(
                {
                    "closed_at": datetime.now(timezone.utc).isoformat(),
                    "closed_by": actor_id,
                }
            )
        return self._update(
            "squat_cases",
            filters={
                "case_id": f"eq.{case_rows[0]['case_id']}",
                "reference_status": f"eq.{expected_status}",
            },
            payload=payload,
        )

    def list_expert_assignments(
        self,
        evaluator_id: str,
    ) -> list[dict[str, Any]]:
        """List assignment cards without exposing computational results."""
        assignments = self._select(
            "squat_expert_assignments",
            params={
                "select": "assignment_id,case_id,status,created_at,updated_at",
                "evaluator_id": f"eq.{evaluator_id}",
                "order": "created_at.desc",
            },
        )
        return [
            self._assignment_view(assignment, evaluator_id=evaluator_id)
            for assignment in assignments
        ]

    def get_expert_assignment(
        self,
        assignment_id: str,
        *,
        evaluator_id: str,
    ) -> dict[str, Any] | None:
        """Load one expert-owned assignment and its own draft only."""
        rows = self._select(
            "squat_expert_assignments",
            params={
                "select": "assignment_id,case_id,status,created_at,updated_at",
                "assignment_id": f"eq.{assignment_id}",
                "evaluator_id": f"eq.{evaluator_id}",
                "limit": "1",
            },
        )
        return (
            self._assignment_view(rows[0], evaluator_id=evaluator_id)
            if rows
            else None
        )

    def save_expert_evaluation(
        self,
        *,
        assignment_id: str,
        evaluator_id: str,
        status: str,
        general_observation: str | None,
        items: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Save a draft or atomically lock a submitted expert evaluation."""
        assignment = self.get_expert_assignment(
            assignment_id,
            evaluator_id=evaluator_id,
        )
        if assignment is None:
            raise SquatPersistenceError("Expert assignment was not found.")
        if assignment["status"] == "submitted":
            raise SquatPersistenceError(
                "Submitted expert evaluations cannot be modified."
            )
        expected_repetitions = {
            repetition["repetition_index"]
            for repetition in assignment.get("repetitions", [])
        }
        submitted_repetitions = {
            int(item["repetition_index"]) for item in items
        }
        if expected_repetitions and not submitted_repetitions.issubset(
            expected_repetitions
        ):
            raise SquatPersistenceError(
                "The evaluation contains repetitions outside the assignment."
            )
        if (
            status == "submitted"
            and expected_repetitions
            and submitted_repetitions != expected_repetitions
        ):
            raise SquatPersistenceError(
                "Every detected repetition must be evaluated before submission."
            )
        existing = self._select(
            "squat_expert_evaluations",
            params={
                "select": "evaluation_id,status",
                "assignment_id": f"eq.{assignment_id}",
                "limit": "1",
            },
        )
        payload = {
            "assignment_id": assignment_id,
            "evaluator_id": evaluator_id,
            "status": status,
            "general_observation": general_observation,
            "submitted_at": (
                datetime.now(timezone.utc).isoformat()
                if status == "submitted"
                else None
            ),
        }
        if existing:
            if existing[0]["status"] == "submitted":
                raise SquatPersistenceError(
                    "Submitted expert evaluations cannot be modified."
                )
            evaluation = self._update(
                "squat_expert_evaluations",
                filters={"evaluation_id": f"eq.{existing[0]['evaluation_id']}"},
                payload=payload,
            )
        else:
            evaluation = self._insert("squat_expert_evaluations", payload)
        evaluation_id = evaluation["evaluation_id"]
        self._delete(
            "squat_expert_evaluation_items",
            filters={"evaluation_id": f"eq.{evaluation_id}"},
        )
        if items:
            self._insert_many(
                "squat_expert_evaluation_items",
                [
                    {
                        **item,
                        "evaluation_id": evaluation_id,
                    }
                    for item in items
                ],
            )
        self._update(
            "squat_expert_assignments",
            filters={"assignment_id": f"eq.{assignment_id}"},
            payload={
                "status": (
                    "submitted" if status == "submitted" else "in_progress"
                )
            },
        )
        return {
            "evaluation_id": evaluation_id,
            "status": status,
        }

    def get_expert_review_artifact(
        self,
        assignment_id: str,
        *,
        evaluator_id: str,
        range_header: str | None = None,
    ) -> SquatStoredArtifact | None:
        """Return only the clean anonymized review video for one assignee."""
        assignment = self.get_expert_assignment(
            assignment_id,
            evaluator_id=evaluator_id,
        )
        if assignment is None:
            return None
        case_rows = self._select(
            "squat_cases",
            params={
                "select": "case_id",
                "external_case_id": f"eq.{assignment['case_id']}",
                "limit": "1",
            },
        )
        if not case_rows:
            return None
        run_rows = self._select(
            "squat_analysis_runs",
            params={
                "select": "run_id",
                "case_id": f"eq.{case_rows[0]['case_id']}",
                "order": "created_at.desc",
                "limit": "1",
            },
        )
        if not run_rows:
            return None
        artifact_rows = self._select(
            "squat_artifacts",
            params={
                "select": "object_path,mime_type",
                "run_id": f"eq.{run_rows[0]['run_id']}",
                "artifact_kind": "eq.review_video",
                "limit": "1",
            },
        )
        if not artifact_rows:
            return None
        return self._download_private_object(
            bucket="squat-artifacts",
            object_path=artifact_rows[0]["object_path"],
            mime_type=artifact_rows[0].get("mime_type"),
            range_header=range_header,
        )

    def get_case_comparison_data(
        self,
        external_case_id: str,
    ) -> dict[str, Any] | None:
        """Load submitted expert judgments, manual references, and report."""
        case_rows = self._select(
            "squat_cases",
            params={
                "select": "case_id,external_case_id,reference_status",
                "external_case_id": f"eq.{external_case_id}",
                "limit": "1",
            },
        )
        if not case_rows:
            return None
        case_id = case_rows[0]["case_id"]
        run_rows = self._select(
            "squat_analysis_runs",
            params={
                "select": "report",
                "case_id": f"eq.{case_id}",
                "status": "eq.completed",
                "order": "created_at.desc",
                "limit": "1",
            },
        )
        assignments = self._select(
            "squat_expert_assignments",
            params={
                "select": "assignment_id,evaluator_id,status",
                "case_id": f"eq.{case_id}",
                "order": "created_at.asc",
            },
        )
        judgments: list[dict[str, Any]] = []
        submitted = 0
        for assignment in assignments:
            if assignment["status"] != "submitted":
                continue
            evaluation_rows = self._select(
                "squat_expert_evaluations",
                params={
                    "select": "evaluation_id",
                    "assignment_id": f"eq.{assignment['assignment_id']}",
                    "evaluator_id": f"eq.{assignment['evaluator_id']}",
                    "status": "eq.submitted",
                    "limit": "1",
                },
            )
            if not evaluation_rows:
                continue
            submitted += 1
            items = self._select(
                "squat_expert_evaluation_items",
                params={
                    "select": (
                        "repetition_index,pattern_key,classification,observed_side,"
                        "confidence"
                    ),
                    "evaluation_id": (
                        f"eq.{evaluation_rows[0]['evaluation_id']}"
                    ),
                    "order": "repetition_index.asc,pattern_key.asc",
                },
            )
            judgments.extend(
                {
                    **item,
                    "evaluator_id": assignment["evaluator_id"],
                }
                for item in items
            )
        manual_references = self._select(
            "squat_expert_references",
            params={
                "select": (
                    "repetition_index,pattern_key,classification,observed_side,"
                    "method,observation"
                ),
                "case_id": f"eq.{case_id}",
                "order": "repetition_index.asc,pattern_key.asc",
            },
        )
        return {
            "case_id": external_case_id,
            "database_case_id": case_id,
            "report": run_rows[0]["report"] if run_rows else None,
            "assigned_evaluators": len(assignments),
            "submitted_evaluations": submitted,
            "reference_status": case_rows[0].get("reference_status", "open"),
            "judgments": judgments,
            "manual_references": manual_references,
        }

    def list_comparison_data(self) -> list[dict[str, Any]]:
        """Load comparison inputs for every completed case."""
        cases = self._select(
            "squat_cases",
            params={
                "select": "external_case_id,reference_status",
                "status": "eq.completed",
                "order": "created_at.asc",
            },
        )
        return [
            payload
            for row in cases
            if (
                payload := self.get_case_comparison_data(
                    row["external_case_id"]
                )
            )
            is not None
        ]

    def save_manual_reference(
        self,
        *,
        external_case_id: str,
        repetition_index: int,
        pattern_key: str,
        classification: str,
        observed_side: str | None,
        observation: str | None,
        resolved_by: str,
    ) -> dict[str, Any]:
        """Upsert a guided consensus recorded by the investigator."""
        case_rows = self._select(
            "squat_cases",
            params={
                "select": "case_id,reference_status",
                "external_case_id": f"eq.{external_case_id}",
                "limit": "1",
            },
        )
        if not case_rows:
            raise SquatPersistenceError("Squat case was not found.")
        if case_rows[0].get("reference_status", "open") != "in_progress":
            raise SquatPersistenceError(
                "Final references can only be edited while review is in progress."
            )
        rows = self._upsert_many(
            "squat_expert_references",
            [
                {
                    "case_id": case_rows[0]["case_id"],
                    "repetition_index": repetition_index,
                    "pattern_key": pattern_key,
                    "classification": classification,
                    "observed_side": observed_side,
                    "method": "consenso_guiado",
                    "observation": observation,
                    "resolved_by": resolved_by,
                }
            ],
            on_conflict="case_id,repetition_index,pattern_key",
            ignore_duplicates=False,
        )
        if not rows:
            raise SquatPersistenceError("Supabase returned no reference row.")
        return rows[0]

    def _assignment_view(
        self,
        assignment: dict[str, Any],
        *,
        evaluator_id: str,
    ) -> dict[str, Any]:
        case_rows = self._select(
            "squat_cases",
            params={
                "select": "external_case_id,reference_status",
                "case_id": f"eq.{assignment['case_id']}",
                "limit": "1",
            },
        )
        evaluation_rows = self._select(
            "squat_expert_evaluations",
            params={
                "select": (
                    "evaluation_id,status,general_observation,"
                    "created_at,updated_at,submitted_at"
                ),
                "assignment_id": f"eq.{assignment['assignment_id']}",
                "evaluator_id": f"eq.{evaluator_id}",
                "limit": "1",
            },
        )
        evaluation = evaluation_rows[0] if evaluation_rows else None
        if evaluation:
            evaluation["items"] = self._select(
                "squat_expert_evaluation_items",
                params={
                    "select": (
                        "repetition_index,pattern_key,classification,observed_side,"
                        "confidence,observation"
                    ),
                    "evaluation_id": f"eq.{evaluation['evaluation_id']}",
                    "order": "repetition_index.asc,pattern_key.asc",
                },
            )
            for item in evaluation["items"]:
                item["observed_side"] = _normalize_expert_observed_side(
                    item.get("observed_side")
                )
        repetitions: list[dict[str, Any]] = []
        if case_rows:
            run_rows = self._select(
                "squat_analysis_runs",
                params={
                    "select": "report",
                    "case_id": f"eq.{assignment['case_id']}",
                    "status": "eq.completed",
                    "order": "created_at.desc",
                    "limit": "1",
                },
            )
            if run_rows:
                report = run_rows[0].get("report") or {}
                segmentation = report.get("segmentation") or {}
                quality = report.get("quality") or {}
                eligible_indexes = set(
                    quality.get("eligible_repetition_indexes") or []
                )
                repetitions = [
                    {
                        "repetition_index": repetition["repetition_index"],
                        "start_seconds": repetition["start_seconds"],
                        "peak_depth_seconds": repetition["peak_depth_seconds"],
                        "end_seconds": repetition["end_seconds"],
                    }
                    for repetition in segmentation.get("repetitions", [])
                    if (
                        not eligible_indexes
                        or repetition["repetition_index"] in eligible_indexes
                    )
                ]
        return {
            "assignment_id": assignment["assignment_id"],
            "case_id": (
                case_rows[0]["external_case_id"] if case_rows else "unknown"
            ),
            "status": assignment["status"],
            "reference_status": (
                case_rows[0].get("reference_status", "open")
                if case_rows
                else "open"
            ),
            "created_at": assignment["created_at"],
            "updated_at": assignment["updated_at"],
            "repetitions": repetitions,
            "evaluation": evaluation,
        }

    def _insert(self, table: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = requests.post(
            f"{self.url}/rest/v1/{table}",
            headers={
                **self._headers(),
                "Content-Type": "application/json",
                "Prefer": "return=representation",
            },
            json=payload,
            timeout=30,
        )
        if response.status_code not in {200, 201}:
            raise SquatPersistenceError(
                f"Failed to insert {table}: {response.status_code} "
                f"{response.text}"
            )
        rows = response.json()
        if not rows:
            raise SquatPersistenceError(f"Supabase returned no {table} row.")
        return rows[0]

    def _insert_many(
        self,
        table: str,
        payload: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        response = requests.post(
            f"{self.url}/rest/v1/{table}",
            headers={
                **self._headers(),
                "Content-Type": "application/json",
                "Prefer": "return=representation",
            },
            json=payload,
            timeout=30,
        )
        if response.status_code not in {200, 201}:
            raise SquatPersistenceError(
                f"Failed to insert {table}: {response.status_code} "
                f"{response.text}"
            )
        return response.json()

    def _upsert_many(
        self,
        table: str,
        payload: list[dict[str, Any]],
        *,
        on_conflict: str,
        ignore_duplicates: bool,
    ) -> list[dict[str, Any]]:
        resolution = (
            "ignore-duplicates" if ignore_duplicates else "merge-duplicates"
        )
        response = requests.post(
            f"{self.url}/rest/v1/{table}",
            params={"on_conflict": on_conflict},
            headers={
                **self._headers(),
                "Content-Type": "application/json",
                "Prefer": f"resolution={resolution},return=representation",
            },
            json=payload,
            timeout=30,
        )
        if response.status_code not in {200, 201}:
            raise SquatPersistenceError(
                f"Failed to upsert {table}: {response.status_code} "
                f"{response.text}"
            )
        return response.json()

    def _update(
        self,
        table: str,
        *,
        filters: dict[str, str],
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        response = requests.patch(
            f"{self.url}/rest/v1/{table}",
            params=filters,
            headers={
                **self._headers(),
                "Content-Type": "application/json",
                "Prefer": "return=representation",
            },
            json=payload,
            timeout=30,
        )
        if response.status_code != 200:
            raise SquatPersistenceError(
                f"Failed to update {table}: {response.status_code} "
                f"{response.text}"
            )
        rows = response.json()
        if not rows:
            raise SquatPersistenceError(f"Supabase updated no {table} row.")
        return rows[0]

    def _delete(
        self,
        table: str,
        *,
        filters: dict[str, str],
    ) -> None:
        response = requests.delete(
            f"{self.url}/rest/v1/{table}",
            params=filters,
            headers=self._headers(),
            timeout=30,
        )
        if response.status_code not in {200, 204}:
            raise SquatPersistenceError(
                f"Failed to delete {table}: {response.status_code} "
                f"{response.text}"
            )

    def _select(
        self,
        table: str,
        *,
        params: dict[str, str],
    ) -> list[dict[str, Any]]:
        self._require_configuration()
        response = requests.get(
            f"{self.url}/rest/v1/{table}",
            params=params,
            headers=self._headers(),
            timeout=30,
        )
        if response.status_code != 200:
            raise SquatPersistenceError(
                f"Failed to select {table}: {response.status_code} "
                f"{response.text}"
            )
        return response.json()

    def _upload_private_file(
        self,
        *,
        bucket: str,
        object_path: str,
        local_path: Path,
        content_type: str,
    ) -> None:
        with local_path.open("rb") as handle:
            response = requests.post(
                f"{self.url}/storage/v1/object/{bucket}/"
                f"{quote(object_path, safe='/')}",
                headers={
                    **self._headers(),
                    "Content-Type": content_type,
                    "x-upsert": "false",
                },
                data=handle,
                timeout=120,
            )
        if response.status_code not in {200, 201}:
            raise SquatPersistenceError(
                f"Failed to store private file: {response.status_code} "
                f"{response.text}"
            )

    def _download_private_object(
        self,
        *,
        bucket: str,
        object_path: str,
        mime_type: str | None,
        range_header: str | None,
    ) -> SquatStoredArtifact | None:
        headers = self._headers()
        if range_header:
            headers["Range"] = range_header
        response = requests.get(
            f"{self.url}/storage/v1/object/authenticated/{bucket}/"
            f"{quote(object_path, safe='/')}",
            headers=headers,
            timeout=120,
        )
        if response.status_code == 404:
            return None
        if response.status_code not in {200, 206}:
            raise SquatPersistenceError(
                f"Failed to read squat artifact: {response.status_code} "
                f"{response.text}"
            )
        return SquatStoredArtifact(
            content=response.content,
            mime_type=(
                mime_type
                or response.headers.get("content-type")
                or "application/octet-stream"
            ),
            status_code=response.status_code,
            content_range=response.headers.get("content-range"),
            accept_ranges=response.headers.get("accept-ranges"),
        )

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.service_key}",
            "apikey": self.service_key,
        }

    def _require_configuration(self) -> None:
        if not self.is_configured:
            raise SquatPersistenceError(
                "Supabase squat persistence is not configured."
            )


def _database_status(report_status: str) -> str:
    return {
        "registro_pendiente": "under_review",
        "registro_rechazado": "excluded",
        "analisis_parcial": "completed",
        "no_apto_para_analisis": "excluded",
        "analisis_completo": "completed",
    }[report_status]


def _run_status(report_status: str) -> str:
    return {
        "registro_pendiente": "inconclusive",
        "registro_rechazado": "inconclusive",
        "analisis_parcial": "completed",
        "no_apto_para_analisis": "inconclusive",
        "analisis_completo": "completed",
    }[report_status]


def _report_artifacts(
    report: SquatCaseReport,
) -> list[tuple[str, str, dict[str, Any]]]:
    payload = report.artifacts.model_dump(mode="json")
    captures = payload.pop("event_captures", [])
    artifacts = [
        (kind, filename, {})
        for kind, filename in payload.items()
        if isinstance(filename, str)
    ]
    artifacts.extend(
        (
            "event_capture",
            capture["relative_path"],
            {
                "repetition_index": capture["repetition_index"],
                "event": capture["event"],
                "timestamp_seconds": capture["timestamp_seconds"],
            },
        )
        for capture in captures
        if isinstance(capture.get("relative_path"), str)
    )
    return artifacts


__all__ = [
    "SquatCasePageData",
    "SquatPersistenceError",
    "SquatStoredArtifact",
    "SupabaseSquatStore",
]
