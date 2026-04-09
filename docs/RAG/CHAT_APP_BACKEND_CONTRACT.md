# Chat App Backend Contract

## Purpose

This document is the shared contract between:

- the chat frontend in `D:\chat-fisioterapia`
- this backend in `D:\sistema-biomecanico`

The goal is to let both evolve in parallel without guessing how the other side stores or exchanges data.

## Shared context rule

Both sides should treat **Supabase** as the shared application state for:

- auth
- user profile
- conversation history
- message history
- attachment metadata
- model catalog

The frontend should not infer state from Qdrant directly.

Qdrant remains only the retrieval engine behind the answering pipeline.

## Auth

Authentication should use **Supabase Auth**.

Application tables rely on `auth.users` and RLS.

The frontend should assume:

- sign up and sign in go through Supabase Auth
- user profile lives in `public.profiles`
- all chat tables are user-scoped with RLS

## New public tables

### `public.profiles`

One row per authenticated user.

Stores:

- `user_id`
- `email`
- `display_name`
- `avatar_url`
- `preferred_theme`
- `preferred_model_key`
- `metadata`

### `public.chat_models`

Catalog of selectable answering models for the UI.

Stores:

- `model_key`
- `provider`
- `display_name`
- `description`
- `answer_backend`
- `answer_model`
- capability flags like `supports_images`, `supports_audio`, `supports_reasoning`

Use this table to populate the model selector in the UI.

### `public.chat_conversations`

One row per chat thread.

Stores:

- `conversation_id`
- `user_id`
- `title`
- `selected_model_key`
- `conversation_status`
- `last_message_preview`
- `last_message_at`
- `metadata`

### `public.chat_messages`

One row per message rendered in the conversation.

Stores:

- `message_id`
- `conversation_id`
- `user_id`
- `role`
- `message_kind`
- `content_text`
- `rendered_blocks`
- `input_context`
- `output_context`
- `selected_model_key`
- `processing_status`
- `metadata`

`rendered_blocks` is the place to store structured assistant sections such as:

- diagnóstico funcional
- tratamiento sugerido
- ejercicios recomendados
- advertencias
- fuentes

### `public.chat_message_attachments`

One row per attachment linked to a message.

Stores:

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
- `metadata`

This is where image-analysis results should be linked to the conversation flow.

## Recommended API contract

The frontend can evolve safely if we keep these endpoints stable.

### 1. `GET /api/chat/models`

Purpose:

- fetch the model picker catalog

Response:

```json
{
  "models": [
    {
      "model_key": "grounded-default",
      "provider": "internal",
      "display_name": "Grounded Response",
      "answer_backend": "grounded",
      "answer_model": null,
      "supports_images": true,
      "supports_audio": false,
      "supports_reasoning": false,
      "is_default": true
    }
  ]
}
```

### 2. `GET /api/chat/conversations`

Purpose:

- list conversation history for the signed-in user

Response:

```json
{
  "items": [
    {
      "conversation_id": "uuid",
      "title": "Dolor de hombro",
      "selected_model_key": "grounded-default",
      "last_message_preview": "No puedo elevar mi brazo derecho completamente",
      "last_message_at": "2026-04-07T11:30:00Z",
      "conversation_status": "active"
    }
  ]
}
```

### 3. `POST /api/chat/conversations`

Purpose:

- create a new conversation

Request:

```json
{
  "title": "Nueva conversación",
  "selected_model_key": "grounded-default"
}
```

### 4. `GET /api/chat/conversations/{conversation_id}/messages`

Purpose:

- fetch full message history for a conversation

Response:

```json
{
  "conversation": {
    "conversation_id": "uuid",
    "title": "Dolor de hombro",
    "selected_model_key": "grounded-default"
  },
  "messages": [
    {
      "message_id": "uuid",
      "role": "user",
      "message_kind": "chat",
      "content_text": "No puedo elevar mi brazo derecho completamente",
      "attachments": []
    },
    {
      "message_id": "uuid",
      "role": "assistant",
      "message_kind": "analysis",
      "content_text": null,
      "rendered_blocks": [
        {
          "type": "section",
          "title": "Diagnóstico funcional",
          "content": "..."
        }
      ],
      "attachments": []
    }
  ]
}
```

### 5. `POST /api/chat/messages`

Purpose:

- send a user message
- optionally attach image-analysis context
- receive assistant reply

Request:

