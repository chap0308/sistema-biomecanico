"""Structured second-layer knowledge analysis using Hugging Face Inference Providers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

import requests
from pydantic import BaseModel, Field

from src.analysis.draft_lineage import infer_analysis_metadata
from src.analysis.knowledge_draft import build_knowledge_draft
from src.core.models import Segment, Source
from src.core.settings import get_rag_settings

HF_ROUTER_URL = "https://router.huggingface.co/v1/chat/completions"


class DraftClassification(BaseModel):
    """Structured top-level classification for one analyzed source."""

    usefulness: Literal["useful", "not_useful", "mixed"] = "useful"
    usefulness_reason: str = ""
    exclusion_reason: str | None = None
    content_kind: Literal[
        "corrective_protocol",
        "exercise_optimization",
        "informational_concept",
        "assessment",
        "mixed",
        "promotional",
        "testimonial",
    ] = "mixed"
    body_regions: list[str] = Field(default_factory=list)
    problem_layers: list[str] = Field(default_factory=list)
    suitable_for_protocol_database: bool = False
    suitable_for_concept_knowledge_base: bool = True
    suitable_for_recommendation_mapping: bool = False
    contains_visual_execution_detail: bool = False
    confidence: Literal["low", "medium", "high"] = "medium"


class DraftKnowledgeUnit(BaseModel):
    """One retrieval-friendly unit of knowledge derived from the evidence."""

    unit_type: Literal[
        "educational_point",
        "corrective_exercise",
        "compensation_pattern",
        "assessment",
        "habit",
        "warning",
    ] = "educational_point"
    title: str
    summary: str = ""
    observable_signs: list[str] = Field(default_factory=list)
    mechanisms: list[str] = Field(default_factory=list)
    execution_steps: list[str] = Field(default_factory=list)
    cues: list[str] = Field(default_factory=list)
    breathing_cues: list[str] = Field(default_factory=list)
    errors_to_avoid: list[str] = Field(default_factory=list)
    when_useful: list[str] = Field(default_factory=list)
    when_not_useful: list[str] = Field(default_factory=list)
    retest: list[str] = Field(default_factory=list)
    advice: list[str] = Field(default_factory=list)
    timestamps: list[str] = Field(default_factory=list)


class DraftSourceArtifacts(BaseModel):
    """Minimal artifact counts stored with the draft."""

    segment_count: int = 0
    asset_count: int = 0


class DraftAnalysisReport(BaseModel):
    """Known Level 1 pipeline status fields exposed to the structured analyzer."""

    audio_extracted: bool | None = None
    transcript_status: str | None = None
    scene_status: str | None = None
    frame_status: str | None = None
    ocr_status: str | None = None
    segment_alignment_status: str | None = None
    scene_count: int | None = None
    transcript_segment_count: int | None = None
    ocr_observation_count: int | None = None
    metadata_status: str | None = None
    download_status: str | None = None


class KnowledgeDraftStructured(BaseModel):
    """Normalized schema for structured knowledge generation."""

    source_url: str
    source_title_hint: str = ""
    analysis_origin: str = "hf_structured_analysis"
    primary_summary: str
    classification: DraftClassification
    searchable_topics: list[str] = Field(default_factory=list)
    searchable_tags: list[str] = Field(default_factory=list)
    problem_statements: list[str] = Field(default_factory=list)
    habits_or_contexts: list[str] = Field(default_factory=list)
    key_visual_points: list[str] = Field(default_factory=list)
    tests_mentioned: list[str] = Field(default_factory=list)
    exercises_mentioned: list[str] = Field(default_factory=list)
    advice_mentioned: list[str] = Field(default_factory=list)
    warnings_or_limitations: list[str] = Field(default_factory=list)
    knowledge_units: list[DraftKnowledgeUnit] = Field(default_factory=list)
    analysis_report: DraftAnalysisReport = Field(default_factory=DraftAnalysisReport)
    source_artifacts: DraftSourceArtifacts = Field(default_factory=DraftSourceArtifacts)


def analyze_level1_result_file_with_hf(
    input_path: str | Path,
    *,
    model: str | None = None,
    fallback_to_heuristic: bool = True,
) -> dict[str, Any]:
    """Load one Level 1 JSON result and convert it into a structured knowledge draft with HF."""
    payload = json.loads(Path(input_path).read_text(encoding="utf-8"))
    source = Source.model_validate(payload["source"])
    segments = [Segment.model_validate(item) for item in payload["segments"]]
    return build_knowledge_draft_with_hf(
        source=source,
        segments=segments,
        analysis_report=payload.get("analysis_report", {}),
        source_payload=payload,
        model=model,
        fallback_to_heuristic=fallback_to_heuristic,
    )


def build_knowledge_draft_with_hf(
    *,
    source: Source,
    segments: list[Segment],
    analysis_report: dict[str, Any] | None = None,
    source_payload: dict[str, Any] | None = None,
    model: str | None = None,
    fallback_to_heuristic: bool = True,
) -> dict[str, Any]:
    """Call Hugging Face structured generation to build a Gemini-like draft from Level 1 evidence."""
    settings = get_rag_settings()
    api_key = settings.hf_token
    target_model = model or settings.hf_analysis_model

    if not api_key:
        if fallback_to_heuristic:
            draft = build_knowledge_draft(
                source=source,
                segments=segments,
                analysis_report=analysis_report,
                source_payload=source_payload,
            )
            draft["analysis_origin"] = "local_level1_plus_hf_unavailable_fallback"
            return draft
        raise RuntimeError("HF_TOKEN is not configured.")

    evidence_payload = _build_evidence_payload(
        source=source,
        segments=segments,
        analysis_report=analysis_report or {},
        source_payload=source_payload or {},
        max_segments=settings.hf_max_segments,
    )
    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "movement_knowledge_draft",
            "schema": KnowledgeDraftStructured.model_json_schema(),
            "strict": True,
        },
    }
    messages = [
        {
            "role": "system",
            "content": (
                "You are a biomechanics educational knowledge extraction engine. "
                "Use only the provided evidence. Return strict JSON that matches the schema. "
                "Do not hallucinate anatomy, exercises, or warnings not supported by the evidence. "
                "Prefer concise, high-signal fields. Mark promotional or testimonial content as not useful."
            ),
        },
        {
            "role": "user",
            "content": (
                "Transform this extracted video evidence into structured knowledge for a biomechanics RAG system. "
                "Keep timestamps when useful. If evidence is incomplete, prefer shorter fields over speculation.\n\n"
                f"{json.dumps(evidence_payload, ensure_ascii=False)}"
            ),
        },
    ]

    try:
        raw = _call_hf_structured_chat(
            api_key=api_key,
            model=target_model,
            router_url=settings.hf_router_url,
            provider=settings.hf_provider,
            timeout_sec=settings.hf_timeout_sec,
            messages=messages,
            response_format=response_format,
        )
        parsed = KnowledgeDraftStructured.model_validate_json(raw)
        draft = parsed.model_dump(mode="json")
        draft["analysis_origin"] = f"hf_structured_analysis:{target_model}"
        provider, quality = infer_analysis_metadata(draft["analysis_origin"])
        draft["analysis_provider"] = provider
        draft["analysis_quality"] = quality
        draft["is_active"] = True
        draft["supersedes_draft_id"] = None
        draft["analysis_report"] = analysis_report or {}
        draft["source_artifacts"] = {
            "segment_count": len(segments),
            "asset_count": len((source_payload or {}).get("assets", [])),
        }
        return draft
    except Exception:
        if not fallback_to_heuristic:
            raise
        draft = build_knowledge_draft(
            source=source,
            segments=segments,
            analysis_report=analysis_report,
            source_payload=source_payload,
        )
        draft["analysis_origin"] = f"local_level1_plus_hf_error_fallback:{target_model}"
        provider, quality = infer_analysis_metadata(draft["analysis_origin"])
        draft["analysis_provider"] = provider
        draft["analysis_quality"] = quality
        draft["is_active"] = True
        draft["supersedes_draft_id"] = None
        return draft


def _build_evidence_payload(
    *,
    source: Source,
    segments: list[Segment],
    analysis_report: dict[str, Any],
    source_payload: dict[str, Any],
    max_segments: int,
) -> dict[str, Any]:
    selected_segments = segments[:max_segments]
    segment_records = []
    for segment in selected_segments:
        segment_records.append(
            {
                "segment_id": segment.segment_id,
                "start_sec": round(segment.start_sec, 2),
                "end_sec": round(segment.end_sec, 2),
                "summary": segment.segment_summary,
                "transcript": _truncate(segment.transcript, 800),
                "ocr_text": _truncate(segment.ocr_text, 240),
                "topics": segment.topics[:8],
                "keywords": segment.keywords[:10],
                "frame_timestamps": [round(frame.sec, 2) for frame in segment.frame_refs[:4]],
            }
        )

    return {
        "source": {
            "source_id": source.source_id,
            "source_type": source.source_type,
            "uri": source.uri,
            "title": source.title,
            "channel_or_author": source.channel_or_author,
            "duration_sec": source.duration_sec,
            "language_hint": source.language_hint,
            "tags": source.tags,
        },
        "analysis_report": analysis_report,
        "artifacts": {
            "asset_count": len(source_payload.get("assets", [])),
            "segment_count": len(segments),
            "selected_segment_count": len(selected_segments),
        },
        "segments": segment_records,
    }


def _call_hf_structured_chat(
    *,
    api_key: str,
    model: str,
    router_url: str,
    provider: str,
    timeout_sec: int,
    messages: list[dict[str, Any]],
    response_format: dict[str, Any],
) -> str:
    body: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "response_format": response_format,
    }
    return _post_hf_chat(
        api_key=api_key,
        router_url=router_url,
        provider=provider,
        timeout_sec=timeout_sec,
        body=body,
    )


def _post_hf_chat(
    *,
    api_key: str,
    router_url: str,
    provider: str,
    timeout_sec: int,
    body: dict[str, Any],
) -> str:
    extra_body: dict[str, Any] = {}
    if provider and provider != "auto":
        extra_body["provider"] = provider
    if extra_body:
        body["extra_body"] = extra_body

    response = requests.post(
        router_url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=body,
        timeout=timeout_sec,
    )
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        if _should_retry_with_json_object(exc, body):
            retry_body = dict(body)
            retry_body["response_format"] = {"type": "json_object"}
            return _post_hf_chat(
                api_key=api_key,
                router_url=router_url,
                provider=provider,
                timeout_sec=timeout_sec,
                body=retry_body,
            )
        raise
    payload = response.json()
    return payload["choices"][0]["message"]["content"]


def _should_retry_with_json_object(exc: requests.HTTPError, body: dict[str, Any]) -> bool:
    response = exc.response
    if response is None:
        return False
    if body.get("response_format", {}).get("type") != "json_schema":
        return False
    if response.status_code != 400:
        return False
    text = response.text.lower()
    return "does not support response format `json_schema`" in text or "param\":\"response_format" in text


def _truncate(value: str | None, max_len: int) -> str:
    if not value:
        return ""
    value = value.strip()
    if len(value) <= max_len:
        return value
    return value[: max_len - 1].rstrip() + "…"
