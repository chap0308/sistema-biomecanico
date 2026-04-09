create table if not exists movement_knowledge.rag_analysis_attempts (
    attempt_id text primary key,
    source_id text not null references movement_knowledge.rag_sources(source_id) on delete cascade,
    source_url text not null,
    requested_backend text not null,
    actual_backend text not null,
    model_name text,
    status text not null,
    promoted_to_active boolean not null default false,
    usefulness text,
    previous_draft_id text,
    new_draft_id text,
    error_code text,
    error_message text,
    artifact_paths jsonb not null default '{}'::jsonb,
    metadata jsonb not null default '{}'::jsonb,
    started_at timestamptz not null default now(),
    finished_at timestamptz not null default now()
);

create index if not exists idx_rag_analysis_attempts_source_id
    on movement_knowledge.rag_analysis_attempts(source_id, started_at desc);

create index if not exists idx_rag_analysis_attempts_status
    on movement_knowledge.rag_analysis_attempts(status, started_at desc);

create index if not exists idx_rag_analysis_attempts_backend
    on movement_knowledge.rag_analysis_attempts(requested_backend, actual_backend, started_at desc);
