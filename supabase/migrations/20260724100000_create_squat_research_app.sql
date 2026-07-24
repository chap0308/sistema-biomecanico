create extension if not exists "pgcrypto";

alter table public.profiles
    add column if not exists squat_role text
        check (squat_role in ('investigator', 'expert'));

create table if not exists public.squat_cases (
    case_id uuid primary key default gen_random_uuid(),
    external_case_id text not null unique,
    created_by uuid not null references public.profiles(user_id),
    participant_code text,
    profile text not null default 'no_etiquetado',
    status text not null default 'draft'
        check (
            status in (
                'draft',
                'uploaded',
                'under_review',
                'processing',
                'completed',
                'excluded',
                'inconclusive',
                'failed'
            )
        ),
    protocol_review_status text,
    exclusion_reason text,
    original_object_path text,
    instrument_1 jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists squat_cases_created_at_idx
    on public.squat_cases(created_at desc);

create table if not exists public.squat_analysis_runs (
    run_id uuid primary key default gen_random_uuid(),
    case_id uuid not null references public.squat_cases(case_id) on delete cascade,
    status text not null default 'queued'
        check (status in ('queued', 'processing', 'completed', 'inconclusive', 'failed')),
    pipeline_version text,
    ruleset_version text,
    report jsonb not null default '{}'::jsonb,
    error_message text,
    created_at timestamptz not null default now(),
    started_at timestamptz,
    completed_at timestamptz
);

create index if not exists squat_analysis_runs_case_id_idx
    on public.squat_analysis_runs(case_id, created_at desc);

create table if not exists public.squat_artifacts (
    artifact_id uuid primary key default gen_random_uuid(),
    run_id uuid not null references public.squat_analysis_runs(run_id) on delete cascade,
    artifact_kind text not null,
    object_path text not null,
    mime_type text,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    unique (run_id, object_path)
);

create table if not exists public.squat_expert_assignments (
    assignment_id uuid primary key default gen_random_uuid(),
    case_id uuid not null references public.squat_cases(case_id) on delete cascade,
    evaluator_id uuid not null references public.profiles(user_id),
    assigned_by uuid not null references public.profiles(user_id),
    status text not null default 'pending'
        check (status in ('pending', 'in_progress', 'submitted')),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (case_id, evaluator_id)
);

create index if not exists squat_expert_assignments_evaluator_idx
    on public.squat_expert_assignments(evaluator_id, status, created_at desc);

create table if not exists public.squat_expert_evaluations (
    evaluation_id uuid primary key default gen_random_uuid(),
    assignment_id uuid not null unique
        references public.squat_expert_assignments(assignment_id) on delete cascade,
    evaluator_id uuid not null references public.profiles(user_id),
    status text not null default 'draft'
        check (status in ('draft', 'submitted')),
    general_observation text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    submitted_at timestamptz
);

create table if not exists public.squat_expert_evaluation_items (
    evaluation_id uuid not null
        references public.squat_expert_evaluations(evaluation_id) on delete cascade,
    pattern_key text not null
        check (
            pattern_key in (
                'trunk_lateral_inclination',
                'pelvis_lateral_shift',
                'visible_dynamic_valgus',
                'bilateral_asymmetry'
            )
        ),
    classification text not null,
    observed_side text,
    confidence text,
    observation text,
    primary key (evaluation_id, pattern_key)
);

drop trigger if exists set_squat_cases_updated_at on public.squat_cases;
create trigger set_squat_cases_updated_at
before update on public.squat_cases
for each row
execute function public.set_updated_at();

drop trigger if exists set_squat_assignments_updated_at
    on public.squat_expert_assignments;
create trigger set_squat_assignments_updated_at
before update on public.squat_expert_assignments
for each row
execute function public.set_updated_at();

drop trigger if exists set_squat_evaluations_updated_at
    on public.squat_expert_evaluations;
create trigger set_squat_evaluations_updated_at
before update on public.squat_expert_evaluations
for each row
execute function public.set_updated_at();

create or replace function public.current_squat_role()
returns text
language sql
stable
security definer
set search_path = public
as $$
    select squat_role
    from public.profiles
    where user_id = auth.uid();
$$;

create or replace function public.handle_new_profile()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
    requested_role text;
begin
    requested_role := new.raw_user_meta_data ->> 'squat_role';
    if requested_role not in ('investigator', 'expert') then
        requested_role := null;
    end if;

    insert into public.profiles (
        user_id,
        email,
        display_name,
        squat_role
    )
    values (
        new.id,
        new.email,
        coalesce(
            new.raw_user_meta_data ->> 'display_name',
            split_part(coalesce(new.email, ''), '@', 1)
        ),
        requested_role
    )
    on conflict (user_id) do update
    set
        email = excluded.email,
        display_name = coalesce(
            public.profiles.display_name,
            excluded.display_name
        ),
        squat_role = coalesce(
            public.profiles.squat_role,
            excluded.squat_role
        );
    return new;
end;
$$;

alter table public.squat_cases enable row level security;
alter table public.squat_analysis_runs enable row level security;
alter table public.squat_artifacts enable row level security;
alter table public.squat_expert_assignments enable row level security;
alter table public.squat_expert_evaluations enable row level security;
alter table public.squat_expert_evaluation_items enable row level security;

drop policy if exists profiles_select_squat_investigator on public.profiles;
create policy profiles_select_squat_investigator
on public.profiles
for select
to authenticated
using (
    public.current_squat_role() = 'investigator'
    and squat_role is not null
);

drop policy if exists squat_cases_investigator_all on public.squat_cases;
create policy squat_cases_investigator_all
on public.squat_cases
for all
to authenticated
using (public.current_squat_role() = 'investigator')
with check (
    public.current_squat_role() = 'investigator'
    and created_by = auth.uid()
);

drop policy if exists squat_cases_expert_assigned_select on public.squat_cases;
create policy squat_cases_expert_assigned_select
on public.squat_cases
for select
to authenticated
using (
    public.current_squat_role() = 'expert'
    and exists (
        select 1
        from public.squat_expert_assignments assignment
        where assignment.case_id = squat_cases.case_id
          and assignment.evaluator_id = auth.uid()
    )
);

drop policy if exists squat_runs_investigator_all
    on public.squat_analysis_runs;
create policy squat_runs_investigator_all
on public.squat_analysis_runs
for all
to authenticated
using (public.current_squat_role() = 'investigator')
with check (public.current_squat_role() = 'investigator');

drop policy if exists squat_artifacts_investigator_all
    on public.squat_artifacts;
create policy squat_artifacts_investigator_all
on public.squat_artifacts
for all
to authenticated
using (public.current_squat_role() = 'investigator')
with check (public.current_squat_role() = 'investigator');

drop policy if exists squat_assignments_investigator_all
    on public.squat_expert_assignments;
create policy squat_assignments_investigator_all
on public.squat_expert_assignments
for all
to authenticated
using (public.current_squat_role() = 'investigator')
with check (
    public.current_squat_role() = 'investigator'
    and assigned_by = auth.uid()
);

drop policy if exists squat_assignments_expert_select
    on public.squat_expert_assignments;
create policy squat_assignments_expert_select
on public.squat_expert_assignments
for select
to authenticated
using (evaluator_id = auth.uid());

drop policy if exists squat_evaluations_investigator_select
    on public.squat_expert_evaluations;
create policy squat_evaluations_investigator_select
on public.squat_expert_evaluations
for select
to authenticated
using (public.current_squat_role() = 'investigator');

drop policy if exists squat_evaluations_expert_select
    on public.squat_expert_evaluations;
create policy squat_evaluations_expert_select
on public.squat_expert_evaluations
for select
to authenticated
using (evaluator_id = auth.uid());

drop policy if exists squat_evaluations_expert_insert
    on public.squat_expert_evaluations;
create policy squat_evaluations_expert_insert
on public.squat_expert_evaluations
for insert
to authenticated
with check (
    evaluator_id = auth.uid()
    and exists (
        select 1
        from public.squat_expert_assignments assignment
        where assignment.assignment_id =
            squat_expert_evaluations.assignment_id
          and assignment.evaluator_id = auth.uid()
    )
);

drop policy if exists squat_evaluations_expert_update_draft
    on public.squat_expert_evaluations;
create policy squat_evaluations_expert_update_draft
on public.squat_expert_evaluations
for update
to authenticated
using (
    evaluator_id = auth.uid()
    and status = 'draft'
)
with check (
    evaluator_id = auth.uid()
    and status in ('draft', 'submitted')
);

drop policy if exists squat_items_investigator_select
    on public.squat_expert_evaluation_items;
create policy squat_items_investigator_select
on public.squat_expert_evaluation_items
for select
to authenticated
using (public.current_squat_role() = 'investigator');

drop policy if exists squat_items_expert_all_own_draft
    on public.squat_expert_evaluation_items;
create policy squat_items_expert_all_own_draft
on public.squat_expert_evaluation_items
for all
to authenticated
using (
    exists (
        select 1
        from public.squat_expert_evaluations evaluation
        where evaluation.evaluation_id =
            squat_expert_evaluation_items.evaluation_id
          and evaluation.evaluator_id = auth.uid()
          and evaluation.status = 'draft'
    )
)
with check (
    exists (
        select 1
        from public.squat_expert_evaluations evaluation
        where evaluation.evaluation_id =
            squat_expert_evaluation_items.evaluation_id
          and evaluation.evaluator_id = auth.uid()
          and evaluation.status = 'draft'
    )
);

insert into storage.buckets (id, name, public)
values
    ('squat-inputs', 'squat-inputs', false),
    ('squat-artifacts', 'squat-artifacts', false),
    ('squat-exports', 'squat-exports', false)
on conflict (id) do update
set public = false;
