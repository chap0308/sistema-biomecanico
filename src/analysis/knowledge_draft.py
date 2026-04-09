"""Lightweight second-layer analysis over retrieval-ready segments."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from src.analysis.draft_lineage import infer_analysis_metadata
from src.core.models import Segment, Source

BODY_REGION_KEYWORDS = {
    "foot": ["foot", "feet", "toe", "toes", "heel", "arch", "plantar", "ankle"],
    "ankle": ["ankle"],
    "scapula": ["scapula", "scapular", "shoulder blade", "winging"],
    "shoulder": ["shoulder", "triceps", "trap", "elbow"],
    "rib_cage": ["rib cage", "ribs", "chest wall"],
    "hip": ["hip", "pelvis", "glute", "glutes", "femur"],
    "neck": ["neck", "scm", "head", "cervical"],
}

PROBLEM_LAYER_KEYWORDS = {
    "mobility_restriction": ["stiff", "tight", "mobility", "range of motion", "restriction"],
    "pain": ["pain", "fasciitis", "hurt", "symptom"],
    "postural": ["posture", "rounded", "winging", "tilt", "compressed"],
    "motor_control": ["control", "compensation", "coordination", "stability"],
    "breathing": ["breathe", "breathing", "exhale", "inhale", "diaphragm"],
}

EXERCISE_TERMS = [
    "exercise",
    "drill",
    "stretch",
    "roll",
    "rolling",
    "extension",
    "hinge",
    "pull",
    "walk",
]

WARNING_TERMS = ["don't", "avoid", "stop", "without", "not", "mistake", "compensation"]
TEST_TERMS = ["test", "retest", "check", "see if", "feel if", "assessment"]
CUE_TERMS = ["keep", "start", "maintain", "feel", "gently", "slowly", "relax", "make sure"]


def analyze_level1_result_file(input_path: str | Path) -> dict[str, Any]:
    """Load one Level 1 JSON result and convert it into a lightweight knowledge draft."""
    payload = json.loads(Path(input_path).read_text(encoding="utf-8"))
    source = Source.model_validate(payload["source"])
    segments = [Segment.model_validate(item) for item in payload["segments"]]
    return build_knowledge_draft(
        source=source,
        segments=segments,
        analysis_report=payload.get("analysis_report", {}),
        source_payload=payload,
    )


def build_knowledge_draft(
    *,
    source: Source,
    segments: list[Segment],
    analysis_report: dict[str, Any] | None = None,
    source_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a local lightweight knowledge draft from source segments."""
    full_text = " ".join(segment.transcript for segment in segments if segment.transcript).strip()
    full_ocr = " ".join(segment.ocr_text for segment in segments if segment.ocr_text).strip()
    sentences = _split_sentences(full_text)

    body_regions = _infer_body_regions(source, full_text)
    problem_layers = _infer_problem_layers(full_text)
    exercises = _extract_exercises(source, sentences)
    tests = _extract_sentences(sentences, TEST_TERMS)
    advice = _extract_sentences(sentences, CUE_TERMS)
    warnings = _extract_sentences(sentences, WARNING_TERMS)
    problem_statements = _extract_problem_statements(sentences)
    habits_or_contexts = _extract_habits_or_contexts(sentences)
    visual_points = _build_visual_points(segments)
    topics = _aggregate_topics(segments, body_regions)
    tags = _aggregate_keywords(segments, source.tags)
    content_kind = _infer_content_kind(exercises, problem_statements, warnings)
    usefulness = "useful" if segments else "not_useful"

    knowledge_units = [_segment_to_knowledge_unit(segment) for segment in segments if segment.transcript or segment.ocr_text]

    analysis_origin = "local_level1_plus_light_analysis"
    provider, quality = infer_analysis_metadata(analysis_origin)
    return {
        "source_url": source.uri,
        "source_title_hint": source.title or "",
        "analysis_origin": analysis_origin,
        "analysis_provider": provider,
        "analysis_quality": quality,
        "is_active": True,
        "supersedes_draft_id": None,
        "primary_summary": _summarize_source(source, segments, exercises, problem_statements),
        "classification": {
            "usefulness": usefulness,
            "usefulness_reason": "Segments contain structured transcript, OCR, and retrieval-ready evidence."
            if usefulness == "useful"
            else "No useful segment evidence was extracted.",
            "exclusion_reason": None if usefulness == "useful" else "empty_segments",
            "content_kind": content_kind,
            "body_regions": body_regions,
            "problem_layers": problem_layers,
            "suitable_for_protocol_database": bool(exercises),
            "suitable_for_concept_knowledge_base": bool(segments),
            "suitable_for_recommendation_mapping": bool(exercises or problem_statements),
            "contains_visual_execution_detail": any(bool(segment.frame_refs or segment.ocr_text) for segment in segments),
            "confidence": _infer_confidence(analysis_report or {}, segments),
        },
        "searchable_topics": topics,
        "searchable_tags": tags,
        "problem_statements": problem_statements,
        "habits_or_contexts": habits_or_contexts,
        "key_visual_points": visual_points,
        "tests_mentioned": tests,
        "exercises_mentioned": exercises,
        "advice_mentioned": advice,
        "warnings_or_limitations": warnings,
        "knowledge_units": knowledge_units,
        "analysis_report": analysis_report or {},
        "source_artifacts": {
            "segment_count": len(segments),
            "asset_count": len((source_payload or {}).get("assets", [])),
        },
    }


