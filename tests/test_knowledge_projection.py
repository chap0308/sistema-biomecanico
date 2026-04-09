"""Tests for projecting knowledge drafts into persistence and retrieval records."""

from __future__ import annotations

from src.analysis.knowledge_projection import project_knowledge_draft
from src.analysis.draft_lineage import infer_analysis_metadata
from src.core.models import Source


def test_project_knowledge_draft_builds_retrieval_segments() -> None:
    source = Source(
        source_type="youtube",
        uri="https://www.youtube.com/watch?v=abc123",
        title="Foot Drill",
        channel_or_author="Conor Harris",
        language_hint="en",
        tags=["foot", "ankle"],
        duration_sec=30.0,
    )
    draft_payload = {
        "source_url": source.uri,
        "source_title_hint": source.title,
        "analysis_origin": "hf_structured_analysis:openai/gpt-oss-120b",
        "primary_summary": "Foot rolling protocol for plantar fasciitis and foot contact.",
        "classification": {
            "usefulness": "useful",
            "usefulness_reason": "Concrete protocol.",
            "content_kind": "corrective_protocol",
            "body_regions": ["foot", "ankle"],
            "problem_layers": ["mobility_restriction"],
            "suitable_for_protocol_database": True,
            "suitable_for_concept_knowledge_base": True,
            "suitable_for_recommendation_mapping": True,
            "contains_visual_execution_detail": True,
            "confidence": "medium",
        },
        "searchable_topics": ["foot rolling", "plantar fasciitis"],
        "searchable_tags": ["foot", "ankle", "lacrosse ball"],
        "problem_statements": ["Poor foot contacts can contribute to plantar fascia symptoms."],
        "habits_or_contexts": ["Random rolling is less effective."],
        "key_visual_points": ["Lacrosse ball under the big toe."],
        "tests_mentioned": [],
        "exercises_mentioned": ["Lacrosse ball foot roll"],
        "advice_mentioned": ["Keep the foot relaxed."],
        "warnings_or_limitations": ["Avoid excessive pressure."],
        "knowledge_units": [
            {
                "unit_type": "corrective_exercise",
                "title": "Lacrosse ball foot roll",
                "summary": "Simple drill to improve foot pressure distribution.",
                "observable_signs": ["Poor heel and toe contact"],
                "mechanisms": ["Improves foot arch mobility"],
                "execution_steps": ["Place the ball under the big toe.", "Roll toward the heel slowly."],
                "cues": ["Keep the foot relaxed."],
                "breathing_cues": [],
                "errors_to_avoid": ["Do not roll too hard."],
                "when_useful": ["Useful for plantar fascia irritation."],
                "when_not_useful": [],
                "retest": ["Check foot pressure after the drill."],
                "advice": ["Perform 15 slow reps."],
                "timestamps": ["00:00", "00:18"],
            }
        ],
        "analysis_report": {"transcript_status": "ok"},
        "source_artifacts": {"segment_count": 28, "asset_count": 27},
    }

    projection = project_knowledge_draft(source, draft_payload)

    assert projection.draft.classification.content_kind == "corrective_protocol"
    assert len(projection.derived_segments) == 1
    assert projection.derived_segments[0].payload["category"] == "knowledge_unit"
    assert "Foot rolling protocol" in projection.derived_segments[0].retrieval_text
    assert projection.content_sha256


def test_project_knowledge_draft_skips_qdrant_segments_for_not_useful() -> None:
    source = Source(
        source_type="youtube",
        uri="https://www.youtube.com/watch?v=promo123",
        title="Promo clip",
        language_hint="en",
    )
    draft_payload = {
        "source_url": source.uri,
        "source_title_hint": source.title,
        "analysis_origin": "gemini_video_analysis_import",
        "primary_summary": "Promotional clip.",
        "classification": {
            "usefulness": "not_useful",
            "usefulness_reason": "Promotional content only.",
            "exclusion_reason": "promotional",
            "content_kind": "promotional",
            "body_regions": [],
            "problem_layers": [],
            "suitable_for_protocol_database": False,
            "suitable_for_concept_knowledge_base": False,
            "suitable_for_recommendation_mapping": False,
            "contains_visual_execution_detail": False,
            "confidence": "medium",
        },
        "knowledge_units": [
            {
                "unit_type": "educational_point",
                "title": "Promo",
                "summary": "Should not be indexed.",
            }
        ],
    }

    projection = project_knowledge_draft(source, draft_payload)

    assert projection.draft.classification.usefulness == "not_useful"
    assert projection.derived_segments == []


def test_infer_analysis_metadata_prefers_fallback_before_model_name() -> None:
    provider, quality = infer_analysis_metadata("local_level1_plus_hf_error_fallback:openai/gpt-oss-120b")

    assert provider == "local_fallback"
    assert quality == "fallback"


def test_project_knowledge_draft_prunes_excess_units_for_short_video() -> None:
    source = Source(
        source_type="youtube",
        uri="https://www.youtube.com/watch?v=short123",
        title="Short shoulder clip",
        language_hint="en",
        duration_sec=45.0,
    )
    draft_payload = {
        "source_url": source.uri,
        "source_title_hint": source.title,
        "analysis_origin": "hf_structured_analysis:openai/gpt-oss-120b",
        "primary_summary": "Short clip with repeated unit extraction noise.",
        "classification": {
            "usefulness": "useful",
            "usefulness_reason": "Still useful after pruning.",
            "content_kind": "mixed",
            "body_regions": ["shoulder"],
            "problem_layers": ["mobility_restriction"],
        },
        "knowledge_units": [
            {
                "unit_type": "corrective_exercise",
                "title": f"Repeated unit {index}",
                "summary": "Same kind of unit from over-segmented draft.",
                "execution_steps": ["Step 1", "Step 1", "Step 2"],
                "timestamps": ["00:01", "00:01", "00:05"],
            }
            for index in range(1, 21)
        ],
    }

    projection = project_knowledge_draft(source, draft_payload)

    assert len(projection.draft.knowledge_units) == 12
    assert len(projection.derived_segments) == 12
    assert projection.draft.knowledge_units[0].execution_steps == ["Step 1", "Step 2"]
    assert projection.draft.knowledge_units[0].timestamps == ["00:01", "00:05"]


def test_project_knowledge_draft_infers_unit_specific_body_regions() -> None:
    source = Source(
        source_type="youtube",
        uri="https://www.youtube.com/watch?v=shoulder123",
        title="Shoulder clip",
        language_hint="en",
        duration_sec=40.0,
    )
    draft_payload = {
        "source_url": source.uri,
        "source_title_hint": source.title,
        "analysis_origin": "hf_structured_analysis:openai/gpt-oss-120b",
        "primary_summary": "Shoulder and ribcage drill.",
        "classification": {
            "usefulness": "useful",
            "content_kind": "mixed",
            "body_regions": ["upper trapezius", "shoulder", "rib cage", "thorax", "core"],
            "problem_layers": ["postural"],
        },
        "knowledge_units": [
            {
                "unit_type": "corrective_exercise",
                "title": "Scapular reach drill",
                "summary": "Improve scapular control and shoulder reach without shrugging.",
                "execution_steps": ["Reach forward gently."],
            }
        ],
    }

    projection = project_knowledge_draft(source, draft_payload)

    body_regions = projection.derived_segments[0].payload["body_regions"]
    assert "scapula" in body_regions
    assert "shoulder" in body_regions
    assert "core" not in body_regions
    assert projection.derived_segments[0].payload["primary_body_region"] == "scapula"
