"""Authorization and contract tests for blinded expert evaluation."""

from __future__ import annotations

from fastapi.testclient import TestClient

from api.auth import SquatApiUser, get_squat_api_user
from api.routes import squat as squat_route
from app.main import app
from src.squat.persistence import SquatStoredArtifact


async def _expert_user() -> SquatApiUser:
    return SquatApiUser(
        user_id="expert-1",
        email="expert@example.test",
        role="expert",
    )


def _assignment() -> dict[str, object]:
    return {
        "assignment_id": "assignment-1",
        "case_id": "caso_ciego_001",
        "status": "pending",
        "created_at": "2026-07-24T10:00:00Z",
        "updated_at": "2026-07-24T10:00:00Z",
        "evaluation": None,
    }


def test_expert_assignment_contract_does_not_expose_system_results(
    monkeypatch,
) -> None:
    class FakeStore:
        def get_expert_assignment(self, *args, **kwargs):
            assert args == ("assignment-1",)
            assert kwargs == {"evaluator_id": "expert-1"}
            return _assignment()

    monkeypatch.setattr(squat_route, "SupabaseSquatStore", FakeStore)
    app.dependency_overrides[get_squat_api_user] = _expert_user
    try:
        response = TestClient(app).get(
            "/api/v1/squat/expert/assignments/assignment-1"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["case_id"] == "caso_ciego_001"
    assert "findings" not in payload
    assert "report" not in payload
    assert "artifacts" not in payload


def test_submitted_expert_evaluation_requires_all_patterns(
    monkeypatch,
) -> None:
    class FakeStore:
        def save_expert_evaluation(self, **kwargs):
            raise AssertionError("Invalid payload must not reach persistence.")

    monkeypatch.setattr(squat_route, "SupabaseSquatStore", FakeStore)
    app.dependency_overrides[get_squat_api_user] = _expert_user
    try:
        response = TestClient(app).put(
            "/api/v1/squat/expert/assignments/assignment-1/evaluation",
            json={
                "status": "submitted",
                "items": [
                    {
                        "pattern_key": "trunk_lateral_inclination",
                        "classification": "ausente",
                    }
                ],
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422


def test_present_classification_requires_a_valid_side(monkeypatch) -> None:
    class FakeStore:
        def save_expert_evaluation(self, **kwargs):
            raise AssertionError("Invalid payload must not reach persistence.")

    monkeypatch.setattr(squat_route, "SupabaseSquatStore", FakeStore)
    app.dependency_overrides[get_squat_api_user] = _expert_user
    try:
        response = TestClient(app).put(
            "/api/v1/squat/expert/assignments/assignment-1/evaluation",
            json={
                "status": "draft",
                "items": [
                    {
                        "pattern_key": "visible_dynamic_valgus",
                        "classification": "presente",
                    }
                ],
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422


def test_expert_can_submit_complete_instrument_3(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeStore:
        def save_expert_evaluation(self, **kwargs):
            captured.update(kwargs)
            return {"evaluation_id": "evaluation-1", "status": "submitted"}

    monkeypatch.setattr(squat_route, "SupabaseSquatStore", FakeStore)
    app.dependency_overrides[get_squat_api_user] = _expert_user
    items = [
        {
            "pattern_key": pattern,
            "classification": "ausente",
            "confidence": "alta",
        }
        for pattern in (
            "trunk_lateral_inclination",
            "pelvis_lateral_shift",
            "visible_dynamic_valgus",
            "bilateral_asymmetry",
        )
    ]
    try:
        response = TestClient(app).put(
            "/api/v1/squat/expert/assignments/assignment-1/evaluation",
            json={"status": "submitted", "items": items},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["status"] == "submitted"
    assert captured["evaluator_id"] == "expert-1"
    assert len(captured["items"]) == 4


def test_expert_video_endpoint_serves_only_review_artifact(
    tmp_path,
    monkeypatch,
) -> None:
    class FakeStore:
        def get_expert_assignment(self, *args, **kwargs):
            return _assignment()

        def get_expert_review_artifact(self, *args, **kwargs):
            assert kwargs["evaluator_id"] == "expert-1"
            return SquatStoredArtifact(
                content=b"review-video",
                mime_type="video/mp4",
                status_code=200,
                accept_ranges="bytes",
            )

    monkeypatch.setattr(squat_route, "SupabaseSquatStore", FakeStore)
    monkeypatch.setattr(squat_route, "_OUTPUT_ROOT", tmp_path / "outputs")
    app.dependency_overrides[get_squat_api_user] = _expert_user
    try:
        response = TestClient(app).get(
            "/api/v1/squat/expert/assignments/assignment-1/video"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.content == b"review-video"
    assert response.headers["content-type"].startswith("video/mp4")


def test_investigator_cannot_open_expert_assignment_list() -> None:
    response = TestClient(app).get("/api/v1/squat/expert/assignments")

    assert response.status_code == 403