def _split_sentences(text: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return []
    parts = re.split(r"(?<=[.!?])\s+", cleaned)
    return [part.strip() for part in parts if part.strip()]


def _infer_body_regions(source: Source, text: str) -> list[str]:
    lowered = text.lower()
    regions = list(source.tags)
    for region, keywords in BODY_REGION_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            regions.append(region)
    return list(dict.fromkeys(regions))


def _infer_problem_layers(text: str) -> list[str]:
    lowered = text.lower()
    layers = [layer for layer, keywords in PROBLEM_LAYER_KEYWORDS.items() if any(keyword in lowered for keyword in keywords)]
    return layers or ["movement_reeducation"]


def _extract_sentences(sentences: list[str], terms: list[str]) -> list[str]:
    extracted = [sentence for sentence in sentences if any(term in sentence.lower() for term in terms)]
    return extracted[:8]


def _extract_problem_statements(sentences: list[str]) -> list[str]:
    markers = ["problem", "pain", "issue", "limited", "tight", "winging", "rounded", "fasciitis", "can't", "incorrect"]
    return [sentence for sentence in sentences if any(marker in sentence.lower() for marker in markers)][:8]


def _extract_habits_or_contexts(sentences: list[str]) -> list[str]:
    markers = ["most people", "usually", "habit", "when you", "people with", "trying to", "sedentary"]
    return [sentence for sentence in sentences if any(marker in sentence.lower() for marker in markers)][:6]


def _extract_exercises(source: Source, sentences: list[str]) -> list[str]:
    found: list[str] = []
    title = (source.title or "").strip()
    if any(term in title.lower() for term in EXERCISE_TERMS):
        found.append(title)

    for sentence in sentences:
        lowered = sentence.lower()
        if any(term in lowered for term in EXERCISE_TERMS):
            found.append(_normalize_exercise_phrase(sentence))

    return list(dict.fromkeys(item for item in found if item))[:8]


def _normalize_exercise_phrase(sentence: str) -> str:
    cleaned = sentence.strip()
    if len(cleaned) > 120:
        cleaned = cleaned[:120].rsplit(" ", 1)[0]
    return cleaned


def _build_visual_points(segments: list[Segment]) -> list[str]:
    points: list[str] = []
    for segment in segments:
        if segment.ocr_text:
            points.append(f"OCR near {segment.start_sec:.1f}s: {segment.ocr_text[:80]}")
        elif segment.frame_refs:
            points.append(f"Representative frame at {segment.frame_refs[0].sec:.1f}s")
    return points[:10]


def _aggregate_topics(segments: list[Segment], body_regions: list[str]) -> list[str]:
    topics = list(body_regions)
    for segment in segments:
        topics.extend(segment.topics)
    return list(dict.fromkeys(topic for topic in topics if topic))[:12]


def _aggregate_keywords(segments: list[Segment], source_tags: list[str]) -> list[str]:
    counter: Counter[str] = Counter()
    for tag in source_tags:
        if tag:
            counter[tag.lower()] += 2
    for segment in segments:
        for keyword in segment.keywords:
            if keyword:
                counter[keyword.lower()] += 1
    return [keyword for keyword, _ in counter.most_common(12)]


def _infer_content_kind(exercises: list[str], problem_statements: list[str], warnings: list[str]) -> str:
    if exercises and problem_statements:
        return "corrective_protocol"
    if exercises and warnings:
        return "exercise_optimization"
    if problem_statements:
        return "informational_concept"
    return "mixed"


def _infer_confidence(analysis_report: dict[str, Any], segments: list[Segment]) -> str:
    if not segments:
        return "low"
    if analysis_report.get("transcript_status") == "ok" and len(segments) >= 5:
        return "medium"
    return "low"


def _segment_to_knowledge_unit(segment: Segment) -> dict[str, Any]:
    text = segment.transcript.strip()
    lowered = text.lower()
    unit_type = "educational_point"
    if any(term in lowered for term in EXERCISE_TERMS):
        unit_type = "corrective_exercise"
    elif any(term in lowered for term in WARNING_TERMS):
        unit_type = "compensation_pattern"
    elif any(term in lowered for term in TEST_TERMS):
        unit_type = "assessment"

    execution_steps = _extract_execution_steps(text) if unit_type == "corrective_exercise" else []
    cues = [sentence for sentence in _split_sentences(text) if any(term in sentence.lower() for term in CUE_TERMS)][:5]
    errors = [sentence for sentence in _split_sentences(text) if any(term in sentence.lower() for term in WARNING_TERMS)][:5]

    return {
        "unit_type": unit_type,
        "title": _make_unit_title(segment, unit_type),
        "summary": segment.segment_summary,
        "observable_signs": [segment.ocr_text] if segment.ocr_text else [],
        "mechanisms": [text] if unit_type == "educational_point" and text else [],
        "execution_steps": execution_steps,
        "cues": cues,
        "breathing_cues": [sentence for sentence in _split_sentences(text) if "breathe" in sentence.lower() or "exhale" in sentence.lower()],
        "errors_to_avoid": errors,
        "when_useful": [],
        "when_not_useful": [],
        "retest": [sentence for sentence in _split_sentences(text) if "feel" in sentence.lower() or "better" in sentence.lower()][:3],
        "advice": cues[:3],
        "timestamps": [_format_ts(segment.start_sec), _format_ts(segment.end_sec)],
    }


def _make_unit_title(segment: Segment, unit_type: str) -> str:
    base = segment.segment_summary.replace("Segment ", "").strip()
    return f"{unit_type.replace('_', ' ').title()}: {base[:90]}"


def _extract_execution_steps(text: str) -> list[str]:
    candidates = re.split(r"\b(?:then|and then|start|keep|slowly|gently|now)\b", text, flags=re.IGNORECASE)
    steps = [candidate.strip(" ,.-") for candidate in candidates if len(candidate.strip()) > 20]
    return steps[:6]


def _format_ts(seconds: float) -> str:
    total = max(0, int(seconds))
    minutes, sec = divmod(total, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{sec:02d}"
    return f"{minutes:02d}:{sec:02d}"


def _summarize_source(source: Source, segments: list[Segment], exercises: list[str], problem_statements: list[str]) -> str:
    if segments:
        first = segments[0].transcript[:160].strip()
        if exercises:
            return f"{source.title or source.uri} explains a movement problem and demonstrates corrective actions such as {exercises[0]}. {first}"
        if problem_statements:
            return f"{source.title or source.uri} describes movement issues including {problem_statements[0]}"
        return f"{source.title or source.uri} contains {len(segments)} retrieval-ready segments for RAG."
    return f"{source.title or source.uri} could not be analyzed into useful segments."
