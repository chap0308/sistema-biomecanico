create table if not exists public.squat_expert_references (
    reference_id uuid primary key default gen_random_uuid(),
    case_id uuid not null
        references public.squat_cases(case_id) on delete cascade,
    pattern_key text not null
        check (
            pattern_key in (
                'trunk_lateral_inclination',
                'pelvis_lateral_shift',
                'visible_dynamic_valgus',
                'bilateral_asymmetry'
            )
        ),
    classification text not null
        check (
            classification in (
                'presente',
                'ausente',
                'no_concluyente'
            )
        ),
    observed_side text
        check (
            observed_side is null
            or observed_side in (
                'izquierda',
                'derecha',
                'bilateral',
                'sin_direccion'
            )
        ),
    method text not null default 'consenso_guiado'
        check (method = 'consenso_guiado'),
    observation text not null,
    resolved_by uuid not null references public.profiles(user_id),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (case_id, pattern_key),
    check (
        (
            classification = 'presente'
            and observed_side is not null
        )
        or (
            classification <> 'presente'
            and observed_side is null
        )
    )
);

create index if not exists squat_expert_references_case_idx
    on public.squat_expert_references(case_id, pattern_key);

drop trigger if exists set_squat_references_updated_at
    on public.squat_expert_references;
create trigger set_squat_references_updated_at
before update on public.squat_expert_references
for each row
execute function public.set_updated_at();

alter table public.squat_expert_references enable row level security;

drop policy if exists squat_references_investigator_all
    on public.squat_expert_references;
create policy squat_references_investigator_all
on public.squat_expert_references
for all
to authenticated
using (public.current_squat_role() = 'investigator')
with check (
    public.current_squat_role() = 'investigator'
    and resolved_by = auth.uid()
);
