# Chat Frontend + Backend Shared Context

## Goal

This document defines the shared contract between:

- the chat web app in `D:\chat-fisioterapia`
- the biomechanics RAG backend in `D:\sistema-biomecanico`

The objective is to let both sides move in parallel without relying on informal context.

## Shared source of truth

The shared context between both projects should come from:

1. Supabase Auth
2. public chat tables in Supabase
3. stable backend request and response payloads

This is more reliable than trying to keep two agent sessions manually synchronized.

## Auth

Authentication should use Supabase Auth.

The profile extension table is:

- `public.profiles`

This means:

- the frontend owns sign in, sign up, session restore, and logout
- the backend trusts the authenticated Supabase user id
- user preferences live in `public.profiles`

## Shared public tables

These are the chat tables the frontend and backend should both treat as canonical:

- `public.profiles`
- `public.chat_models`
- `public.chat_conversations`
- `public.chat_messages`
- `public.chat_message_attachments`
- `public.chat_message_analysis_jobs`

## Conversation model

### `public.chat_conversations`

One row per user thread.

Important fields:

- `conversation_id`
- `user_id`
- `title`
- `selected_model_key`
- `conversation_status`
- `last_message_preview`
- `last_message_at`
- `metadata`

Frontend implications:

- sidebar history should query this table
- `Nueva conversación` creates one row here
- model picker updates `selected_model_key`

## Message model

### `public.chat_messages`

Each visible chat bubble should map to one row.

Important fields:

- `message_id`
- `conversation_id`
- `role`
- `message_kind`
- `content_text`
- `rendered_blocks`
- `input_context`
- `output_context`
- `selected_model_key`
- `processing_status`
- `metadata`

Recommended interpretation:

- `role = user` for user messages
- `role = assistant` for final replies
- `role = tool` for future intermediate system events if we decide to expose them

`rendered_blocks` is the correct place to keep structured UI sections such as:

- diagnóstico funcional
- tratamiento sugerido
- ejercicios recomendados
- advertencias
- fuentes

## Attachments

### `public.chat_message_attachments`

Used for images now and audio later.

Important fields:

- `attachment_id`
- `message_id`
- `attachment_kind`
- `storage_provider`
- `original_filename`
- `mime_type`
- `file_size_bytes`
- `storage_path`
- `public_url`
- `thumbnail_url`
- `analysis_status`
- `analysis_payload`

Current intended usage:

- image attachments from the user go here first
- later audio uploads will use the same table
- debug images can also be stored here as `debug_image`

## Image analysis pipeline

### `public.chat_message_analysis_jobs`

Tracks intermediate analysis work for attachments.

Important fields:

- `analysis_job_id`
- `conversation_id`
- `message_id`
- `attachment_id`
- `analysis_kind`
- `endpoint_name`
- `status`
- `detected_deficiencies`
- `metrics_payload`
- `request_payload`
- `response_payload`
- `error_code`
- `error_message`

This is the right place to represent the image flow:

1. user sends image + optional text
2. create attachment row
3. create `image_metrics` analysis job
4. metrics endpoint returns values and deficiencies
5. deficiencies are passed to the RAG query endpoint
6. assistant response is stored as a normal chat message

## Recommended endpoint flow

### `GET /api/chat/models`

Used to populate the model selector from `public.chat_models`.

### `GET /api/chat/conversations`

Used to populate sidebar history.

### `POST /api/chat/conversations`

Creates a new conversation row.

### `GET /api/chat/conversations/{conversation_id}/messages`

Loads the full thread, including attachments.

### `POST /api/chat/messages`

Creates the user message and optional attachment records.

### `POST /api/chat/image-analysis`

Runs the visual analysis pipeline and stores the resulting deficiencies and metrics.

### `POST /api/chat/messages/{message_id}/respond`

Runs the orchestration:

- if image exists, use image-analysis output first
- pass deficiencies + message text to the RAG endpoint
- store the assistant response

## Why this helps two agents work in parallel

The frontend agent does not need the backend internals.

It only needs:

- Supabase table names
- payload shapes
- endpoint names and response contracts

Meanwhile the backend can keep improving:

- retrieval
- reranking
- citation quality
- attachment analysis
- model routing

without breaking the UI, as long as these contracts stay stable.

## Practical rule

Use this as the coordination rule:

- frontend owns rendering and interaction states
- backend owns retrieval, orchestration, and persistence semantics
- Supabase is the shared state layer
- Qdrant remains invisible to the frontend
