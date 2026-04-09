"""Supabase-backed registry for YouTube Shorts scraping runs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from psycopg.types.json import Jsonb

from src.core.ids import stable_id
from src.ingestion.youtube import build_youtube_source
from video.movement_knowledge_import import get_database_url
from video.youtube_shorts import ShortsVideo, normalize_channel_shorts_url


@dataclass(slots=True)
class ScrapeSelection:
    videos: list[ShortsVideo]
    analyzed_video_ids: set[str]
    pending_videos: list[ShortsVideo]


class YoutubeScrapeStore:
    """Persist scrape runs and ask Supabase which videos already have active drafts."""

    def __init__(self, db_url: str | None = None) -> None:
        self.db_url = db_url or get_database_url()

    def record_scrape_run(
        self,
        *,
        channel_url: str,
        order: str,
        limit: int,
        browser_channel: str,
        videos: list[ShortsVideo],
    ) -> dict[str, object]:
        from psycopg import connect
        from psycopg.rows import dict_row

        canonical_channel_url = normalize_channel_shorts_url(channel_url)
        channel_id = stable_id("ychan", canonical_channel_url)
        run_id = stable_id("yscrape", f"{canonical_channel_url}:{order}:{limit}:{len(videos)}:{videos[0].video_id if videos else 'empty'}")
        source_map = {video.video_id: build_youtube_source(uri=video.url, title=video.title, language_hint="en") for video in videos}
        source_ids = [source.source_id for source in source_map.values()]
        active_source_ids = self._fetch_active_source_ids(source_ids)

        with connect(self.db_url, autocommit=False, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    insert into movement_knowledge.youtube_channels (
                        channel_id, channel_url, canonical_channel_url, last_scraped_at
                    ) values (%s, %s, %s, now())
                    on conflict (channel_id) do update set
                        channel_url = excluded.channel_url,
                        canonical_channel_url = excluded.canonical_channel_url,
                        last_scraped_at = now(),
                        updated_at = now()
                    """,
                    (channel_id, channel_url, canonical_channel_url),
                )
                cur.execute(
                    """
                    insert into movement_knowledge.youtube_scrape_runs (
                        run_id, channel_id, channel_url, scrape_order, scrape_limit, browser_channel, total_found, new_found, metadata
                    ) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    on conflict (run_id) do update set
                        total_found = excluded.total_found,
                        new_found = excluded.new_found,
                        metadata = excluded.metadata
                    """,
                    (
                        run_id,
                        channel_id,
                        channel_url,
                        order,
                        limit,
                        browser_channel,
                        len(videos),
                        sum(1 for video in videos if source_map[video.video_id].source_id not in active_source_ids),
                        Jsonb({"video_ids": [video.video_id for video in videos]}),
                    ),
                )
                for video in videos:
                    source = source_map[video.video_id]
                    has_active_draft = source.source_id in active_source_ids
                    item_id = stable_id("yscrapeitem", f"{channel_id}:{video.video_id}")
                    cur.execute(
                        """
                        insert into movement_knowledge.youtube_scrape_items (
                            item_id,
                            run_id,
                            channel_id,
                            video_id,
                            video_url,
                            canonical_video_url,
                            source_id,
                            title,
                            views_label,
                            order_index,
                            was_known,
                            has_active_draft,
                            metadata
                        ) values (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        on conflict (channel_id, video_id) do update set
                            run_id = excluded.run_id,
                            video_url = excluded.video_url,
                            canonical_video_url = excluded.canonical_video_url,
                            source_id = excluded.source_id,
                            title = excluded.title,
                            views_label = excluded.views_label,
                            order_index = excluded.order_index,
                            was_known = excluded.was_known,
                            has_active_draft = excluded.has_active_draft,
                            metadata = excluded.metadata,
                            last_seen_at = now(),
                            updated_at = now()
                        """,
                        (
                            item_id,
                            run_id,
                            channel_id,
                            video.video_id,
                            video.url,
                            source.canonical_uri or source.uri,
                            source.source_id,
                            video.title,
                            video.views_label,
                            video.order_index,
                            has_active_draft,
                            has_active_draft,
                            Jsonb({"channel_url": channel_url}),
                        ),
                    )
            conn.commit()

        return {
            "channel_id": channel_id,
            "run_id": run_id,
            "analyzed_video_ids": {video.video_id for video in videos if source_map[video.video_id].source_id in active_source_ids},
            "pending_videos": [video for video in videos if source_map[video.video_id].source_id not in active_source_ids],
        }

    def select_pending(self, videos: Iterable[ShortsVideo]) -> ScrapeSelection:
        video_list = list(videos)
        source_map = {video.video_id: build_youtube_source(uri=video.url, title=video.title, language_hint="en") for video in video_list}
        active_source_ids = self._fetch_active_source_ids([source.source_id for source in source_map.values()])
        analyzed_ids = {video.video_id for video in video_list if source_map[video.video_id].source_id in active_source_ids}
        pending = [video for video in video_list if video.video_id not in analyzed_ids]
        return ScrapeSelection(videos=video_list, analyzed_video_ids=analyzed_ids, pending_videos=pending)

    def refresh_active_draft_flags(self, video_ids: list[str]) -> None:
        """Refresh has_active_draft for known scrape items after analysis completes."""
        from psycopg import connect
        from psycopg.rows import dict_row

        if not video_ids:
            return
        with connect(self.db_url, autocommit=False, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select video_id, source_id
                    from movement_knowledge.youtube_scrape_items
                    where video_id = any(%s)
                    """,
                    (video_ids,),
                )
                rows = cur.fetchall()
                source_ids = [str(row["source_id"]) for row in rows]
                active_source_ids = self._fetch_active_source_ids(source_ids)
                for row in rows:
                    has_active = str(row["source_id"]) in active_source_ids
                    cur.execute(
                        """
                        update movement_knowledge.youtube_scrape_items
                        set has_active_draft = %s,
                            was_known = %s,
                            updated_at = now()
                        where video_id = %s
                        """,
                        (has_active, has_active, str(row["video_id"])),
                    )
            conn.commit()

    def _fetch_active_source_ids(self, source_ids: list[str]) -> set[str]:
        from psycopg import connect

        if not source_ids:
            return set()
        with connect(self.db_url, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select distinct source_id
                    from movement_knowledge.rag_knowledge_drafts
                    where source_id = any(%s)
                      and is_active = true
                    """,
                    (source_ids,),
                )
                return {str(row[0]) for row in cur.fetchall()}
