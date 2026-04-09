# RAG Segments And Pipelines

## Objetivo

Definir:

- el esquema de datos de cada segmento
- las reglas de segmentaci\u00f3n
- los pipelines de procesamiento
- la forma en que cada segmento termina en retrieval

## Entidades principales

### 1. Source

Representa el origen l\u00f3gico del contenido.

```json
{
  "source_id": "src_01J...",
  "source_type": "youtube",
  "uri": "https://youtube.com/shorts/abc",
  "canonical_uri": "https://youtube.com/watch?v=abc",
  "title": "Ejemplo",
  "channel_or_author": "Canal X",
  "language_hint": "es",
  "course_id": "biomechanics_knowledge_v1",
  "tags": ["short", "escapula"],
  "duration_sec": 42.1,
  "created_at": "2026-04-04T12:00:00Z",
  "ingest_status": "processed"
}
```

### 2. Asset

Representa archivos derivados del source.

```json
{
  "asset_id": "ast_01J...",
  "source_id": "src_01J...",
  "kind": "audio",
  "path": "data/staging/src_01J/audio.wav",
  "mime_type": "audio/wav",
  "start_sec": 0.0,
  "end_sec": 42.1,
  "metadata": {
    "sample_rate": 16000
  }
}
```

### 3. Segment

Es la unidad m\u00e1s importante del sistema RAG.

Cada segmento debe ser:

- temporalmente acotado
- sem\u00e1nticamente \u00fatil
- recuperable por embeddings
- citable por timestamp

```json
{
  "segment_id": "seg_01J...",
  "source_id": "src_01J...",
  "segment_index": 3,
  "start_sec": 12.4,
  "end_sec": 18.9,
  "duration_sec": 6.5,
  "transcript": "La esc\u00e1pula comienza a rotar hacia arriba...",
  "ocr_text": "UPWARD ROTATION",
  "visual_description": "Vista posterior del hombro con flecha superpuesta indicando rotaci\u00f3n escapular",
  "segment_summary": "Explica el inicio de la rotaci\u00f3n escapular durante la elevaci\u00f3n.",
  "topics": ["escapula", "upward rotation"],
  "keywords": ["rotacion", "elevacion", "hombro"],
  "entities": ["escapula"],
  "speaker": "unknown",
  "language": "es",
  "confidence": {
    "asr": 0.91,
    "ocr": 0.77,
    "vision": 0.88
  },
  "frame_refs": [
    {
      "sec": 13.0,
      "path": "data/processed/src_01J/frames/seg_03_kf_01.jpg"
    }
  ],
  "retrieval_text": "Ejemplo | La esc\u00e1pula comienza a rotar hacia arriba... | UPWARD ROTATION | Vista posterior ... | Explica el inicio ...",
  "payload": {
    "source_type": "youtube",
    "course_id": "biomechanics_knowledge_v1",
    "channel_or_author": "Canal X",
    "title": "Ejemplo"
  }
}
```

## Reglas de segmentaci\u00f3n

Para Shorts y videos educativos cortos no conviene chunking largo.

### Regla base

- m\u00ednimo: `4-6 s`
- objetivo: `6-15 s`
- m\u00e1ximo: `20 s`

### Se\u00f1ales para cortar

- cambio de escena
- pausa fuerte en el habla
- cambio importante de OCR
- cambio de idea o subtema
- demostraci\u00f3n nueva del movimiento
- cambio de ejercicio o fase del ejercicio

### Regla de fusi\u00f3n

Fusionar segmentos contiguos cuando:

- la escena sigue siendo la misma
- el OCR es continuidad directa
- el transcript qued\u00f3 demasiado corto
- ambos segmentos describen una misma idea indivisible

## Construcci\u00f3n de `retrieval_text`

El texto final a embeber no debe ser solo transcript.

Debe mezclar:

- transcript
- OCR
- descripci\u00f3n visual
- resumen del segmento
- topics
- keywords
- metadata \u00fatil

Ejemplo:

