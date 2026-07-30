"""Tests for persistent squat artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from types import SimpleNamespace

import pytest

from src.squat.contracts import (
    SquatArtifactManifest,
    SquatCaseRecordContract,
    SquatCaseReport,
    SquatEventCapture,
    SquatManualProtocolReview,
)
from src.squat.models import (
    SquatCaseRecord,
    SquatRegistrationResult,
    VideoTechnicalMetadata,
)
from src.squat.persistence import (
    SquatPersistenceError,
    SupabaseSquatStore,
    _normalize_expert_observed_side,
)


class RecordingStore(SupabaseSquatStore):
    """In-memory recording double for PostgREST and Storage calls."""

    def __init__(self) -> None:
        self.uploads: list[tuple[str, str, str]] = []
        self.inserts: list[tuple[str, dict[str, Any]]] = []

    def _require_configuration(self) -> None:
        return None

    def _upload_private_file(
        self,
        *,
        bucket: str,
        object_path: str,
        local_path: Path,
        content_type: str,
    ) -> None:
        assert local_path.is_file()
        self.uploads.append((bucket, object_path, content_type))

    def _insert(self, table: str, payload: dict[str, Any]) -> dict[str, Any]:
        self.inserts.append((table, payload))
        if table == "squat_cases":
            return {"case_id": "database-case-id"}
        if table == "squat_analysis_runs":
            return {"run_id": "analysis-run-id"}
        return {"artifact_id": f"artifact-{len(self.inserts)}"}


def test_normalize_expert_observed_side_supports_legacy_labels() -> None:
    assert _normalize_expert_observed_side("predominio_izquierdo") == "izquierda"
    assert _normalize_expert_observed_side("predominio_derecho") == "derecha"
    assert _normalize_expert_observed_side("bilateral") == "bilateral"
    assert _normalize_expert_observed_side(None) is None


def test_list_cases_accepts_postgrest_partial_content(monkeypatch) -> None:
    response = SimpleNamespace(
        status_code=206,
        headers={"content-range": "0-9/12"},
        text="",
        json=lambda: [{"external_case_id": "case-1"}],
    )
    monkeypatch.setattr(
        "src.squat.persistence.requests.get",
        lambda *_args, **_kwargs: response,
    )
    store = RecordingStore()
    store.url = "http://supabase.test"
    store.service_key = "service-key"

    result = store.list_cases(page=1, page_size=10)

    assert result.total == 12
    assert result.rows == [{"external_case_id": "case-1"}]


def test_assign_case_rejects_report_without_valid_repetitions() -> None:
    class NoEligibleRepetitionStore(RecordingStore):
        def _select(self, table: str, *, params: dict[str, str]):
            assert table == "squat_cases"
            return [
                {
                    "case_id": "database-case-id",
                    "status": "completed",
                    "reference_status": "open",
                }
            ]

        def get_case_report(self, external_case_id: str):
            return {
                "quality": {
                    "eligible_repetition_indexes": [],
                }
            }

    with pytest.raises(
        SquatPersistenceError,
        match="no valid repetitions",
    ):
        NoEligibleRepetitionStore().assign_case(
            external_case_id="case-no-valid-repetition",
            evaluator_ids=["expert-1"],
            assigned_by="investigator-1",
        )


def test_persist_completed_case_uploads_only_manifest_artifacts(
    tmp_path: Path,
) -> None:
    upload = tmp_path / "input.mp4"
    output_dir = tmp_path / "outputs"
    output_dir.mkdir()
    upload.write_bytes(b"input")
    (output_dir / "overlay.mp4").write_bytes(b"overlay")
    (output_dir / "review.mp4").write_bytes(b"review")
    (output_dir / "rep_01_maxima_profundidad.png").write_bytes(b"capture")
    (output_dir / "internal.json").write_text("{}", encoding="utf-8")

    case = SquatCaseRecord(
        case_id="caso_persistencia_001",
        video_path=str(upload),
        participant_code="P-001",
    )
    registration = SquatRegistrationResult.from_case(
        case,
        VideoTechnicalMetadata(
            path=str(upload),
            suffix=".mp4",
            width_px=1080,
            height_px=1920,
            fps=30.0,
            frame_count=300,
            duration_seconds=10.0,
            first_frame_readable=True,
        ),
    )
    record = SquatCaseRecordContract(
        registration=registration,
        manual_protocol_review=SquatManualProtocolReview(),
    )
    report = SquatCaseReport(
        case_id=case.case_id,
        status="analisis_completo",
        case_record_path="case_record.json",
        pipeline_version="test",
        artifacts=SquatArtifactManifest(
            overlay_video="overlay.mp4",
            review_video="review.mp4",
            event_captures=[
                SquatEventCapture(
                    repetition_index=1,
                    event="maxima_profundidad",
                    frame_index=100,
                    timestamp_seconds=3.3,
                    relative_path="rep_01_maxima_profundidad.png",
                )
            ],
        ),
    )
    store = RecordingStore()

    store.persist_completed_case(
        created_by="user-id",
        upload_path=upload,
        output_dir=output_dir,
        content_type="video/mp4",
        case_record=record,
        report=report,
    )

    uploaded_paths = {path for _, path, _ in store.uploads}
    assert uploaded_paths == {
        "caso_persistencia_001/original.mp4",
        "caso_persistencia_001/overlay.mp4",
        "caso_persistencia_001/review.mp4",
        "caso_persistencia_001/rep_01_maxima_profundidad.png",
    }
    artifact_rows = [
        payload for table, payload in store.inserts if table == "squat_artifacts"
    ]
    assert len(artifact_rows) == 3
    assert artifact_rows[2]["metadata"]["event"] == "maxima_profundidad"
