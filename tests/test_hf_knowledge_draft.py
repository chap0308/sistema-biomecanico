"""Tests for Hugging Face structured second-layer analysis."""

from __future__ import annotations

import json
from typing import Any

from src.analysis.hf_knowledge_draft import build_knowledge_draft_with_hf
from src.chunking.segment_builder import build_segment
from src.core.models import Source
from src.core.settings import get_rag_settings


def _make_source_and_segments() -> tuple[Source, list[Any]]:
    source = Source(
        source_type="youtube",
        uri="https://www.youtube.com/watch?v=abc123",
        title="Foot Drill",
        channel_or_author="Conor Harris",
        language_hint="en",
        tags=["foot", "ankle"],
        duration_sec=30.0,
    )
    segments = [
        build_segment(
            source_id=source.source_id or "",
            segment_index=1,
            start_sec=0.0,
            end_sec=8.0,
            transcript="Most people with plantar fasciitis roll randomly and keep having problems with their feet.",
            ocr_text="PLANTAR FASCIITIS",
            topics=["foot"],
            keywords=["fasciitis", "foot"],
            payload={"source_type": "youtube"},
        ),
        build_segment(
            source_id=source.source_id or "",
            segment_index=2,
            start_sec=8.0,
            end_sec=18.0,
            transcript="Start with the lacrosse ball under the big toe and slowly roll toward the heel.",
            topics=["drill"],
            keywords=["lacrosse", "roll"],
            payload={"source_type": "youtube"},
        ),
    ]
    return source, segments


def test_build_knowledge_draft_with_hf_falls_back_without_token(monkeypatch: Any) -> None:
    source, segments = _make_source_and_segments()
    monkeypatch.setenv("HF_TOKEN", "")
    get_rag_settings.cache_clear()

    draft = build_knowledge_draft_with_hf(
        source=source,
        segments=segments,
        analysis_report={"transcript_status": "ok"},
        source_payload={"assets": []},
        fallback_to_heuristic=True,
    )

    assert draft["classification"]["usefulness"] == "useful"
    assert draft["analysis_origin"] == "local_level1_plus_hf_unavailable_fallback"


def test_build_knowledge_draft_with_hf_parses_structured_response(monkeypatch: Any) -> None:
    source, segments = _make_source_and_segments()
    monkeypatch.setenv("HF_TOKEN", "test-token")
    get_rag_settings.cache_clear()

    response_payload = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "source_url": source.uri,
                            "source_title_hint": source.title,
                            "analysis_origin": "hf_structured_analysis",
                            "primary_summary": "The video explains a foot drill and how to perform it.",
                            "classification": {
                                "usefulness": "useful",
                                "usefulness_reason": "The evidence describes a concrete corrective drill.",
                                "exclusion_reason": None,
                                "content_kind": "corrective_protocol",
                                "body_regions": ["foot", "ankle"],
                                "problem_layers": ["mobility_restriction"],
                                "suitable_for_protocol_database": True,
                                "suitable_for_concept_knowledge_base": True,
                                "suitable_for_recommendation_mapping": True,
                                "contains_visual_execution_detail": True,
                                "confidence": "medium",
                            },
                            "searchable_topics": ["foot", "ankle", "mobility"],
                            "searchable_tags": ["foot", "ankle", "lacrosse ball"],
                            "problem_statements": ["People with plantar fasciitis often keep having foot problems."],
                            "habits_or_contexts": ["Most people roll randomly without a focused drill."],
                            "key_visual_points": ["The lacrosse ball starts under the big toe."],
                            "tests_mentioned": [],
                            "exercises_mentioned": ["Lacrosse ball foot roll"],
                            "advice_mentioned": ["Roll from the big toe toward the heel."],
                            "warnings_or_limitations": ["Do not roll randomly."],
                            "knowledge_units": [
                                {
                                    "unit_type": "corrective_exercise",
                                    "title": "Lacrosse ball foot roll",
                                    "summary": "A simple foot drill for plantar fascia and foot contact.",
                                    "observable_signs": ["Plantar fasciitis", "Poor foot contact"],
                                    "mechanisms": [],
                                    "execution_steps": [
                                        "Place the lacrosse ball under the big toe.",
                                        "Slowly roll toward the heel.",
                                    ],
                                    "cues": ["Keep the foot relaxed."],
                                    "breathing_cues": [],
                                    "errors_to_avoid": ["Do not roll randomly."],
                                    "when_useful": ["Useful when the feet feel stiff or symptomatic."],
                                    "when_not_useful": [],
                                    "retest": [],
                                    "advice": ["Move slowly."],
                                    "timestamps": ["00:00", "00:18"],
                                }
                            ],
                            "analysis_report": {},
                            "source_artifacts": {"segment_count": 2, "asset_count": 0},
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
        assert kwargs["headers"]["Authorization"] == "Bearer test-token"
        assert kwargs["json"]["model"] == "openai/gpt-oss-120b"
        assert kwargs["json"]["response_format"]["type"] == "json_schema"
        return DummyResponse()

    monkeypatch.setattr("src.analysis.hf_knowledge_draft.requests.post", fake_post)

    draft = build_knowledge_draft_with_hf(
        source=source,
        segments=segments,
        analysis_report={"transcript_status": "ok"},
        source_payload={"assets": []},
        fallback_to_heuristic=False,
    )

    assert draft["analysis_origin"] == "hf_structured_analysis:openai/gpt-oss-120b"
    assert draft["classification"]["content_kind"] == "corrective_protocol"
    assert draft["knowledge_units"][0]["unit_type"] == "corrective_exercise"
    get_rag_settings.cache_clear()


