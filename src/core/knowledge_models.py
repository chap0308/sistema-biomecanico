"""Normalized models for second-layer knowledge drafts and units."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class KnowledgeDraftClassification(BaseModel):
    usefulness: str = "useful"
    usefulness_reason: str = ""
    exclusion_reason: str | None = None
    content_kind: str = "mixed"
    body_regions: list[str] = Field(default_factory=list)
    problem_layers: list[str] = Field(default_factory=list)
    suitable_for_protocol_database: bool = False
    suitable_for_concept_knowledge_base: bool = True
    suitable_for_recommendation_mapping: bool = False
    contains_visual_execution_detail: bool = False
    confidence: str = "medium"


class KnowledgeDraftUnit(BaseModel):
    unit_type: str = "educational_point"
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


class KnowledgeDraftSourceArtifacts(BaseModel):
    segment_count: int = 0
    asset_count: int = 0


class KnowledgeDraft(BaseModel):
    source_url: str
    source_title_hint: str = ""
    analysis_origin: str = "unknown"
    analysis_provider: str = "unknown"
    analysis_quality: str = "standard"
    is_active: bool = True
    supersedes_draft_id: str | None = None
    primary_summary: str = ""
    classification: KnowledgeDraftClassification = Field(default_factory=KnowledgeDraftClassification)
    searchable_topics: list[str] = Field(default_factory=list)
    searchable_tags: list[str] = Field(default_factory=list)
    problem_statements: list[str] = Field(default_factory=list)
    habits_or_contexts: list[str] = Field(default_factory=list)
    key_visual_points: list[str] = Field(default_factory=list)
    tests_mentioned: list[str] = Field(default_factory=list)
    exercises_mentioned: list[str] = Field(default_factory=list)
    advice_mentioned: list[str] = Field(default_factory=list)
    warnings_or_limitations: list[str] = Field(default_factory=list)
    knowledge_units: list[KnowledgeDraftUnit] = Field(default_factory=list)
    analysis_report: dict[str, Any] = Field(default_factory=dict)
    source_artifacts: KnowledgeDraftSourceArtifacts = Field(default_factory=KnowledgeDraftSourceArtifacts)


KnowledgeUnitCategory = Literal["knowledge_unit"]
