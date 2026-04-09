"""Tests for quality-based retrieval and grounded answering helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from src.core.settings import get_rag_settings
from src.rag.answering import (
    _merge_translated_citation_titles,
    _normalize_answer_payload,
    _payload_looks_english_heavy,
    _text_looks_english_heavy,
    answer_query,
    answer_with_hf,
    answer_with_ollama,
    answer_with_openai,
)
from src.retrieval.hybrid import (
    RetrievalBundle,
    _filter_results_by_focus_signal,
    _filter_results_by_region_family,
    _infer_query_regions,
    _rerank_and_diversify_results,
    _tokenize_query,
)


@dataclass
class DummyResult:
    point_id: str
    score: float
    payload: dict[str, object]


def test_answer_with_hf_parses_grounded_answer(monkeypatch: Any) -> None:
    monkeypatch.setenv("HF_TOKEN", "test-token")
    get_rag_settings.cache_clear()

    bundle = RetrievalBundle(
        quality="medium",
        knowledge_results=[
            DummyResult(
                point_id="1",
                score=0.9,
                payload={
                    "knowledge_unit_title": "Three-Role Lacrosse-Ball Foot Roll",
                    "knowledge_unit_type": "corrective_exercise",
                    "knowledge_unit_summary": "A structured foot rolling drill.",
                    "execution_steps": ["Roll under the big toe.", "Roll toward the heel."],
                    "cues": ["Move slowly."],
                    "errors_to_avoid": ["Do not use excessive pressure."],
                    "when_useful": ["Plantar fascia symptoms"],
                    "when_not_useful": [],
                    "retest": ["Check foot pressure after the drill."],
                    "advice": ["Perform 15 reps."],
                    "body_regions": ["foot", "ankle"],
                    "problem_layers": ["plantar fasciitis"],
                    "source_uri": "https://www.youtube.com/shorts/mI2n6asSFos",
                    "timestamps_raw": ["0:00-0:27"],
                },
            )
        ],
        evidence_results=[],
        evidence_rows=[],
    )

    response_payload = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "answer": "A helpful starting point is a lacrosse-ball foot roll focused on heel and toe contact.",
                            "recommended_exercises": ["Three-Role Lacrosse-Ball Foot Roll"],
                            "key_points": ["This drill targets foot contact and plantar fascia symptoms."],
                            "cautions": ["Do not use excessive pressure."],
                            "citations": [
                                {
                                    "source_type": "youtube",
                                    "title": "This Secret Release Technique Unlocks Your Feet & Ankles",
                                    "source_uri": "https://www.youtube.com/shorts/mI2n6asSFos",
                                    "segment_id": None,
                                    "knowledge_unit_title": "Three-Role Lacrosse-Ball Foot Roll",
                                    "timestamp_hint": "0:00-0:27",
                                }
                            ],
                            "retrieval_quality": "medium",
                            "used_collections": ["video_knowledge_units_v1"],
                        }
                    )
                }
            }
        ]
    }

    class DummyResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, Any]:
            return response_payload

    def fake_post(*args: Any, **kwargs: Any) -> DummyResponse:
        assert kwargs["json"]["model"] == "openai/gpt-oss-120b"
        assert kwargs["json"]["max_tokens"] in {900, 1600}
        return DummyResponse()

    monkeypatch.setattr("src.rag.answering.requests.post", fake_post)
    result = answer_with_hf("Tengo dolor plantar y mal contacto del pie", bundle)

    assert result["recommended_exercises"] == ["Three-Role Lacrosse-Ball Foot Roll"]
    assert result["used_collections"] == ["video_knowledge_units_v1"]


def test_normalize_answer_payload_supports_qwen_nested_answer_shape() -> None:
    bundle = RetrievalBundle(
        quality="high",
        knowledge_results=[],
        evidence_results=[],
        evidence_rows=[],
    )

    payload = {
        "answer": {
            "summary": "Resumen en español.",
            "key_points": ["Punto clave 1.", "Punto clave 2."],
            "exercises": [
                {"name": "Ejercicio A", "description": "Descripción A."},
                {"name": "Ejercicio B", "description": "Descripción B."},
            ],
            "cautions": ["Precaución 1.", "Precaución 2."],
        }
    }

    normalized = _normalize_answer_payload(payload, bundle=bundle)

    assert normalized["answer"] == "Resumen en español."
    assert normalized["recommended_exercises"] == ["Ejercicio A", "Ejercicio B"]
    assert normalized["key_points"] == [
        "Punto clave 1.",
        "Punto clave 2.",
        "Descripción A.",
        "Descripción B.",
    ]
    assert normalized["cautions"] == ["Precaución 1.", "Precaución 2."]


def test_answer_with_ollama_parses_grounded_answer(monkeypatch: Any) -> None:
    monkeypatch.setenv("OLLAMA_ANSWER_MODEL", "qwen3:8b")
    get_rag_settings.cache_clear()

    bundle = RetrievalBundle(
        quality="medium",
        knowledge_results=[
            DummyResult(
                point_id="1",
                score=0.9,
                payload={
                    "knowledge_unit_title": "Heel-Supported Wall Breathing",
                    "knowledge_unit_type": "corrective_exercise",
                    "knowledge_unit_summary": "A wall-supported breathing drill for pelvic position and trunk control.",
                    "execution_steps": ["Place heels on the wall.", "Exhale and reach forward."],
                    "cues": ["Keep the ribs down."],
                    "errors_to_avoid": ["Do not arch the lower back."],
                    "when_useful": ["Anterior pelvic tilt pattern"],
                    "when_not_useful": [],
                    "retest": ["Check standing posture after the drill."],
                    "advice": ["Perform slow breaths."],
                    "body_regions": ["pelvis", "ribcage"],
                    "problem_layers": ["postural strategy"],
                    "source_uri": "https://www.youtube.com/shorts/0cQxyJiVzzg",
                    "timestamps_raw": ["0:00-0:22"],
                },
            )
        ],
        evidence_results=[],
        evidence_rows=[],
    )

    class DummyResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, Any]:
            return {
                "message": {
                    "content": json.dumps(
                        {
                            "answer": "A helpful starting point is a wall-supported breathing drill to improve pelvic and rib position.",
                            "recommended_exercises": ["Heel-Supported Wall Breathing"],
                            "key_points": ["This drill can help with pelvic and trunk control."],
                            "cautions": ["Do not arch the lower back."],
                            "citations": [
                                {
                                    "source_type": "youtube",
                                    "title": "Stop Sucking In Your Belly",
                                    "source_uri": "https://www.youtube.com/shorts/0cQxyJiVzzg",
                                    "segment_id": None,
                                    "knowledge_unit_title": "Heel-Supported Wall Breathing",
                                    "timestamp_hint": "0:00-0:22",
                                }
                            ],
                            "retrieval_quality": "medium",
                            "used_collections": ["video_knowledge_units_v1"],
                        }
                    )
                }
            }

    def fake_post(*args: Any, **kwargs: Any) -> DummyResponse:
        assert "/api/chat" in args[0]
        assert kwargs["json"]["model"] == "qwen3:8b"
        return DummyResponse()

    monkeypatch.setattr("src.rag.answering.requests.post", fake_post)
    result = answer_with_ollama("Tengo swayback y me cuesta controlar la pelvis", bundle)

    assert result["recommended_exercises"] == ["Heel-Supported Wall Breathing"]
    assert result["answer_backend"] == "ollama"


def test_answer_query_auto_falls_back_from_ollama_to_hf(monkeypatch: Any) -> None:
    monkeypatch.setenv("ANSWER_BACKEND", "auto")
    monkeypatch.setenv("HF_TOKEN", "test-token")
    get_rag_settings.cache_clear()

    bundle = RetrievalBundle(
        quality="low",
        knowledge_results=[],
        evidence_results=[],
        evidence_rows=[],
    )

    def fake_ollama(query: str, bundle: RetrievalBundle) -> dict[str, Any]:
        raise RuntimeError("ollama unavailable")

    def fake_hf(query: str, bundle: RetrievalBundle) -> dict[str, Any]:
        return {
            "answer": "fallback to hf worked",
            "recommended_exercises": [],
            "key_points": [],
            "cautions": [],
            "citations": [],
            "retrieval_quality": bundle.quality,
            "used_collections": [],
            "model_used": "hf-model",
            "answer_backend": "hf",
        }

    monkeypatch.setattr("src.rag.answering.answer_with_ollama", fake_ollama)
    monkeypatch.setattr("src.rag.answering.answer_with_hf", fake_hf)

    result = answer_query("consulta", bundle)

    assert result["answer_backend"] == "hf"


def test_answer_with_openai_parses_grounded_answer(monkeypatch: Any) -> None:
    monkeypatch.setenv("API_KEY_OPENAI", "test-openai-key")
    monkeypatch.setenv("OPENAI_ANSWER_MODEL", "gpt-5-mini")
    get_rag_settings.cache_clear()

    bundle = RetrievalBundle(
        quality="medium",
        knowledge_results=[
            DummyResult(
                point_id="1",
                score=0.95,
                payload={
                    "knowledge_unit_title": "Optimized Seated Face Pull Technique",
                    "knowledge_unit_type": "corrective_exercise",
                    "knowledge_unit_summary": "A seated face pull variation for better scapular retraction.",
                    "execution_steps": ["Sit supported.", "Pull elbows back toward face level."],
                    "cues": ["Lead with the elbows."],
                    "errors_to_avoid": ["Do not shrug the shoulders."],
                    "body_regions": ["shoulder", "scapula"],
                    "problem_layers": ["movement_coordination"],
                    "source_uri": "https://www.youtube.com/shorts/d7fXiLxQFyc",
                    "timestamps_raw": ["0:00-0:18"],
                },
            )
        ],
        evidence_results=[],
        evidence_rows=[],
    )

    class DummyResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, Any]:
            return {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "answer": "Una opcion util es un face pull sentado con apoyo para mejorar la retraccion escapular sin compensar con el cuello.",
                                    "recommended_exercises": ["Optimized Seated Face Pull Technique"],
                                    "key_points": ["Puede ayudar a mejorar el control escapular."],
                                    "cautions": ["No eleves los hombros al tirar."],
                                    "citations": [
                                        {
                                            "source_type": "youtube",
                                            "title": "Optimized Seated Face Pull Technique",
                                            "source_uri": "https://www.youtube.com/shorts/d7fXiLxQFyc",
                                            "segment_id": None,
                                            "knowledge_unit_title": "Optimized Seated Face Pull Technique",
                                            "timestamp_hint": "0:00-0:18",
                                        }
                                    ],
                                    "retrieval_quality": "medium",
                                    "used_collections": ["video_knowledge_units_v1"],
                                }
                            )
                        }
                    }
                ]
            }

    def fake_post(*args: Any, **kwargs: Any) -> DummyResponse:
        assert "api.openai.com" in args[0]
        assert kwargs["json"]["model"] == "gpt-5-mini"
        return DummyResponse()

    monkeypatch.setattr("src.rag.answering.requests.post", fake_post)
    result = answer_with_openai("Tengo rigidez escapular derecha", bundle)

    assert result["answer_backend"] == "openai"
    assert result["model_used"] == "gpt-5-mini"


def test_infer_query_regions_detects_shoulder_scapula_ribcage_for_cross_body_reach() -> None:
    query = "Me duele el pecho al querer tocar mi omóplato contrario con mi brazo derecho"
    regions = _infer_query_regions(query)
    assert "shoulder" in regions
    assert "scapula" in regions
    assert "rib_cage" in regions


def test_tokenize_query_normalizes_accents_for_cross_body_reach() -> None:
    query = "Me duele el pecho al querer tocar mi omóplato contrario con mi brazo derecho"
    tokens = _tokenize_query(query)
    assert "pecho" in tokens
    assert "shoulder" in tokens
    assert "scapula" in tokens


def test_infer_query_regions_detects_pelvis_for_spanish_posture_terms() -> None:
    query = "Tengo anteversión pélvica, swayback y tensión en flexores de cadera"
    regions = _infer_query_regions(query)
    assert "pelvis" in regions


def test_infer_query_regions_does_not_confuse_de_pie_with_foot() -> None:
    query = "Tengo anteversión pélvica y me cuesta controlar la pelvis al estar de pie"
    regions = _infer_query_regions(query)
    assert "pelvis" in regions
    assert "foot" not in regions


def test_infer_query_regions_detects_foot_and_ankle_for_pronation_query() -> None:
    query = "Se me colapsa el arco y pronación del tobillo derecho"
    regions = _infer_query_regions(query)
    assert "foot" in regions
    assert "ankle" in regions


def test_infer_query_regions_detects_jaw_and_neck_for_tmj_query() -> None:
    query = "TMJ con dolor cervical y mordida apretada"
    regions = _infer_query_regions(query)
    assert "jaw" in regions
    assert "neck" in regions


def test_grounded_fallback_exposes_structured_error_code(monkeypatch: Any) -> None:
    monkeypatch.setenv("API_KEY_OPENAI", "test-openai-key")
    get_rag_settings.cache_clear()

    bundle = RetrievalBundle(
        quality="medium",
        knowledge_results=[],
        evidence_results=[],
        evidence_rows=[],
    )

    class DummyResponse:
        status_code = 429
        text = '{"error":{"message":"You exceeded your current quota","type":"insufficient_quota","code":"insufficient_quota"}}'

        def raise_for_status(self) -> None:
            raise requests.HTTPError("429 Client Error: Too Many Requests for url", response=self)  # type: ignore[arg-type]

        def json(self) -> dict[str, Any]:
            return {}

    def fake_post(*args: Any, **kwargs: Any) -> DummyResponse:
        return DummyResponse()

    import requests

    monkeypatch.setattr("src.rag.answering.requests.post", fake_post)
    result = answer_with_openai("consulta", bundle)

    assert result["answer_backend"] == "grounded_fallback"
    assert result["fallback_error_code"] == "insufficient_quota"


def test_rerank_and_diversify_limits_same_source() -> None:
    results = [
        DummyResult("1", 0.8, {"source_id": "src-a", "knowledge_unit_title": "Shoulder control drill", "body_regions": ["shoulder"]}),
        DummyResult("2", 0.79, {"source_id": "src-a", "knowledge_unit_title": "Scapula drill", "body_regions": ["scapula"]}),
        DummyResult("3", 0.78, {"source_id": "src-a", "knowledge_unit_title": "Another shoulder drill", "body_regions": ["shoulder"]}),
        DummyResult("4", 0.77, {"source_id": "src-b", "knowledge_unit_title": "Pelvis drill", "body_regions": ["pelvis"]}),
    ]

    reranked = _rerank_and_diversify_results(
        "rigidez hombro escapula",
        results,  # type: ignore[arg-type]
        limit=3,
        max_per_source=2,
    )

    source_ids = [item.payload.get("source_id") for item in reranked]
    assert source_ids.count("src-a") == 2
    assert len(reranked) == 3


def test_rerank_prefers_matching_body_region() -> None:
    results = [
        DummyResult("1", 0.82, {"source_id": "src-foot", "knowledge_unit_title": "Foot drill", "body_regions": ["foot"]}),
        DummyResult("2", 0.80, {"source_id": "src-shoulder", "knowledge_unit_title": "Scapular posture drill", "body_regions": ["scapula", "shoulder"]}),
    ]

    reranked = _rerank_and_diversify_results(
        "no puedo mover bien el omoplato y el hombro derecho",
        results,  # type: ignore[arg-type]
        limit=2,
        max_per_source=1,
    )

    assert reranked[0].payload.get("source_id") == "src-shoulder"


def test_region_family_filter_prefers_shoulder_family_when_available() -> None:
    results = [
        DummyResult("1", 0.95, {"source_id": "src-foot", "body_regions": ["foot", "ankle"]}),
        DummyResult("2", 0.80, {"source_id": "src-scap", "body_regions": ["scapula", "shoulder"]}),
        DummyResult("3", 0.79, {"source_id": "src-ribs", "body_regions": ["rib_cage"]}),
    ]

    filtered = _filter_results_by_region_family(results, ["shoulder"], minimum_keep=2)  # type: ignore[arg-type]

    source_ids = [item.payload.get("source_id") for item in filtered]
    assert "src-foot" not in source_ids
    assert "src-scap" in source_ids
    assert "src-ribs" in source_ids


def test_rerank_penalizes_generic_broad_units_when_query_is_specific() -> None:
    results = [
        DummyResult(
            "1",
            0.9,
            {
                "source_id": "src-generic",
                "knowledge_unit_title": "Corrective Exercise: 9.2-11.8s",
                "knowledge_unit_summary": "A generic clip about movement patterns without shoulder-specific detail.",
                "body_regions": ["foot", "ankle", "scapula", "shoulder", "pelvis", "neck"],
                "primary_body_region": "foot",
            },
        ),
        DummyResult(
            "2",
            0.82,
            {
                "source_id": "src-specific",
                "knowledge_unit_title": "Side Plank with Wall Push for Scapular Repositioning",
                "knowledge_unit_summary": "Improve scapular stability by keeping the shoulder blade on the rib cage.",
                "body_regions": ["scapula", "shoulder", "upper_back"],
                "primary_body_region": "scapula",
            },
        ),
    ]

    reranked = _rerank_and_diversify_results(
        "no puedo mover bien el omoplato y el hombro derecho",
        results,  # type: ignore[arg-type]
        limit=2,
        max_per_source=1,
    )

    assert reranked[0].payload.get("source_id") == "src-specific"


def test_focus_signal_filter_prefers_primary_or_explicit_region_mentions() -> None:
    results = [
        DummyResult(
            "1",
            0.9,
            {
                "source_id": "src-generic",
                "knowledge_unit_title": "Wall posture correction drill",
                "knowledge_unit_summary": "A drill for stacked posture and breathing.",
                "body_regions": ["shoulder", "neck", "rib_cage", "pelvis"],
                "primary_body_region": "pelvis",
            },
        ),
        DummyResult(
            "2",
            0.82,
            {
                "source_id": "src-focused",
                "knowledge_unit_title": "Scapular wall slide",
                "knowledge_unit_summary": "Improve shoulder blade upward rotation.",
                "body_regions": ["scapula", "shoulder", "rib_cage"],
                "primary_body_region": "scapula",
            },
        ),
        DummyResult(
            "3",
            0.8,
            {
                "source_id": "src-shoulder",
                "knowledge_unit_title": "Shoulder external rotation drill",
                "knowledge_unit_summary": "Improve shoulder control.",
                "body_regions": ["shoulder"],
                "primary_body_region": "shoulder",
            },
        ),
    ]

    filtered = _filter_results_by_focus_signal(results, ["shoulder"], minimum_keep=2)  # type: ignore[arg-type]

    source_ids = [item.payload.get("source_id") for item in filtered]
    assert "src-focused" in source_ids
    assert "src-shoulder" in source_ids
    assert "src-generic" not in source_ids


def test_query_region_inference_handles_domain_terms() -> None:
    regions = _infer_query_regions("Tengo swayback, anterior pelvic tilt y butt wink")

    assert "pelvis" in regions

    foot_regions = _infer_query_regions("Pie plano funcional con pronacion, colapso medial y tobillo inestable")
    assert "foot" in foot_regions
    assert "ankle" in foot_regions

    jaw_regions = _infer_query_regions("Tengo TMJ, mordida desviada y dolor en la mandibula")
    assert "jaw" in jaw_regions


def test_query_tokenization_expands_domain_terms() -> None:
    tokens = _tokenize_query("Tengo swayback y flat feet con pronation")

    assert "pelvis" in tokens
    assert "foot" in tokens
    assert "arch" in tokens


def test_normalize_answer_payload_handles_qwen_nested_answer_shape() -> None:
    bundle = RetrievalBundle(
        quality="high",
        knowledge_results=[
            DummyResult(
                point_id="1",
                score=0.9,
                payload={
                    "knowledge_unit_title": "Side Plank with Overhead Arm for Rib Cage Expansion",
                    "knowledge_unit_type": "corrective_exercise",
                    "knowledge_unit_summary": "Opens the rib cage and supports scapular motion.",
                    "errors_to_avoid": ["Do not flare the ribs."],
                    "source_uri": "https://www.youtube.com/shorts/xFNPwIoJbTI",
                    "timestamps_raw": ["1:13-2:39"],
                },
            )
        ],
        evidence_results=[],
        evidence_rows=[],
    )
    payload = {
        "answer": {
            "diagnosis": "Possible thoracic rotation restriction with scapular compensation.",
            "mechanism": "Thoracic stiffness can force the shoulder girdle to compensate.",
            "corrective_plan": [
                {
                    "exercise": "Side Plank with Overhead Arm for Rib Cage Expansion",
                    "purpose": "Improve rib cage mobility.",
                    "execution": "Use relaxed breathing while opening the rib cage.",
                }
            ],
            "avoid": ["Forced overhead reaching without thoracic rotation"],
            "evidence_support": ["Detected shoulder asymmetry may contribute to compensation."],
        }
    }

    normalized = _normalize_answer_payload(payload, bundle=bundle)

    assert "thoracic" in normalized["answer"].lower()
    assert normalized["recommended_exercises"] == ["Side Plank with Overhead Arm for Rib Cage Expansion"]
    assert normalized["retrieval_quality"] == "high"


def test_normalize_answer_payload_handles_assessment_shape() -> None:
    bundle = RetrievalBundle(
        quality="high",
        knowledge_results=[
            DummyResult(
                point_id="1",
                score=0.9,
                payload={
                    "knowledge_unit_title": "Upper Body Rotation Test (Shoulder Rotation)",
                    "knowledge_unit_type": "assessment_test",
                    "knowledge_unit_summary": "Self-assessment for upper body rotation.",
                    "source_uri": "https://www.youtube.com/shorts/yHWRnhSC9rA",
                    "timestamps_raw": ["1:09-1:26"],
                },
            )
        ],
        evidence_results=[],
        evidence_rows=[],
    )
    payload = {
        "assessment": {
            "title": "Upper Body Rotation Test (Shoulder Rotation)",
            "summary": "A test to assess rotational mobility of the thorax and shoulder blade mechanics.",
            "when_useful": ["Identify side-to-side rotational differences."],
        },
        "possible_causes": [
            {
                "title": "Impact of Thoracic Spine Extension on Scapular Movement",
                "summary": "Thoracic positioning can reduce scapular congruence.",
            }
        ],
        "recommended_exercises": [
            {
                "title": "Side Plank with Overhead Arm for Rib Cage Expansion",
                "summary": "Improves lateral rib cage opening.",
                "steps": ["Breathe slowly."],
            }
        ],
    }

    normalized = _normalize_answer_payload(payload, bundle=bundle)

    assert "Upper Body Rotation Test" in normalized["answer"]
    assert normalized["recommended_exercises"] == ["Side Plank with Overhead Arm for Rib Cage Expansion"]
    assert normalized["retrieval_quality"] == "high"


def test_payload_looks_english_heavy_detects_english_list_fields() -> None:
    payload = {
        "answer": "Posible patrón respiratorio alterado.",
        "recommended_exercises": [
            "All Fours Hand Walk with Exhale for Rib Cage Expansion and Posture",
        ],
        "key_points": [
            "This exercise aims to improve rib cage mobility.",
        ],
        "cautions": [
            "Do not shrug the shoulders during the push.",
        ],
    }

    assert _payload_looks_english_heavy(payload) is True


def test_merge_translated_citation_titles_preserves_url_fields() -> None:
    merged = _merge_translated_citation_titles(
        original_citations=[
            {
                "source_uri": "https://example.com",
                "title": "Original title",
                "knowledge_unit_title": "Original title",
            }
        ],
        translated_titles=["Título traducido"],
    )

    assert merged[0]["source_uri"] == "https://example.com"
    assert merged[0]["title"] == "Título traducido"


def test_text_looks_english_heavy_detects_english_sentence() -> None:
    assert _text_looks_english_heavy("Do not shrug the shoulders during the push.") is True


def teardown_function() -> None:
    get_rag_settings.cache_clear()
