"""API contract tests for bilateral-squat analysis."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from api.routes import squat as squat_route
from app.main import app
from src.squat.contracts import (
    SquatArtifactManifest,
    SquatCaseReport,
    write_case_record_contract,
)
from src.squat.models import (
    SquatCaseRecord,
    SquatRegistrationResult,
    VideoTechnicalMetadata,
)
from src.squat.persistence import SquatCasePageData


def _report(case_id: str) -> SquatCaseReport:
    return SquatCaseReport(
        case_id=case_id,
        status="analisis_parcial",
        case_record_path="case_record.json",
        pipeline_version="test",
        artifacts=SquatArtifactManifest(overlay_video="overlay.mp4"),
    )


def test_squat_endpoint_receives_video_and_manual_review(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(squat_route, "_DATA_ROOT", tmp_path)
    monkeypatch.setattr(squat_route, "_UPLOAD_ROOT", tmp_path / "uploads")
    monkeypatch.setattr(squat_route, "_OUTPUT_ROOT", tmp_path / "outputs")
    monkeypatch.setattr(squat_route, "_REGISTRY_PATH", tmp_path / "casos.csv")

    captured: dict[str, object] = {}

    def fake_analysis(case, **kwargs):
        captured["case"] = case
        captured["manual_review"] = kwargs["manual_review"]
        return _report(case.case_id)

    monkeypatch.setattr(squat_route, "run_squat_case_analysis", fake_analysis)
    client = TestClient(app)
    response = client.post(
        "/api/v1/squat/cases",
        data={
            "case_id": "caso_api_001",
            "manual_review_json": json.dumps(
                {"lighting": "adecuada", "support_condition_compliant": True}
            ),
        },
        files={"video": ("squat.mp4", b"video-bytes", "video/mp4")},
    )

    assert response.status_code == 200
    assert response.json()["case_id"] == "caso_api_001"
    assert captured["manual_review"].lighting == "adecuada"
    assert Path(captured["case"].video_path).read_bytes() == b"video-bytes"


def test_squat_report_and_asset_endpoints(
    tmp_path: Path,
    monkeypatch,
) -> None:
    output_root = tmp_path / "outputs"
    case_dir = output_root / "caso_api_002"
    case_dir.mkdir(parents=True)
    report = _report("caso_api_002")
    (case_dir / "case_report.json").write_text(
        report.model_dump_json(indent=2),
        encoding="utf-8",
    )
    registration = SquatRegistrationResult.from_case(
        SquatCaseRecord(case_id="caso_api_002", video_path="video.mp4"),
        VideoTechnicalMetadata(
            path="video.mp4",
            suffix=".mp4",
            width_px=1080,
            height_px=1920,
            fps=30.0,
            frame_count=300,
            duration_seconds=10.0,
            first_frame_readable=True,
        ),
    )
    write_case_record_contract(registration, case_dir / "case_record.json")
    (case_dir / "overlay.mp4").write_bytes(b"overlay")
    monkeypatch.setattr(squat_route, "_OUTPUT_ROOT", output_root)
    client = TestClient(app)

    report_response = client.get("/api/v1/squat/cases/caso_api_002")
    record_response = client.get("/api/v1/squat/cases/caso_api_002/record")
    asset_response = client.get(
        "/api/v1/squat/cases/caso_api_002/assets/overlay.mp4"
    )
    private_file_response = client.get(
        "/api/v1/squat/cases/caso_api_002/assets/case_record.json"
    )

    assert report_response.status_code == 200
    assert report_response.json()["status"] == "analisis_parcial"
    assert record_response.status_code == 200
    assert record_response.json()["contract"] == "squat_case_record"
    assert asset_response.status_code == 200
    assert asset_response.content == b"overlay"
    assert private_file_response.status_code == 404


def test_squat_endpoint_rejects_non_video_upload() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/squat/cases",
        data={"case_id": "caso_api_003"},
        files={"video": ("notes.txt", b"text", "text/plain")},
    )

    assert response.status_code == 415


def test_squat_history_endpoint_returns_pagination(
    monkeypatch,
) -> None:
    class FakeStore:
        def list_cases(self, **kwargs) -> SquatCasePageData:
            assert kwargs == {
                "page": 2,
                "page_size": 10,
                "status_filter": "completed",
            }
            return SquatCasePageData(
                rows=[
                    {
                        "external_case_id": "caso_api_004",
                        "participant_code": "P-004",
                        "status": "completed",
                        "protocol_review_status": "aceptado",
                        "created_at": "2026-07-24T10:00:00Z",
                        "updated_at": "2026-07-24T10:05:00Z",
                    }
                ],
                total=11,
            )

    monkeypatch.setattr(squat_route, "SupabaseSquatStore", FakeStore)
    response = TestClient(app).get(
        "/api/v1/squat/cases",
        params={"page": 2, "page_size": 10, "status": "completed"},
    )

    assert response.status_code == 200
    assert response.json()["total"] == 11
    assert response.json()["total_pages"] == 2
    assert response.json()["items"][0]["case_id"] == "caso_api_004"
