---
name: local-video-fallback
description: Build or update the local-first video analysis fallback pipeline using ASR, scene detection, OCR, frame sampling, and optional visual captioning. Use when Codex needs to process videos without relying on Gemini or when a reproducible low-cost pipeline is needed for the RAG system.
---

# Local Video Fallback

Use the local path when:

- Gemini quota is exhausted
- cost should be minimized
- reproducibility matters more than premium understanding

The fallback pipeline should follow this order:

1. extract audio
2. run ASR
3. detect scenes
4. sample keyframes
5. run OCR
6. optionally add visual captions
7. align all signals into segments

Keep outputs structured and timestamped.

Each intermediate output should be traceable to:

- `source_id`
- `asset_id`
- `segment_id`

Do not let the local path depend on cloud services.

Prefer modules shaped like:

- `whisper_asr.py`
- `scene_detect.py`
- `frame_sampler.py`
- `ocr.py`
- `visual_caption.py`

The local path is successful only when it produces retrieval-ready segments, not just raw transcripts.
