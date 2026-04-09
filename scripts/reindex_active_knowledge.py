"""Rebuild Qdrant knowledge-unit collection from active Supabase drafts."""

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

from src.analysis.knowledge_projection import project_knowledge_draft
from src.core.knowledge_models import KnowledgeDraft
from src.core.models import Source
from src.core.settings import get_rag_settings
from src.indexing.qdrant_store import QdrantStore
from src.pipelines.persist_knowledge import persist_and_index_knowledge
from src.storage.supabase_store import SupabaseRagStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Reindex active knowledge drafts into Qdrant.")
    parser.add_argument("--limit", type=int, help="Optional limit of active drafts to reindex.")
    parser.add_argument("--output-json", required=True, help="Path to save the rebuild summary.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    settings = get_rag_settings()
    supabase_store = SupabaseRagStore()
    rows = supabase_store.fetch_active_knowledge_drafts(limit=args.limit)
    qdrant_kwargs = {"collection_name": settings.qdrant_knowledge_collection}
    if settings.qdrant_prefer_embedded:
        qdrant_kwargs["path"] = settings.qdrant_path
    else:
        qdrant_kwargs["url"] = settings.qdrant_url
        qdrant_kwargs["api_key"] = settings.qdrant_api_key
    qdrant_store = QdrantStore(**qdrant_kwargs)

    processed: list[dict[str, object]] = []
    for row in rows:
        source = Source(
            source_id=row["source_id"],
            source_type=row["source_type"],
            uri=row["uri"],
            canonical_uri=row["canonical_uri"],
            title=row["title"],
            channel_or_author=row["channel_or_author"],
            language_hint=row["language_hint"],
            course_id=row["course_id"],
            tags=row["tags"] or [],
            duration_sec=row["duration_sec"],
            ingest_status=row["ingest_status"],
            metadata=row["metadata"] or {},
        )
        draft = KnowledgeDraft.model_validate(row["draft_payload"])
        projection = project_knowledge_draft(source, draft.model_dump(mode="json"))
        result = persist_and_index_knowledge(
            source=source,
            projection=projection,
            supabase_store=supabase_store,
            qdrant_store=qdrant_store,
        )
        processed.append(
            {
                "source_id": result.source_id,
                "draft_id": result.draft_id,
                "knowledge_units_upserted": result.knowledge_units_upserted,
                "qdrant_points_upserted": result.qdrant_points_upserted,
            }
        )

    summary = {
        "processed_count": len(processed),
        "items": processed,
    }
    output_path = Path(args.output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"Summary saved to: {output_path}")


if __name__ == "__main__":
    main()
