---
name: qdrant-indexing
description: Create or maintain the Qdrant indexing layer for the video RAG system. Use when Codex needs to define collections, vector payloads, upsert logic, hybrid retrieval inputs, or reindexing behavior for retrieval-ready segments.
---

# Qdrant Indexing

Use Qdrant as the retrieval engine.

Use Supabase as the system of record.

That means:

- Supabase owns structured metadata
- Qdrant owns retrieval vectors and payload filters

Each indexed point should be keyed by stable `segment_id`.

Recommended payload fields:

- `source_id`
- `segment_id`
- `start_sec`
- `end_sec`
- `source_type`
- `course_id`
- `language`
- `title`
- `uri`
- `channel_or_author`
- `topics`
- `keywords`

Preferred collection shape:

- dense vector: `dense_main`
- sparse vector: `sparse_main`

Indexing requirements:

- support incremental upsert
- do not duplicate points on reindex
- preserve filterable payloads
- allow retrieval by source type, language, and author/channel

When changing indexing logic, keep payload construction centralized in one module.
