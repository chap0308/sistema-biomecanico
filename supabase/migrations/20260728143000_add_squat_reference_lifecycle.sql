alter table public.squat_cases
    add column if not exists reference_status text not null default 'open'
        check (reference_status in ('open', 'in_progress', 'closed')),
    add column if not exists reference_started_at timestamptz,
    add column if not exists reference_started_by uuid
        references public.profiles(user_id),
    add column if not exists closed_at timestamptz,
    add column if not exists closed_by uuid
        references public.profiles(user_id);

alter table public.squat_expert_references
    alter column observation drop not null;
