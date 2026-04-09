# RAG Pending Implementations

Este archivo concentra lo pendiente, lo implementable a futuro y los siguientes pasos naturales del pivot a RAG.

## 1. Qdrant Cloud

### Estado actual

- El proyecto ya puede usar Qdrant local embebido en disco mediante `qdrant-client`.
- Esto sirve para desarrollo, pruebas locales y validaci\u00f3n inicial del pipeline.

### Pendiente

Implementar Qdrant en la nube para:

- retrieval compartido entre entornos
- mayor persistencia operativa
- consultas remotas
- separaci\u00f3n entre desarrollo local y producci\u00f3n

### Trabajo futuro

1. Crear instancia de Qdrant Cloud.
2. Definir variables de entorno para URL y API key.
3. Cambiar `qdrant_prefer_embedded=false`.
4. Ejecutar un reindex completo desde `rag_segments`.
5. Validar consultas y payload filters en remoto.

### Variables previstas

- `QDRANT_URL`
- `QDRANT_API_KEY`
- `QDRANT_COLLECTION`

## 2. Pipeline local de video real

### Estado actual

- Existe bootstrap de `Source`, `Asset` y `Segment`.
- Existe indexaci\u00f3n local en Qdrant.
- Existe persistencia estructurada en Supabase.

### Pendiente

Implementar la versi\u00f3n completa de an\u00e1lisis local:

- extracci\u00f3n de audio
- ASR local
- scene detection
- frame sampling
- OCR
- visual captioning opcional
- alineaci\u00f3n temporal real

## 3. Gemini premium path

### Estado actual

- La arquitectura ya define la ruta premium.
- Existe trabajo previo de an\u00e1lisis con Gemini.

### Pendiente

- integrar la salida de Gemini al modelo `Segment`
- normalizar timestamps y visual notes
- comparar Gemini vs local fallback
- decidir reglas de escalamiento a premium

## 3.1. Upgrade de drafts a Gemini

### Estado actual

- el proyecto ya puede producir drafts con `Gemini` y con `local + HF`
- el esquema ya puede guardar metadata de proveedor y calidad

### Pendiente

- crear un comando que seleccione drafts activos `standard` o `fallback`
- volver a analizar esos mismos `source` con Gemini cuando haya cuota
- insertar la nueva versión como draft `premium`
- desactivar la versión previa
- reindexar solo el draft activo en Qdrant

## 4. Retrieval h\u00edbrido

### Estado actual

- ya existe dense vector
- ya existe generaci\u00f3n de pesos sparse

### Pendiente

- usar sparse retrieval real en Qdrant o estrategia equivalente
- fusionar dense + sparse
- reranking
- expansi\u00f3n de vecinos temporales

## 5. Answering grounded

### Pendiente

- construir prompt final con evidencia
- traer contexto ampliado desde Supabase
- generar respuestas con citas por `source`, `title` y `timestamp`
- agregar reglas anti-hallucination

## 6. Buckets y assets

### Pendiente

Definir qu\u00e9 assets s\u00ed deben ir a Supabase Storage:

- keyframes seleccionados
- transcripts persistidos
- OCR exports
- videos propios del usuario
- videos generados por IA a partir de descripciones de ejercicios

### Regla actual

No subir por defecto todos los videos p\u00fablicos de YouTube.

## 7. Custom MCP `video-rag-local`

### Estado actual

Existe el esqueleto en:

- [server.py](/D:/sistema-biomecanico/mcp/video-rag-local/server.py)
- [README.md](/D:/sistema-biomecanico/mcp/video-rag-local/README.md)

### Pendiente para volverlo operativo

1. Completar handlers reales:
   - `ingest_source`
   - `analyze_with_gemini`
   - `analyze_local`
   - `build_segments`
   - `index_source`
   - `query_segments`
   - `show_timeline`
2. Conectar esos handlers a `src/ingestion`, `src/pipelines` y `src/indexing`.
3. Definir formato estable de respuestas MCP.
4. Agregar logs, manejo de errores y timeouts.
5. Probar el servidor localmente desde el cliente MCP.

### Paso manual fuera del repo

El registro del MCP en Codex/Desktop no se hace solo con estos archivos. Hay que:

1. configurar el cliente MCP del entorno
2. apuntarlo al entrypoint del servidor
3. reiniciar o recargar el cliente
4. validar que las herramientas aparezcan disponibles

## 8. Evaluaci\u00f3n

### Pendiente

- retrieval eval set
- queries biomec\u00e1nicas representativas
- medici\u00f3n de precision@k / recall@k
- evaluaci\u00f3n manual de grounding

## 9. Limpieza de esquema legacy

### Pendiente

Decidir c\u00f3mo convivir\u00e1n a largo plazo:

- `source_videos`
- `video_analyses`
- `knowledge_units`

con:

- `rag_sources`
- `rag_assets`
- `rag_segments`

La recomendaci\u00f3n actual es mantener ambas capas por ahora y consolidar m\u00e1s adelante.
