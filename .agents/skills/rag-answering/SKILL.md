---
name: rag-answering
description: Implement grounded answering for the video RAG system using retrieved segments and citations. Use when Codex needs to build prompts, answer assembly, citation formatting, retrieval context selection, or anti-hallucination rules for responses based on indexed evidence.
---

# RAG Answering

The answer layer must be grounded in retrieved evidence.

Rules:

- if the evidence is insufficient, say so
- do not invent missing facts
- cite the source and timestamp
- prefer concise answers with explicit grounding

The answer pipeline should follow this order:

1. receive query and filters
2. run retrieval
3. optionally rerank
4. build prompt from top segments
5. answer using only retrieved context
6. attach citations

Each citation should include:

- source title
- source url or canonical reference
- start and end timestamp

If multiple adjacent segments belong to the same source and idea, they may be grouped before prompting.

Do not let answer formatting hide uncertainty.
