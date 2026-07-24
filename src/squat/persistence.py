"""Supabase persistence for web-managed bilateral-squat cases."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests

from app.config import Settings, get_settings
from src.squat.contracts import SquatCaseRecordContract, SquatCaseReport


class SquatPersistenceError(RuntimeError):
    """Raised when Supabase rejects a case persistence operation."""


@dataclass(slots=True, frozen=True)
class SquatCasePageData:
    """One page returned by PostgREST plus its exact total."""

    rows: list[dict[str, Any]]
    total: int


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
        content_type: str,
        case_record: SquatCaseRecordContract,
        report: SquatCaseReport,
    ) -> None:
        """Store the original video and aggregate contracts atomically enough for F2."""
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
        self._insert(
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
                f"Failed to store input video: {response.status_code} "
                f"{response.text}"
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


__all__ = [
    "SquatCasePageData",
    "SquatPersistenceError",
    "SupabaseSquatStore",
]
