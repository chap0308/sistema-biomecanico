"""Persistence helpers for chat conversations, messages, attachments, and analysis jobs."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from src.core.chat_models import (
    ChatModel,
    ChatConversation,
    ChatMessage,
    ChatMessageAnalysisJob,
    ChatMessageAttachment,
    ChatUserProfile,
)
from video.movement_knowledge_import import get_database_url


class SupabaseChatStore:
    """Typed persistence layer for chat application data in Supabase/Postgres."""

    def __init__(self, db_url: str | None = None) -> None:
        self.db_url = db_url or get_database_url()

    def upsert_user_profile(self, profile: ChatUserProfile) -> ChatUserProfile:
        from psycopg import connect

        with connect(self.db_url, autocommit=True, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    insert into public.profiles (
                        user_id,
                        email,
                        display_name,
                        avatar_url,
                        preferred_theme,
                        preferred_model_key,
                        metadata
                    ) values (%s, %s, %s, %s, %s, %s, %s)
                    on conflict (user_id) do update set
                        email = excluded.email,
                        display_name = excluded.display_name,
                        avatar_url = excluded.avatar_url,
                        preferred_theme = excluded.preferred_theme,
                        preferred_model_key = excluded.preferred_model_key,
                        metadata = excluded.metadata,
                        updated_at = now()
                    returning *
                    """,
                    (
                        profile.user_id,
                        profile.email,
                        profile.display_name,
                        profile.avatar_url,
                        profile.preferred_theme,
                        profile.preferred_model_key,
                        Jsonb(profile.metadata),
                    ),
                )
                return ChatUserProfile.model_validate(cur.fetchone())

    def list_models(self) -> list[ChatModel]:
        from psycopg import connect

        with connect(self.db_url, autocommit=True, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select *
                    from public.chat_models
                    where is_active = true
                    order by is_default desc, display_name asc
                    """
                )
                return [ChatModel.model_validate(row) for row in cur.fetchall()]

    def get_model(self, model_key: str) -> ChatModel | None:
        from psycopg import connect

        with connect(self.db_url, autocommit=True, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select *
                    from public.chat_models
                    where model_key = %s
                    limit 1
                    """,
                    (model_key,),
                )
                row = cur.fetchone()
                return ChatModel.model_validate(row) if row else None

    def get_default_model(self) -> ChatModel | None:
        from psycopg import connect

        with connect(self.db_url, autocommit=True, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select *
                    from public.chat_models
                    where is_active = true
                    order by is_default desc, display_name asc
                    limit 1
                    """
                )
                row = cur.fetchone()
                return ChatModel.model_validate(row) if row else None

    def create_conversation(
        self,
        *,
        user_id: UUID,
        title: str = "Nueva conversación",
        selected_model_key: str | None = "grounded-default",
        metadata: dict[str, Any] | None = None,
    ) -> ChatConversation:
        from psycopg import connect

        with connect(self.db_url, autocommit=True, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    insert into public.chat_conversations (
                        user_id,
                        title,
                        selected_model_key,
                        metadata
                    ) values (%s, %s, %s, %s)
                    returning *
                    """,
                    (
                        user_id,
                        title,
                        selected_model_key,
                        Jsonb(metadata or {}),
                    ),
                )
                return ChatConversation.model_validate(cur.fetchone())

    def list_conversations(self, *, user_id: UUID, limit: int = 50) -> list[ChatConversation]:
        from psycopg import connect

        with connect(self.db_url, autocommit=True, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select *
                    from public.chat_conversations
                    where user_id = %s
                      and conversation_status <> 'deleted'
                    order by coalesce(last_message_at, created_at) desc
                    limit %s
                    """,
                    (user_id, limit),
                )
                return [ChatConversation.model_validate(row) for row in cur.fetchall()]

    def get_conversation(self, *, conversation_id: UUID, user_id: UUID) -> ChatConversation | None:
        from psycopg import connect

        with connect(self.db_url, autocommit=True, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select *
                    from public.chat_conversations
                    where conversation_id = %s
                      and user_id = %s
                      and conversation_status <> 'deleted'
                    limit 1
                    """,
                    (conversation_id, user_id),
                )
                row = cur.fetchone()
                return ChatConversation.model_validate(row) if row else None

    def update_conversation(
        self,
        *,
        conversation_id: UUID,
        user_id: UUID,
        title: str | None = None,
        selected_model_key: str | None = None,
        conversation_status: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ChatConversation:
        from psycopg import connect

        with connect(self.db_url, autocommit=True, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    update public.chat_conversations
                    set title = coalesce(%s, title),
                        selected_model_key = coalesce(%s, selected_model_key),
                        conversation_status = coalesce(%s, conversation_status),
                        metadata = coalesce(%s, metadata),
                        updated_at = now()
                    where conversation_id = %s
                      and user_id = %s
                    returning *
                    """,
                    (
                        title,
                        selected_model_key,
                        conversation_status,
                        Jsonb(metadata) if metadata is not None else None,
                        conversation_id,
                        user_id,
                    ),
                )
                row = cur.fetchone()
                if row is None:
                    raise ValueError(f"Conversation {conversation_id} was not found for user {user_id}.")
                return ChatConversation.model_validate(row)

    def add_message(
        self,
        *,
        conversation_id: UUID,
        role: str,
        content_text: str | None = None,
        user_id: UUID | None = None,
        message_kind: str = "chat",
        selected_model_key: str | None = None,
        processing_status: str = "completed",
        rendered_blocks: list[dict[str, Any]] | None = None,
        input_context: dict[str, Any] | None = None,
        output_context: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ChatMessage:
        from psycopg import connect

        with connect(self.db_url, autocommit=True, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    insert into public.chat_messages (
                        conversation_id,
                        user_id,
                        role,
                        message_kind,
                        content_text,
                        rendered_blocks,
                        input_context,
                        output_context,
                        selected_model_key,
                        processing_status,
                        metadata
                    ) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    returning *
                    """,
                    (
                        conversation_id,
                        user_id,
                        role,
                        message_kind,
                        content_text,
                        Jsonb(rendered_blocks or []),
                        Jsonb(input_context or {}),
                        Jsonb(output_context or {}),
                        selected_model_key,
                        processing_status,
                        Jsonb(metadata or {}),
                    ),
                )
                message = ChatMessage.model_validate(cur.fetchone())
                cur.execute(
                    """
                    update public.chat_conversations
                    set last_message_preview = case
                            when %s = 'user' then %s
                            else coalesce(%s, last_message_preview)
                        end,
                        last_message_at = now(),
                        updated_at = now()
                    where conversation_id = %s
                    """,
                    (role, content_text, content_text, conversation_id),
                )
                return message

    def list_messages(self, *, conversation_id: UUID) -> list[ChatMessage]:
        from psycopg import connect

        with connect(self.db_url, autocommit=True, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select *
                    from public.chat_messages
                    where conversation_id = %s
                    order by created_at asc
                    """,
                    (conversation_id,),
                )
                return [ChatMessage.model_validate(row) for row in cur.fetchall()]

    def update_message(
        self,
        *,
        message_id: UUID,
        conversation_id: UUID,
        content_text: str | None = None,
        rendered_blocks: list[dict[str, Any]] | None = None,
        input_context: dict[str, Any] | None = None,
        output_context: dict[str, Any] | None = None,
        processing_status: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ChatMessage:
        from psycopg import connect

        with connect(self.db_url, autocommit=True, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    update public.chat_messages
                    set content_text = coalesce(%s, content_text),
                        rendered_blocks = coalesce(%s, rendered_blocks),
                        input_context = coalesce(%s, input_context),
                        output_context = coalesce(%s, output_context),
                        processing_status = coalesce(%s, processing_status),
                        metadata = coalesce(%s, metadata),
                        updated_at = now()
                    where message_id = %s
                      and conversation_id = %s
                    returning *
                    """,
                    (
                        content_text,
                        Jsonb(rendered_blocks) if rendered_blocks is not None else None,
                        Jsonb(input_context) if input_context is not None else None,
                        Jsonb(output_context) if output_context is not None else None,
                        processing_status,
                        Jsonb(metadata) if metadata is not None else None,
                        message_id,
                        conversation_id,
                    ),
                )
                row = cur.fetchone()
                if row is None:
                    raise ValueError(f"Message {message_id} was not found for conversation {conversation_id}.")
                return ChatMessage.model_validate(row)

    def add_attachment(
        self,
        attachment: ChatMessageAttachment,
    ) -> ChatMessageAttachment:
        from psycopg import connect

        with connect(self.db_url, autocommit=True, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                        insert into public.chat_message_attachments (
                            attachment_id,
                            message_id,
                            attachment_kind,
                            storage_provider,
                            original_filename,
                            mime_type,
                            file_size_bytes,
                            storage_path,
                            public_url,
                            thumbnail_url,
                            analysis_status,
                            analysis_payload,
                            metadata
                    ) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    on conflict (attachment_id) do update set
                        storage_provider = excluded.storage_provider,
                        original_filename = excluded.original_filename,
                        mime_type = excluded.mime_type,
                        file_size_bytes = excluded.file_size_bytes,
                        storage_path = excluded.storage_path,
                        public_url = excluded.public_url,
                        thumbnail_url = excluded.thumbnail_url,
                        analysis_status = excluded.analysis_status,
                        analysis_payload = excluded.analysis_payload,
                        metadata = excluded.metadata,
                        updated_at = now()
                    returning *
                    """,
                    (
                        attachment.attachment_id,
                        attachment.message_id,
                        attachment.attachment_kind,
                        attachment.storage_provider,
                        attachment.original_filename,
                        attachment.mime_type,
                        attachment.file_size_bytes,
                        attachment.storage_path,
                        attachment.public_url,
                        attachment.thumbnail_url,
                        attachment.analysis_status,
                        Jsonb(attachment.analysis_payload),
                        Jsonb(attachment.metadata),
                    ),
                )
                return ChatMessageAttachment.model_validate(cur.fetchone())

    def list_attachments_for_messages(self, *, message_ids: list[UUID]) -> list[ChatMessageAttachment]:
        if not message_ids:
            return []
        from psycopg import connect

        with connect(self.db_url, autocommit=True, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select *
                    from public.chat_message_attachments
                    where message_id = any(%s)
                    order by created_at asc
                    """,
                    (message_ids,),
                )
                return [ChatMessageAttachment.model_validate(row) for row in cur.fetchall()]

    def list_attachments_for_message(self, *, message_id: UUID) -> list[ChatMessageAttachment]:
        return self.list_attachments_for_messages(message_ids=[message_id])

    def create_analysis_job(self, job: ChatMessageAnalysisJob) -> ChatMessageAnalysisJob:
        from psycopg import connect

        with connect(self.db_url, autocommit=True, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    insert into public.chat_message_analysis_jobs (
                        analysis_job_id,
                        conversation_id,
                        message_id,
                        attachment_id,
                        user_id,
                        analysis_kind,
                        endpoint_name,
                        status,
                        detected_deficiencies,
                        metrics_payload,
                        request_payload,
                        response_payload,
                        error_code,
                        error_message,
                        completed_at
                    ) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    on conflict (analysis_job_id) do update set
                        endpoint_name = excluded.endpoint_name,
                        status = excluded.status,
                        detected_deficiencies = excluded.detected_deficiencies,
                        metrics_payload = excluded.metrics_payload,
                        request_payload = excluded.request_payload,
                        response_payload = excluded.response_payload,
                        error_code = excluded.error_code,
                        error_message = excluded.error_message,
                        completed_at = excluded.completed_at,
                        updated_at = now()
                    returning *
                    """,
                    (
                        job.analysis_job_id,
                        job.conversation_id,
                        job.message_id,
                        job.attachment_id,
                        job.user_id,
                        job.analysis_kind,
                        job.endpoint_name,
                        job.status,
                        Jsonb(job.detected_deficiencies),
                        Jsonb(job.metrics_payload),
                        Jsonb(job.request_payload),
                        Jsonb(job.response_payload),
                        job.error_code,
                        job.error_message,
                        job.completed_at,
                    ),
                )
                return ChatMessageAnalysisJob.model_validate(cur.fetchone())

    def list_analysis_jobs_for_message(self, *, message_id: UUID) -> list[ChatMessageAnalysisJob]:
        from psycopg import connect

        with connect(self.db_url, autocommit=True, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select *
                    from public.chat_message_analysis_jobs
                    where message_id = %s
                    order by created_at asc
                    """,
                    (message_id,),
                )
                return [ChatMessageAnalysisJob.model_validate(row) for row in cur.fetchall()]

    def fetch_analysis_jobs_by_ids(self, *, analysis_job_ids: list[UUID], user_id: UUID) -> list[ChatMessageAnalysisJob]:
        if not analysis_job_ids:
            return []
        from psycopg import connect

        with connect(self.db_url, autocommit=True, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select j.*
                    from public.chat_message_analysis_jobs j
                    join public.chat_conversations c on c.conversation_id = j.conversation_id
                    where j.analysis_job_id = any(%s)
                      and c.user_id = %s
                    order by j.created_at asc
                    """,
                    (analysis_job_ids, user_id),
                )
                return [ChatMessageAnalysisJob.model_validate(row) for row in cur.fetchall()]

    def list_debug_attachments_for_analysis_jobs(
        self,
        *,
        analysis_job_ids: list[UUID],
        user_id: UUID,
    ) -> list[ChatMessageAttachment]:
        if not analysis_job_ids:
            return []
        from psycopg import connect

        with connect(self.db_url, autocommit=True, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select a.*
                    from public.chat_message_attachments a
                    join public.chat_messages m on m.message_id = a.message_id
                    join public.chat_conversations c on c.conversation_id = m.conversation_id
                    join public.chat_message_analysis_jobs j on j.message_id = m.message_id
                    where j.analysis_job_id = any(%s)
                      and c.user_id = %s
                      and a.attachment_kind = 'debug_image'
                    order by a.created_at asc
                    """,
                    (analysis_job_ids, user_id),
                )
                return [ChatMessageAttachment.model_validate(row) for row in cur.fetchall()]
