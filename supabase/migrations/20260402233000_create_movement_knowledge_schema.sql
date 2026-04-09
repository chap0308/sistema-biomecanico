create extension if not exists pgcrypto;
create extension if not exists pg_trgm;

create schema if not exists movement_knowledge;

create or replace function movement_knowledge.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create table if not exists movement_knowledge.import_jobs (
  id uuid primary key default gen_random_uuid(),
  importer_name text not null,
  dataset_name text not null,
  source_root text,
  started_at timestamptz not null default now(),
  completed_at timestamptz,
  status text not null default 'running',
  files_discovered integer not null default 0,
  files_inserted integer not null default 0,
  files_skipped integer not null default 0,
  files_failed integer not null default 0,
  metadata jsonb not null default '{}'::jsonb
);

create table if not exists movement_knowledge.source_videos (
  id uuid primary key default gen_random_uuid(),
  external_video_id text not null,
  source_type text not null,
  source_url text not null unique,
  canonical_url text not null,
  title_hint text not null default '',
  creator_name text,
  channel_url text,
  language_code text,
  published_at timestamptz,
  latest_analysis_id uuid,
  source_metadata jsonb not null default '{}'::jsonb,
  first_seen_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_mk_source_videos_external_video_id on movement_knowledge.source_videos (external_video_id);
create index if not exists idx_mk_source_videos_source_type on movement_knowledge.source_videos (source_type);
create index if not exists idx_mk_source_videos_title_trgm on movement_knowledge.source_videos using gin (title_hint gin_trgm_ops);

create table if not exists movement_knowledge.video_analyses (
  id uuid primary key default gen_random_uuid(),
  source_video_id uuid not null references movement_knowledge.source_videos(id) on delete cascade,
  import_job_id uuid references movement_knowledge.import_jobs(id) on delete set null,
  dataset_name text not null default 'movement_knowledge_base',
  analysis_origin text not null,
  source_file_path text,
  source_file_name text,
  content_sha256 text not null unique,
  model_name text,
  analysis_schema_version text not null default 'gemini_video_analysis_v1',
  prompt_version text,
  primary_summary text not null,
  usefulness text not null,
  usefulness_reason text not null default '',
  exclusion_reason text,
  content_kind text not null,
  confidence text not null default '',
  suitable_for_protocol_database boolean not null default false,
  suitable_for_concept_knowledge_base boolean not null default false,
  suitable_for_recommendation_mapping boolean not null default false,
  contains_visual_execution_detail boolean not null default false,
  visual_validation_level text not null default 'ai_visual_review',
  review_status text not null default 'draft',
  body_regions text[] not null default '{}'::text[],
  problem_layers text[] not null default '{}'::text[],
  searchable_topics text[] not null default '{}'::text[],
  searchable_tags text[] not null default '{}'::text[],
  problem_statements text[] not null default '{}'::text[],
  habits_or_contexts text[] not null default '{}'::text[],
  key_visual_points text[] not null default '{}'::text[],
  tests_mentioned text[] not null default '{}'::text[],
  exercises_mentioned text[] not null default '{}'::text[],
  advice_mentioned text[] not null default '{}'::text[],
  warnings_or_limitations text[] not null default '{}'::text[],
  raw_payload jsonb not null default '{}'::jsonb,
  normalized_payload jsonb not null default '{}'::jsonb,
  extra_payload jsonb not null default '{}'::jsonb,
  analyzed_at timestamptz,
  imported_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table movement_knowledge.source_videos
  add constraint fk_mk_source_videos_latest_analysis
  foreign key (latest_analysis_id)
  references movement_knowledge.video_analyses(id)
  on delete set null;

create index if not exists idx_mk_video_analyses_source_video_id on movement_knowledge.video_analyses (source_video_id);
create index if not exists idx_mk_video_analyses_import_job_id on movement_knowledge.video_analyses (import_job_id);
create index if not exists idx_mk_video_analyses_usefulness on movement_knowledge.video_analyses (usefulness);
create index if not exists idx_mk_video_analyses_content_kind on movement_knowledge.video_analyses (content_kind);
create index if not exists idx_mk_video_analyses_review_status on movement_knowledge.video_analyses (review_status);
create index if not exists idx_mk_video_analyses_protocol_bool on movement_knowledge.video_analyses (suitable_for_protocol_database);
create index if not exists idx_mk_video_analyses_regions_gin on movement_knowledge.video_analyses using gin (body_regions);
create index if not exists idx_mk_video_analyses_layers_gin on movement_knowledge.video_analyses using gin (problem_layers);
create index if not exists idx_mk_video_analyses_tags_gin on movement_knowledge.video_analyses using gin (searchable_tags);
create index if not exists idx_mk_video_analyses_topics_gin on movement_knowledge.video_analyses using gin (searchable_topics);
create index if not exists idx_mk_video_analyses_summary_trgm on movement_knowledge.video_analyses using gin (primary_summary gin_trgm_ops);
create index if not exists idx_mk_video_analyses_raw_payload_gin on movement_knowledge.video_analyses using gin (raw_payload jsonb_path_ops);

create table if not exists movement_knowledge.knowledge_units (
  id uuid primary key default gen_random_uuid(),
  analysis_id uuid not null references movement_knowledge.video_analyses(id) on delete cascade,
  ordinal integer not null,
  unit_type text not null,
  title text not null,
  summary text not null,
  observable_signs text[] not null default '{}'::text[],
  mechanisms text[] not null default '{}'::text[],
  execution_steps text[] not null default '{}'::text[],
  cues text[] not null default '{}'::text[],
  breathing_cues text[] not null default '{}'::text[],
  errors_to_avoid text[] not null default '{}'::text[],
  when_useful text[] not null default '{}'::text[],
  when_not_useful text[] not null default '{}'::text[],
  retest text[] not null default '{}'::text[],
  advice text[] not null default '{}'::text[],
  timestamps text[] not null default '{}'::text[],
  extra_payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (analysis_id, ordinal)
);

create index if not exists idx_mk_knowledge_units_analysis_id on movement_knowledge.knowledge_units (analysis_id);
create index if not exists idx_mk_knowledge_units_unit_type on movement_knowledge.knowledge_units (unit_type);
create index if not exists idx_mk_knowledge_units_title_trgm on movement_knowledge.knowledge_units using gin (title gin_trgm_ops);
create index if not exists idx_mk_knowledge_units_summary_trgm on movement_knowledge.knowledge_units using gin (summary gin_trgm_ops);
create index if not exists idx_mk_knowledge_units_exec_steps_gin on movement_knowledge.knowledge_units using gin (execution_steps);

create table if not exists movement_knowledge.taxonomy_terms (
  id uuid primary key default gen_random_uuid(),
  namespace text not null,
  value text not null,
  normalized_value text not null,
  usage_count integer not null default 1,
  first_seen_at timestamptz not null default now(),
  last_seen_at timestamptz not null default now(),
  sample_source_video_id uuid references movement_knowledge.source_videos(id) on delete set null,
  metadata jsonb not null default '{}'::jsonb,
  unique (namespace, normalized_value)
);

create index if not exists idx_mk_taxonomy_namespace on movement_knowledge.taxonomy_terms (namespace);
create index if not exists idx_mk_taxonomy_value_trgm on movement_knowledge.taxonomy_terms using gin (value gin_trgm_ops);

create trigger trg_mk_source_videos_updated_at
before update on movement_knowledge.source_videos
for each row
execute function movement_knowledge.set_updated_at();

create trigger trg_mk_video_analyses_updated_at
before update on movement_knowledge.video_analyses
for each row
execute function movement_knowledge.set_updated_at();

create trigger trg_mk_knowledge_units_updated_at
before update on movement_knowledge.knowledge_units
for each row
execute function movement_knowledge.set_updated_at();

create or replace view movement_knowledge.v_useful_analyses as
select
  va.id as analysis_id,
  sv.external_video_id,
  sv.source_url,
  sv.title_hint,
  va.content_kind,
  va.body_regions,
  va.problem_layers,
  va.primary_summary,
  va.suitable_for_protocol_database,
  va.suitable_for_concept_knowledge_base,
  va.suitable_for_recommendation_mapping,
  va.visual_validation_level,
  va.review_status,
  va.imported_at
from movement_knowledge.video_analyses va
join movement_knowledge.source_videos sv on sv.id = va.source_video_id
where va.usefulness in ('useful', 'maybe_useful');

create or replace view movement_knowledge.v_protocol_candidates as
select
  va.id as analysis_id,
  sv.external_video_id,
  sv.source_url,
  sv.title_hint,
  va.content_kind,
  va.body_regions,
  va.problem_layers,
  va.primary_summary,
  ku.id as knowledge_unit_id,
  ku.unit_type,
  ku.title as unit_title,
  ku.summary as unit_summary,
  ku.execution_steps,
  ku.cues,
  ku.breathing_cues,
  ku.retest
from movement_knowledge.video_analyses va
join movement_knowledge.source_videos sv on sv.id = va.source_video_id
left join movement_knowledge.knowledge_units ku on ku.analysis_id = va.id
where va.usefulness in ('useful', 'maybe_useful')
  and va.suitable_for_protocol_database = true;
