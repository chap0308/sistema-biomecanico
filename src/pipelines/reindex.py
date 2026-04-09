"""Helpers to persist and index segments from one source."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.models import Asset, Segment, Source
from src.indexing.qdrant_store import QdrantStore
from src.storage.supabase_store import SupabaseRagStore


@dataclass(slots=True)
class ReindexResult:
    source_id: str
    assets_upserted: int
    segments_inserted: int
    segments_skipped: int
    qdrant_points_upserted: int


def persist_and_index(
    *,
    source: Source,
    assets: list[Asset],
    segments: list[Segment],
    supabase_store: SupabaseRagStore,
    qdrant_store: QdrantStore | None = None,
) -> ReindexResult:
    """Persist structured records and optionally index them into Qdrant."""
    source_id = supabase_store.upsert_source(source)
    assets_upserted = supabase_store.upsert_assets(assets)
    segments_inserted, segments_skipped = supabase_store.upsert_segments(segments)
    qdrant_points_upserted = 0
    if qdrant_store is not None and segments:
        qdrant_points_upserted = qdrant_store.upsert_segments(segments)
    return ReindexResult(
        source_id=source_id,
        assets_upserted=assets_upserted,
        segments_inserted=segments_inserted,
        segments_skipped=segments_skipped,
        qdrant_points_upserted=qdrant_points_upserted,
    )
