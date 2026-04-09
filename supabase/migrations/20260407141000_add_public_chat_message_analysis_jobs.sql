create table if not exists public.chat_message_analysis_jobs (
    analysis_job_id uuid primary key default gen_random_uuid(),
    conversation_id uuid not null references public.chat_conversations (conversation_id) on delete cascade,
    message_id uuid not null references public.chat_messages (message_id) on delete cascade,
    attachment_id uuid references public.chat_message_attachments (attachment_id) on delete cascade,
    user_id uuid references auth.users (id) on delete set null,
    analysis_kind text not null check (analysis_kind in ('image_metrics', 'audio_transcription', 'debug_overlay')),
    endpoint_name text,
    status text not null default 'queued' check (status in ('queued', 'running', 'completed', 'error')),
    detected_deficiencies jsonb not null default '[]'::jsonb,
    metrics_payload jsonb not null default '{}'::jsonb,
    request_payload jsonb not null default '{}'::jsonb,
    response_payload jsonb not null default '{}'::jsonb,
    error_code text,
    error_message text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    completed_at timestamptz
);

create index if not exists chat_message_analysis_jobs_message_id_idx
    on public.chat_message_analysis_jobs (message_id, created_at desc);

drop trigger if exists set_chat_message_analysis_jobs_updated_at on public.chat_message_analysis_jobs;
create trigger set_chat_message_analysis_jobs_updated_at
before update on public.chat_message_analysis_jobs
for each row
execute function public.set_updated_at();

alter table public.chat_message_analysis_jobs enable row level security;

drop policy if exists chat_message_analysis_jobs_select_own on public.chat_message_analysis_jobs;
create policy chat_message_analysis_jobs_select_own
on public.chat_message_analysis_jobs
for select
to authenticated
using (
    exists (
        select 1
        from public.chat_conversations c
        where c.conversation_id = chat_message_analysis_jobs.conversation_id
          and c.user_id = auth.uid()
    )
);

drop policy if exists chat_message_analysis_jobs_insert_own on public.chat_message_analysis_jobs;
create policy chat_message_analysis_jobs_insert_own
on public.chat_message_analysis_jobs
for insert
to authenticated
with check (
    exists (
        select 1
        from public.chat_conversations c
        where c.conversation_id = chat_message_analysis_jobs.conversation_id
          and c.user_id = auth.uid()
    )
);

drop policy if exists chat_message_analysis_jobs_update_own on public.chat_message_analysis_jobs;
create policy chat_message_analysis_jobs_update_own
on public.chat_message_analysis_jobs
for update
to authenticated
using (
    exists (
        select 1
        from public.chat_conversations c
        where c.conversation_id = chat_message_analysis_jobs.conversation_id
          and c.user_id = auth.uid()
    )
)
with check (
    exists (
        select 1
        from public.chat_conversations c
        where c.conversation_id = chat_message_analysis_jobs.conversation_id
          and c.user_id = auth.uid()
    )
);
