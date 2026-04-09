create table if not exists movement_knowledge.rag_sources (
  source_id text primary key,
  source_type text not null,
  uri text not null,
  canonical_uri text not null,
  title text,
  channel_or_author text,
  language_hint text not null default 'es',
  course_id text not null default 'biomechanics_knowledge_v1',
  tags text[] not null default '{}'::text[],
  duration_sec double precision,
  ingest_status text not null default 'discovered',
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_mk_rag_sources_type on movement_knowledge.rag_sources (source_type);
create index if not exists idx_mk_rag_sources_course on movement_knowledge.rag_sources (course_id);
create index if not exists idx_mk_rag_sources_tags on movement_knowledge.rag_sources using gin (tags);

create table if not exists movement_knowledge.rag_assets (
  asset_id text primary key,
  source_id text not null references movement_knowledge.rag_sources(source_id) on delete cascade,
  kind text not null,
  path text not null,
  mime_type text not null,
  start_sec double precision not null default 0.0,
  end_sec double precision,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_mk_rag_assets_source on movement_knowledge.rag_assets (source_id);
create index if not exists idx_mk_rag_assets_kind on movement_knowledge.rag_assets (kind);

create table if not exists movement_knowledge.rag_segments (
  segment_id text primary key,
  source_id text not null references movement_knowledge.rag_sources(source_id) on delete cascade,
  segment_index integer not null,
  start_sec double precision not null,
  end_sec double precision not null,
  duration_sec double precision not null,
  transcript text not null default '',
  ocr_text text not null default '',
  visual_description text not null default '',
  segment_summary text not null default '',
  topics text[] not null default '{}'::text[],
  keywords text[] not null default '{}'::text[],
  entities text[] not null default '{}'::text[],
  speaker text,
  language text not null default 'es',
  confidence jsonb not null default '{}'::jsonb,
  frame_refs jsonb not null default '[]'::jsonb,
  retrieval_text text not null default '',
  payload jsonb not null default '{}'::jsonb,
  content_sha256 text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (source_id, segment_index),
  unique (content_sha256)
);

create index if not exists idx_mk_rag_segments_source on movement_knowledge.rag_segments (source_id);
create index if not exists idx_mk_rag_segments_language on movement_knowledge.rag_segments (language);
create index if not exists idx_mk_rag_segments_topics on movement_knowledge.rag_segments using gin (topics);
create index if not exists idx_mk_rag_segments_keywords on movement_knowledge.rag_segments using gin (keywords);
create index if not exists idx_mk_rag_segments_retrieval_text on movement_knowledge.rag_segments using gin (retrieval_text gin_trgm_ops);

create trigger trg_mk_rag_sources_updated_at
before update on movement_knowledge.rag_sources
for each row
execute function movement_knowledge.set_updated_at();

create trigger trg_mk_rag_assets_updated_at
before update on movement_knowledge.rag_assets
for each row
execute function movement_knowledge.set_updated_at();

create trigger trg_mk_rag_segments_updated_at
before update on movement_knowledge.rag_segments
for each row
execute function movement_knowledge.set_updated_at();
