"""Persist one knowledge draft JSON into Supabase and Qdrant."""

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
from src.core.models import Source
from src.core.settings import get_rag_settings
from src.ingestion.youtube import build_youtube_source
from src.indexing.qdrant_store import QdrantStore
from src.pipelines.persist_knowledge import persist_and_index_knowledge
from src.storage.supabase_store import SupabaseRagStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Persist one second-layer knowledge draft into Supabase and Qdrant.")
    parser.add_argument("--draft-json", required=True, help="Path to a knowledge draft JSON output.")
    parser.add_argument(
        "--source-json",
        help="Optional Level 1 JSON that contains the original source object. If omitted, the draft source_url is used.",
    )
    parser.add_argument("--write-qdrant", action="store_true", help="Also index derived knowledge units in Qdrant.")
    parser.add_argument("--output-json", help="Optional path to save the sync result.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    draft_payload = json.loads(Path(args.draft_json).read_text(encoding="utf-8"))
    source = _load_source(args.source_json, draft_payload)

    projection = project_knowledge_draft(source, draft_payload)
    supabase_store = SupabaseRagStore()
    qdrant_store = None
    if args.write_qdrant:
        settings = get_rag_settings()
        qdrant_kwargs = {"collection_name": settings.qdrant_knowledge_collection}
        if settings.qdrant_prefer_embedded:
            qdrant_kwargs["path"] = settings.qdrant_path
        else:
            qdrant_kwargs["url"] = settings.qdrant_url
            qdrant_kwargs["api_key"] = settings.qdrant_api_key
        qdrant_store = QdrantStore(**qdrant_kwargs)

    result = persist_and_index_knowledge(
        source=source,
        projection=projection,
        supabase_store=supabase_store,
        qdrant_store=qdrant_store,
    )
    payload = {
        "source_id": result.source_id,
        "draft_id": result.draft_id,
        "knowledge_units_upserted": result.knowledge_units_upserted,
        "derived_segments_indexed": len(projection.derived_segments),
        "qdrant_points_upserted": result.qdrant_points_upserted,
    }
    serialized = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.output_json:
        output_path = Path(args.output_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(serialized, encoding="utf-8")
    print(serialized)


def _load_source(source_json_path: str | None, draft_payload: dict[str, object]) -> Source:
    if source_json_path:
        level1_payload = json.loads(Path(source_json_path).read_text(encoding="utf-8"))
        return Source.model_validate(level1_payload["source"])
    source_url = str(draft_payload.get("source_url", "")).strip()
    source_title = str(draft_payload.get("source_title_hint", "")).strip() or None
    if _is_youtube_url(source_url):
        return build_youtube_source(
            uri=source_url,
            title=source_title,
            language_hint="en",
        ).model_copy(update={"ingest_status": "knowledge_enriched"})
    return Source(
        source_type="webpage",
        uri=source_url,
        title=source_title,
        language_hint="en",
        ingest_status="knowledge_enriched",
    )


def _is_youtube_url(uri: str) -> bool:
    lowered = uri.lower()
    return "youtube.com" in lowered or "youtu.be" in lowered


if __name__ == "__main__":
    main()
