create extension if not exists pgcrypto;

create table if not exists movement_knowledge.chat_user_profiles (
    user_id uuid primary key references auth.users (id) on delete cascade,
    display_name text,
    avatar_url text,
    preferred_answer_backend text not null default 'grounded',
    preferred_model_name text,
    preferred_theme text not null default 'system',
    locale text not null default 'es-PE',
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists movement_knowledge.chat_conversations (
    conversation_id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users (id) on delete cascade,
    title text not null default 'Nueva conversación',
    status text not null default 'active',
    selected_backend text not null default 'grounded',
    selected_model text,
    latest_user_message text,
    last_message_at timestamptz,
    archived_at timestamptz,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint chat_conversations_status_check check (status in ('active', 'archived', 'deleted')),
    constraint chat_conversations_backend_check check (selected_backend in ('grounded', 'ollama', 'openai', 'hf', 'auto'))
);

create index if not exists idx_chat_conversations_user_last_message
    on movement_knowledge.chat_conversations (user_id, coalesce(last_message_at, created_at) desc);

create table if not exists movement_knowledge.chat_messages (
    message_id uuid primary key default gen_random_uuid(),
    conversation_id uuid not null references movement_knowledge.chat_conversations (conversation_id) on delete cascade,
    user_id uuid references auth.users (id) on delete set null,
    role text not null,
    status text not null default 'completed',
    content_text text,
    selected_backend text,
    selected_model text,
    retrieval_quality text,
    answer_backend_used text,
    answer_model_used text,
    parent_message_id uuid references movement_knowledge.chat_messages (message_id) on delete set null,
    payload jsonb not null default '{}'::jsonb,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint chat_messages_role_check check (role in ('system', 'user', 'assistant', 'tool')),
    constraint chat_messages_status_check check (status in ('pending', 'streaming', 'completed', 'error'))
);

create index if not exists idx_chat_messages_conversation_created
    on movement_knowledge.chat_messages (conversation_id, created_at asc);

create table if not exists movement_knowledge.chat_message_attachments (
    attachment_id uuid primary key default gen_random_uuid(),
    message_id uuid not null references movement_knowledge.chat_messages (message_id) on delete cascade,
    user_id uuid references auth.users (id) on delete set null,
    attachment_kind text not null,
    storage_bucket text,
    storage_path text,
    local_path text,
    source_url text,
    mime_type text,
    file_name text,
    size_bytes bigint,
    status text not null default 'uploaded',
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint chat_message_attachments_kind_check check (attachment_kind in ('image', 'audio', 'debug_image', 'file')),
    constraint chat_message_attachments_status_check check (status in ('uploaded', 'processing', 'completed', 'error'))
);

create index if not exists idx_chat_message_attachments_message
    on movement_knowledge.chat_message_attachments (message_id, created_at asc);

create table if not exists movement_knowledge.chat_message_analysis_jobs (
    analysis_job_id uuid primary key default gen_random_uuid(),
    conversation_id uuid not null references movement_knowledge.chat_conversations (conversation_id) on delete cascade,
    message_id uuid not null references movement_knowledge.chat_messages (message_id) on delete cascade,
    attachment_id uuid references movement_knowledge.chat_message_attachments (attachment_id) on delete cascade,
    user_id uuid references auth.users (id) on delete set null,
    analysis_kind text not null,
    endpoint_name text,
    status text not null default 'queued',
    detected_deficiencies jsonb not null default '[]'::jsonb,
    metrics_payload jsonb not null default '{}'::jsonb,
    request_payload jsonb not null default '{}'::jsonb,
    response_payload jsonb not null default '{}'::jsonb,
    error_code text,
    error_message text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    completed_at timestamptz,
    constraint chat_message_analysis_jobs_kind_check check (analysis_kind in ('image_metrics', 'audio_transcription', 'debug_overlay')),
    constraint chat_message_analysis_jobs_status_check check (status in ('queued', 'running', 'completed', 'error'))
);

create index if not exists idx_chat_message_analysis_jobs_message
    on movement_knowledge.chat_message_analysis_jobs (message_id, created_at desc);

alter table movement_knowledge.chat_user_profiles enable row level security;
alter table movement_knowledge.chat_conversations enable row level security;
alter table movement_knowledge.chat_messages enable row level security;
alter table movement_knowledge.chat_message_attachments enable row level security;
alter table movement_knowledge.chat_message_analysis_jobs enable row level security;

drop policy if exists "chat_user_profiles_select_own" on movement_knowledge.chat_user_profiles;
create policy "chat_user_profiles_select_own"
    on movement_knowledge.chat_user_profiles
    for select
    using (auth.uid() = user_id);

drop policy if exists "chat_user_profiles_upsert_own" on movement_knowledge.chat_user_profiles;
create policy "chat_user_profiles_upsert_own"
    on movement_knowledge.chat_user_profiles
    for all
    using (auth.uid() = user_id)
    with check (auth.uid() = user_id);

drop policy if exists "chat_conversations_select_own" on movement_knowledge.chat_conversations;
create policy "chat_conversations_select_own"
    on movement_knowledge.chat_conversations
    for select
    using (auth.uid() = user_id);

drop policy if exists "chat_conversations_write_own" on movement_knowledge.chat_conversations;
create policy "chat_conversations_write_own"
    on movement_knowledge.chat_conversations
    for all
    using (auth.uid() = user_id)
    with check (auth.uid() = user_id);

drop policy if exists "chat_messages_select_own" on movement_knowledge.chat_messages;
create policy "chat_messages_select_own"
    on movement_knowledge.chat_messages
    for select
    using (
        exists (
            select 1
            from movement_knowledge.chat_conversations c
            where c.conversation_id = chat_messages.conversation_id
              and c.user_id = auth.uid()
        )
    );

drop policy if exists "chat_messages_write_own" on movement_knowledge.chat_messages;
create policy "chat_messages_write_own"
    on movement_knowledge.chat_messages
    for all
    using (
        exists (
            select 1
            from movement_knowledge.chat_conversations c
            where c.conversation_id = chat_messages.conversation_id
              and c.user_id = auth.uid()
        )
    )
    with check (
        exists (
            select 1
            from movement_knowledge.chat_conversations c
            where c.conversation_id = chat_messages.conversation_id
              and c.user_id = auth.uid()
        )
    );

drop policy if exists "chat_message_attachments_select_own" on movement_knowledge.chat_message_attachments;
create policy "chat_message_attachments_select_own"
    on movement_knowledge.chat_message_attachments
    for select
    using (
        exists (
            select 1
            from movement_knowledge.chat_messages m
            join movement_knowledge.chat_conversations c
              on c.conversation_id = m.conversation_id
            where m.message_id = chat_message_attachments.message_id
              and c.user_id = auth.uid()
        )
    );

drop policy if exists "chat_message_attachments_write_own" on movement_knowledge.chat_message_attachments;
create policy "chat_message_attachments_write_own"
    on movement_knowledge.chat_message_attachments
    for all
    using (
        exists (
            select 1
            from movement_knowledge.chat_messages m
            join movement_knowledge.chat_conversations c
              on c.conversation_id = m.conversation_id
            where m.message_id = chat_message_attachments.message_id
              and c.user_id = auth.uid()
        )
    )
    with check (
        exists (
            select 1
            from movement_knowledge.chat_messages m
            join movement_knowledge.chat_conversations c
              on c.conversation_id = m.conversation_id
            where m.message_id = chat_message_attachments.message_id
              and c.user_id = auth.uid()
        )
    );

drop policy if exists "chat_message_analysis_jobs_select_own" on movement_knowledge.chat_message_analysis_jobs;
create policy "chat_message_analysis_jobs_select_own"
    on movement_knowledge.chat_message_analysis_jobs
    for select
    using (
        exists (
            select 1
            from movement_knowledge.chat_conversations c
            where c.conversation_id = chat_message_analysis_jobs.conversation_id
              and c.user_id = auth.uid()
        )
    );

drop policy if exists "chat_message_analysis_jobs_write_own" on movement_knowledge.chat_message_analysis_jobs;
create policy "chat_message_analysis_jobs_write_own"
    on movement_knowledge.chat_message_analysis_jobs
    for all
    using (
        exists (
            select 1
            from movement_knowledge.chat_conversations c
            where c.conversation_id = chat_message_analysis_jobs.conversation_id
              and c.user_id = auth.uid()
        )
    )
    with check (
        exists (
            select 1
            from movement_knowledge.chat_conversations c
            where c.conversation_id = chat_message_analysis_jobs.conversation_id
              and c.user_id = auth.uid()
        )
    );
