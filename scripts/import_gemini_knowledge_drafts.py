"""Bulk import normalized Gemini drafts into Supabase and Qdrant."""

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

from src.analysis.gemini_draft_normalizer import is_importable_gemini_draft, normalize_gemini_draft
from src.analysis.knowledge_projection import project_knowledge_draft
from src.core.models import Source
from src.core.settings import get_rag_settings
from src.ingestion.youtube import build_youtube_source
from src.indexing.qdrant_store import QdrantStore
from src.pipelines.persist_knowledge import persist_and_index_knowledge
from src.storage.supabase_store import SupabaseRagStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bulk import Gemini video knowledge drafts into Supabase and Qdrant.")
    parser.add_argument(
        "--input-dir",
        action="append",
        dest="input_dirs",
        default=None,
        help="Root directory containing Gemini draft JSON files.",
    )
    parser.add_argument("--write-qdrant", action="store_true", help="Also index derived knowledge units into Qdrant.")
    parser.add_argument("--limit", type=int, help="Optional limit of importable draft files to process.")
    parser.add_argument(
        "--reset-rag-storage",
        action="store_true",
        help="Delete existing rag_* data in Supabase before importing.",
    )
    parser.add_argument(
        "--reset-qdrant",
        action="store_true",
        help="Delete and recreate the knowledge collection in Qdrant before importing.",
    )
    parser.add_argument("--output-json", help="Optional output path for the import summary.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    supabase_store = SupabaseRagStore()
    qdrant_store = _build_qdrant_store() if args.write_qdrant or args.reset_qdrant else None
    input_dirs = _resolve_input_dirs(args.input_dirs)

    if args.reset_rag_storage:
        _reset_rag_storage(supabase_store)
    if args.reset_qdrant and qdrant_store is not None:
        _reset_qdrant_collections(qdrant_store)

    importable_paths = []
    for input_dir in input_dirs:
        for path in sorted(input_dir.rglob("*.json")):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            if is_importable_gemini_draft(payload):
                importable_paths.append(path)
    if args.limit is not None:
        importable_paths = importable_paths[: args.limit]

    imported = 0
    qdrant_points = 0
    units_upserted = 0
    not_useful_drafts = 0
    qdrant_skipped_not_useful = 0
    processed_files: list[dict[str, object]] = []

    for path in importable_paths:
        raw_payload = json.loads(path.read_text(encoding="utf-8"))
        normalized = normalize_gemini_draft(raw_payload)
        source = _build_source_from_draft(normalized)
        projection = project_knowledge_draft(source, normalized)
        usefulness = projection.draft.classification.usefulness.strip().lower()
        if usefulness == "not_useful":
            not_useful_drafts += 1
        result = persist_and_index_knowledge(
            source=source,
            projection=projection,
            supabase_store=supabase_store,
            qdrant_store=qdrant_store if usefulness != "not_useful" else None,
        )
        imported += 1
        qdrant_points += result.qdrant_points_upserted
        units_upserted += result.knowledge_units_upserted
        if usefulness == "not_useful":
            qdrant_skipped_not_useful += 1
        processed_files.append(
            {
                "file": str(path),
                "source_id": result.source_id,
                "draft_id": result.draft_id,
                "usefulness": usefulness,
                "knowledge_units_upserted": result.knowledge_units_upserted,
                "qdrant_points_upserted": result.qdrant_points_upserted,
            }
        )

    summary = {
        "input_dirs": [str(path) for path in input_dirs],
        "importable_files": len(importable_paths),
        "processed_files": imported,
        "not_useful_drafts": not_useful_drafts,
        "qdrant_skipped_not_useful": qdrant_skipped_not_useful,
        "knowledge_units_upserted": units_upserted,
        "qdrant_points_upserted": qdrant_points,
        "files": processed_files,
    }
    serialized = json.dumps(summary, indent=2, ensure_ascii=False)
    if args.output_json:
        output_path = Path(args.output_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(serialized, encoding="utf-8")
    print(serialized)


def _build_qdrant_store() -> QdrantStore:
    settings = get_rag_settings()
    kwargs = {"collection_name": settings.qdrant_knowledge_collection}
    if settings.qdrant_prefer_embedded:
        kwargs["path"] = settings.qdrant_path
    else:
        kwargs["url"] = settings.qdrant_url
        kwargs["api_key"] = settings.qdrant_api_key
    return QdrantStore(**kwargs)


def _resolve_input_dirs(input_dirs: list[str] | None) -> list[Path]:
    values = input_dirs or ["data/knowledge/video_knowledge_drafts"]
    return [Path(value).resolve() for value in values]


def _reset_rag_storage(supabase_store: SupabaseRagStore) -> None:
    from psycopg import connect

    with connect(supabase_store.db_url, autocommit=True) as conn:
        with conn.cursor() as cur:
            tables = [
                "movement_knowledge.youtube_scrape_items",
                "movement_knowledge.youtube_scrape_runs",
                "movement_knowledge.youtube_channels",
                "movement_knowledge.rag_knowledge_units",
                "movement_knowledge.rag_knowledge_drafts",
                "movement_knowledge.rag_segments",
                "movement_knowledge.rag_assets",
                "movement_knowledge.rag_sources",
            ]
            for table_name in tables:
                cur.execute(f"truncate table {table_name} restart identity cascade")


def _reset_qdrant_collections(qdrant_store: QdrantStore) -> None:
    settings = get_rag_settings()
    client = qdrant_store._make_client()
    try:
        collections = {item.name for item in client.get_collections().collections}
        for collection_name in {qdrant_store.collection_name, settings.qdrant_collection}:
            if collection_name in collections:
                client.delete_collection(collection_name)
    finally:
        client.close()


def _build_source_from_draft(draft_payload: dict[str, object]) -> Source:
    source_url = str(draft_payload.get("source_url", "")).strip()
    source_title = str(draft_payload.get("source_title_hint", "")).strip() or None
    if _is_youtube_url(source_url):
        return build_youtube_source(
            uri=source_url,
            title=source_title,
            language_hint="en",
        ).model_copy(update={"ingest_status": "knowledge_enriched", "metadata": {"origin": "gemini_draft_import"}})
    return Source(
        source_type="webpage",
        uri=source_url,
        title=source_title,
        language_hint="en",
        ingest_status="knowledge_enriched",
        metadata={"origin": "gemini_draft_import"},
    )


def _is_youtube_url(uri: str) -> bool:
    lowered = uri.lower()
    return "youtube.com" in lowered or "youtu.be" in lowered


if __name__ == "__main__":
    main()
