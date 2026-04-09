"""Tests for normalizing legacy Gemini draft JSON payloads."""

from src.analysis.gemini_draft_normalizer import normalize_gemini_draft


def test_normalize_gemini_draft_maps_types_and_regions() -> None:
    payload = {
        "source_url": "https://www.youtube.com/shorts/example123",
        "source_title_hint": "Foot drill",
        "primary_summary": "Video about foot rolling.",
        "classification": {
            "usefulness": "useful",
            "content_kind": "Mixed",
            "body_regions": ["Foot", "Thoracic Spine"],
            "problem_layers": ["Biomechanical Dysfunction", "Pain"],
            "suitable_for_protocol_database": True,
            "suitable_for_concept_knowledge_base": True,
            "suitable_for_recommendation_mapping": True,
            "contains_visual_execution_detail": True,
            "confidence": "High",
        },
        "knowledge_units": [
            {
                "unit_type": "mobility_drill",
                "title": "Lacrosse Ball Roll",
                "summary": "Drill summary",
                "execution_steps": ["Step 1", "Step 2"],
                "timestamps": ["00:10", "00:30"],
            },
            {
                "unit_type": "biomechanical_mechanism",
                "title": "Arch mechanics",
                "summary": "Mechanism summary",
            },
        ],
    }

    normalized = normalize_gemini_draft(payload)

    assert normalized["analysis_origin"] == "gemini_video_analysis_import"
    assert normalized["classification"]["content_kind"] == "mixed"
    assert normalized["classification"]["body_regions"] == ["foot", "thoracic_spine"]
    assert normalized["classification"]["problem_layers"] == ["biomechanical_dysfunction", "pain"]
    assert normalized["knowledge_units"][0]["unit_type"] == "corrective_exercise"
    assert normalized["knowledge_units"][1]["unit_type"] == "educational_point"
