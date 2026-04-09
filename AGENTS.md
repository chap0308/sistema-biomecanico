# AGENTS.md

## Objective

Build a local-first multimodal RAG system for biomechanics knowledge using:

- YouTube Shorts
- local videos
- webpages
- structured biomechanical metadata

The project uses:

- Supabase as system of record
- Qdrant as vector retrieval engine
- Gemini as optional premium video understanding
- local fallback pipelines for ASR, OCR, scene detection, and enrichment

## Current Direction

Do not optimize for model training as the primary solution.

Optimize for:

1. source ingestion
2. segment construction
3. embeddings and indexing
4. hybrid retrieval
5. grounded answer generation with citations

## Guardrails

- Do not remove the existing YouTube Shorts scraping and deduplication flow.
- Keep Windows compatibility for scripts unless explicitly noted otherwise.
- Prefer incremental pipelines that can skip already-processed sources.
- All public Python functions should use type hints.
- Avoid introducing heavy dependencies without documenting why.
- Keep Supabase as the metadata store and Qdrant as the retrieval store.
- Treat Gemini as optional and quota-limited.

## Key Existing Modules To Preserve

- `video/youtube_shorts.py`
- `video/gemini_knowledge.py`
- `video/movement_knowledge_import.py`
- `scripts/run_youtube_batch.py`
- `scripts/import_movement_knowledge_to_supabase.py`
- `scripts/sync_movement_knowledge_supabase.py`

## Preferred New Modules

- `src/core/models.py`
- `src/ingestion/*.py`
- `src/analysis/*.py`
- `src/chunking/*.py`
- `src/indexing/*.py`
- `src/retrieval/*.py`
- `src/rag/*.py`
- `src/pipelines/*.py`

## Commands

- Run tests:
  - `D:\anaconda4\envs\analisis-bio\python.exe -m pytest`
- Push DB migrations:
  - `supabase db push`
- Incremental knowledge sync:
  - `D:\anaconda4\envs\analisis-bio\python.exe scripts\sync_movement_knowledge_supabase.py`

## Architecture References

- `docs/RAG_LOCAL_ARCHITECTURE.md`
- `docs/RAG_SEGMENTS_AND_PIPELINES.md`
- `docs/knowledge/SUPABASE_MOVEMENT_KNOWLEDGE_SCHEMA.md`

## Definition of Done

A pipeline change is not done unless:

- code is typed
- at least basic validation exists
- the workflow is reproducible from `scripts/`
- the docs reflect the new behavior
