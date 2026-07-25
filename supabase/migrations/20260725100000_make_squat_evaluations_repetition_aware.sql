alter table public.squat_expert_evaluation_items
    add column if not exists repetition_index integer not null default 1
        check (repetition_index >= 1);

alter table public.squat_expert_evaluation_items
    drop constraint if exists squat_expert_evaluation_items_pkey;

alter table public.squat_expert_evaluation_items
    add primary key (evaluation_id, repetition_index, pattern_key);

alter table public.squat_expert_references
    add column if not exists repetition_index integer not null default 1
        check (repetition_index >= 1);

alter table public.squat_expert_references
    drop constraint if exists squat_expert_references_case_id_pattern_key_key;

alter table public.squat_expert_references
    add constraint squat_expert_references_case_repetition_pattern_key
        unique (case_id, repetition_index, pattern_key);

drop index if exists public.squat_expert_references_case_idx;
create index squat_expert_references_case_idx
    on public.squat_expert_references(
        case_id,
        repetition_index,
        pattern_key
    );
