"""Persist and index second-layer knowledge drafts."""

from __future__ import annotations

from dataclasses import dataclass

from src.analysis.knowledge_projection import KnowledgeProjection
from src.core.models import Source
from src.indexing.qdrant_store import QdrantStore
from src.storage.supabase_store import SupabaseRagStore


@dataclass(slots=True)
class PersistKnowledgeResult:
    source_id: str
    draft_id: str
    knowledge_units_upserted: int
    qdrant_points_upserted: int


def persist_and_index_knowledge(
    *,
    source: Source,
    projection: KnowledgeProjection,
    supabase_store: SupabaseRagStore,
    qdrant_store: QdrantStore | None = None,
) -> PersistKnowledgeResult:
    """Persist one knowledge draft and optionally index derived knowledge units."""
    source_id = supabase_store.upsert_source(source)
    draft_id = supabase_store.upsert_knowledge_draft(
        source=source,
        draft=projection.draft,
        content_sha256=projection.content_sha256,
    )
    knowledge_units_upserted = supabase_store.replace_knowledge_units(
        draft_id=draft_id,
        source=source,
        draft=projection.draft,
    )
    qdrant_points_upserted = 0
    if qdrant_store is not None and projection.draft.is_active:
        qdrant_store.delete_by_source_id(source_id)
        if projection.derived_segments:
            qdrant_points_upserted = qdrant_store.upsert_segments(projection.derived_segments)
    return PersistKnowledgeResult(
        source_id=source_id,
        draft_id=draft_id,
        knowledge_units_upserted=knowledge_units_upserted,
        qdrant_points_upserted=qdrant_points_upserted,
    )
