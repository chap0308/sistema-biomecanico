alter table movement_knowledge.rag_knowledge_drafts
    add column if not exists analysis_provider text not null default 'unknown',
    add column if not exists analysis_quality text not null default 'standard',
    add column if not exists is_active boolean not null default true,
    add column if not exists supersedes_draft_id text references movement_knowledge.rag_knowledge_drafts(draft_id),
    add column if not exists superseded_at timestamptz;

create index if not exists idx_rag_knowledge_drafts_provider
    on movement_knowledge.rag_knowledge_drafts(analysis_provider);

create index if not exists idx_rag_knowledge_drafts_quality
    on movement_knowledge.rag_knowledge_drafts(analysis_quality);

create index if not exists idx_rag_knowledge_drafts_is_active
    on movement_knowledge.rag_knowledge_drafts(is_active);

create unique index if not exists uq_rag_knowledge_drafts_active_source
    on movement_knowledge.rag_knowledge_drafts(source_id)
    where is_active;
