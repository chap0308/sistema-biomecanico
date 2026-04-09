# Supabase + Qdrant In This Project

## Goal

This document explains the current responsibility split after the pivot to RAG.

The main conclusion is:

- Supabase is not the main semantic retrieval engine
- Qdrant is the main retrieval engine
- Supabase remains the system of record and traceability layer

They do not compete with each other. They play different roles.

## Responsibility split

### Supabase

Supabase should store structured and persistent records:

- content sources
- video and webpage metadata
- derived assets
- canonical segments
- analysis drafts
- knowledge units
- scraping and URL discovery registry
- validation and attempt states
- references to buckets or generated artifacts when needed

In other words, Supabase is the `system of record`.

### Qdrant

Qdrant should store retrieval-oriented records:

- dense embeddings
- filter payload
- references to `source_id` and `segment_id`
- only the minimum metadata needed for ranking and filtering

In other words, Qdrant is the `retrieval memory`.

## Current Supabase tables

The active RAG schema is `movement_knowledge`.

For the chat application, the active tables live in `public` because they need direct Supabase Auth and frontend access with RLS.

### Operational tables in the current pipeline

- `rag_sources`
- `rag_assets`
- `rag_segments`
- `rag_knowledge_drafts`
- `rag_knowledge_units`
- `rag_analysis_attempts`
- `public.profiles`
- `public.chat_models`
- `public.chat_conversations`
- `public.chat_messages`
- `public.chat_message_attachments`
- `public.chat_message_analysis_jobs`
- `youtube_channels`
- `youtube_scrape_runs`
- `youtube_scrape_items`

### Operational chat tables for the frontend app

- `public.profiles`
- `public.chat_models`
- `public.chat_conversations`
- `public.chat_messages`
- `public.chat_message_attachments`

Legacy tables from the pre-RAG direction are no longer part of the active workflow.

## What each table stores

### `rag_sources`

One row per logical source:

- YouTube Short
- local video
- public video URL
- webpage

It answers:

- what content exists
- what its canonical URI is
- what its ingest status is
- when it was processed

### `rag_assets`

Derived artifacts from a source:

- extracted audio
- transcript files
- OCR outputs
- keyframes
- thumbnails
- generated intermediate or persistent artifacts

Not every source needs persisted assets, but the table exists for the ones that do.

### `rag_segments`

The canonical evidence segments of the system.

It stores:

- timestamps
- transcript
- OCR
- visual description
- topics
- keywords
- `retrieval_text`
- quality metadata
- `content_sha256` for deduplication

This table is the bridge between Supabase and Qdrant when base evidence is indexed.

### `rag_knowledge_drafts`

Structured analysis output for a source.

It stores:

- `analysis_origin`
- `analysis_provider`
- `analysis_quality`
- `is_active`
- classification
- summary
- full normalized draft payload

It is used to preserve analysis history and determine which version is active for retrieval.

### `rag_knowledge_units`

Structured units derived from a draft:

- exercises
- educational points
- warnings
- tests
- cues

This is the structured source later projected into `video_knowledge_units_v1` in Qdrant.

### `rag_analysis_attempts`

Operational audit log of analysis executions.

This table is where errors, retries, and artifact references should live.

It stores:

- requested backend
- actual backend used
- model name
- success or error status
- whether the result was promoted to active
- usefulness when available
- previous and new draft ids
- error code and error message
- JSON artifact paths
- metadata about the attempt
- timestamps

This table should be used for:

- audit trail
- retry decisions
- understanding failures like `403 PERMISSION_DENIED`
- keeping references to generated JSON files without polluting `rag_knowledge_drafts`

### `youtube_channels`, `youtube_scrape_runs`, `youtube_scrape_items`

These tables record the discovery phase of URLs.

They help answer:

- when a channel was scraped
- which URLs were discovered
- which videos already have an active draft in Supabase
- which URLs still need analysis
- how a batch was reproduced by order (`newest`, `popular`, `oldest`)

Pending versus analyzed logic should come from these tables together with `rag_knowledge_drafts`, not from Qdrant.

## What should go to Qdrant

### `video_segments_v1`

Collection for base evidence:

- segments derived from `rag_segments`
- transcript
- OCR
- timestamps
- minimal payload for grounding

### `video_knowledge_units_v1`

Collection for derived knowledge:

- units derived from `rag_knowledge_units`
- exercises
- cues
- warnings
- context of use

### Current rule

- `useful` or `mixed` active drafts can be indexed into Qdrant
- `not_useful` drafts are not indexed into Qdrant
- `not_useful` drafts can still be stored in Supabase for traceability
- only the active version of a source should remain in Qdrant

That last rule matters:

- Supabase keeps history
- Qdrant keeps the current active retrieval version

## How to handle errors

Errors should not be represented as fake drafts.

Recommended rule:

- valid analysis result -> `rag_knowledge_drafts`
- valid derived units -> `rag_knowledge_units`
- execution attempt, retry, or failure -> `rag_analysis_attempts`

This avoids a common problem:

- if a Gemini attempt fails, that does not mean we should insert a broken Gemini draft
- the source may still have a perfectly valid active local or HF draft

## How to handle generated JSON files

The JSON files created during analysis do not need to be fully copied into Supabase.

Better rule:

- keep the files on disk
- store references to them in `rag_analysis_attempts.artifact_paths`
- promote a file to `rag_assets` only if it becomes a canonical artifact we want to preserve

This keeps the database lean while preserving reproducibility.

## What does not need to be in buckets

We should not store every original video by default.

### Cases where bucket storage is usually unnecessary

- public YouTube Shorts
- public webpages
- external videos used only as a knowledge source

In those cases it is usually enough to keep:

- canonical URL
- metadata
- transcript
- segments
- timestamps

### Cases where bucket storage is worth it

- user-uploaded videos
- local videos we want to preserve remotely
- expensive derived artifacts
- selected keyframes
- AI-generated exercise videos

## Retrieval rule

### For retrieval

Use Qdrant.

### For context reconstruction, citations, metadata, or artifacts

Use Supabase.

### For answering the user

Recommended flow:

```text
user query
-> retrieval in Qdrant
-> recover relevant source_id / segment_id
-> expand metadata and evidence from Supabase
-> build grounded answer with citations and timestamps
```

## Adapting to future changes

The domain will keep evolving, so not everything should be modeled as rigid tables from the start.

Practical rule:

1. accept new classifications first in flexible payload and metadata
2. if a structure appears repeatedly, promote it to a column or dedicated table
3. keep Supabase as the canonical traceability layer
4. keep Qdrant focused on retrieval quality

## Current recommendation

For this project the right architecture is:

- Supabase for `sources`, `assets`, `segments`, `knowledge drafts`, `analysis attempts`, scraping registry, and traceability
- Qdrant for vector and hybrid retrieval
- buckets only for assets that are truly worth preserving
- public YouTube content mainly as an external source reference, not as a required blob

This keeps the system flexible without turning Supabase into an improvised vector database or Qdrant into a full document system.

## Diferencia entre bases de datos

`https://share.google/aimode/8QPWecguQQ5uyfexv`