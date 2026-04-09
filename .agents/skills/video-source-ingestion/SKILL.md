---
name: video-source-ingestion
description: Normalize and ingest YouTube Shorts, local video files, public video URLs, and webpages into the project source model. Use when Codex needs to create or update source ingestion flows, metadata normalization, deduplication, canonical URL handling, or artifact staging for the video RAG system.
---

# Video Source Ingestion

Build ingestion around a stable `Source` object.

Use these rules:

- Prefer deterministic source ids.
- Preserve both `uri` and `canonical_uri`.
- Keep ingestion idempotent whenever possible.
- Store enough metadata to trace every downstream asset back to the source.

Minimum source fields:

- `source_id`
- `source_type`
- `uri`
- `canonical_uri`
- `title`
- `channel_or_author`
- `language_hint`
- `tags`
- `duration_sec`
- `ingest_status`

Expected source types:

- `youtube`
- `local_video`
- `public_video_url`
- `webpage`

When working on YouTube ingestion:

- preserve the current Playwright-based discovery flow
- preserve deduplication based on stable video ids
- keep rank/order metadata if available

When working on webpage ingestion:

- extract the main readable content
- detect embedded video URLs
- create linked sources instead of flattening everything into one record

When adding scripts:

- make them invocable from `scripts/`
- keep Windows compatibility
