---
name: repo-bootstrap
description: Prepare the local development environment for the biomechanics video RAG project. Use when Codex needs to validate environment setup, check required binaries, verify Supabase and Qdrant dependencies, or confirm that ingestion and retrieval scripts can run locally.
---

# Repo Bootstrap

Bootstrap the repo around local-first execution.

Check these first:

- Python environment
- Supabase CLI
- Qdrant availability
- ffmpeg
- OCR tool availability
- environment variables in `.env`

Expected infrastructure roles:

- Supabase: metadata and structured records
- Qdrant: vector retrieval

Useful validation steps:

- run import dry-runs
- verify Supabase migration status
- verify Qdrant can accept indexed points
- confirm scripts in `scripts/` are executable in the current environment

When documenting setup, keep commands reproducible and Windows-friendly.