```json
{
  "conversation_id": "uuid",
  "selected_model_key": "grounded-default",
  "message": {
    "content_text": "No puedo tomar mi omóplato contrario con el brazo derecho",
    "attachments": [
      {
        "attachment_kind": "image",
        "storage_provider": "external_url",
        "public_url": "https://...",
        "analysis_payload": {
          "metrics": {
            "shoulder_elevation_delta": 0.12
          },
          "deficiencies": [
            "elevacion escapular derecha",
            "rotacion interna humeral leve"
          ]
        }
      }
    ]
  }
}
```

Response:

```json
{
  "conversation_id": "uuid",
  "user_message": {
    "message_id": "uuid"
  },
  "assistant_message": {
    "message_id": "uuid",
    "role": "assistant",
    "message_kind": "analysis",
    "rendered_blocks": [
      {
        "type": "section",
        "title": "Diagnóstico funcional",
        "content": "..."
      },
      {
        "type": "section",
        "title": "Tratamiento sugerido",
        "content": "..."
      },
      {
        "type": "list",
        "title": "Ejercicios recomendados",
        "items": ["...", "..."]
      }
    ],
    "output_context": {
      "retrieval_quality": "high",
      "used_collections": ["video_knowledge_units_v1", "video_segments_v1"],
      "selected_model_key": "grounded-default"
    }
  }
}
```

### 6. `POST /api/v1/chat/image-analysis`

Purpose:

- process uploaded static image groups before the final RAG call

This endpoint belongs to the visual-analysis pipeline, not the main answering pipeline.

Current MVP scope:

- `rest_phase1` only

Not integrated yet in chat:

- `isa`
- movement videos
- audio uploads

The chat wrapper currently uses the grouped static-image analysis flow under:

- `POST /api/v1/analyze/image/rest`

For `rest_phase1`, the wrapper does **not** rely on ad-hoc chat heuristics anymore. It now derives findings and deficiencies from the same threshold-based detector modules used by the baseline orchestration layer:

- `detection/findings.py`
- `detection/deficiencies.py`
- `detection/thresholds.py`

and keeps these as future upgrade targets:

- `POST /api/v1/analyze/rest/baseline`
- `POST /api/v1/analyze/video/movement`

Request:

- multipart form data
- required fields:
  - `user_id`
  - `conversation_id`
- optional fields:
  - `selected_model_key`
  - `note_text`
- file fields currently supported:
  - `rest_phase1_front`
  - `rest_phase1_side`
  - `rest_phase1_back`

Response should be shaped so the frontend can display:

- processing steps
- metrics
- deficiencies
- debug image URLs
- original image URLs

Response shape:

```json
{
  "conversation_id": "uuid",
  "analysis_message": {
    "message_id": "uuid",
    "role": "user",
    "message_kind": "analysis",
    "attachments": []
  },
  "analysis_job": {
    "analysis_job_id": "uuid",
    "analysis_kind": "image_metrics",
    "status": "completed",
    "detected_deficiencies": []
  },
  "detected_deficiencies": [],
  "debug_attachments": [
    {
      "attachment_kind": "debug_image",
      "public_url": "https://<supabase-project>/storage/v1/object/public/chat-media/..."
    }
  ],
  "response_artifact_path": "debug/chat/.../response.json"
}
```

Storage behavior for the MVP:

- the frontend uploads the three `rest_phase1` images to the backend
- the backend runs analysis
- the backend uploads both originals and debug overlays to the Supabase Storage bucket configured by `SUPABASE_CHAT_BUCKET`
- if Storage is unavailable, the backend falls back to local debug paths so the chat flow does not break during development

### Debug assets

Debug artifacts generated by the chat analysis flow are served by FastAPI under:

- `/debug-assets/...`

That means the frontend can render `public_url` directly without talking to Supabase Storage first.

## Frontend implementation notes

The frontend in `D:\chat-fisioterapia` already has the right product shape:

- sidebar with history
- chat panel
- model selector
- image attachments
- analysis panel

What it needs from the backend now is not more UI invention, but a stable contract for:

- listing conversations
- creating conversations
- sending messages
- loading messages
- loading model options
- passing image-analysis results into the RAG query

## Parallel work rule

To let two agents work in parallel:

- the frontend agent should only depend on this document plus Supabase table names
- the backend agent should avoid changing public payload shapes casually
- if payload shape changes, update this document first

That keeps both sides aligned even when they are developed at the same time.
