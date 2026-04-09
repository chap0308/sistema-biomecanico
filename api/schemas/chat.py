"""Schemas for chat endpoints and chat-specific image analysis."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ChatModelSummary(BaseModel):
    model_key: str
    provider: str
    display_name: str
    description: str | None = None
    answer_backend: str
    answer_model: str | None = None
    supports_images: bool
    supports_audio: bool
    supports_reasoning: bool
    is_default: bool


class ChatModelsResponse(BaseModel):
    models: list[ChatModelSummary]


class CreateConversationRequest(BaseModel):
    user_id: UUID
    title: str = "Nueva conversación"
    selected_model_key: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ConversationSummaryResponse(BaseModel):
    conversation_id: UUID
    title: str
    selected_model_key: str | None = None
    conversation_status: str
    last_message_preview: str | None = None
    last_message_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class ConversationsResponse(BaseModel):
    items: list[ConversationSummaryResponse]


class AttachmentResponse(BaseModel):
    attachment_id: UUID
    attachment_kind: str
    original_filename: str | None = None
    mime_type: str | None = None
    storage_provider: str
    storage_path: str | None = None
    public_url: str | None = None
    thumbnail_url: str | None = None
    analysis_status: str
    analysis_payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AnalysisJobResponse(BaseModel):
    analysis_job_id: UUID
    analysis_kind: str
    endpoint_name: str | None = None
    status: str
    detected_deficiencies: list[dict[str, Any]] = Field(default_factory=list)
    metrics_payload: dict[str, Any] = Field(default_factory=dict)
    response_payload: dict[str, Any] = Field(default_factory=dict)
    error_code: str | None = None
    error_message: str | None = None
    completed_at: datetime | None = None


class MessageResponse(BaseModel):
    message_id: UUID
    role: str
    message_kind: str
    content_text: str | None = None
    rendered_blocks: list[dict[str, Any]] = Field(default_factory=list)
    input_context: dict[str, Any] = Field(default_factory=dict)
    output_context: dict[str, Any] = Field(default_factory=dict)
    selected_model_key: str | None = None
    processing_status: str
    attachments: list[AttachmentResponse] = Field(default_factory=list)
    analysis_jobs: list[AnalysisJobResponse] = Field(default_factory=list)
    created_at: datetime


class ConversationMessagesResponse(BaseModel):
    conversation: ConversationSummaryResponse
    messages: list[MessageResponse]


class ChatImageAnalysisResponse(BaseModel):
    conversation_id: UUID
    analysis_message: MessageResponse
    analysis_job: AnalysisJobResponse
    detected_deficiencies: list[dict[str, Any]] = Field(default_factory=list)
    debug_attachments: list[AttachmentResponse] = Field(default_factory=list)
    response_artifact_path: str | None = None


class SendChatMessageRequest(BaseModel):
    user_id: UUID
    conversation_id: UUID
    content_text: str
    selected_model_key: str | None = None
    response_quality: str = "high"
    answer_profile: str | None = None
    related_analysis_job_ids: list[UUID] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SendChatMessageResponse(BaseModel):
    conversation_id: UUID
    user_message: MessageResponse
    assistant_message: MessageResponse
    debug_attachments: list[AttachmentResponse] = Field(default_factory=list)
