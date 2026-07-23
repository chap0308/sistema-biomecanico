"""CSV registry for the bilateral squat thesis sample."""

from __future__ import annotations

import csv
from pathlib import Path

from src.squat.models import SquatCaseRecord

CASE_REGISTRY_COLUMNS: tuple[str, ...] = (
    "case_id",
    "video_path",
    "participant_code",
    "profile",
    "intended_findings",
    "protocol_review_status",
    "exclusion_reason",
    "view",
    "plane",
    "load_condition",
)


def initialize_case_registry(registry_path: str | Path) -> Path:
    """Create an empty case registry with the canonical header if needed."""
    path = Path(registry_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=CASE_REGISTRY_COLUMNS)
            writer.writeheader()
    return path


def load_case_registry(registry_path: str | Path) -> list[SquatCaseRecord]:
    """Load and validate all records from a squat case registry."""
    path = initialize_case_registry(registry_path)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != CASE_REGISTRY_COLUMNS:
            raise ValueError(f"Unexpected case registry columns in {path}")
        return [_row_to_case(row) for row in reader]


def append_case_record(registry_path: str | Path, case: SquatCaseRecord) -> Path:
    """Append one validated case while preventing duplicate identifiers."""
    path = initialize_case_registry(registry_path)
    existing_ids = {record.case_id for record in load_case_registry(path)}
    if case.case_id in existing_ids:
        raise ValueError(f"case_id already exists in registry: {case.case_id}")

    with path.open("a", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CASE_REGISTRY_COLUMNS)
        writer.writerow(_case_to_row(case))
    return path


def _case_to_row(case: SquatCaseRecord) -> dict[str, str]:
    payload = case.model_dump(mode="json")
    payload["intended_findings"] = ";".join(case.intended_findings)
    return {column: "" if payload[column] is None else str(payload[column]) for column in CASE_REGISTRY_COLUMNS}


def _row_to_case(row: dict[str, str]) -> SquatCaseRecord:
    payload: dict[str, object] = dict(row)
    payload["participant_code"] = row["participant_code"] or None
    payload["exclusion_reason"] = row["exclusion_reason"] or None
    payload["intended_findings"] = [
        value for value in row["intended_findings"].split(";") if value
    ]
    return SquatCaseRecord.model_validate(payload)


__all__ = [
    "CASE_REGISTRY_COLUMNS",
    "append_case_record",
    "initialize_case_registry",
    "load_case_registry",
]
