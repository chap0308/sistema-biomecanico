---
name: gemini-video-analysis
description: Use Gemini as the premium video understanding path for the biomechanics RAG system. Use when Codex needs to analyze quota-limited videos, extract richer visual understanding, segment educational videos, or compare Gemini outputs against the local fallback pipeline.
---

# Gemini Video Analysis

Use Gemini selectively.

Prefer Gemini when:

- the video is visually dense
- OCR/transcript alone is not enough
- a premium pass is justified

Do not make the whole pipeline depend on Gemini availability.

Expected outputs from Gemini:

- structured summary
- content classification
- knowledge units
- visual points
- exercise or mechanism descriptions
- timestamps when available

After Gemini output:

- normalize fields
- preserve raw response
- build retrieval-ready segments
- persist structured records to Supabase

Treat Gemini as one analysis route, not the source of truth for the whole system.
