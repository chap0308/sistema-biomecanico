"""Core Pydantic models for sources, assets, and retrieval segments."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from src.core.ids import stable_id

SourceType = Literal["youtube", "local_video", "public_video_url", "webpage"]
AssetKind = Literal["audio", "video", "frame", "transcript", "ocr", "metadata"]


class Source(BaseModel):
    """Normalized logical origin of content that can be processed into segments."""

    source_id: str | None = None
    source_type: SourceType
    uri: str
    canonical_uri: str | None = None
    title: str | None = None
    channel_or_author: str | None = None
    language_hint: str = "es"
    course_id: str = "biomechanics_knowledge_v1"
    tags: list[str] = Field(default_factory=list)
    duration_sec: float | None = None
    ingest_status: str = "discovered"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def set_defaults(self) -> "Source":
        if not self.canonical_uri:
            self.canonical_uri = self.uri
        if not self.source_id:
            self.source_id = stable_id("src", f"{self.source_type}:{self.canonical_uri}")
        return self


class Asset(BaseModel):
    """Derived asset created from a source."""

    asset_id: str | None = None
    source_id: str
    kind: AssetKind
    path: str
    mime_type: str
    start_sec: float = 0.0
    end_sec: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def set_asset_id(self) -> "Asset":
        if not self.asset_id:
            self.asset_id = stable_id("ast", f"{self.source_id}:{self.kind}:{self.path}")
        return self


class ConfidenceScores(BaseModel):
    """Confidence bundle for multimodal extraction stages."""

    asr: float | None = None
    ocr: float | None = None
    vision: float | None = None


class FrameRef(BaseModel):
    """Reference to a representative frame inside a segment."""

    sec: float
    path: str


class Segment(BaseModel):
    """Retrieval-ready unit built from one source and one time range."""

    segment_id: str | None = None
    source_id: str
    segment_index: int
    start_sec: float
    end_sec: float
    duration_sec: float | None = None
    transcript: str = ""
    ocr_text: str = ""
    visual_description: str = ""
    segment_summary: str = ""
    topics: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)
    speaker: str | None = None
    language: str = "es"
    confidence: ConfidenceScores = Field(default_factory=ConfidenceScores)
    frame_refs: list[FrameRef] = Field(default_factory=list)
    retrieval_text: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def set_computed_fields(self) -> "Segment":
        if self.duration_sec is None:
            self.duration_sec = max(0.0, self.end_sec - self.start_sec)
        if not self.segment_id:
            self.segment_id = stable_id(
                "seg",
                f"{self.source_id}:{self.segment_index}:{self.start_sec:.3f}:{self.end_sec:.3f}",
            )
        return self
