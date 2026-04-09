# Supabase Movement Knowledge Schema

## Nombre recomendado

- Proyecto Supabase: `biomechanics-knowledge-base`
- Schema PostgreSQL: `movement_knowledge`
- Dataset lógico inicial: `movement_knowledge_base`

La idea es que el proyecto completo represente una base de conocimiento biomecánico multimodal y no solo una tabla de ejercicios.

## Objetivo del diseño

La base debe soportar tres realidades al mismo tiempo:

1. Videos correctivos con ejercicios detallados.
2. Videos informativos o conceptuales que no son solo `deficiencia -> ejercicio`.
3. Evolución futura del schema cuando aparezcan nuevas clasificaciones, nuevos campos o nuevas formas de contenido.

Por eso el modelo es híbrido:

- normaliza lo que sí consultaremos mucho
- conserva el JSON crudo y normalizado para no perder información
- usa `jsonb` y una tabla de taxonomía observada para adaptarse a valores nuevos sin exigir migraciones inmediatas

## Tablas principales

### `movement_knowledge.source_videos`

Una fila por video fuente.

Campos clave:

- `external_video_id`
- `source_url`
- `source_type`
- `title_hint`
- `creator_name`
- `channel_url`
- `latest_analysis_id`
- `source_metadata jsonb`

### `movement_knowledge.video_analyses`

Una fila por versión de análisis.

Esto es importante porque el mismo video puede analizarse más de una vez:

- hoy con Gemini y visual AI básica
- mañana con una pasada visual más detallada
- después con revisión humana aprobada

Campos clave:

- `source_video_id`
- `content_sha256`
- `analysis_origin`
- `dataset_name`
- `analysis_schema_version`
- `primary_summary`
- `usefulness`
- `content_kind`
- `confidence`
- flags de utilidad
- `visual_validation_level`
- `review_status`
- arrays consultables como `body_regions`, `problem_layers`, `searchable_tags`, `tests_mentioned`, `exercises_mentioned`
- `raw_payload jsonb`
- `normalized_payload jsonb`
- `extra_payload jsonb`

### `movement_knowledge.knowledge_units`

Una fila por unidad de conocimiento extraída dentro de un análisis.

Esto permite que un mismo video contenga varias piezas reutilizables:

- mecanismo biomecánico
- patrón compensatorio
- ejercicio correctivo
- test funcional
- consejo práctico

Campos clave:

- `analysis_id`
- `ordinal`
- `unit_type`
- `title`
- `summary`
- listas consultables como `observable_signs`, `mechanisms`, `execution_steps`, `cues`, `breathing_cues`, `retest`
- `extra_payload jsonb`

### `movement_knowledge.taxonomy_terms`

Tabla para absorber nuevas clasificaciones sin romper el modelo.

El importador registra automáticamente valores observados como:

- `content_kind`
- `body_region`
- `problem_layer`
- `unit_type`
- `searchable_tag`
- `searchable_topic`
- `exercise_name`
- `test_name`

Con eso puedes detectar drift semántico antes de crear columnas o tablas nuevas.

### `movement_knowledge.import_jobs`

Audita cada importación:

- cuántos archivos se descubrieron
- cuántos se insertaron
- cuántos se omitieron por ya existir
- cuántos fallaron

## Método de adaptación a nuevas estructuras

El mecanismo principal de adaptación es este:

1. Los nuevos valores categóricos no rompen la base porque se guardan como `text`, `text[]` o `jsonb`.
2. El importador registra automáticamente términos nuevos en `taxonomy_terms`.
3. El JSON original queda en `raw_payload`.
4. El JSON ya limpiado queda en `normalized_payload`.
5. Si un patrón nuevo se vuelve estable y consultado con frecuencia, recién ahí se promueve a columna o tabla dedicada.

Ese enfoque evita migraciones apresuradas por cada video nuevo.

## Qué hacer con videos no totalmente validados

Los videos aún no validados visualmente al 100% no deben descartarse. Deben entrar con un nivel explícito de confianza.

Campo recomendado:

- `visual_validation_level`

Valores esperables:

- `ai_visual_review`
- `text_only_curated`
- `manual_visual_review`
- `approved_clinical_review`

Con eso puedes guardar material preliminar sin confundirlo con conocimiento ya aprobado.

## Implementación incluida

- Migración SQL: [20260402233000_create_movement_knowledge_schema.sql](/D:/sistema-biomecanico/supabase/migrations/20260402233000_create_movement_knowledge_schema.sql)
- Importador incremental: [import_movement_knowledge_to_supabase.py](/D:/sistema-biomecanico/scripts/import_movement_knowledge_to_supabase.py)
- Transformaciones: [movement_knowledge_import.py](/D:/sistema-biomecanico/video/movement_knowledge_import.py)

## Carga inicial recomendada

1. Aplicar la migración en Supabase.
2. Correr el importador contra `data/knowledge/video_knowledge_drafts`.
3. Revisar los términos detectados en `taxonomy_terms`.
4. Decidir qué clases nuevas merecen normalización adicional.
