from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from src.rag.chat_flow import (
    build_chat_deficiencies_from_static_analysis,
    build_chat_query,
    build_rendered_blocks,
    build_rest_phase1_findings_and_deficiencies,
)


def _load_static_analysis_payload() -> dict:
    response_path = Path("debug/posture_test/prueba-1/response.json")
    raw = json.loads(response_path.read_text(encoding="utf-8"))
    return raw["body"]


def test_build_chat_deficiencies_from_static_analysis_returns_actionable_items() -> None:
    payload = _load_static_analysis_payload()
    deficiencies = build_chat_deficiencies_from_static_analysis(payload)
    labels = {item["label"] for item in deficiencies}
    assert deficiencies
    assert "Asimetría postural de hombros" in labels
    assert any(item["body_region"] in {"scapula", "shoulder", "pelvis", "thoracic_spine"} for item in deficiencies)


def test_build_rest_phase1_findings_and_deficiencies_uses_formal_detector_rules() -> None:
    payload = _load_static_analysis_payload()
    findings, deficiencies = build_rest_phase1_findings_and_deficiencies(payload)
    finding_ids = {item["id"] for item in findings}
    deficiency_ids = {item["id"] for item in deficiencies}
    assert "shoulder_height_asymmetry" in finding_ids
    assert "thoracic_flattening_bias" in finding_ids
    assert "postural_shoulder_asymmetry" in deficiency_ids


def test_build_chat_query_includes_detected_deficiencies() -> None:
    payload = _load_static_analysis_payload()
    deficiencies = build_chat_deficiencies_from_static_analysis(payload)
    query = build_chat_query(
        user_message="No puedo elevar mi brazo derecho completamente",
        deficiencies=deficiencies,
        analysis_jobs=[{"detected_deficiencies": deficiencies}],
    )
    assert "Deficiencias detectadas por análisis de imágenes" in query
    assert "Asimetría postural de hombros" in query


def test_build_rendered_blocks_surfaces_sections() -> None:
    blocks = build_rendered_blocks(
        answer_payload={
            "answer": "La evidencia sugiere un patrón escapular asimétrico.",
            "key_points": ["Hay asimetría escapular."],
            "recommended_exercises": ["Side plank with wall push"],
            "cautions": ["No reemplaza evaluación clínica."],
            "citations": [{"title": "Video A", "source_uri": "https://example.com"}],
        },
        deficiencies=[{"label": "Asimetría escapular", "summary": "Escápula derecha más elevada."}],
    )
    titles = [item["title"] for item in blocks]
    assert "Diagnóstico funcional orientativo" in titles
    assert "Ejercicios sugeridos" in titles
    assert "Fuentes relacionadas" in titles


def test_chat_models_endpoint_returns_catalog() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/chat/models")
    assert response.status_code == 200
    payload = response.json()
    assert payload["models"]
    assert any(item["model_key"] == "grounded-default" for item in payload["models"])

