create extension if not exists "pgcrypto";

create table if not exists public.profiles (
    user_id uuid primary key references auth.users(id) on delete cascade,
    email text,
    display_name text,
    avatar_url text,
    preferred_theme text not null default 'system' check (preferred_theme in ('light', 'dark', 'system')),
    preferred_model_key text,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.chat_models (
    model_key text primary key,
    provider text not null,
    display_name text not null,
    description text,
    answer_backend text not null,
    answer_model text,
    is_active boolean not null default true,
    is_default boolean not null default false,
    supports_images boolean not null default false,
    supports_audio boolean not null default false,
    supports_reasoning boolean not null default false,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.chat_conversations (
    conversation_id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    title text not null default 'Nueva conversación',
    selected_model_key text references public.chat_models(model_key),
    conversation_status text not null default 'active' check (conversation_status in ('active', 'archived', 'deleted')),
    last_message_preview text,
    last_message_at timestamptz,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists chat_conversations_user_id_idx
    on public.chat_conversations(user_id, last_message_at desc nulls last, created_at desc);

create table if not exists public.chat_messages (
    message_id uuid primary key default gen_random_uuid(),
    conversation_id uuid not null references public.chat_conversations(conversation_id) on delete cascade,
    user_id uuid references auth.users(id) on delete set null,
    role text not null check (role in ('system', 'user', 'assistant', 'tool')),
    message_kind text not null default 'chat' check (message_kind in ('chat', 'analysis', 'status', 'error')),
    content_text text,
    rendered_blocks jsonb not null default '[]'::jsonb,
    input_context jsonb not null default '{}'::jsonb,
    output_context jsonb not null default '{}'::jsonb,
    selected_model_key text references public.chat_models(model_key),
    processing_status text not null default 'completed' check (processing_status in ('queued', 'processing', 'completed', 'failed')),
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists chat_messages_conversation_id_idx
    on public.chat_messages(conversation_id, created_at asc);

create table if not exists public.chat_message_attachments (
    attachment_id uuid primary key default gen_random_uuid(),
    message_id uuid not null references public.chat_messages(message_id) on delete cascade,
    attachment_kind text not null check (attachment_kind in ('image', 'audio', 'video', 'document', 'debug_image')),
    storage_provider text not null default 'local_ref' check (storage_provider in ('local_ref', 'supabase_storage', 'external_url', 'base64_inline')),
    original_filename text,
    mime_type text,
    file_size_bytes bigint,
    storage_path text,
    public_url text,
    thumbnail_url text,
    analysis_status text not null default 'pending' check (analysis_status in ('pending', 'processing', 'completed', 'failed', 'skipped')),
    analysis_payload jsonb not null default '{}'::jsonb,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists chat_message_attachments_message_id_idx
    on public.chat_message_attachments(message_id, created_at asc);

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

drop trigger if exists set_profiles_updated_at on public.profiles;
create trigger set_profiles_updated_at
before update on public.profiles
for each row
execute function public.set_updated_at();

drop trigger if exists set_chat_models_updated_at on public.chat_models;
create trigger set_chat_models_updated_at
before update on public.chat_models
for each row
execute function public.set_updated_at();

drop trigger if exists set_chat_conversations_updated_at on public.chat_conversations;
create trigger set_chat_conversations_updated_at
before update on public.chat_conversations
for each row
execute function public.set_updated_at();

drop trigger if exists set_chat_messages_updated_at on public.chat_messages;
create trigger set_chat_messages_updated_at
before update on public.chat_messages
for each row
execute function public.set_updated_at();

drop trigger if exists set_chat_message_attachments_updated_at on public.chat_message_attachments;
create trigger set_chat_message_attachments_updated_at
before update on public.chat_message_attachments
for each row
execute function public.set_updated_at();

create or replace function public.handle_new_profile()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
    insert into public.profiles (user_id, email, display_name)
    values (
        new.id,
        new.email,
        coalesce(new.raw_user_meta_data ->> 'display_name', split_part(coalesce(new.email, ''), '@', 1))
    )
    on conflict (user_id) do nothing;
    return new;
end;
$$;

drop trigger if exists on_auth_user_created_profile on auth.users;
create trigger on_auth_user_created_profile
after insert on auth.users
for each row
execute function public.handle_new_profile();

alter table public.profiles enable row level security;
alter table public.chat_models enable row level security;
alter table public.chat_conversations enable row level security;
alter table public.chat_messages enable row level security;
alter table public.chat_message_attachments enable row level security;

drop policy if exists profiles_select_own on public.profiles;
create policy profiles_select_own
on public.profiles
for select
to authenticated
using (auth.uid() = user_id);

drop policy if exists profiles_update_own on public.profiles;
create policy profiles_update_own
on public.profiles
for update
to authenticated
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

drop policy if exists profiles_insert_own on public.profiles;
create policy profiles_insert_own
on public.profiles
for insert
to authenticated
with check (auth.uid() = user_id);

drop policy if exists chat_models_read_active on public.chat_models;
create policy chat_models_read_active
on public.chat_models
for select
to authenticated
using (is_active = true);

drop policy if exists chat_conversations_select_own on public.chat_conversations;
create policy chat_conversations_select_own
on public.chat_conversations
for select
to authenticated
using (auth.uid() = user_id);

drop policy if exists chat_conversations_insert_own on public.chat_conversations;
create policy chat_conversations_insert_own
on public.chat_conversations
for insert
to authenticated
with check (auth.uid() = user_id);

drop policy if exists chat_conversations_update_own on public.chat_conversations;
create policy chat_conversations_update_own
on public.chat_conversations
for update
to authenticated
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

drop policy if exists chat_conversations_delete_own on public.chat_conversations;
create policy chat_conversations_delete_own
on public.chat_conversations
for delete
to authenticated
using (auth.uid() = user_id);

drop policy if exists chat_messages_select_own on public.chat_messages;
create policy chat_messages_select_own
on public.chat_messages
for select
to authenticated
using (
    exists (
        select 1
        from public.chat_conversations c
        where c.conversation_id = chat_messages.conversation_id
          and c.user_id = auth.uid()
    )
);

drop policy if exists chat_messages_insert_own on public.chat_messages;
create policy chat_messages_insert_own
on public.chat_messages
for insert
to authenticated
with check (
    exists (
        select 1
        from public.chat_conversations c
        where c.conversation_id = chat_messages.conversation_id
          and c.user_id = auth.uid()
    )
);

drop policy if exists chat_messages_update_own on public.chat_messages;
create policy chat_messages_update_own
on public.chat_messages
for update
to authenticated
using (
    exists (
        select 1
        from public.chat_conversations c
        where c.conversation_id = chat_messages.conversation_id
          and c.user_id = auth.uid()
    )
)
with check (
    exists (
        select 1
        from public.chat_conversations c
        where c.conversation_id = chat_messages.conversation_id
          and c.user_id = auth.uid()
    )
);

drop policy if exists chat_message_attachments_select_own on public.chat_message_attachments;
create policy chat_message_attachments_select_own
on public.chat_message_attachments
for select
to authenticated
using (
    exists (
        select 1
        from public.chat_messages m
        join public.chat_conversations c on c.conversation_id = m.conversation_id
        where m.message_id = chat_message_attachments.message_id
          and c.user_id = auth.uid()
    )
);

drop policy if exists chat_message_attachments_insert_own on public.chat_message_attachments;
create policy chat_message_attachments_insert_own
on public.chat_message_attachments
for insert
to authenticated
with check (
    exists (
        select 1
        from public.chat_messages m
        join public.chat_conversations c on c.conversation_id = m.conversation_id
        where m.message_id = chat_message_attachments.message_id
          and c.user_id = auth.uid()
    )
);

drop policy if exists chat_message_attachments_update_own on public.chat_message_attachments;
create policy chat_message_attachments_update_own
on public.chat_message_attachments
for update
to authenticated
using (
    exists (
        select 1
        from public.chat_messages m
        join public.chat_conversations c on c.conversation_id = m.conversation_id
        where m.message_id = chat_message_attachments.message_id
          and c.user_id = auth.uid()
    )
)
with check (
    exists (
        select 1
        from public.chat_messages m
        join public.chat_conversations c on c.conversation_id = m.conversation_id
        where m.message_id = chat_message_attachments.message_id
          and c.user_id = auth.uid()
    )
);

insert into public.chat_models (
    model_key,
    provider,
    display_name,
    description,
    answer_backend,
    answer_model,
    is_active,
    is_default,
    supports_images,
    supports_audio,
    supports_reasoning,
    metadata
)
values
    (
        'grounded-default',
        'internal',
        'Grounded Response',
        'Respuesta grounded sin depender de un LLM externo para la generación final.',
        'grounded',
        null,
        true,
        true,
        true,
        false,
        false,
        '{"tier":"local_default"}'::jsonb
    ),
    (
        'ollama-qwen3-4b',
        'ollama',
        'Qwen 3 4B (Ollama)',
        'Modelo local razonable para answering cuando el hardware lo permita.',
        'ollama',
        'qwen3:4b',
        true,
        false,
        true,
        false,
        true,
        '{"tier":"local_optional"}'::jsonb
    ),
    (
        'openai-gpt-5-mini',
        'openai',
        'GPT-5 Mini',
        'Modelo externo ligero para answering cuando exista cuota de OpenAI.',
        'openai',
        'gpt-5-mini',
        true,
        false,
        true,
        false,
        true,
        '{"tier":"cloud_optional"}'::jsonb
    ),
    (
        'hf-gpt-oss-120b',
        'huggingface',
        'GPT OSS 120B (HF)',
        'Ruta cloud opcional vía Hugging Face; no debe asumirse siempre disponible.',
        'hf',
        'openai/gpt-oss-120b',
        true,
        false,
        true,
        false,
        true,
        '{"tier":"cloud_optional"}'::jsonb
    )
on conflict (model_key) do update set
    provider = excluded.provider,
    display_name = excluded.display_name,
    description = excluded.description,
    answer_backend = excluded.answer_backend,
    answer_model = excluded.answer_model,
    is_active = excluded.is_active,
    is_default = excluded.is_default,
    supports_images = excluded.supports_images,
    supports_audio = excluded.supports_audio,
    supports_reasoning = excluded.supports_reasoning,
    metadata = excluded.metadata,
    updated_at = now();
