"""Shared analysis runners for YouTube Shorts batches."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from src.analysis.gemini_draft_normalizer import normalize_gemini_draft
from src.analysis.knowledge_projection import project_knowledge_draft
from src.core.settings import get_rag_settings
from src.indexing.qdrant_store import QdrantStore
from src.ingestion.youtube import build_youtube_source
from src.pipelines.persist_knowledge import persist_and_index_knowledge
from src.storage.supabase_store import SupabaseRagStore
from src.storage.youtube_scrape_store import YoutubeScrapeStore
from video.gemini_knowledge import analyze_youtube_video

ROOT = Path(__file__).resolve().parents[2]


def run_local_pipeline(videos: list[Any], output_dir: Path) -> list[dict[str, object]]:
    """Run the local Level 1 + HF analysis + sync pipeline for a list of ShortsVideo-like objects."""
    results: list[dict[str, object]] = []
    for video in videos:
        results.append(_run_local_pipeline_for_video(video, output_dir))
    _refresh_scrape_flags(videos)
    return results


def run_gemini_pipeline(videos: list[Any], output_dir: Path, *, model: str) -> list[dict[str, object]]:
    """Run Gemini direct analysis and persist normalized knowledge.

    If Gemini fails for one video, the pipeline falls back to the local route
    for that specific video and continues with the rest of the batch.
    """
    settings = get_rag_settings()
    qdrant_kwargs = {"collection_name": settings.qdrant_knowledge_collection}
    if settings.qdrant_prefer_embedded:
        qdrant_kwargs["path"] = settings.qdrant_path
    else:
        qdrant_kwargs["url"] = settings.qdrant_url
        qdrant_kwargs["api_key"] = settings.qdrant_api_key
    qdrant_store = QdrantStore(**qdrant_kwargs)
    supabase_store = SupabaseRagStore()

    results: list[dict[str, object]] = []
    for video in videos:
        prefix = f"{video.order_index + 1:03d}_{video.video_id}"
        draft_path = output_dir / f"{prefix}.json"
        print(f"[gemini] Rank {video.order_index + 1}: {video.video_id} -> Gemini analysis")
        try:
            analysis = analyze_youtube_video(video_url=video.url, title_hint=video.title, model=model)
            raw_payload = analysis.model_dump(mode="json")
            draft_path.write_text(json.dumps(raw_payload, indent=2, ensure_ascii=False), encoding="utf-8")
            normalized = normalize_gemini_draft(raw_payload)
            source = build_youtube_source(uri=video.url, title=video.title, language_hint="en").model_copy(
                update={"ingest_status": "knowledge_enriched"}
            )
            projection = project_knowledge_draft(source, normalized)
            persist_and_index_knowledge(
                source=source,
                projection=projection,
                supabase_store=supabase_store,
                qdrant_store=qdrant_store if projection.draft.classification.usefulness != "not_useful" else None,
            )
            results.append(
                {
                    "video_id": video.video_id,
                    "url": video.url,
                    "title": video.title,
                    "rank": video.order_index + 1,
                    "draft_file": str(draft_path),
                    "usefulness": projection.draft.classification.usefulness,
                    "analysis_backend_used": "gemini",
                }
            )
        except Exception as exc:
            print(
                f"[warn] gemini failed for {video.video_id}. Falling back to local pipeline. Reason: {exc}",
                file=sys.stderr,
            )
            local_result = _run_local_pipeline_for_video(video, output_dir)
            local_result["analysis_backend_requested"] = "gemini"
            local_result["analysis_backend_used"] = "local_fallback"
            local_result["fallback_reason"] = str(exc)
            results.append(local_result)
    _refresh_scrape_flags(videos)
    return results


def _run_local_pipeline_for_video(video: Any, output_dir: Path) -> dict[str, object]:
    process_script = ROOT / "scripts" / "process_rag_source.py"
    analyze_script = ROOT / "scripts" / "analyze_rag_segments.py"
    sync_script = ROOT / "scripts" / "sync_rag_knowledge_draft.py"

    prefix = f"{video.order_index + 1:03d}_{video.video_id}"
    level1_path = output_dir / f"{prefix}_level1.json"
    draft_path = output_dir / f"{prefix}_knowledge_draft.json"
    sync_path = output_dir / f"{prefix}_sync.json"
    print(f"[local] Rank {video.order_index + 1}: {video.video_id} -> Level 1")
    _run_command(
        [
            sys.executable,
            str(process_script),
            "--youtube-url",
            video.url,
            "--language",
            "en",
            "--write-supabase",
            "--write-qdrant",
            "--output-json",
            str(level1_path),
        ],
        label=f"process_rag_source:{video.video_id}",
    )
    print(f"[local] Rank {video.order_index + 1}: {video.video_id} -> HF draft")
    _run_command(
        [
            sys.executable,
            str(analyze_script),
            "--input-json",
            str(level1_path),
            "--backend",
            "hf",
            "--output-json",
            str(draft_path),
        ],
        label=f"analyze_rag_segments:{video.video_id}",
    )
    print(f"[local] Rank {video.order_index + 1}: {video.video_id} -> Supabase/Qdrant sync")
    _run_command(
        [
            sys.executable,
            str(sync_script),
            "--draft-json",
            str(draft_path),
            "--source-json",
            str(level1_path),
            "--write-qdrant",
            "--output-json",
            str(sync_path),
        ],
        label=f"sync_rag_knowledge_draft:{video.video_id}",
    )
    return {
        "video_id": video.video_id,
        "url": video.url,
        "title": video.title,
        "rank": video.order_index + 1,
        "level1_file": str(level1_path),
        "draft_file": str(draft_path),
        "sync_file": str(sync_path),
        "analysis_backend_used": "local",
    }


def _run_command(command: list[str], *, label: str) -> None:
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        print(f"[error] {label} failed with exit code {completed.returncode}", file=sys.stderr)
        stdout_tail = completed.stdout[-4000:] if completed.stdout else ""
        stderr_tail = completed.stderr[-4000:] if completed.stderr else ""
        if stdout_tail:
            print(stdout_tail)
        if stderr_tail:
            print(stderr_tail, file=sys.stderr)
        raise SystemExit(completed.returncode)
    print(f"[ok] {label}")


def _refresh_scrape_flags(videos: list[Any]) -> None:
    store = YoutubeScrapeStore()
    store.refresh_active_draft_flags([video.video_id for video in videos])
