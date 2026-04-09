"""Rebuild Qdrant evidence collection from persisted Supabase RAG segments."""

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
from src.indexing.qdrant_store import QdrantStore
from src.storage.supabase_store import SupabaseRagStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Reindex persisted RAG segments into Qdrant.")
    parser.add_argument("--limit", type=int, help="Optional limit of persisted segments to reindex.")
    parser.add_argument("--output-json", required=True, help="Path to save the rebuild summary.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    settings = get_rag_settings()
    supabase_store = SupabaseRagStore()
    segments = supabase_store.fetch_segments_for_reindex(limit=args.limit)

    qdrant_kwargs = {"collection_name": settings.qdrant_collection}
    if settings.qdrant_prefer_embedded:
        qdrant_kwargs["path"] = settings.qdrant_path
    else:
        qdrant_kwargs["url"] = settings.qdrant_url
        qdrant_kwargs["api_key"] = settings.qdrant_api_key
    qdrant_store = QdrantStore(**qdrant_kwargs)

    points_upserted = qdrant_store.upsert_segments(segments)
    source_ids = sorted({segment.source_id for segment in segments})
    summary = {
        "segment_count": len(segments),
        "source_count": len(source_ids),
        "qdrant_points_upserted": points_upserted,
        "collection_name": settings.qdrant_collection,
    }

    output_path = Path(args.output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"Summary saved to: {output_path}")


if __name__ == "__main__":
    main()
