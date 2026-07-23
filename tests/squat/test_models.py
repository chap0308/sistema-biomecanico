"""Tests for bilateral squat data contracts."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from src.squat.models import (
    CRITICAL_LANDMARKS,
    TARGET_FINDINGS,
    SquatCaseRecord,
    SquatRegistrationResult,
    VideoTechnicalMetadata,
)


def _video_metadata(tmp_path: Path) -> VideoTechnicalMetadata:
    return VideoTechnicalMetadata(
        path=str(tmp_path / "case.mp4"),
        suffix=".mp4",
        width_px=1080,
        height_px=1920,
        fps=30.0,
        frame_count=300,
        duration_seconds=10.0,
        first_frame_readable=True,
    )


def test_case_contract_fixes_the_approved_capture_scope() -> None:
    case = SquatCaseRecord(case_id="caso_001", video_path="case.mp4")

    assert case.view == "anterior"
    assert case.plane == "frontal"
    assert case.load_condition == "sin_carga_externa"
    assert case.protocol_review_status == "pendiente"


@pytest.mark.parametrize("case_id", ["x", "case with spaces", "case/001"])
def test_case_contract_rejects_unsafe_identifiers(case_id: str) -> None:
    with pytest.raises(ValidationError):
        SquatCaseRecord(case_id=case_id, video_path="case.mp4")


def test_case_contract_rejects_findings_outside_thesis_scope() -> None:
    with pytest.raises(ValidationError, match="unsupported intended findings"):
        SquatCaseRecord(
            case_id="caso_001",
            video_path="case.mp4",
            intended_findings=["diagnostico_escoliosis"],
        )


def test_case_contract_deduplicates_findings_and_normalizes_empty_reason() -> None:
    case = SquatCaseRecord(
        case_id=" caso_001 ",
        video_path="case.mp4",
        intended_findings=["valgo_dinamico_visible", "valgo_dinamico_visible"],
        exclusion_reason="   ",
    )

    assert case.case_id == "caso_001"
    assert case.intended_findings == ["valgo_dinamico_visible"]
    assert case.exclusion_reason is None


def test_rejected_case_requires_an_exclusion_reason() -> None:
    with pytest.raises(ValidationError, match="exclusion_reason is required"):
        SquatCaseRecord(
            case_id="caso_001",
            video_path="case.mp4",
            protocol_review_status="rechazado",
        )


def test_pending_registration_is_not_ready_for_pose(tmp_path: Path) -> None:
    case = SquatCaseRecord(case_id="caso_001", video_path="case.mp4")

    result = SquatRegistrationResult.from_case(case, _video_metadata(tmp_path))

    assert result.status == "pendiente_revision_protocolo"
    assert result.ready_for_pose is False
    assert result.critical_landmarks == list(CRITICAL_LANDMARKS)
    assert result.target_findings == list(TARGET_FINDINGS)
    assert result.notes


def test_accepted_registration_is_ready_for_pose(tmp_path: Path) -> None:
    case = SquatCaseRecord(
        case_id="caso_001",
        video_path="case.mp4",
        protocol_review_status="aceptado",
    )

    result = SquatRegistrationResult.from_case(case, _video_metadata(tmp_path))

    assert result.status == "listo_para_pose"
    assert result.ready_for_pose is True
    assert result.notes == []


def test_rejected_registration_keeps_exclusion_reason(tmp_path: Path) -> None:
    case = SquatCaseRecord(
        case_id="caso_001",
        video_path="case.mp4",
        protocol_review_status="rechazado",
        exclusion_reason="Vista fuera del protocolo.",
    )

    result = SquatRegistrationResult.from_case(case, _video_metadata(tmp_path))

    assert result.status == "rechazado"
    assert result.ready_for_pose is False
    assert result.notes == ["Vista fuera del protocolo."]
