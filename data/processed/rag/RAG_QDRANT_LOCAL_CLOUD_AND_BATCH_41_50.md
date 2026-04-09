# RAG Qdrant Local, Cloud y Batch 41-50

## Estado actual

- Qdrant local está levantado y responde en `http://127.0.0.1:6333/collections`
- Colecciones activas:
  - `video_knowledge_units_v1`
  - `video_segments_v1`

Conteos verificados después de la corrida `41-50`:

- `video_knowledge_units_v1`: `261`
- `video_segments_v1`: `627`

## Para qué sirve usar Qdrant local vs Qdrant Cloud

### Qdrant local

Conviene usarlo cuando:

- estamos desarrollando el pipeline y queremos iterar rápido
- necesitamos resetear colecciones sin tocar producción
- queremos probar cambios de retrieval, payloads o embeddings en una máquina local
- no queremos depender de conectividad externa para validar lógica

Ventajas:

- más rápido para depuración
- fácil de reiniciar
- sin costo extra de infraestructura

Limitaciones:

- queda atado a una sola máquina
- no es el mejor destino final para la web o APIs multiusuario
- no da la persistencia remota que conviene para despliegue

### Qdrant Cloud

Conviene usarlo cuando:

- queremos un vector store accesible por la API real y por la web
- necesitamos persistencia remota
- queremos separar desarrollo local de entorno más estable
- vamos a empezar a tratar el retrieval como una pieza de infraestructura del producto

Ventajas:

- endpoint remoto estable
- persistencia fuera de la máquina local
- más fácil de conectar con frontend, backend desplegado u otros clientes

Limitaciones:

- exige configuración inicial de cluster
- puede requerir índices de payload para ciertos filtros
- añade dependencia externa y cuota/plan

### Recomendación práctica en este proyecto

- seguir usando local para depuración rápida y experimentación
- usar Cloud como destino principal de retrieval para el MVP integrado con la web
- mantener ambos caminos disponibles porque cumplen roles distintos

## Corrida ejecutada: Shorts 41-50 con Gemini

Comando usado:

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\run_youtube_batch.py `
  --range 41-50 `
  --channel-url https://www.youtube.com/@conorharris/shorts `
  --order newest `
  --analysis-backend gemini
```

Resumen generado:

- `D:\sistema-biomecanico\data\knowledge\video_knowledge_drafts\conorharris_newest_41_50_gemini\run_summary.json`

Resultado:

- `10` videos seleccionados
- `8` procesados directamente con `Gemini`
- `2` con fallback a `local` por error `503 UNAVAILABLE` de Gemini

Videos con fallback local:

- `3N6Nst5UqeI`
- `G4314fq_b_Q`

Esto confirma que el fallback por video funciona: el lote no se detiene si Gemini falla en algunos elementos.

## Dónde quedan los artefactos

### Gemini directo

Cuando Gemini funciona, el draft queda en:

- `data\knowledge\video_knowledge_drafts\conorharris_newest_41_50_gemini\0NN_<video_id>.json`

### Fallback local

Cuando Gemini falla y cae a local, se generan:

- `*_level1.json`
- `*_knowledge_draft.json`
- `*_sync.json`

Además, el procesamiento multimodal local deja artefactos por `source_id` en:

- `D:\sistema-biomecanico\data\processed\rag\src_<source_id>\`

Ejemplos de archivos dentro de cada carpeta:

- `audio.wav`
- `transcript.txt`
- `ocr.txt`
- `frames\...`

## Cómo verificar Qdrant local

### API HTTP

```powershell
Invoke-WebRequest -Uri http://127.0.0.1:6333/collections -UseBasicParsing
```

### Navegador

- `http://127.0.0.1:6333/collections`
- `http://127.0.0.1:6333/collections/video_knowledge_units_v1`
- `http://127.0.0.1:6333/collections/video_segments_v1`

### Reiniciar Qdrant local

Si Qdrant local queda inconsistente:

```powershell
powershell -ExecutionPolicy Bypass -File D:\sistema-biomecanico\scripts\reset_qdrant_server.ps1
```

Reset completo del storage:

```powershell
powershell -ExecutionPolicy Bypass -File D:\sistema-biomecanico\scripts\reset_qdrant_server.ps1 -FullReset
```

## Paso a Qdrant Cloud

### Qué sí hay que hacer manualmente

Hoy lo correcto es crear el cluster primero en Qdrant Cloud. El proyecto todavía no crea clusters por API.

Pasos:

1. Crear una cuenta o entrar al dashboard de Qdrant Cloud.
2. Ir a `Clusters`.
3. Crear un cluster `Free` o `Standard`.
4. Copiar:
   - `Cluster URL`
   - `Database API Key`
5. Configurar el proyecto para usar ese endpoint en lugar del local.

La vía manual es la más simple para este proyecto ahora mismo. Qdrant también ofrece `Cloud API`, así que más adelante podríamos automatizar creación, lectura y borrado de clusters desde código, pero todavía no lo hemos integrado aquí.

Referencias oficiales:

