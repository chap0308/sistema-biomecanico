"""Upgrade active non-Gemini knowledge drafts to Gemini and promote only useful results."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.analysis.gemini_draft_normalizer import normalize_gemini_draft
from src.analysis.knowledge_projection import project_knowledge_draft
from src.core.settings import get_rag_settings
from src.indexing.qdrant_store import QdrantStore
from src.ingestion.youtube import build_youtube_source
from src.pipelines.persist_knowledge import persist_and_index_knowledge
from src.storage.supabase_store import SupabaseRagStore
from video.gemini_knowledge import analyze_youtube_video


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Upgrade existing active drafts to Gemini.")
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of active standard/fallback drafts to upgrade. Default: 10.",
    )
    selection.add_argument(
        "--url",
        action="append",
        dest="urls",
        help="Specific YouTube URL to upgrade. Repeat the flag for multiple URLs.",
    )
    parser.add_argument(
        "--order",
        choices=("asc", "desc"),
        default="asc",
        help="Selection order for --limit mode. Default: asc.",
    )
    parser.add_argument(
        "--model",
        default="gemini-2.5-flash",
        help="Gemini model to use for the upgrade.",
    )
    parser.add_argument(
        "--cooldown-hours",
        type=int,
        default=24,
        help="Ignore sources with a failed Gemini upgrade attempt in the last N hours when using --limit. Default: 24.",
    )
    parser.add_argument(
        "--output-json",
        default="data/knowledge/rag_runs/upgrade_drafts_to_gemini_summary.json",
        help="Path to save the upgrade summary.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    store = SupabaseRagStore()
    candidates = _select_candidates(store, args)

    settings = get_rag_settings()
    qdrant_kwargs = {"collection_name": settings.qdrant_knowledge_collection}
    if settings.qdrant_prefer_embedded:
        qdrant_kwargs["path"] = settings.qdrant_path
    else:
        qdrant_kwargs["url"] = settings.qdrant_url
        qdrant_kwargs["api_key"] = settings.qdrant_api_key
    qdrant_store = QdrantStore(**qdrant_kwargs)

    results: list[dict[str, object]] = []
    artifact_root = Path(args.output_json).resolve().with_suffix("")
    artifact_root.mkdir(parents=True, exist_ok=True)
    for candidate in candidates:
        source_url = str(candidate["source_url"])
        title_hint = str(candidate.get("source_title_hint") or candidate.get("source_title") or "").strip()
        source = build_youtube_source(uri=source_url, title=title_hint, language_hint="en").model_copy(
            update={"ingest_status": "knowledge_enriched"}
        )
        prefix = f"{source.source_id}_{source_url.rstrip('/').split('/')[-1]}"
        draft_output_path = artifact_root / f"{prefix}_gemini_draft.json"
        attempt_id = store.create_analysis_attempt(
            source_id=source.source_id or "",
            source_url=source_url,
            requested_backend="gemini_upgrade",
            actual_backend="gemini",
            model_name=args.model,
            previous_draft_id=str(candidate["draft_id"]),
            artifact_paths={"draft_json": str(draft_output_path)},
            metadata={
                "selection_mode": "urls" if args.urls else "limit",
                "order": getattr(args, "order", None),
            },
        )
        print(f"[gemini-upgrade] {candidate['source_id']} -> {source_url}")
        try:
            analysis = analyze_youtube_video(video_url=source_url, title_hint=title_hint, model=args.model)
            raw_payload = analysis.model_dump(mode="json")
            draft_output_path.write_text(json.dumps(raw_payload, indent=2, ensure_ascii=False), encoding="utf-8")
            normalized = normalize_gemini_draft(raw_payload)
            usefulness = str(normalized.get("classification", {}).get("usefulness", "")).strip().lower()
            should_promote = usefulness != "not_useful"
            normalized["analysis_origin"] = f"gemini_video_analysis:{args.model}"
            normalized["analysis_provider"] = "gemini"
            normalized["analysis_quality"] = "premium"
            normalized["is_active"] = should_promote
            normalized["supersedes_draft_id"] = str(candidate["draft_id"]) if should_promote else None

            projection = project_knowledge_draft(source, normalized)
            persist_result = persist_and_index_knowledge(
                source=source,
                projection=projection,
                supabase_store=store,
                qdrant_store=qdrant_store,
            )
            store.finish_analysis_attempt(
                attempt_id=attempt_id,
                status="success",
                promoted_to_active=should_promote,
                usefulness=usefulness,
                new_draft_id=persist_result.draft_id,
                artifact_paths={"draft_json": str(draft_output_path)},
                metadata={
                    "knowledge_units_upserted": persist_result.knowledge_units_upserted,
                    "qdrant_points_upserted": persist_result.qdrant_points_upserted,
                },
            )
            results.append(
                {
                    "source_id": source.source_id,
                    "source_url": source_url,
                    "previous_draft_id": str(candidate["draft_id"]),
                    "previous_analysis_provider": str(candidate["analysis_provider"]),
                    "new_draft_id": persist_result.draft_id,
                    "gemini_model": args.model,
                    "usefulness": usefulness,
                    "promoted_to_active": should_promote,
                    "knowledge_units_upserted": persist_result.knowledge_units_upserted,
                    "qdrant_points_upserted": persist_result.qdrant_points_upserted,
                }
            )
            print(f"[ok] {source_url} -> promoted={should_promote} usefulness={usefulness}")
        except Exception as exc:
            error_code = _infer_error_code(exc)
            store.finish_analysis_attempt(
                attempt_id=attempt_id,
                status="error",
                promoted_to_active=False,
                error_code=error_code,
                error_message=str(exc),
                artifact_paths={"draft_json": str(draft_output_path)} if draft_output_path.exists() else {},
            )
            results.append(
                {
                    "source_id": str(candidate["source_id"]),
                    "source_url": source_url,
                    "previous_draft_id": str(candidate["draft_id"]),
                    "status": "error",
                    "error_code": error_code,
                    "error": str(exc),
                }
            )
            print(f"[error] {source_url} -> {exc}", file=sys.stderr)

    summary = {
        "selection_mode": "urls" if args.urls else "limit",
        "requested_limit": None if args.urls else args.limit,
        "requested_urls": args.urls or [],
        "selected_count": len(candidates),
        "model": args.model,
        "results": results,
    }
    output_path = Path(args.output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"Summary saved to: {output_path}")


def _select_candidates(store: SupabaseRagStore, args: argparse.Namespace) -> list[dict[str, object]]:
    if args.urls:
        candidates = store.fetch_upgrade_candidates_by_urls(args.urls)
        return [row for row in candidates if _is_upgradeable_candidate(row)]
    return store.list_gemini_upgrade_candidates(
        limit=args.limit,
        ascending=args.order == "asc",
        cooldown_hours=args.cooldown_hours,
    )


def _is_upgradeable_candidate(row: dict[str, object]) -> bool:
    provider = str(row.get("analysis_provider", "")).strip().lower()
    quality = str(row.get("analysis_quality", "")).strip().lower()
    return provider != "gemini" and quality in {"standard", "fallback"}


def _infer_error_code(exc: Exception) -> str:
    text = str(exc).lower()
    if "permission_denied" in text or "403" in text:
        return "permission_denied"
    if "quota" in text or "resource_exhausted" in text or "429" in text:
        return "quota_exhausted"
    if "503" in text or "unavailable" in text:
        return "service_unavailable"
    if "timeout" in text:
        return "timeout"
    return "unknown_error"


if __name__ == "__main__":
    main()
