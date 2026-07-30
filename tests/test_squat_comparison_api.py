"""API tests for investigator comparison and exports."""

from __future__ import annotations

from fastapi.testclient import TestClient

from api.auth import SquatApiUser, get_squat_api_user
from api.routes import squat as squat_route
from app.main import app


async def _investigator_user() -> SquatApiUser:
    return SquatApiUser(
        user_id="investigator-1",
        email="investigator@example.test",
        role="investigator",
    )


async def _expert_user() -> SquatApiUser:
    return SquatApiUser(
        user_id="expert-1",
        email="expert@example.test",
        role="expert",
    )


def _comparison_payload(*, complete: bool = True) -> dict[str, object]:
    patterns = (
        "trunk_lateral_inclination",
        "pelvis_lateral_shift",
        "visible_dynamic_valgus",
        "bilateral_asymmetry",
    )
    judgments = []
    evaluators = ("expert-1", "expert-2") if complete else ("expert-1",)
    for evaluator in evaluators:
        judgments.extend(
            {
                "evaluator_id": evaluator,
                "repetition_index": 1,
                "pattern_key": pattern,
                "classification": "ausente",
                "observed_side": None,
                "confidence": "alta",
                "observation": "Ejecución visible.",
            }
            for pattern in patterns
        )
    return {
        "case_id": "caso_comparison_001",
        "assigned_evaluators": 2,
        "submitted_evaluations": len(evaluators),
        "judgments": judgments,
        "evaluator_observations": [
            {
                "evaluator_id": evaluator,
                "general_observation": "Sin oclusiones relevantes.",
            }
            for evaluator in evaluators
        ],
        "manual_references": [],
        "report": {
            "findings": {
                "decisions": [
                    {
                        "repetition_index": 1,
                        "finding": finding,
                        "status": "ausente",
                        "direction": None,
                    }
                    for finding in (
                        "inclinacion_lateral_tronco",
                        "desplazamiento_lateral_pelvis",
                        "valgo_dinamico_visible",
                        "asimetria_bilateral_observable",
                    )
                ]
            }
        },
    }


def test_investigator_gets_consolidated_case_comparison(monkeypatch) -> None:
    class FakeStore:
        def get_case_comparison_data(self, case_id):
            assert case_id == "caso_comparison_001"
            return _comparison_payload()

    monkeypatch.setattr(squat_route, "SupabaseSquatStore", FakeStore)
    app.dependency_overrides[get_squat_api_user] = _investigator_user
    try:
        response = TestClient(app).get(
            "/api/v1/squat/cases/caso_comparison_001/comparison"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["ready_for_metrics"] is True
    assert len(payload["patterns"]) == 4
    assert payload["patterns"][0]["reference"]["label"] == "ausente"
    assert payload["patterns"][0]["expert_judgments"][0]["confidence"] == "alta"
    assert (
        payload["patterns"][0]["expert_judgments"][0]["observation"]
        == "Ejecución visible."
    )
    assert payload["evaluator_observations"][0]["general_observation"]
    assert all(row["exact_match"] for row in payload["patterns"])


def test_expert_cannot_read_dataset_metrics(monkeypatch) -> None:
    class FakeStore:
        pass

    monkeypatch.setattr(squat_route, "SupabaseSquatStore", FakeStore)
    app.dependency_overrides[get_squat_api_user] = _expert_user
    try:
        response = TestClient(app).get("/api/v1/squat/comparison/metrics")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403


def test_comparative_export_requires_all_references(monkeypatch) -> None:
    class FakeStore:
        pass

    monkeypatch.setattr(squat_route, "SupabaseSquatStore", FakeStore)
    monkeypatch.setattr(
        squat_route,
        "_load_export_payload",
        lambda *_args: (
            _comparison_payload(complete=False),
            {"registration": {}},
            {"case_id": "caso_comparison_001"},
            [_comparison_payload(complete=False)],
        ),
    )
    app.dependency_overrides[get_squat_api_user] = _investigator_user
    try:
        response = TestClient(app).get(
            "/api/v1/squat/cases/caso_comparison_001/"
            "exports/instruments.xlsx"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409


def test_final_export_requires_closed_case(monkeypatch) -> None:
    class FakeStore:
        pass

    monkeypatch.setattr(squat_route, "SupabaseSquatStore", FakeStore)
    monkeypatch.setattr(
        squat_route,
        "_load_export_payload",
        lambda *_args: (
            _comparison_payload(),
            {"registration": {}},
            {"case_id": "caso_comparison_001"},
            [_comparison_payload()],
        ),
    )
    app.dependency_overrides[get_squat_api_user] = _investigator_user
    try:
        response = TestClient(app).get(
            "/api/v1/squat/cases/caso_comparison_001/"
            "exports/instruments.xlsx"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert "closed" in response.json()["detail"]


def test_manual_reference_allows_optional_observation(monkeypatch) -> None:
    saved: dict[str, object] = {}

    class FakeStore:
        def get_case_comparison_data(self, _case_id):
            return _comparison_payload()

        def save_manual_reference(self, **kwargs):
            saved.update(kwargs)

    monkeypatch.setattr(squat_route, "SupabaseSquatStore", FakeStore)
    app.dependency_overrides[get_squat_api_user] = _investigator_user
    try:
        response = TestClient(app).put(
            "/api/v1/squat/cases/caso_comparison_001/comparison/"
            "references/1/trunk_lateral_inclination",
            json={
                "classification": "ausente",
                "observation": "",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert saved["observation"] == ""


def test_manual_reference_can_override_direct_agreement_during_review(
    monkeypatch,
) -> None:
    saved: dict[str, object] = {}

    class FakeStore:
        def get_case_comparison_data(self, _case_id):
            return _comparison_payload()

        def save_manual_reference(self, **kwargs):
            saved.update(kwargs)

    monkeypatch.setattr(squat_route, "SupabaseSquatStore", FakeStore)
    app.dependency_overrides[get_squat_api_user] = _investigator_user
    try:
        response = TestClient(app).put(
            "/api/v1/squat/cases/caso_comparison_001/comparison/"
            "references/1/trunk_lateral_inclination",
            json={
                "classification": "presente",
                "observed_side": "izquierda",
                "observation": "Intento de sobrescritura.",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert saved["classification"] == "presente"


def test_start_reference_requires_every_assigned_evaluation(monkeypatch) -> None:
    class FakeStore:
        def get_case_comparison_data(self, _case_id):
            payload = _comparison_payload(complete=False)
            payload["assigned_evaluators"] = 2
            return payload

        def set_reference_status(self, **kwargs):
            raise AssertionError("An incomplete roster must remain open.")

    monkeypatch.setattr(squat_route, "SupabaseSquatStore", FakeStore)
    app.dependency_overrides[get_squat_api_user] = _investigator_user
    try:
        response = TestClient(app).post(
            "/api/v1/squat/cases/caso_comparison_001/reference/start"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409


def test_start_reference_locks_complete_roster(monkeypatch) -> None:
    transitions: list[dict[str, object]] = []

    class FakeStore:
        def get_case_comparison_data(self, _case_id):
            return _comparison_payload()

        def set_reference_status(self, **kwargs):
            transitions.append(kwargs)

    monkeypatch.setattr(squat_route, "SupabaseSquatStore", FakeStore)
    app.dependency_overrides[get_squat_api_user] = _investigator_user
    try:
        response = TestClient(app).post(
            "/api/v1/squat/cases/caso_comparison_001/reference/start"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert transitions[0]["expected_status"] == "open"
    assert transitions[0]["next_status"] == "in_progress"
