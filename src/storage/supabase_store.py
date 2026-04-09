"""Supabase/Postgres persistence helpers for RAG sources, assets, segments, and knowledge drafts."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Iterable

from psycopg.types.json import Jsonb

from src.core.knowledge_models import KnowledgeDraft
from src.core.models import Asset, ConfidenceScores, FrameRef, Segment, Source
from video.movement_knowledge_import import get_database_url


def compute_segment_sha(segment: Segment) -> str:
    """Compute a stable content hash for one segment."""
    payload = {
        "segment_id": segment.segment_id,
        "source_id": segment.source_id,
        "segment_index": segment.segment_index,
        "start_sec": segment.start_sec,
        "end_sec": segment.end_sec,
        "transcript": segment.transcript,
        "ocr_text": segment.ocr_text,
        "visual_description": segment.visual_description,
        "segment_summary": segment.segment_summary,
        "topics": segment.topics,
        "keywords": segment.keywords,
        "entities": segment.entities,
        "language": segment.language,
        "retrieval_text": segment.retrieval_text,
        "payload": segment.payload,
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    import hashlib

    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class SupabaseRagStore:
    """Persist RAG sources, assets, and segments in Postgres."""

    def __init__(self, db_url: str | None = None) -> None:
        self.db_url = db_url or get_database_url()

    def upsert_source(self, source: Source) -> str:
        """Upsert one source and return its id."""
        from psycopg import connect
        from psycopg.rows import dict_row

        with connect(self.db_url, autocommit=True, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    insert into movement_knowledge.rag_sources (
                        source_id,
                        source_type,
                        uri,
                        canonical_uri,
                        title,
                        channel_or_author,
                        language_hint,
                        course_id,
                        tags,
                        duration_sec,
                        ingest_status,
                        metadata
                    ) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    on conflict (source_id) do update set
                        canonical_uri = excluded.canonical_uri,
                        title = excluded.title,
                        channel_or_author = excluded.channel_or_author,
                        language_hint = excluded.language_hint,
                        course_id = excluded.course_id,
                        tags = excluded.tags,
                        duration_sec = excluded.duration_sec,
                        ingest_status = excluded.ingest_status,
                        metadata = excluded.metadata,
                        updated_at = now()
                    returning source_id
                    """,
                    (
                        source.source_id,
                        source.source_type,
                        source.uri,
                        source.canonical_uri,
                        source.title,
                        source.channel_or_author,
                        source.language_hint,
                        source.course_id,
                        source.tags,
                        source.duration_sec,
                        source.ingest_status,
                        Jsonb(source.metadata),
                    ),
                )
                return str(cur.fetchone()["source_id"])

    def upsert_assets(self, assets: Iterable[Asset]) -> int:
        """Upsert assets by asset id."""
        from psycopg import connect

        asset_list = list(assets)
        if not asset_list:
            return 0
        with connect(self.db_url, autocommit=True) as conn:
            with conn.cursor() as cur:
                for asset in asset_list:
                    cur.execute(
                        """
                        insert into movement_knowledge.rag_assets (
                            asset_id,
                            source_id,
                            kind,
                            path,
                            mime_type,
                            start_sec,
                            end_sec,
                            metadata
                        ) values (%s, %s, %s, %s, %s, %s, %s, %s)
                        on conflict (asset_id) do update set
                            path = excluded.path,
                            mime_type = excluded.mime_type,
                            start_sec = excluded.start_sec,
                            end_sec = excluded.end_sec,
                            metadata = excluded.metadata,
                            updated_at = now()
                        """,
                        (
                            asset.asset_id,
                            asset.source_id,
                            asset.kind,
                            asset.path,
                            asset.mime_type,
                            asset.start_sec,
                            asset.end_sec,
                            Jsonb(asset.metadata),
                        ),
                    )
        return len(asset_list)

    def upsert_segments(self, segments: Iterable[Segment]) -> tuple[int, int]:
        """Upsert segments and skip identical content already stored."""
        from psycopg import connect
        from psycopg.rows import dict_row

        segment_list = list(segments)
        inserted = 0
        skipped = 0

        with connect(self.db_url, autocommit=False, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                for segment in segment_list:
                    content_sha = compute_segment_sha(segment)
                    cur.execute(
                        """
                        select content_sha256
                        from movement_knowledge.rag_segments
                        where segment_id = %s
                        """,
                        (segment.segment_id,),
                    )
                    existing = cur.fetchone()
                    if existing and existing["content_sha256"] == content_sha:
                        skipped += 1
                        continue

                    cur.execute(
                        """
                        insert into movement_knowledge.rag_segments (
                            segment_id,
                            source_id,
                            segment_index,
                            start_sec,
                            end_sec,
                            duration_sec,
                            transcript,
                            ocr_text,
                            visual_description,
                            segment_summary,
                            topics,
                            keywords,
                            entities,
                            speaker,
                            language,
                            confidence,
                            frame_refs,
                            retrieval_text,
                            payload,
                            content_sha256
                        ) values (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        on conflict (segment_id) do update set
                            start_sec = excluded.start_sec,
                            end_sec = excluded.end_sec,
                            duration_sec = excluded.duration_sec,
                            transcript = excluded.transcript,
                            ocr_text = excluded.ocr_text,
                            visual_description = excluded.visual_description,
                            segment_summary = excluded.segment_summary,
                            topics = excluded.topics,
                            keywords = excluded.keywords,
                            entities = excluded.entities,
                            speaker = excluded.speaker,
                            language = excluded.language,
                            confidence = excluded.confidence,
                            frame_refs = excluded.frame_refs,
                            retrieval_text = excluded.retrieval_text,
                            payload = excluded.payload,
                            content_sha256 = excluded.content_sha256,
                            updated_at = now()
                        """,
                        (
                            segment.segment_id,
                            segment.source_id,
                            segment.segment_index,
                            segment.start_sec,
                            segment.end_sec,
                            segment.duration_sec,
                            segment.transcript,
                            segment.ocr_text,
                            segment.visual_description,
                            segment.segment_summary,
                            segment.topics,
                            segment.keywords,
                            segment.entities,
                            segment.speaker,
                            segment.language,
                            Jsonb(segment.confidence.model_dump(mode="json")),
                            Jsonb([frame.model_dump(mode="json") for frame in segment.frame_refs]),
                            segment.retrieval_text,
                            Jsonb(segment.payload),
                            content_sha,
                        ),
                    )
                    inserted += 1
            conn.commit()

        return inserted, skipped

    def upsert_knowledge_draft(self, *, source: Source, draft: KnowledgeDraft, content_sha256: str) -> str:
        """Upsert one structured knowledge draft and return its id."""
        from psycopg import connect
        from psycopg.rows import dict_row

        draft_id = draft.model_dump(mode="json").get("draft_id") or None
        if not draft_id:
            from src.core.ids import stable_id

            draft_id = stable_id("kdraft", f"{source.source_id}:{draft.analysis_origin}:{content_sha256}")

        with connect(self.db_url, autocommit=False, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                supersedes_draft_id = draft.supersedes_draft_id
                if draft.is_active:
                    cur.execute(
                        """
                        select draft_id
                        from movement_knowledge.rag_knowledge_drafts
                        where source_id = %s
                          and is_active = true
                          and draft_id <> %s
                        order by updated_at desc nulls last, created_at desc
                        limit 1
                        """,
                        (source.source_id, draft_id),
                    )
                    active_row = cur.fetchone()
                    if active_row:
                        supersedes_draft_id = supersedes_draft_id or str(active_row["draft_id"])
                        cur.execute(
                            """
                            update movement_knowledge.rag_knowledge_drafts
                            set is_active = false,
                                superseded_at = now(),
                                updated_at = now()
                            where source_id = %s
                              and draft_id <> %s
                              and is_active = true
                            """,
                            (source.source_id, draft_id),
                        )
                cur.execute(
                    """
                    insert into movement_knowledge.rag_knowledge_drafts (
                        draft_id,
                        source_id,
                        source_url,
                        source_title_hint,
                        analysis_origin,
                        analysis_provider,
                        analysis_quality,
                        is_active,
                        supersedes_draft_id,
                        primary_summary,
                        classification,
                        searchable_topics,
                        searchable_tags,
                        problem_statements,
                        habits_or_contexts,
                        key_visual_points,
                        tests_mentioned,
                        exercises_mentioned,
                        advice_mentioned,
                        warnings_or_limitations,
                        analysis_report,
                        source_artifacts,
                        raw_payload,
                        content_sha256
                    ) values (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    on conflict (draft_id) do update set
                        source_url = excluded.source_url,
                        source_title_hint = excluded.source_title_hint,
                        analysis_origin = excluded.analysis_origin,
                        analysis_provider = excluded.analysis_provider,
                        analysis_quality = excluded.analysis_quality,
                        is_active = excluded.is_active,
                        supersedes_draft_id = excluded.supersedes_draft_id,
                        primary_summary = excluded.primary_summary,
                        classification = excluded.classification,
                        searchable_topics = excluded.searchable_topics,
                        searchable_tags = excluded.searchable_tags,
                        problem_statements = excluded.problem_statements,
                        habits_or_contexts = excluded.habits_or_contexts,
                        key_visual_points = excluded.key_visual_points,
                        tests_mentioned = excluded.tests_mentioned,
                        exercises_mentioned = excluded.exercises_mentioned,
                        advice_mentioned = excluded.advice_mentioned,
                        warnings_or_limitations = excluded.warnings_or_limitations,
                        analysis_report = excluded.analysis_report,
                        source_artifacts = excluded.source_artifacts,
                        raw_payload = excluded.raw_payload,
                        content_sha256 = excluded.content_sha256,
                        updated_at = now()
                    returning draft_id
                    """,
                    (
                        draft_id,
                        source.source_id,
                        draft.source_url,
                        draft.source_title_hint,
                        draft.analysis_origin,
                        draft.analysis_provider,
                        draft.analysis_quality,
                        draft.is_active,
                        supersedes_draft_id,
                        draft.primary_summary,
                        Jsonb(draft.classification.model_dump(mode="json")),
                        draft.searchable_topics,
                        draft.searchable_tags,
                        draft.problem_statements,
                        draft.habits_or_contexts,
                        draft.key_visual_points,
                        draft.tests_mentioned,
                        draft.exercises_mentioned,
                        draft.advice_mentioned,
                        draft.warnings_or_limitations,
                        Jsonb(draft.analysis_report),
                        Jsonb(draft.source_artifacts.model_dump(mode="json")),
                        Jsonb(draft.model_dump(mode="json")),
                        content_sha256,
                    ),
                )
                inserted_draft_id = str(cur.fetchone()["draft_id"])
            conn.commit()
        return inserted_draft_id

    def replace_knowledge_units(
        self,
        *,
        draft_id: str,
        source: Source,
        draft: KnowledgeDraft,
    ) -> int:
        """Replace structured knowledge units for one knowledge draft."""
        from psycopg import connect

        units = draft.knowledge_units
        with connect(self.db_url, autocommit=False) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "delete from movement_knowledge.rag_knowledge_units where draft_id = %s",
                    (draft_id,),
                )
                for index, unit in enumerate(units, start=1):
                    unit_id = self._make_knowledge_unit_id(source.source_id or "", draft_id, index, unit.title)
                    cur.execute(
                        """
                        insert into movement_knowledge.rag_knowledge_units (
                            unit_id,
                            draft_id,
                            source_id,
                            unit_index,
                            unit_type,
                            title,
                            summary,
                            observable_signs,
                            mechanisms,
                            execution_steps,
                            cues,
                            breathing_cues,
                            errors_to_avoid,
                            when_useful,
                            when_not_useful,
                            retest,
                            advice,
                            timestamps,
                            raw_payload
                        ) values (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        """,
                        (
                            unit_id,
                            draft_id,
                            source.source_id,
                            index,
                            unit.unit_type,
                            unit.title,
                            unit.summary,
                            unit.observable_signs,
                            unit.mechanisms,
                            unit.execution_steps,
                            unit.cues,
                            unit.breathing_cues,
                            unit.errors_to_avoid,
                            unit.when_useful,
                            unit.when_not_useful,
                            unit.retest,
                            unit.advice,
                            unit.timestamps,
                            Jsonb(unit.model_dump(mode="json")),
                        ),
                    )
            conn.commit()
        return len(units)

    def fetch_segments_by_ids(self, segment_ids: Iterable[str]) -> list[dict[str, object]]:
        """Fetch canonical segment rows for answer grounding."""
        from psycopg import connect
        from psycopg.rows import dict_row

        ids = list(dict.fromkeys(segment_ids))
        if not ids:
            return []
        with connect(self.db_url, autocommit=True, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select
                        segment_id,
                        source_id,
                        start_sec,
                        end_sec,
                        transcript,
                        ocr_text,
                        visual_description,
                        segment_summary,
                        topics,
                        keywords,
                        payload
                    from movement_knowledge.rag_segments
                    where segment_id = any(%s)
                    """,
                    (ids,),
                )
                return [dict(row) for row in cur.fetchall()]

    def fetch_active_knowledge_drafts(self, *, limit: int | None = None) -> list[dict[str, object]]:
        """Fetch active drafts with their source metadata for reindexing or audits."""
        from psycopg import connect
        from psycopg.rows import dict_row

        sql = """
            select
                d.draft_id,
                d.source_id,
                d.raw_payload as draft_payload,
                s.source_type,
                s.uri,
                s.canonical_uri,
                s.title,
                s.channel_or_author,
                s.language_hint,
                s.course_id,
                s.tags,
                s.duration_sec,
                s.ingest_status,
                s.metadata
            from movement_knowledge.rag_knowledge_drafts d
            join movement_knowledge.rag_sources s
              on s.source_id = d.source_id
            where d.is_active = true
            order by d.created_at asc, d.draft_id asc
        """
        params: tuple[object, ...] = ()
        if limit is not None:
            sql += " limit %s"
            params = (limit,)
        with connect(self.db_url, autocommit=True, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                return [dict(row) for row in cur.fetchall()]

    def fetch_segments_for_reindex(self, *, limit: int | None = None) -> list[Segment]:
        """Fetch persisted RAG segments to rebuild the evidence collection in Qdrant."""
        from psycopg import connect
        from psycopg.rows import dict_row

        sql = """
            select
                segment_id,
                source_id,
                segment_index,
                start_sec,
                end_sec,
                duration_sec,
                transcript,
                ocr_text,
                visual_description,
                segment_summary,
                topics,
                keywords,
                entities,
                speaker,
                language,
                confidence,
                frame_refs,
                retrieval_text,
                payload
            from movement_knowledge.rag_segments
            order by source_id asc, segment_index asc, segment_id asc
        """
        params: tuple[object, ...] = ()
        if limit is not None:
            sql += " limit %s"
            params = (limit,)

        with connect(self.db_url, autocommit=True, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()

        segments: list[Segment] = []
        for row in rows:
            confidence_payload = row["confidence"] or {}
            frame_refs_payload = row["frame_refs"] or []
            segments.append(
                Segment(
                    segment_id=row["segment_id"],
                    source_id=row["source_id"],
                    segment_index=row["segment_index"],
                    start_sec=row["start_sec"],
                    end_sec=row["end_sec"],
                    duration_sec=row["duration_sec"],
                    transcript=row["transcript"] or "",
                    ocr_text=row["ocr_text"] or "",
                    visual_description=row["visual_description"] or "",
                    segment_summary=row["segment_summary"] or "",
                    topics=list(row["topics"] or []),
                    keywords=list(row["keywords"] or []),
                    entities=list(row["entities"] or []),
                    speaker=row["speaker"],
                    language=row["language"] or "es",
                    confidence=ConfidenceScores.model_validate(confidence_payload),
                    frame_refs=[FrameRef.model_validate(item) for item in frame_refs_payload],
                    retrieval_text=row["retrieval_text"] or "",
                    payload=dict(row["payload"] or {}),
                )
            )
        return segments

    def list_gemini_upgrade_candidates(
        self,
        *,
        limit: int = 10,
        ascending: bool = True,
        cooldown_hours: int = 24,
    ) -> list[dict[str, object]]:
        """Return active non-Gemini drafts eligible for premium upgrade."""
        from psycopg import connect
        from psycopg.rows import dict_row

        direction = "asc" if ascending else "desc"
        with connect(self.db_url, autocommit=True, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cooldown_clause = ""
                params: list[object] = []
                if cooldown_hours > 0:
                    cooldown_clause = """
                      and not exists (
                          select 1
                          from movement_knowledge.rag_analysis_attempts a
                          where a.source_id = d.source_id
                            and a.requested_backend = 'gemini_upgrade'
                            and a.status = 'error'
                            and a.started_at >= now() - (%s || ' hours')::interval
                      )
                    """
                    params.append(cooldown_hours)
                params.append(limit)
                cur.execute(
                    f"""
                    select
                        d.draft_id,
                        d.source_id,
                        d.source_url,
                        d.source_title_hint,
                        d.analysis_origin,
                        d.analysis_provider,
                        d.analysis_quality,
                        d.is_active,
                        d.classification,
                        d.created_at,
                        s.title as source_title,
                        s.channel_or_author
                    from movement_knowledge.rag_knowledge_drafts d
                    join movement_knowledge.rag_sources s
                      on s.source_id = d.source_id
                    where d.is_active = true
                      and d.analysis_provider <> 'gemini'
                      and d.analysis_quality in ('standard', 'fallback')
                      {cooldown_clause}
                    order by d.created_at {direction}, d.draft_id {direction}
                    limit %s
                    """,
                    params,
                )
                return [dict(row) for row in cur.fetchall()]

    def fetch_upgrade_candidates_by_urls(self, urls: Iterable[str]) -> list[dict[str, object]]:
        """Return active drafts for the provided URLs using source_id canonicalization."""
        from psycopg import connect
        from psycopg.rows import dict_row

        source_ids = [self._source_id_from_url(url) for url in urls]
        source_ids = [item for item in dict.fromkeys(source_ids) if item]
        if not source_ids:
            return []
        with connect(self.db_url, autocommit=True, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select
                        d.draft_id,
                        d.source_id,
                        d.source_url,
                        d.source_title_hint,
                        d.analysis_origin,
                        d.analysis_provider,
                        d.analysis_quality,
                        d.is_active,
                        d.classification,
                        d.created_at,
                        s.title as source_title,
                        s.channel_or_author
                    from movement_knowledge.rag_knowledge_drafts d
                    join movement_knowledge.rag_sources s
                      on s.source_id = d.source_id
                    where d.is_active = true
                      and d.source_id = any(%s)
                    order by d.created_at asc, d.draft_id asc
                    """,
                    (source_ids,),
                )
                return [dict(row) for row in cur.fetchall()]

    def list_failed_analysis_attempts(
        self,
        *,
        requested_backend: str = "gemini_upgrade",
        limit: int = 10,
        ascending: bool = False,
    ) -> list[dict[str, object]]:
        """Return unresolved latest failed analysis attempts."""
        from psycopg import connect
        from psycopg.rows import dict_row

        direction = "asc" if ascending else "desc"
        with connect(self.db_url, autocommit=True, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    with ranked_attempts as (
                        select
                            a.*,
                            row_number() over (
                                partition by a.source_id, a.requested_backend
                                order by a.started_at desc, a.attempt_id desc
                            ) as rn
                        from movement_knowledge.rag_analysis_attempts a
                        where a.requested_backend = %s
                    )
                    select
                        attempt_id,
                        source_id,
                        source_url,
                        requested_backend,
                        actual_backend,
                        model_name,
                        status,
                        error_code,
                        error_message,
                        previous_draft_id,
                        new_draft_id,
                        artifact_paths,
                        metadata,
                        started_at,
                        finished_at
                    from ranked_attempts a
                    where a.rn = 1
                      and a.status = 'error'
                      and not exists (
                          select 1
                          from movement_knowledge.rag_knowledge_drafts d
                          where d.source_id = a.source_id
                            and d.is_active = true
                            and d.analysis_provider = 'gemini'
                            and d.analysis_quality = 'premium'
                            and d.created_at >= a.started_at
                      )
                    order by started_at {direction}, attempt_id {direction}
                    limit %s
                    """,
                    (requested_backend, limit),
                )
                return [dict(row) for row in cur.fetchall()]

    def reconcile_resolved_analysis_errors(self, *, requested_backend: str = "gemini_upgrade") -> int:
        """Mark stale error attempts as resolved when a newer active premium Gemini draft exists."""
        from psycopg import connect

        with connect(self.db_url, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    with latest_errors as (
                        select
                            a.attempt_id,
                            a.source_id,
                            a.started_at,
                            row_number() over (
                                partition by a.source_id, a.requested_backend
                                order by a.started_at desc, a.attempt_id desc
                            ) as rn
                        from movement_knowledge.rag_analysis_attempts a
                        where a.requested_backend = %s
                          and a.status = 'error'
                    )
                    update movement_knowledge.rag_analysis_attempts a
                    set status = 'resolved',
                        metadata = coalesce(a.metadata, '{}'::jsonb) || jsonb_build_object(
                            'resolved_by', 'active_premium_gemini_draft',
                            'resolved_at', now()
                        ),
                        finished_at = now()
                    from latest_errors e
                    where a.attempt_id = e.attempt_id
                      and e.rn = 1
                      and exists (
                          select 1
                          from movement_knowledge.rag_knowledge_drafts d
                          where d.source_id = e.source_id
                            and d.is_active = true
                            and d.analysis_provider = 'gemini'
                            and d.analysis_quality = 'premium'
                            and d.created_at >= e.started_at
                      )
                    """,
                    (requested_backend,),
                )
                return cur.rowcount or 0

    def create_analysis_attempt(
        self,
        *,
        source_id: str,
        source_url: str,
        requested_backend: str,
        actual_backend: str,
        model_name: str | None = None,
        previous_draft_id: str | None = None,
        artifact_paths: dict[str, object] | None = None,
        metadata: dict[str, object] | None = None,
    ) -> str:
        """Create one analysis attempt record and return its id."""
        from psycopg import connect
        from src.core.ids import stable_id

        started_at = datetime.now(timezone.utc)
        attempt_id = stable_id(
            "attempt",
            f"{source_id}:{requested_backend}:{actual_backend}:{model_name or ''}:{started_at.isoformat()}",
        )
        with connect(self.db_url, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    insert into movement_knowledge.rag_analysis_attempts (
                        attempt_id,
                        source_id,
                        source_url,
                        requested_backend,
                        actual_backend,
                        model_name,
                        status,
                        previous_draft_id,
                        artifact_paths,
                        metadata,
                        started_at,
                        finished_at
                    ) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        attempt_id,
                        source_id,
                        source_url,
                        requested_backend,
                        actual_backend,
                        model_name,
                        "running",
                        previous_draft_id,
                        Jsonb(artifact_paths or {}),
                        Jsonb(metadata or {}),
                        started_at,
                        started_at,
                    ),
                )
        return attempt_id

    def finish_analysis_attempt(
        self,
        *,
        attempt_id: str,
        status: str,
        promoted_to_active: bool = False,
        usefulness: str | None = None,
        new_draft_id: str | None = None,
        error_code: str | None = None,
        error_message: str | None = None,
        artifact_paths: dict[str, object] | None = None,
        metadata: dict[str, object] | None = None,
    ) -> None:
        """Mark one analysis attempt as finished."""
        from psycopg import connect

        finished_at = datetime.now(timezone.utc)
        with connect(self.db_url, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    update movement_knowledge.rag_analysis_attempts
                    set status = %s,
                        promoted_to_active = %s,
                        usefulness = %s,
                        new_draft_id = %s,
                        error_code = %s,
                        error_message = %s,
                        artifact_paths = coalesce(artifact_paths, '{}'::jsonb) || %s::jsonb,
                        metadata = coalesce(metadata, '{}'::jsonb) || %s::jsonb,
                        finished_at = %s
                    where attempt_id = %s
                    """,
                    (
                        status,
                        promoted_to_active,
                        usefulness,
                        new_draft_id,
                        error_code,
                        error_message,
                        json.dumps(artifact_paths or {}, ensure_ascii=False),
                        json.dumps(metadata or {}, ensure_ascii=False),
                        finished_at,
                        attempt_id,
                    ),
                )

    @staticmethod
    def _make_knowledge_unit_id(source_id: str, draft_id: str, unit_index: int, title: str) -> str:
        from src.core.ids import stable_id

        return stable_id("kunit", f"{source_id}:{draft_id}:{unit_index}:{title}")

    @staticmethod
    def _source_id_from_url(url: str) -> str:
        from src.ingestion.youtube import build_youtube_source

        source = build_youtube_source(uri=url, language_hint="en")
        return source.source_id or ""
