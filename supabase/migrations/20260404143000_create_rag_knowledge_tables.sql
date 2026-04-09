create table if not exists movement_knowledge.rag_knowledge_drafts (
    draft_id text primary key,
    source_id text not null references movement_knowledge.rag_sources(source_id) on delete cascade,
    source_url text not null,
    source_title_hint text not null default '',
    analysis_origin text not null,
    primary_summary text not null default '',
    classification jsonb not null default '{}'::jsonb,
    searchable_topics text[] not null default '{}',
    searchable_tags text[] not null default '{}',
    problem_statements text[] not null default '{}',
    habits_or_contexts text[] not null default '{}',
    key_visual_points text[] not null default '{}',
    tests_mentioned text[] not null default '{}',
    exercises_mentioned text[] not null default '{}',
    advice_mentioned text[] not null default '{}',
    warnings_or_limitations text[] not null default '{}',
    analysis_report jsonb not null default '{}'::jsonb,
    source_artifacts jsonb not null default '{}'::jsonb,
    raw_payload jsonb not null default '{}'::jsonb,
    content_sha256 text not null unique,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists movement_knowledge.rag_knowledge_units (
    unit_id text primary key,
    draft_id text not null references movement_knowledge.rag_knowledge_drafts(draft_id) on delete cascade,
    source_id text not null references movement_knowledge.rag_sources(source_id) on delete cascade,
    unit_index integer not null,
    unit_type text not null,
    title text not null,
    summary text not null default '',
    observable_signs text[] not null default '{}',
    mechanisms text[] not null default '{}',
    execution_steps text[] not null default '{}',
    cues text[] not null default '{}',
    breathing_cues text[] not null default '{}',
    errors_to_avoid text[] not null default '{}',
    when_useful text[] not null default '{}',
    when_not_useful text[] not null default '{}',
    retest text[] not null default '{}',
    advice text[] not null default '{}',
    timestamps text[] not null default '{}',
    raw_payload jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (draft_id, unit_index)
);

create index if not exists idx_rag_knowledge_drafts_source_id
    on movement_knowledge.rag_knowledge_drafts(source_id);

create index if not exists idx_rag_knowledge_drafts_analysis_origin
    on movement_knowledge.rag_knowledge_drafts(analysis_origin);

create index if not exists idx_rag_knowledge_units_source_id
    on movement_knowledge.rag_knowledge_units(source_id);

create index if not exists idx_rag_knowledge_units_unit_type
    on movement_knowledge.rag_knowledge_units(unit_type);
