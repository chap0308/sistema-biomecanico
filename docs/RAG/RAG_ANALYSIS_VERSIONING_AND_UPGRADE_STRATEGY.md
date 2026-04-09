# RAG Analysis Versioning And Upgrade Strategy

This document defines how the project should coexist with two active analysis routes:

- `Gemini` as the premium route
- `local pipeline + Hugging Face` as the standard or fallback route

The main goal is to improve knowledge quality without making the Supabase schema or Qdrant collections unstable.

## Goal

We want the vector database to contain useful and consistent knowledge even when videos are not analyzed with the same provider or quality level at the same time.

Because of that:

- the main schema must stay stable
- quality can vary by version
- one `source` can have multiple analysis versions over time

## Main rule

The model should not define the database.
The project taxonomy should define the database.

That means:

- `rag_knowledge_drafts`
- `rag_knowledge_units`
- `video_knowledge_units_v1`

must remain stable even if the analysis provider changes.

What changes between providers is not the central structure, but:

- completeness
- semantic cleanliness
- visual grounding quality
- knowledge unit quality

## Active routes

### 1. Premium route

`video -> Gemini -> knowledge draft -> Supabase -> Qdrant`

Use it when:

- Gemini quota is available
- the video depends heavily on visual demonstration
- we want the best active draft for retrieval

Benefits:

- better multimodal understanding
- better separation between problem, mechanism, exercise, habit, and test
- better `key_visual_points`
- better `knowledge_units`

### 2. Standard or fallback route

`video -> local extraction -> HF analysis -> knowledge draft -> Supabase -> Qdrant`

Use it when:

- Gemini quota is not available
- we want to populate many videos quickly
- transcript + OCR + keyframes already capture most of the signal

Benefits:

- lower cost
- local reproducibility
- better throughput
- enough quality to keep growing the base while the premium path is limited

## What "local draft" actually means

It does not mean that raw extracted evidence goes directly into the database.

The local route still has two layers:

1. `Level 1`
   - extracts transcript, OCR, scenes, keyframes, and segments
2. `Layer 2`
   - tries to analyze that evidence with Hugging Face
   - if HF fails, it generates a heuristic local draft

That output is still a structured `knowledge draft`.

So the actual flow is:

- extracted evidence
- structured draft
- persistence in Supabase
- indexing in Qdrant only if the draft is useful

## What can change between routes

These should not change:

- the main tables
- the main collections
- the internal taxonomy
- the retrieval payload base

These can change:

- `analysis_origin`
- `analysis_provider`
- `analysis_quality`
- `raw_payload`
- completeness and cleanliness of `classification`
- completeness and quality of `knowledge_units`

## Versioning model

Each `source` can have multiple drafts.

Each draft should store:

- `analysis_origin`
- `analysis_provider`
- `analysis_quality`
- `is_active`
- `supersedes_draft_id`

### Field meaning

- `analysis_origin`
  - identifies the exact route that produced the draft
  - examples:
    - `gemini_video_analysis`
    - `hf_structured_analysis:openai/gpt-oss-120b`
    - `local_level1_plus_hf_error_fallback:openai/gpt-oss-120b`

- `analysis_provider`
  - stable provider category
  - examples:
    - `gemini`
    - `hf_structured`
    - `local_fallback`

- `analysis_quality`
  - operational quality tier
  - recommended values:
    - `premium`
    - `standard`
    - `fallback`

- `is_active`
  - marks the version currently used for retrieval and indexing

- `supersedes_draft_id`
  - connects a better draft to the previous active one

## Recommended policy

### Daily ingestion

1. analyze with Gemini while quota lasts
2. continue with the `local + HF` route
3. persist both under the same schema

### Upgrade later

When Gemini quota is available again:

1. select active drafts with `standard` or `fallback`
2. reanalyze the source with Gemini
3. insert the new draft as `premium`
4. mark the previous draft as inactive
5. reindex only the active version in Qdrant

## Why this is better than blind replacement

If we replace the old draft directly:

- we lose traceability
- we cannot compare quality
- we cannot audit improvements or regressions

If we keep versions:

- we can compare `Gemini vs HF`
- we keep history
- we can audit quality
- we can switch the active version without breaking retrieval

## Effect on Supabase

Supabase remains the system of record.

It should store:

- the `source`
- all draft versions
- the `knowledge_units`
- provider and quality metadata

Supabase is where the full history lives.

## Effect on Qdrant

Qdrant should not index every version at the same time for normal answering.

Recommended rule:

- index only the active draft
- or reindex when the active draft changes

That avoids:

- semantic duplicates
- version conflicts
- answers mixing an old draft with a better one from the same video

## Batch failure behavior

When a batch runs with backend `gemini`, the intended behavior is:

- try Gemini per video
- if Gemini fails because of quota, timeout, or another recoverable error, fall back to the local route for that video
- continue with the rest of the batch

That means already-processed videos are not lost, and one provider failure does not kill the whole run.

## Product rule

- `Gemini` improves content quality
- it does not redefine the schema
- `HF/local` is not discarded
- it remains the fast population path and the operational fallback path

## Current project state

Today the project already has the foundation for this:

- provider and quality metadata in `KnowledgeDraft`
- active draft support in Supabase
- Gemini draft import into the current schema
- per-video fallback from Gemini to local in batch processing

Next recommended steps:

1. implement the explicit "upgrade to Gemini" command for `standard` and `fallback` drafts
2. reindex only the active version automatically
3. add quality comparison reports by source for auditing
