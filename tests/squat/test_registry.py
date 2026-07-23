"""Tests for the local squat case registry."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.squat.models import SquatCaseRecord
from src.squat.registry import (
    CASE_REGISTRY_COLUMNS,
    append_case_record,
    initialize_case_registry,
    load_case_registry,
)


def test_registry_initialization_and_round_trip(tmp_path: Path) -> None:
    registry_path = tmp_path / "metadata" / "casos.csv"
    case = SquatCaseRecord(
        case_id="caso_001",
        video_path="D:/videos/caso_001.mp4",
        participant_code="P001",
        profile="positivo_controlado",
        intended_findings=["valgo_dinamico_visible"],
        protocol_review_status="aceptado",
    )

    initialized = initialize_case_registry(registry_path)
    append_case_record(initialized, case)
    loaded = load_case_registry(initialized)

    assert initialized == registry_path
    assert loaded == [case]


def test_registry_rejects_duplicate_case_id(tmp_path: Path) -> None:
    path = tmp_path / "casos.csv"
    case = SquatCaseRecord(case_id="caso_001", video_path="case.mp4")
    append_case_record(path, case)

    with pytest.raises(ValueError, match="already exists"):
        append_case_record(path, case)


def test_registry_rejects_unexpected_columns(tmp_path: Path) -> None:
    path = tmp_path / "casos.csv"
    path.write_text("case_id,wrong_column\ncaso_001,value\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Unexpected case registry columns"):
        load_case_registry(path)


def test_registry_column_contract_is_stable() -> None:
    assert CASE_REGISTRY_COLUMNS[0] == "case_id"
    assert CASE_REGISTRY_COLUMNS[-1] == "load_condition"