def test_build_knowledge_draft_with_hf_retries_with_json_object(monkeypatch: Any) -> None:
    source, segments = _make_source_and_segments()
    monkeypatch.setenv("HF_TOKEN", "test-token")
    get_rag_settings.cache_clear()

    response_payload = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "source_url": source.uri,
                            "source_title_hint": source.title,
                            "analysis_origin": "hf_structured_analysis",
                            "primary_summary": "The video explains a foot drill and how to perform it.",
                            "classification": {
                                "usefulness": "useful",
                                "usefulness_reason": "The evidence describes a concrete corrective drill.",
                                "exclusion_reason": None,
                                "content_kind": "corrective_protocol",
                                "body_regions": ["foot", "ankle"],
                                "problem_layers": ["mobility_restriction"],
                                "suitable_for_protocol_database": True,
                                "suitable_for_concept_knowledge_base": True,
                                "suitable_for_recommendation_mapping": True,
                                "contains_visual_execution_detail": True,
                                "confidence": "medium",
                            },
                            "searchable_topics": ["foot"],
                            "searchable_tags": ["foot"],
                            "problem_statements": [],
                            "habits_or_contexts": [],
                            "key_visual_points": [],
                            "tests_mentioned": [],
                            "exercises_mentioned": ["Lacrosse ball foot roll"],
                            "advice_mentioned": [],
                            "warnings_or_limitations": [],
                            "knowledge_units": [],
                            "analysis_report": {},
                            "source_artifacts": {"segment_count": 2, "asset_count": 0},
                        }
                    )
                }
            }
        ]
    }

    class DummyErrorResponse:
        status_code = 400
        text = '{"error":{"message":"This model does not support response format `json_schema`","param":"response_format"}}'

    class FailingThenPassingResponse:
        def __init__(self, should_fail: bool) -> None:
            self.should_fail = should_fail

        def raise_for_status(self) -> None:
            if self.should_fail:
                import requests

                raise requests.HTTPError("bad request", response=DummyErrorResponse())

        def json(self) -> dict[str, Any]:
            return response_payload

    calls: list[dict[str, Any]] = []

    def fake_post(*args: Any, **kwargs: Any) -> FailingThenPassingResponse:
        calls.append(kwargs["json"])
        if len(calls) == 1:
            return FailingThenPassingResponse(True)
        return FailingThenPassingResponse(False)

    monkeypatch.setattr("src.analysis.hf_knowledge_draft.requests.post", fake_post)

    draft = build_knowledge_draft_with_hf(
        source=source,
        segments=segments,
        analysis_report={"transcript_status": "ok"},
        source_payload={"assets": []},
        fallback_to_heuristic=False,
    )

    assert calls[0]["response_format"]["type"] == "json_schema"
    assert calls[1]["response_format"]["type"] == "json_object"
    assert draft["analysis_origin"] == "hf_structured_analysis:openai/gpt-oss-120b"
    get_rag_settings.cache_clear()
