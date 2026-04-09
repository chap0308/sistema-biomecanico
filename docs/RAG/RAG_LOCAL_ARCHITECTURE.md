# RAG Local Architecture

## Objetivo

Definir la arquitectura local-first del proyecto para construir un sistema RAG multimodal centrado en:

- YouTube Shorts
- videos locales
- p\u00e1ginas web con contenido embebido
- conocimiento biomec\u00e1nico reutilizable

La idea central ya no es entrenar un modelo propio como eje del sistema. El eje pasa a ser:

```text
source ingestion
-> video understanding
-> segmentation
-> indexing
-> retrieval
-> grounded answer generation
```

## Principio de dise\u00f1o

Separar claramente dos capas:

### 1. Capa de conocimiento

Aprende de:

- videos educativos
- documentos
- p\u00e1ginas web
- material curado interno

Produce:

- segmentos indexables
- unidades de conocimiento
- metadata consultable

### 2. Capa anal\u00edtica del usuario

Analiza:

- m\u00e9tricas biomec\u00e1nicas
- findings
- deficiencies
- contexto del usuario

Produce:

- contexto estructurado para retrieval
- restricciones y filtros
- explicaci\u00f3n y recomendaci\u00f3n final

La capa RAG no reemplaza el pipeline biomec\u00e1nico del usuario. Lo complementa.

## Componentes principales

### A. Source Ingestion

Responsable de aceptar y normalizar:

- `youtube`
- `local_video`
- `public_video_url`
- `webpage`

Debe generar un `source` estable con:

- `source_id`
- `source_type`
- `uri`
- `canonical_uri`
- `title`
- `channel_or_author`
- `language_hint`
- `tags`
- `duration_sec`

### B. Asset Derivation

Produce archivos derivados del source:

- audio extra\u00eddo
- keyframes
- miniaturas
- transcript bruto
- OCR por frame
- captions visuales

Esta capa no responde preguntas. Solo prepara insumos.

### C. Video Understanding

Dos rutas:

#### Ruta premium

Usa Gemini cuando haya cuota disponible o el video lo justifique.

Ideal para:

- shorts muy dependientes de lo visual
- explicaci\u00f3n t\u00e9cnica con overlays
- ejercicios donde el gesto visual importa mucho

#### Ruta local

Usa pipeline local con:

- ASR
- scene detection
- frame sampling
- OCR
- captioning visual opcional

Ideal para:

- volumen grande
- reducci\u00f3n de costo
- reindexaciones repetibles

### D. Segment Builder

Convierte la informaci\u00f3n temporal del video en `segments` \u00fatiles para retrieval.

Cada segmento debe integrar:

- transcript
- OCR
- descripci\u00f3n visual
- resumen sem\u00e1ntico
- topics
- keywords
- source metadata
- timestamps

### E. Storage

Se usar\u00e1 una arquitectura dual:

#### Supabase

Como sistema de registro estructurado:

- `sources`
- `assets`
- `segments`
- `analysis runs`
- `knowledge units`
- jobs y trazabilidad

#### Qdrant

Como motor vectorial de retrieval:

- dense vectors
- sparse vectors
- hybrid retrieval
- filtros por payload

## Flujo operativo

### Flujo A. Ingesta de YouTube Short

```text
URL de YouTube
-> scraper / metadata
-> source
-> transcript o an\u00e1lisis visual
-> segmentaci\u00f3n
-> embeddings
-> upsert a Qdrant
-> metadata estructurada a Supabase
```

### Flujo B. Video local

```text
path local
-> source
-> extracci\u00f3n de audio y frames
-> ASR / OCR / scene detect
-> segmentaci\u00f3n
-> embeddings
-> indexaci\u00f3n
```

### Flujo C. P\u00e1gina web

```text
URL web
-> extractor de contenido principal
-> detecci\u00f3n de embeds
-> source webpage
-> contenido textual indexable
-> si hay video relacionado: source vinculado y proceso de video
```

### Flujo D. Query RAG

```text
query + filtros + contexto biomec\u00e1nico
-> query embedding
-> dense retrieval
-> sparse retrieval
-> fusi\u00f3n y reranking
-> expansi\u00f3n temporal opcional
-> prompt con citas
-> respuesta grounded
```

## Estructura propuesta del repo

```text
src/
  core/
    models.py
    settings.py
    ids.py
  ingestion/
    youtube.py
    local_video.py
    webpage.py
  analysis/
    router.py
    gemini_video.py
    whisper_asr.py
    scene_detect.py
    frame_sampler.py
    ocr.py
    visual_caption.py
  chunking/
    align_segments.py
    merge_rules.py
    segment_builder.py
  indexing/
    embeddings.py
    sparse.py
    qdrant_store.py
    payloads.py
  retrieval/
    hybrid_search.py
    rerank.py
    filters.py
  rag/
    prompts.py
    answer.py
    citations.py
  pipelines/
    process_source.py
    process_video_local.py
    process_video_premium.py
    process_webpage.py
    reindex.py
  eval/
    retrieval_eval.py
    rag_eval.py
```

## M\u00f3dulos actuales que s\u00ed conviene conservar

El pivot a RAG no implica borrar el trabajo hecho.

Se pueden conservar directamente:

- `video/youtube_shorts.py`
- `scripts/scrape_youtube_shorts.py`
- `scripts/run_youtube_batch.py`
- `scripts/list_pending_youtube_shorts.py`
- `video/gemini_knowledge.py`
- `video/movement_knowledge_import.py`
- `scripts/import_movement_knowledge_to_supabase.py`
- `scripts/sync_movement_knowledge_supabase.py`

## Qu\u00e9 debe cambiar del enfoque actual

### Antes

```text
video -> protocolo -> recomendaci\u00f3n
```

### Ahora

```text
video -> segments + knowledge units + embeddings -> retrieval -> answer
```

Los protocolos siguen siendo \u00fatiles, pero ahora son solo un tipo de conocimiento, no el \u00fanico.

## Herramientas recomendadas

### Obligatorias para v1 local

- Supabase
- Qdrant
- ffmpeg
- OCR local
- ASR local
- Python backend

### Opcionales para mejorar precisi\u00f3n

- Gemini para videos dif\u00edciles
- reranker dedicado
- visual captioning local
- evaluaci\u00f3n retrieval/RAG

## Orden recomendado de implementaci\u00f3n

### Fase 1

- modelos `Source`, `Asset`, `Segment`
- ingesta de YouTube/local/webpage
- persistencia en Supabase
- segmentaci\u00f3n m\u00ednima
- embeddings dense
- indexaci\u00f3n en Qdrant

### Fase 2

- OCR
- scene detection
- hybrid retrieval
- citas por timestamp

### Fase 3

- pipeline premium con Gemini
- reranking
- evaluaci\u00f3n de retrieval

### Fase 4

- custom MCP del proyecto
- dashboard
- despliegue cloud

## Decisi\u00f3n final

La arquitectura correcta para este proyecto es:

```text
local-first multimodal RAG
with
Supabase as system of record
and
Qdrant as retrieval engine
```

No conviene empezar desde cero. Conviene pivotear el repo actual hacia esta arquitectura.