```python
def make_retrieval_text(seg):
    return " | ".join([
        seg.transcript.strip(),
        seg.ocr_text.strip(),
        seg.visual_description.strip(),
        seg.segment_summary.strip(),
        " ".join(seg.topics),
        " ".join(seg.keywords),
    ])
```

## Pipelines

### Pipeline A. YouTube Short premium

Usar cuando:

- el video depende mucho de lo visual
- hay presupuesto/cuota para Gemini
- se necesita extraer cues visuales complejos

```text
1. recibir URL
2. obtener metadata
3. intentar transcript
4. analizar con Gemini si es necesario
5. pedir salida segmentada o semiestructurada
6. normalizar
7. construir Segment[]
8. generar embeddings
9. upsert a Qdrant
10. persistir metadata a Supabase
```

### Pipeline B. YouTube/local fallback local

Usar cuando:

- se quiere ahorrar costo
- hay volumen de videos
- se requiere reprocesamiento repetible

```text
1. obtener video o audio
2. ASR local
3. scene detection
4. frame sampling
5. OCR
6. captioning visual opcional
7. alinear transcript + escenas + OCR + frames
8. construir Segment[]
9. generar embeddings
10. upsert a Qdrant
11. persistir metadata a Supabase
```

### Pipeline C. Webpage

```text
1. recibir URL
2. extraer contenido principal
3. detectar embeds
4. indexar el texto de la p\u00e1gina
5. si hay video relacionado:
   crear source vinculado
   procesarlo con pipeline A o B
```

### Pipeline D. Query RAG

```text
1. recibir query
2. detectar filtros
3. dense retrieval
4. sparse retrieval
5. fusionar resultados
6. reranking opcional
7. expandir vecinos temporales si conviene
8. construir prompt
9. responder con citas por fuente y timestamp
```

## Payload recomendado para Qdrant

Qdrant debe indexar el vector, pero tambi\u00e9n necesita payload \u00fatil para filtrar.

```json
{
  "source_id": "src_01J...",
  "segment_id": "seg_01J...",
  "start_sec": 12.4,
  "end_sec": 18.9,
  "source_type": "youtube",
  "course_id": "biomechanics_knowledge_v1",
  "language": "es",
  "title": "Ejemplo",
  "uri": "https://youtube.com/watch?v=abc&t=12",
  "channel_or_author": "Canal X",
  "topics": ["escapula", "upward rotation"],
  "keywords": ["rotacion", "hombro"]
}
```

## Colecci\u00f3n recomendada en Qdrant

```python
COLLECTION = "video_segments_v1"
VECTORS = {
    "dense_main": {"size": 1024, "distance": "Cosine"}
}
SPARSE_VECTORS = {
    "sparse_main": {}
}
```

Uso esperado:

- `dense_main` para similitud sem\u00e1ntica
- `sparse_main` para keywords
- filtros por `course_id`, `source_type`, `language`, `channel_or_author`

## Relaci\u00f3n Supabase + Qdrant

### Supabase

Guardar:

- sources
- assets
- segments
- jobs
- an\u00e1lisis
- knowledge units

### Qdrant

Guardar:

- embeddings dense
- embeddings sparse
- payload de retrieval

### Regla de sincronizaci\u00f3n

1. el `segment_id` es la referencia estable
2. Supabase es la fuente de verdad estructurada
3. Qdrant es el \u00edndice de recuperaci\u00f3n
4. si cambia un segmento, se reindexa por `segment_id`

## Respuesta final con citas

La respuesta del sistema debe citar siempre:

- `source`
- `title`
- `start_sec`
- `end_sec`
- opcionalmente URL con timestamp

Ejemplo:

```text
Seg\u00fan "Why Rotator Cuff Exercises Don't Work", entre 00:12 y 00:20, el video explica que la rotaci\u00f3n externa aparente puede venir de compensaci\u00f3n espinal y no de espacio real del hombro.
```

## Decisi\u00f3n de dise\u00f1o

El segmento, no el video completo, es la unidad central del RAG.

Todo pipeline debe terminar generando:

- `segments`
- `retrieval_text`
- embeddings
- payload filtrable

Sin eso, no hay recuperaci\u00f3n \u00fatil ni respuesta grounded.
