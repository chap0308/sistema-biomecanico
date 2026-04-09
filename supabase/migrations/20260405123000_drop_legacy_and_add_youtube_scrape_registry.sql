drop view if exists movement_knowledge.v_protocol_candidates;
drop view if exists movement_knowledge.v_useful_analyses;

drop table if exists movement_knowledge.import_jobs cascade;
drop table if exists movement_knowledge.knowledge_units cascade;
drop table if exists movement_knowledge.video_analyses cascade;
drop table if exists movement_knowledge.source_videos cascade;
drop table if exists movement_knowledge.taxonomy_terms cascade;

create table if not exists movement_knowledge.youtube_channels (
    channel_id text primary key,
    channel_url text not null unique,
    canonical_channel_url text not null,
    title text,
    metadata jsonb not null default '{}'::jsonb,
    last_scraped_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists movement_knowledge.youtube_scrape_runs (
    run_id text primary key,
    channel_id text not null references movement_knowledge.youtube_channels(channel_id) on delete cascade,
    channel_url text not null,
    scrape_order text not null,
    scrape_limit integer not null,
    browser_channel text,
    total_found integer not null default 0,
    new_found integer not null default 0,
    metadata jsonb not null default '{}'::jsonb,
    scraped_at timestamptz not null default now()
);

create table if not exists movement_knowledge.youtube_scrape_items (
    item_id text primary key,
    run_id text not null references movement_knowledge.youtube_scrape_runs(run_id) on delete cascade,
    channel_id text not null references movement_knowledge.youtube_channels(channel_id) on delete cascade,
    video_id text not null,
    video_url text not null,
    canonical_video_url text not null,
    source_id text not null,
    title text,
    views_label text,
    order_index integer not null,
    was_known boolean not null default false,
    has_active_draft boolean not null default false,
    first_discovered_at timestamptz not null default now(),
    last_seen_at timestamptz not null default now(),
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique(channel_id, video_id)
);

create index if not exists idx_youtube_scrape_runs_channel_id
    on movement_knowledge.youtube_scrape_runs(channel_id, scraped_at desc);

create index if not exists idx_youtube_scrape_items_source_id
    on movement_knowledge.youtube_scrape_items(source_id);

create index if not exists idx_youtube_scrape_items_active_draft
    on movement_knowledge.youtube_scrape_items(has_active_draft);
