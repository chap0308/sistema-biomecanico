"""Transformation helpers for importing video knowledge JSON into Supabase/Postgres."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from video.youtube_shorts import extract_video_id

DEFAULT_DATASET_NAME = "movement_knowledge_base"
DEFAULT_ANALYSIS_SCHEMA_VERSION = "gemini_video_analysis_v1"
DEFAULT_VISUAL_VALIDATION_LEVEL = "ai_visual_review"
DEFAULT_REVIEW_STATUS = "draft"


@dataclass(slots=True)
class SourceVideoRecord:
    external_video_id: str
    source_type: str
    source_url: str
    canonical_url: str
    title_hint: str
    creator_name: str | None
    channel_url: str | None
    source_metadata: dict[str, Any]


@dataclass(slots=True)
class AnalysisRecord:
    dataset_name: str
    analysis_origin: str
    source_file_path: str
    source_file_name: str
    content_sha256: str
    model_name: str | None
    analysis_schema_version: str
    prompt_version: str | None
    primary_summary: str
    usefulness: str
    usefulness_reason: str
    exclusion_reason: str | None
    content_kind: str
    confidence: str
    suitable_for_protocol_database: bool
    suitable_for_concept_knowledge_base: bool
    suitable_for_recommendation_mapping: bool
    contains_visual_execution_detail: bool
    visual_validation_level: str
    review_status: str
    body_regions: list[str]
    problem_layers: list[str]
    searchable_topics: list[str]
    searchable_tags: list[str]
    problem_statements: list[str]
    habits_or_contexts: list[str]
    key_visual_points: list[str]
    tests_mentioned: list[str]
    exercises_mentioned: list[str]
    advice_mentioned: list[str]
    warnings_or_limitations: list[str]
    raw_payload: dict[str, Any]
    normalized_payload: dict[str, Any]
    extra_payload: dict[str, Any]


@dataclass(slots=True)
class KnowledgeUnitRecord:
    ordinal: int
    unit_type: str
    title: str
    summary: str
    observable_signs: list[str]
    mechanisms: list[str]
    execution_steps: list[str]
    cues: list[str]
    breathing_cues: list[str]
    errors_to_avoid: list[str]
    when_useful: list[str]
    when_not_useful: list[str]
    retest: list[str]
    advice: list[str]
    timestamps: list[str]
    extra_payload: dict[str, Any]


@dataclass(slots=True)
class ParsedKnowledgeDocument:
    source_video: SourceVideoRecord
    analysis: AnalysisRecord
    knowledge_units: list[KnowledgeUnitRecord]
    taxonomy_entries: list[tuple[str, str]]


def load_env_value(key: str) -> str | None:
    """Load a setting from the environment or local env files."""
    value = os.getenv(key)
    if value:
        return value.strip().strip('"').strip("'")

    for candidate in (Path(".env"), Path(".env.example")):
        if not candidate.exists():
            continue
        for raw_line in candidate.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            env_key, env_value = line.split("=", 1)
            if env_key.strip() == key:
                return env_value.strip().strip('"').strip("'")
    return None


def get_database_url() -> str:
    """Resolve the Postgres connection URL for Supabase."""
    for key in ("SUPABASE_DB_URL", "DATABASE_URL", "POSTGRES_URL"):
        value = load_env_value(key)
        if value:
            return value
    raise RuntimeError("No database URL found in SUPABASE_DB_URL, DATABASE_URL, POSTGRES_URL, .env, or .env.example")


def is_gemini_analysis_document(payload: Any) -> bool:
    """Return True when the JSON object matches the Gemini analysis shape."""
    if not isinstance(payload, dict):
        return False
    required_keys = {"source_url", "primary_summary", "classification", "knowledge_units"}
    if not required_keys.issubset(payload):
        return False
    classification = payload.get("classification")
    return isinstance(classification, dict) and "content_kind" in classification and "usefulness" in classification


def should_skip_json_file(path: Path) -> bool:
    """Filter out aggregate and helper JSON files that are not single analysis records."""
    name = path.name.lower()
    if name.startswith("aggregate_"):
        return True
    if name in {"aggregate.json", "run_summary.json", "latest_scrape.json", "pending_top20.json", "pending_21_30.json", "conorharris_state.json", "video_knowledge_registry.json"}:
        return True
    return False


def compute_content_sha256(payload: dict[str, Any]) -> str:
    """Hash the semantic JSON content so exact duplicates are not imported twice."""
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def normalize_string_list(values: Any) -> list[str]:
    """Normalize list-like text content into a unique, ordered list of non-empty strings."""
    if not isinstance(values, list):
        return []
    normalized: list[str] = []
    seen: set[str] = set()
    for raw_value in values:
        if raw_value is None:
            continue
        value = str(raw_value).strip()
        if not value:
            continue
        dedupe_key = value.casefold()
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        normalized.append(value)
    return normalized


def infer_source_type(source_url: str) -> str:
    """Infer a broad source type from the source URL."""
    parsed = urlparse(source_url)
    if "youtube.com" in parsed.netloc and "/shorts/" in parsed.path:
        return "youtube_short"
    if "youtube.com" in parsed.netloc:
        return "youtube_video"
    return "external_video"


def infer_external_video_id(source_url: str) -> str:
    """Extract a stable source identifier from the URL or fall back to a URL hash."""
    video_id = extract_video_id(source_url)
    if video_id:
        return video_id
    return hashlib.sha256(source_url.encode("utf-8")).hexdigest()[:24]


def infer_channel_url(source_url: str) -> str | None:
    """Best-effort channel URL inference for known sources."""
    parsed = urlparse(source_url)
    if "youtube.com" not in parsed.netloc:
        return None
    return "https://www.youtube.com"


def build_source_video_record(payload: dict[str, Any]) -> SourceVideoRecord:
    """Extract source-level metadata shared across analysis versions."""
    source_url = str(payload.get("source_url", "")).strip()
    return SourceVideoRecord(
        external_video_id=infer_external_video_id(source_url),
        source_type=infer_source_type(source_url),
        source_url=source_url,
        canonical_url=source_url,
        title_hint=str(payload.get("source_title_hint", "")).strip(),
        creator_name=None,
        channel_url=infer_channel_url(source_url),
        source_metadata={},
    )


def build_analysis_record(payload: dict[str, Any], *, source_file_path: Path, dataset_name: str = DEFAULT_DATASET_NAME) -> AnalysisRecord:
    """Build the normalized analysis row for a Gemini JSON document."""
    classification = payload.get("classification", {})
    raw_payload = json.loads(json.dumps(payload))
    normalized_payload = {
        "source_url": payload.get("source_url", ""),
        "primary_summary": payload.get("primary_summary", ""),
        "classification": classification,
        "searchable_topics": normalize_string_list(payload.get("searchable_topics", [])),
        "searchable_tags": normalize_string_list(payload.get("searchable_tags", [])),
        "problem_statements": normalize_string_list(payload.get("problem_statements", [])),
        "habits_or_contexts": normalize_string_list(payload.get("habits_or_contexts", [])),
        "key_visual_points": normalize_string_list(payload.get("key_visual_points", [])),
        "tests_mentioned": normalize_string_list(payload.get("tests_mentioned", [])),
        "exercises_mentioned": normalize_string_list(payload.get("exercises_mentioned", [])),
        "advice_mentioned": normalize_string_list(payload.get("advice_mentioned", [])),
        "warnings_or_limitations": normalize_string_list(payload.get("warnings_or_limitations", [])),
    }
    return AnalysisRecord(
        dataset_name=dataset_name,
        analysis_origin="gemini_video_analysis",
        source_file_path=str(source_file_path),
        source_file_name=source_file_path.name,
        content_sha256=compute_content_sha256(raw_payload),
        model_name=None,
        analysis_schema_version=DEFAULT_ANALYSIS_SCHEMA_VERSION,
        prompt_version=None,
        primary_summary=str(payload.get("primary_summary", "")).strip(),
        usefulness=str(classification.get("usefulness", "")).strip(),
        usefulness_reason=str(classification.get("usefulness_reason", "")).strip(),
        exclusion_reason=_optional_str(classification.get("exclusion_reason")),
        content_kind=str(classification.get("content_kind", "")).strip(),
        confidence=str(classification.get("confidence", "")).strip(),
        suitable_for_protocol_database=bool(classification.get("suitable_for_protocol_database", False)),
        suitable_for_concept_knowledge_base=bool(classification.get("suitable_for_concept_knowledge_base", False)),
        suitable_for_recommendation_mapping=bool(classification.get("suitable_for_recommendation_mapping", False)),
        contains_visual_execution_detail=bool(classification.get("contains_visual_execution_detail", False)),
        visual_validation_level=DEFAULT_VISUAL_VALIDATION_LEVEL,
        review_status=DEFAULT_REVIEW_STATUS,
        body_regions=normalize_string_list(classification.get("body_regions", [])),
        problem_layers=normalize_string_list(classification.get("problem_layers", [])),
        searchable_topics=normalize_string_list(payload.get("searchable_topics", [])),
        searchable_tags=normalize_string_list(payload.get("searchable_tags", [])),
        problem_statements=normalize_string_list(payload.get("problem_statements", [])),
        habits_or_contexts=normalize_string_list(payload.get("habits_or_contexts", [])),
        key_visual_points=normalize_string_list(payload.get("key_visual_points", [])),
        tests_mentioned=normalize_string_list(payload.get("tests_mentioned", [])),
        exercises_mentioned=normalize_string_list(payload.get("exercises_mentioned", [])),
        advice_mentioned=normalize_string_list(payload.get("advice_mentioned", [])),
        warnings_or_limitations=normalize_string_list(payload.get("warnings_or_limitations", [])),
        raw_payload=raw_payload,
        normalized_payload=normalized_payload,
        extra_payload={},
    )


def build_knowledge_units(payload: dict[str, Any]) -> list[KnowledgeUnitRecord]:
    """Normalize knowledge units into child rows."""
    records: list[KnowledgeUnitRecord] = []
    for ordinal, unit in enumerate(payload.get("knowledge_units", []), start=1):
        if not isinstance(unit, dict):
            continue
        records.append(
            KnowledgeUnitRecord(
                ordinal=ordinal,
                unit_type=str(unit.get("unit_type", "")).strip(),
                title=str(unit.get("title", "")).strip(),
                summary=str(unit.get("summary", "")).strip(),
                observable_signs=normalize_string_list(unit.get("observable_signs", [])),
                mechanisms=normalize_string_list(unit.get("mechanisms", [])),
                execution_steps=normalize_string_list(unit.get("execution_steps", [])),
                cues=normalize_string_list(unit.get("cues", [])),
                breathing_cues=normalize_string_list(unit.get("breathing_cues", [])),
                errors_to_avoid=normalize_string_list(unit.get("errors_to_avoid", [])),
                when_useful=normalize_string_list(unit.get("when_useful", [])),
                when_not_useful=normalize_string_list(unit.get("when_not_useful", [])),
                retest=normalize_string_list(unit.get("retest", [])),
                advice=normalize_string_list(unit.get("advice", [])),
                timestamps=normalize_string_list(unit.get("timestamps", [])),
                extra_payload={},
            )
        )
    return records


def build_taxonomy_entries(payload: dict[str, Any], units: list[KnowledgeUnitRecord]) -> list[tuple[str, str]]:
    """Capture observed taxonomy values so new labels are tracked without schema changes."""
    classification = payload.get("classification", {})
    entries: list[tuple[str, str]] = []
    entries.extend(_taxonomy_from_list("body_region", classification.get("body_regions", [])))
    entries.extend(_taxonomy_from_list("problem_layer", classification.get("problem_layers", [])))
    entries.extend(_taxonomy_from_list("searchable_tag", payload.get("searchable_tags", [])))
    entries.extend(_taxonomy_from_list("searchable_topic", payload.get("searchable_topics", [])))
    entries.extend(_taxonomy_from_list("exercise_name", payload.get("exercises_mentioned", [])))
    entries.extend(_taxonomy_from_list("test_name", payload.get("tests_mentioned", [])))
    entries.extend(_taxonomy_from_list("unit_type", [unit.unit_type for unit in units]))
    entries.extend(_taxonomy_from_list("content_kind", [classification.get("content_kind", "")]))
    entries.extend(_taxonomy_from_list("usefulness", [classification.get("usefulness", "")]))
    return entries


def parse_gemini_analysis_file(path: Path, *, dataset_name: str = DEFAULT_DATASET_NAME) -> ParsedKnowledgeDocument:
    """Parse a Gemini analysis JSON file into source, analysis and child records."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not is_gemini_analysis_document(payload):
        raise ValueError(f"{path} is not a Gemini knowledge analysis JSON file.")
    source_video = build_source_video_record(payload)
    analysis = build_analysis_record(payload, source_file_path=path, dataset_name=dataset_name)
    knowledge_units = build_knowledge_units(payload)
    taxonomy_entries = build_taxonomy_entries(payload, knowledge_units)
    return ParsedKnowledgeDocument(
        source_video=source_video,
        analysis=analysis,
        knowledge_units=knowledge_units,
        taxonomy_entries=taxonomy_entries,
    )


def discover_gemini_analysis_files(root: Path) -> list[Path]:
    """Find importable per-video JSON analysis files under the given root."""
    paths: list[Path] = []
    for path in sorted(root.rglob("*.json")):
        if should_skip_json_file(path):
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if is_gemini_analysis_document(payload):
            paths.append(path)
    return paths


def _taxonomy_from_list(namespace: str, values: Any) -> list[tuple[str, str]]:
    return [(namespace, value) for value in normalize_string_list(values)]


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
