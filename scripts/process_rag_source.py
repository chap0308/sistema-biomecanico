"""Bootstrap one source through the RAG MVP local pipeline."""

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

from src.core.settings import get_rag_settings
from src.ingestion.local_video import build_local_video_source
from src.ingestion.webpage import build_webpage_source
from src.ingestion.youtube import build_youtube_source
from src.indexing.qdrant_store import QdrantStore
from src.pipelines.process_video_local import process_video_local
from src.pipelines.reindex import persist_and_index
from src.storage.supabase_store import SupabaseRagStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Process one source through the local RAG bootstrap pipeline.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--youtube-url")
    group.add_argument("--local-video")
    group.add_argument("--webpage-url")
    parser.add_argument("--title")
    parser.add_argument("--author")
    parser.add_argument("--language", default="es")
    parser.add_argument("--tag", action="append", dest="tags", default=[])
    parser.add_argument("--duration-sec", type=float)
    parser.add_argument("--write-supabase", action="store_true")
    parser.add_argument("--write-qdrant", action="store_true")
    parser.add_argument("--output-json")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    settings = get_rag_settings()

    if args.youtube_url:
        source = build_youtube_source(
            uri=args.youtube_url,
            title=args.title,
            channel_or_author=args.author,
            language_hint=args.language,
            tags=args.tags,
            duration_sec=args.duration_sec,
        )
    elif args.local_video:
        source = build_local_video_source(args.local_video, language_hint=args.language, tags=args.tags)
        if args.title:
            source.title = args.title
        if args.duration_sec is not None:
            source.duration_sec = args.duration_sec
    else:
        source = build_webpage_source(args.webpage_url, title=args.title, author=args.author, language_hint=args.language)
        source.tags = list(args.tags)

    if source.source_type == "webpage":
        result_payload = {
            "source": source.model_dump(mode="json"),
            "assets": [],
            "segments": [],
            "pipeline": "process_webpage",
            "status": "bootstrap_ready",
        }
    else:
        result = process_video_local(source)
        result_payload = {
            "source": result["source"].model_dump(mode="json"),
            "assets": [asset.model_dump(mode="json") for asset in result["assets"]],
            "segments": [segment.model_dump(mode="json") for segment in result["segments"]],
            "pipeline": result["pipeline"],
            "status": result["status"],
        }
        if "analysis_report" in result:
            result_payload["analysis_report"] = result["analysis_report"]

        if args.write_supabase:
            supabase_store = SupabaseRagStore()
            qdrant_store = None
            if args.write_qdrant:
                qdrant_kwargs = {"collection_name": settings.qdrant_collection}
                if settings.qdrant_prefer_embedded:
                    qdrant_kwargs["path"] = settings.qdrant_path
                else:
                    qdrant_kwargs["url"] = settings.qdrant_url
                    qdrant_kwargs["api_key"] = settings.qdrant_api_key
                qdrant_store = QdrantStore(**qdrant_kwargs)
            sync_result = persist_and_index(
                source=result["source"],
                assets=result["assets"],
                segments=result["segments"],
                supabase_store=supabase_store,
                qdrant_store=qdrant_store,
            )
            result_payload["sync_result"] = {
                "source_id": sync_result.source_id,
                "assets_upserted": sync_result.assets_upserted,
                "segments_inserted": sync_result.segments_inserted,
                "segments_skipped": sync_result.segments_skipped,
                "qdrant_points_upserted": sync_result.qdrant_points_upserted,
            }

    serialized = json.dumps(result_payload, indent=2, ensure_ascii=False)
    if args.output_json:
        output_path = Path(args.output_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(serialized, encoding="utf-8")
    print(serialized)


if __name__ == "__main__":
    main()
