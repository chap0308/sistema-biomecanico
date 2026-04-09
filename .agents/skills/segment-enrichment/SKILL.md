---
name: segment-enrichment
description: Build or refine the segment construction and enrichment pipeline for the video RAG system. Use when Codex needs to align transcript, OCR, scene boundaries, visual notes, topics, keywords, and timestamps into retrieval-ready segments.
---

# Segment Enrichment

Treat the segment as the core unit of retrieval.

Each segment should combine:

- transcript
- OCR text
- visual description
- segment summary
- topics
- keywords
- timestamps

Segmenting rules:

- minimum target length: `4-6s`
- preferred length: `6-15s`
- maximum target length: `20s`

Cut on:

- scene changes
- strong pauses
- OCR changes
- idea changes
- exercise phase transitions

Merge adjacent pieces when:

- the scene is effectively the same
- the transcript is too short
- the idea is continuous

Always build `retrieval_text`.

`retrieval_text` should mix:

- transcript
- OCR
- visual description
- summary
- topics
- keywords

Do not index raw transcript alone when richer information exists.
