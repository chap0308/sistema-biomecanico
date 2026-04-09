"""Normalize legacy Gemini video drafts into the current knowledge draft schema."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from src.analysis.draft_lineage import infer_analysis_metadata
from src.core.knowledge_models import KnowledgeDraft


def load_and_normalize_gemini_draft(path: str | Path) -> dict[str, Any]:
    """Load one Gemini draft JSON file and normalize it for current persistence/indexing."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return normalize_gemini_draft(payload)


def normalize_gemini_draft(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize a Gemini-produced draft into the current KnowledgeDraft-compatible shape."""
    analysis_origin = str(payload.get("analysis_origin", "gemini_video_analysis_import")).strip() or "gemini_video_analysis_import"
    analysis_provider, analysis_quality = infer_analysis_metadata(analysis_origin)
    normalized = {
        "source_url": str(payload.get("source_url", "")).strip(),
        "source_title_hint": str(payload.get("source_title_hint", "")).strip(),
        "analysis_origin": analysis_origin,
        "analysis_provider": analysis_provider,
        "analysis_quality": analysis_quality,
        "is_active": True,
        "supersedes_draft_id": None,
        "primary_summary": str(payload.get("primary_summary", "")).strip(),
        "classification": _normalize_classification(payload.get("classification", {})),
        "searchable_topics": _normalize_string_list(payload.get("searchable_topics", [])),
        "searchable_tags": _normalize_string_list(payload.get("searchable_tags", [])),
        "problem_statements": _normalize_string_list(payload.get("problem_statements", [])),
        "habits_or_contexts": _normalize_string_list(payload.get("habits_or_contexts", [])),
        "key_visual_points": _normalize_string_list(payload.get("key_visual_points", [])),
        "tests_mentioned": _normalize_string_list(payload.get("tests_mentioned", [])),
        "exercises_mentioned": _normalize_string_list(payload.get("exercises_mentioned", [])),
        "advice_mentioned": _normalize_string_list(payload.get("advice_mentioned", [])),
        "warnings_or_limitations": _normalize_string_list(payload.get("warnings_or_limitations", [])),
        "knowledge_units": [_normalize_unit(unit) for unit in payload.get("knowledge_units", []) if isinstance(unit, dict)],
        "analysis_report": _normalize_analysis_report(payload.get("analysis_report", {})),
        "source_artifacts": _normalize_source_artifacts(payload.get("source_artifacts", {})),
    }
    return KnowledgeDraft.model_validate(normalized).model_dump(mode="json")


def is_importable_gemini_draft(payload: dict[str, Any]) -> bool:
    """Return True when a JSON payload looks like one usable Gemini draft."""
    return isinstance(payload, dict) and bool(payload.get("source_url")) and isinstance(payload.get("knowledge_units"), list)


def _normalize_classification(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "usefulness": str(payload.get("usefulness", "useful")).strip().lower() or "useful",
        "usefulness_reason": str(payload.get("usefulness_reason", "")).strip(),
        "exclusion_reason": payload.get("exclusion_reason"),
        "content_kind": _snake(str(payload.get("content_kind", "mixed"))),
        "body_regions": [_snake(value) for value in _normalize_string_list(payload.get("body_regions", []))],
        "problem_layers": [_snake(value) for value in _normalize_string_list(payload.get("problem_layers", []))],
        "suitable_for_protocol_database": bool(payload.get("suitable_for_protocol_database", False)),
        "suitable_for_concept_knowledge_base": bool(payload.get("suitable_for_concept_knowledge_base", True)),
        "suitable_for_recommendation_mapping": bool(payload.get("suitable_for_recommendation_mapping", False)),
        "contains_visual_execution_detail": bool(payload.get("contains_visual_execution_detail", False)),
        "confidence": str(payload.get("confidence", "medium")).strip().lower() or "medium",
    }


def _normalize_unit(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "unit_type": _normalize_unit_type(str(payload.get("unit_type", "educational_point"))),
        "title": str(payload.get("title", "")).strip(),
        "summary": str(payload.get("summary", "")).strip(),
        "observable_signs": _normalize_string_list(payload.get("observable_signs", [])),
        "mechanisms": _normalize_string_list(payload.get("mechanisms", [])),
        "execution_steps": _normalize_string_list(payload.get("execution_steps", [])),
        "cues": _normalize_string_list(payload.get("cues", [])),
        "breathing_cues": _normalize_string_list(payload.get("breathing_cues", [])),
        "errors_to_avoid": _normalize_string_list(payload.get("errors_to_avoid", [])),
        "when_useful": _normalize_string_list(payload.get("when_useful", [])),
        "when_not_useful": _normalize_string_list(payload.get("when_not_useful", [])),
        "retest": _normalize_string_list(payload.get("retest", [])),
        "advice": _normalize_string_list(payload.get("advice", [])),
        "timestamps": _normalize_string_list(payload.get("timestamps", [])),
    }


def _normalize_analysis_report(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    return {str(key): value for key, value in payload.items()}


def _normalize_source_artifacts(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        payload = {}
    segment_count = payload.get("segment_count")
    asset_count = payload.get("asset_count")
    return {
        "segment_count": int(segment_count) if isinstance(segment_count, (int, float)) else 0,
        "asset_count": int(asset_count) if isinstance(asset_count, (int, float)) else 0,
    }


def _normalize_string_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value or "").strip()
        if not text:
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(text)
    return cleaned


def _normalize_unit_type(value: str) -> str:
    raw = _snake(value)
    mapping = {
        "mobility_drill": "corrective_exercise",
        "strength_drill": "corrective_exercise",
        "breathing_drill": "corrective_exercise",
        "technique_correction": "corrective_exercise",
        "functional_test": "assessment",
        "biomechanical_mechanism": "educational_point",
        "practical_advice": "educational_point",
        "deficiency_pattern": "compensation_pattern",
        "habit_pattern": "habit",
    }
    return mapping.get(raw, raw or "educational_point")


def _snake(value: str) -> str:
    text = value.strip().replace("-", " ").replace("/", " ").replace("&", " and ")
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", text)
    text = re.sub(r"[^a-zA-Z0-9]+", "_", text)
    return text.strip("_").lower()
