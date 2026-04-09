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
        'hf-qwen3-32b-balanced',
        'huggingface',
        'HF Qwen3 32B (balanced)',
        'Perfil balanceado para answering con mejor calidad semántica.',
        'hf',
        'Qwen/Qwen3-32B',
        true,
        false,
        true,
        false,
        true,
        '{"answer_profile":"balanced","cost_tier":"balanced"}'::jsonb
    ),
    (
        'hf-qwen3-4b-cheap',
        'huggingface',
        'HF Qwen3 4B (cheap)',
        'Perfil económico para answering con menor costo.',
        'hf',
        'Qwen/Qwen3-4B-Instruct-2507',
        true,
        false,
        true,
        false,
        true,
        '{"answer_profile":"cheap","cost_tier":"cheap"}'::jsonb
    )
on conflict (model_key) do update set
    provider = excluded.provider,
    display_name = excluded.display_name,
    description = excluded.description,
    answer_backend = excluded.answer_backend,
    answer_model = excluded.answer_model,
    is_active = excluded.is_active,
    supports_images = excluded.supports_images,
    supports_audio = excluded.supports_audio,
    supports_reasoning = excluded.supports_reasoning,
    metadata = excluded.metadata,
    updated_at = now();