- [Cloud Quickstart](https://qdrant.tech/documentation/cloud/quickstart-cloud/)
- [Create a Cluster](https://qdrant.tech/documentation/cloud/create-cluster/)
- [Cluster Access](https://qdrant.tech/documentation/cloud/cluster-access/)
- [Authentication](https://qdrant.tech/documentation/cloud/authentication/)
- [Cloud API](https://qdrant.tech/documentation/cloud-api/)

### Variables que hay que ajustar en este proyecto

En `.env`:

```env
QDRANT_PREFER_EMBEDDED=false
QDRANT_URL=https://<tu-cluster>.cloud.qdrant.io:6333
QDRANT_API_KEY=<tu-database-api-key>
```

Luego reiniciar cualquier proceso que use settings.

## Implementación realizada en este proyecto

La conexión a Qdrant Cloud ya quedó operativa usando:

```env
QDRANT_PREFER_EMBEDDED=false
QDRANT_URL=https://<tu-cluster>.cloud.qdrant.io
QDRANT_API_KEY=<tu-database-api-key>
```

Además se añadió soporte para reindexar ambas colecciones desde Supabase hacia Cloud:

- `D:\sistema-biomecanico\scripts\reindex_active_knowledge.py`
- `D:\sistema-biomecanico\scripts\reindex_active_segments.py`

También se ajustó el wrapper:

- `D:\sistema-biomecanico\src\indexing\qdrant_store.py`

para crear índice de payload sobre `source_id`, necesario en Qdrant Cloud cuando hacemos borrado por filtro.

## Reindexación ejecutada hacia Cloud

### Knowledge units

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\reindex_active_knowledge.py `
  --output-json data\knowledge\rag_runs\reindex_active_knowledge_qdrant_cloud.json
```

Resultado:

- `processed_count`: `50`
- resumen:
  - `D:\sistema-biomecanico\data\knowledge\rag_runs\reindex_active_knowledge_qdrant_cloud.json`

### Evidence segments

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\reindex_active_segments.py `
  --output-json data\knowledge\rag_runs\reindex_active_segments_qdrant_cloud.json
```

Resultado:

- `segment_count`: `627`
- `source_count`: `22`
- resumen:
  - `D:\sistema-biomecanico\data\knowledge\rag_runs\reindex_active_segments_qdrant_cloud.json`

## Estado real del cluster Cloud después de la migración

Colecciones verificadas:

- `video_knowledge_units_v1`: `261`
- `video_segments_v1`: `627`

## Prueba real de consulta contra Qdrant Cloud

Comando:

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\ask_rag.py `
  --query "No puedo tocar mi omoplato contrario con mi brazo derecho y siento rigidez en el hombro" `
  --response-quality high `
  --answer-backend grounded `
  --output-json data\knowledge\rag_runs\ask_rag_qdrant_cloud_shoulder.json
```

Salida:

- `D:\sistema-biomecanico\data\knowledge\rag_runs\ask_rag_qdrant_cloud_shoulder.json`

Esto confirma que retrieval + answering ya están funcionando sobre el cluster remoto.

### Verificación rápida de conexión

```powershell
Invoke-WebRequest `
  -Uri "https://<tu-cluster>.cloud.qdrant.io:6333/collections" `
  -Headers @{ "api-key" = "<tu-database-api-key>" } `
  -UseBasicParsing
```

## Sobre `mcp-server-qdrant`

Repositorio oficial:

- [qdrant/mcp-server-qdrant](https://github.com/qdrant/mcp-server-qdrant)

Qué resuelve:

- exponer una colección de Qdrant como herramientas MCP para clientes compatibles
- consultar o almacenar información desde un cliente MCP

Qué no reemplaza:

- no sustituye la creación inicial del cluster en Qdrant Cloud
- no reemplaza la configuración principal del proyecto Python

Cuándo tiene sentido usarlo:

- cuando ya existe un cluster local o cloud operativo
- cuando quieres exponer una colección concreta a un cliente MCP
- cuando quieras usar Qdrant como memoria semántica desde agentes/herramientas externas

Ejemplo de configuración del repo oficial:

- requiere `QDRANT_URL`
- requiere `QDRANT_API_KEY` si es cloud
- requiere `COLLECTION_NAME`

## Recomendación para el siguiente paso

1. Mantener Qdrant local mientras seguimos afinando retrieval y poblando más videos.
2. Crear el cluster en Qdrant Cloud manualmente.
3. Duplicar o migrar luego las colecciones activas:
   - `video_knowledge_units_v1`
   - `video_segments_v1`
4. Solo después decidir si conviene añadir `mcp-server-qdrant` como capa extra.

## Archivos clave relacionados

- `D:\sistema-biomecanico\scripts\run_youtube_batch.py`
- `D:\sistema-biomecanico\scripts\reindex_active_knowledge.py`
- `D:\sistema-biomecanico\scripts\reindex_active_segments.py`
- `D:\sistema-biomecanico\src\pipelines\youtube_batch_analysis.py`
- `D:\sistema-biomecanico\src\indexing\qdrant_store.py`
- `D:\sistema-biomecanico\data\knowledge\video_knowledge_drafts\conorharris_newest_41_50_gemini\run_summary.json`
