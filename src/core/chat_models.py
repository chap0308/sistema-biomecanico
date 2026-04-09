"""Typed models for public chat/auth tables shared with the chat frontend."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


ChatRole = Literal["system", "user", "assistant", "tool"]
MessageKind = Literal["chat", "analysis", "status", "error"]
MessageStatus = Literal["queued", "processing", "completed", "failed"]
ConversationStatus = Literal["active", "archived", "deleted"]
AttachmentKind = Literal["image", "audio", "video", "document", "debug_image"]
AttachmentStorageProvider = Literal["local_ref", "supabase_storage", "external_url", "base64_inline"]
AttachmentAnalysisStatus = Literal["pending", "processing", "completed", "failed", "skipped"]
AnalysisJobKind = Literal["image_metrics", "audio_transcription", "debug_overlay"]
AnalysisJobStatus = Literal["queued", "running", "completed", "error"]


class ChatUserProfile(BaseModel):
    user_id: UUID
    email: str | None = None
    display_name: str | None = None
    avatar_url: str | None = None
    preferred_theme: str = "system"
    preferred_model_key: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChatModel(BaseModel):
    model_key: str
    provider: str
    display_name: str
    description: str | None = None
    answer_backend: str
    answer_model: str | None = None
    is_active: bool = True
    is_default: bool = False
    supports_images: bool = False
    supports_audio: bool = False
    supports_reasoning: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChatConversation(BaseModel):
    conversation_id: UUID
    user_id: UUID
    title: str = "Nueva conversación"
    selected_model_key: str | None = None
    conversation_status: ConversationStatus = "active"
    last_message_preview: str | None = None
    last_message_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChatMessage(BaseModel):
    message_id: UUID
    conversation_id: UUID
    user_id: UUID | None = None
    role: ChatRole
    message_kind: MessageKind = "chat"
    content_text: str | None = None
    rendered_blocks: list[dict[str, Any]] = Field(default_factory=list)
    input_context: dict[str, Any] = Field(default_factory=dict)
    output_context: dict[str, Any] = Field(default_factory=dict)
    selected_model_key: str | None = None
    processing_status: MessageStatus = "completed"
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChatMessageAttachment(BaseModel):
    attachment_id: UUID
    message_id: UUID
    attachment_kind: AttachmentKind
    storage_provider: AttachmentStorageProvider = "local_ref"
    original_filename: str | None = None
    mime_type: str | None = None
    file_size_bytes: int | None = None
    storage_path: str | None = None
    public_url: str | None = None
    thumbnail_url: str | None = None
    analysis_status: AttachmentAnalysisStatus = "pending"
    analysis_payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChatMessageAnalysisJob(BaseModel):
    analysis_job_id: UUID
    conversation_id: UUID
    message_id: UUID
    attachment_id: UUID | None = None
    user_id: UUID | None = None
    analysis_kind: AnalysisJobKind
    endpoint_name: str | None = None
    status: AnalysisJobStatus = "queued"
    detected_deficiencies: list[dict[str, Any]] = Field(default_factory=list)
    metrics_payload: dict[str, Any] = Field(default_factory=dict)
    request_payload: dict[str, Any] = Field(default_factory=dict)
    response_payload: dict[str, Any] = Field(default_factory=dict)
    error_code: str | None = None
    error_message: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
