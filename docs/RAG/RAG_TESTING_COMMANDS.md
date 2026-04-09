# RAG Testing Commands

## Objetivo

Concentrar los comandos operativos y de validación del sistema RAG actual, indicando para qué sirve cada uno y con qué archivos o módulos se relaciona.

Todos los comandos asumen este entorno:

```powershell
D:\anaconda4\envs\analisis-bio\python.exe
```

## 1. Ejecutar pruebas del proyecto

### Comando

```powershell
D:\anaconda4\envs\analisis-bio\python.exe -m pytest
```

### Para qué sirve

- valida el proyecto completo
- detecta regresiones en extracción, segmentación, indexación y análisis

### Archivos relacionados

- [tests](/D:/sistema-biomecanico/tests)
- [AGENTS.md](/D:/sistema-biomecanico/AGENTS.md)

## 2. Registrar Shorts descubiertos en Supabase

### Comando

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\scrape_youtube_shorts.py `
  --channel-url https://www.youtube.com/@conorharris/shorts `
  --limit 12 `
  --order newest `
  --browser-channel msedge `
  --output-file data/knowledge/youtube_channels/conorharris_first12_scrape.json
```

### Para qué sirve

- scrapea la pestaña de Shorts con Playwright
- mantiene el estado JSON local de descubrimiento
- registra el scraping en Supabase
- marca cuáles URLs ya tienen draft activo y cuáles siguen pendientes

### Archivos relacionados

- [scrape_youtube_shorts.py](/D:/sistema-biomecanico/scripts/scrape_youtube_shorts.py)
- [youtube_shorts.py](/D:/sistema-biomecanico/video/youtube_shorts.py)
- [youtube_scrape_store.py](/D:/sistema-biomecanico/src/storage/youtube_scrape_store.py)

### Variante: scrape + análisis inmediato

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\scrape_youtube_shorts.py `
  --channel-url https://www.youtube.com/@conorharris/shorts `
  --limit 12 `
  --order newest `
  --browser-channel msedge `
  --analyze-pending `
  --analysis-backend local `
  --analysis-output-dir data/knowledge/video_knowledge_drafts/conorharris_first12_local `
  --output-file data/knowledge/youtube_channels/conorharris_first12_scrape_and_analyze.json
```

Sirve para:

- descubrir URLs
- registrar el scrape en Supabase
- filtrar pendientes desde Supabase
- analizar inmediatamente los pendientes con el backend elegido

El backend por defecto es `local`.

## 3. Listar pendientes desde Supabase

### Comando

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\list_pending_youtube_shorts.py `
  --channel-url https://www.youtube.com/@conorharris/shorts `
  --order newest `
  --limit 12 `
  --start-rank 1 `
  --end-rank 12 `
  --browser-channel msedge `
  --output-file data/knowledge/youtube_channels/conorharris_first12_pending.json
```

### Para qué sirve

- toma los Shorts del rango pedido
- consulta en Supabase cuáles ya tienen draft activo
- devuelve solo los que siguen pendientes de análisis

### Archivos relacionados

- [list_pending_youtube_shorts.py](/D:/sistema-biomecanico/scripts/list_pending_youtube_shorts.py)
- [youtube_scrape_store.py](/D:/sistema-biomecanico/src/storage/youtube_scrape_store.py)

## 4. Procesar un video local con la capa 1

### Comando

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\process_rag_source.py `
  --local-video "D:\sistema-biomecanico\data\to-learn\Fix Scapular Winging - For Good.mp4" `
  --language en `
  --tag scapula `
  --tag shoulder `
  --output-json "D:\sistema-biomecanico\data\knowledge\rag_runs\fix_scapular_winging_local_level1.json"
```

### Para qué sirve

- ejecuta el `Nivel 1`
- extrae audio, transcript, escenas, keyframes y OCR
- construye segmentos listos para retrieval

### Archivos relacionados

- [process_rag_source.py](/D:/sistema-biomecanico/scripts/process_rag_source.py)
- [process_video_local.py](/D:/sistema-biomecanico/src/pipelines/process_video_local.py)
- [whisper_asr.py](/D:/sistema-biomecanico/src/analysis/whisper_asr.py)
- [scene_detect.py](/D:/sistema-biomecanico/src/analysis/scene_detect.py)
- [frame_sampler.py](/D:/sistema-biomecanico/src/analysis/frame_sampler.py)
- [ocr.py](/D:/sistema-biomecanico/src/analysis/ocr.py)
- [align_segments.py](/D:/sistema-biomecanico/src/chunking/align_segments.py)

## 5. Procesar una URL de YouTube con la capa 1

### Comando

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\process_rag_source.py `
  --youtube-url "https://www.youtube.com/shorts/mI2n6asSFos" `
  --language en `
  --output-json "D:\sistema-biomecanico\data\knowledge\rag_runs\mI2n6asSFos_youtube_level1.json"
```

### Para qué sirve

- descarga el video desde YouTube
- lo pasa por la misma extracción local del `Nivel 1`
- genera un JSON con evidencia estructurada

### Archivos relacionados

- [process_rag_source.py](/D:/sistema-biomecanico/scripts/process_rag_source.py)
- [youtube_fetch.py](/D:/sistema-biomecanico/src/analysis/youtube_fetch.py)
- [process_video_local.py](/D:/sistema-biomecanico/src/pipelines/process_video_local.py)

## 6. Procesar y escribir en Supabase y Qdrant

### Comando

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\process_rag_source.py `
  --youtube-url "https://www.youtube.com/shorts/mI2n6asSFos" `
  --language en `
  --write-supabase `
  --write-qdrant `
  --output-json "D:\sistema-biomecanico\data\knowledge\rag_runs\mI2n6asSFos_youtube_level1_synced.json"
```

### Para qué sirve

- ejecuta el `Nivel 1`
- persiste `source`, `assets` y `segments` en Supabase
- indexa los segmentos en Qdrant

### Archivos relacionados

- [process_rag_source.py](/D:/sistema-biomecanico/scripts/process_rag_source.py)
- [supabase_store.py](/D:/sistema-biomecanico/src/storage/supabase_store.py)
- [qdrant_store.py](/D:/sistema-biomecanico/src/indexing/qdrant_store.py)
- [reindex.py](/D:/sistema-biomecanico/src/pipelines/reindex.py)

## 7. Generar knowledge draft heurístico

### Comando

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\analyze_rag_segments.py `
  --input-json "D:\sistema-biomecanico\data\knowledge\rag_runs\mI2n6asSFos_youtube_level1.json" `
  --backend heuristic `
  --output-json "D:\sistema-biomecanico\data\knowledge\rag_runs\mI2n6asSFos_youtube_knowledge_draft_heuristic.json"
```

### Para qué sirve

- usa la capa 2 local basada en reglas
- genera un draft de conocimiento sin depender de servicios externos

### Archivos relacionados

- [analyze_rag_segments.py](/D:/sistema-biomecanico/scripts/analyze_rag_segments.py)
- [knowledge_draft.py](/D:/sistema-biomecanico/src/analysis/knowledge_draft.py)

## 8. Generar knowledge draft con Hugging Face

### Comando

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\analyze_rag_segments.py `
  --input-json "D:\sistema-biomecanico\data\knowledge\rag_runs\mI2n6asSFos_youtube_level1.json" `
  --backend hf `
  --model "openai/gpt-oss-120b" `
  --output-json "D:\sistema-biomecanico\data\knowledge\rag_runs\mI2n6asSFos_youtube_knowledge_draft_hf.json"
```

### Para qué sirve

- usa la capa 2 con Hugging Face Inference Providers
- transforma la evidencia extraída del `Nivel 1` en JSON estructurado
- busca aproximarse a una salida tipo Gemini sin usar Gemini

### Modelo recomendado hoy

- `openai/gpt-oss-120b`

### Nota

- `Qwen/Qwen3-32B` sigue siendo una opción interesante, pero en esta etapa quedó más estable `openai/gpt-oss-120b` para `structured output`

### Requisitos

- `HF_TOKEN` en [.env](/D:/sistema-biomecanico/.env)

### Archivos relacionados

- [analyze_rag_segments.py](/D:/sistema-biomecanico/scripts/analyze_rag_segments.py)
- [hf_knowledge_draft.py](/D:/sistema-biomecanico/src/analysis/hf_knowledge_draft.py)
- [settings.py](/D:/sistema-biomecanico/src/core/settings.py)

## 9. Generar knowledge draft en modo automático

### Comando

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\analyze_rag_segments.py `
  --input-json "D:\sistema-biomecanico\data\knowledge\rag_runs\mI2n6asSFos_youtube_level1.json" `
  --backend auto `
  --output-json "D:\sistema-biomecanico\data\knowledge\rag_runs\mI2n6asSFos_youtube_knowledge_draft_auto.json"
```

### Para qué sirve

- intenta usar Hugging Face
- si no hay token o la llamada falla, cae al análisis heurístico

### Archivos relacionados

- [analyze_rag_segments.py](/D:/sistema-biomecanico/scripts/analyze_rag_segments.py)
- [hf_knowledge_draft.py](/D:/sistema-biomecanico/src/analysis/hf_knowledge_draft.py)

## 10. Consultar RAG con perfil de costo/calidad para HF

### Comando

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\ask_rag.py `
  --query "No puedo tocar mi omoplato contrario con mi brazo derecho y siento rigidez en el hombro" `
  --response-quality high `
  --answer-backend hf `
  --answer-profile balanced `
  --output-json "D:\sistema-biomecanico\data\knowledge\rag_runs\ask_rag_hf_balanced.json"
```

### Perfiles disponibles

- `balanced`
  - usa `Qwen/Qwen3-32B`
  - recomendado como mejor equilibrio actual para answering
- `cheap`
  - usa `Qwen/Qwen3-4B-Instruct-2507`
  - recomendado cuando importa más bajar costo que maximizar calidad

### Para qué sirve

- permite alternar entre modelos HF de answering sin tocar código
- usa la misma base RAG y el mismo retrieval
- sirve para comparar costo/calidad en consultas reales

### Archivos relacionados

- [ask_rag.py](/D:/sistema-biomecanico/scripts/ask_rag.py)
- [answering.py](/D:/sistema-biomecanico/src/rag/answering.py)
- [settings.py](/D:/sistema-biomecanico/src/core/settings.py)
- [knowledge_draft.py](/D:/sistema-biomecanico/src/analysis/knowledge_draft.py)

## 10. Ejecutar un lote de Shorts con backend seleccionable

### Comando

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\run_youtube_batch.py `
  --range 1-1 `
  --channel-url https://www.youtube.com/@conorharris/shorts `
  --order newest
```

### Para qué sirve

- scrapea y registra el rango en Supabase
- filtra automáticamente los videos ya analizados
- ejecuta el backend elegido para el análisis
- por defecto usa `local`

### Backends actuales

- `local` (default): `Nivel 1 local -> análisis HF -> sync a Supabase/Qdrant`
- `gemini`: análisis premium directo y persistencia posterior

### Nota de resiliencia

- si `gemini` falla en un video por cuota, timeout o error recuperable, el batch baja ese video a la ruta `local`
- el resto del lote continúa

### Backends reservados para después

- `skill_seekers`
- `hf_video_direct`

### Archivos relacionados

- [run_youtube_batch.py](/D:/sistema-biomecanico/scripts/run_youtube_batch.py)
- [process_rag_source.py](/D:/sistema-biomecanico/scripts/process_rag_source.py)
- [analyze_rag_segments.py](/D:/sistema-biomecanico/scripts/analyze_rag_segments.py)
- [sync_rag_knowledge_draft.py](/D:/sistema-biomecanico/scripts/sync_rag_knowledge_draft.py)

## 11. Consultar segmentos indexados en Qdrant

### Comando

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\query_rag_segments.py `
  --text "foot pronation corrective drill" `
  --limit 5 `
  --output-json "D:\sistema-biomecanico\data\knowledge\rag_runs\query_rag_segments_local.json"
```

### Para qué sirve

- consulta la colección actual de Qdrant
- devuelve los segmentos con mayor similitud semántica

### Archivos relacionados

- [query_rag_segments.py](/D:/sistema-biomecanico/scripts/query_rag_segments.py)
- [qdrant_store.py](/D:/sistema-biomecanico/src/indexing/qdrant_store.py)

## 12. Persistir knowledge draft en Supabase y Qdrant

### Comando

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\sync_rag_knowledge_draft.py `
  --draft-json "D:\sistema-biomecanico\data\knowledge\rag_runs\mI2n6asSFos_youtube_knowledge_draft_hf_gpt_oss.json" `
  --source-json "D:\sistema-biomecanico\data\knowledge\rag_runs\mI2n6asSFos_youtube_level1.json" `
  --write-qdrant `
  --output-json "D:\sistema-biomecanico\data\knowledge\rag_runs\mI2n6asSFos_youtube_knowledge_sync.json"
```

### Para qué sirve

- toma el draft de capa 2
- lo guarda como `rag_knowledge_drafts` y `rag_knowledge_units` en Supabase
- deriva segmentos de conocimiento y los indexa en la colección de conocimiento de Qdrant

### Archivos relacionados

- [sync_rag_knowledge_draft.py](/D:/sistema-biomecanico/scripts/sync_rag_knowledge_draft.py)
- [knowledge_projection.py](/D:/sistema-biomecanico/src/analysis/knowledge_projection.py)
- [persist_knowledge.py](/D:/sistema-biomecanico/src/pipelines/persist_knowledge.py)
- [supabase_store.py](/D:/sistema-biomecanico/src/storage/supabase_store.py)
- [qdrant_store.py](/D:/sistema-biomecanico/src/indexing/qdrant_store.py)

## 13. Importar drafts históricos de Gemini a Supabase y Qdrant

### Comando

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\import_gemini_knowledge_drafts.py `
  --write-qdrant `
  --output-json "D:\sistema-biomecanico\data\knowledge\rag_runs\import_gemini_knowledge_drafts_summary.json"
```

### Para qué sirve

- recorre `data/knowledge/video_knowledge_drafts`
- detecta qué JSON son drafts usables
- los normaliza al esquema actual
- los persiste en `rag_knowledge_drafts` y `rag_knowledge_units`
- indexa sus unidades de conocimiento en `video_knowledge_units_v1`

### Archivos relacionados

- [import_gemini_knowledge_drafts.py](/D:/sistema-biomecanico/scripts/import_gemini_knowledge_drafts.py)
- [gemini_draft_normalizer.py](/D:/sistema-biomecanico/src/analysis/gemini_draft_normalizer.py)
- [knowledge_projection.py](/D:/sistema-biomecanico/src/analysis/knowledge_projection.py)
- [persist_knowledge.py](/D:/sistema-biomecanico/src/pipelines/persist_knowledge.py)

## 14. Hacer una consulta RAG al sistema

### Comando

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\ask_rag.py `
  --query "No puedo elevar mi brazo derecho completamente" `
  --response-quality medium `
  --answer-backend auto `
  --output-json "D:\sistema-biomecanico\data\knowledge\rag_runs\ask_rag_medium.json"
```

### Para qué sirve

- ejecuta retrieval según la calidad elegida
- usa la colección de conocimiento y, si corresponde, la colección de evidencia
- genera una respuesta final con el backend configurado

### Calidad disponible

- `low`: prioriza `video_knowledge_units_v1`
- `medium`: usa conocimiento derivado y algo de evidencia
- `high`: usa retrieval híbrido más profundo

### Backends disponibles

- `auto`: intenta Ollama local, luego Hugging Face y finalmente fallback grounded
- `openai`: usa la API de OpenAI para redactar la respuesta grounded
- `ollama`: fuerza respuesta con el modelo local configurado
- `hf`: fuerza respuesta con Hugging Face Inference Providers
- `grounded`: no usa un LLM; arma una respuesta simple desde el contexto recuperado

### Variables relacionadas

- `ANSWER_BACKEND`
- `OLLAMA_BASE_URL`
- `OLLAMA_ANSWER_MODEL`
- `OLLAMA_TIMEOUT_SEC`
- `OPENAI_API_KEY` o `API_KEY_OPENAI`
- `OPENAI_ANSWER_MODEL`
- `HF_ANSWER_MODEL`

### Ejemplo usando Ollama

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\ask_rag.py `
  --query "Siento rigidez en el hombro y no puedo tocar mi omoplato contrario" `
  --response-quality high `
  --answer-backend ollama `
  --output-json "D:\sistema-biomecanico\data\knowledge\rag_runs\ask_rag_ollama_shoulder.json"
```

### Ejemplo usando OpenAI

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\ask_rag.py `
  --query "No puedo tocar mi omoplato contrario con mi brazo derecho y siento rigidez en el hombro" `
  --response-quality high `
  --answer-backend openai `
  --answer-model gpt-5-mini `
  --output-json "D:\sistema-biomecanico\data\knowledge\rag_runs\ask_rag_openai_shoulder.json"
```

### Archivos relacionados

- [ask_rag.py](/D:/sistema-biomecanico/scripts/ask_rag.py)
- [hybrid.py](/D:/sistema-biomecanico/src/retrieval/hybrid.py)
- [answering.py](/D:/sistema-biomecanico/src/rag/answering.py)
- [RAG_RETRIEVAL_COLLECTIONS_AND_QUALITY.md](/D:/sistema-biomecanico/docs/RAG/RAG_RETRIEVAL_COLLECTIONS_AND_QUALITY.md)

## 15. Validar solo la capa 2 y answering

### Comando

```powershell
D:\anaconda4\envs\analisis-bio\python.exe -m pytest `
  tests\test_knowledge_draft.py `
  tests\test_hf_knowledge_draft.py `
  tests\test_retrieval_and_answering.py `
  tests\test_imports.py
```

### Para qué sirve

- valida la capa heurística
- valida la integración estructurada de Hugging Face con mocks
- valida el answering con contexto recuperado
- confirma que los imports críticos siguen sanos

### Archivos relacionados

- [test_knowledge_draft.py](/D:/sistema-biomecanico/tests/test_knowledge_draft.py)
- [test_hf_knowledge_draft.py](/D:/sistema-biomecanico/tests/test_hf_knowledge_draft.py)
- [test_retrieval_and_answering.py](/D:/sistema-biomecanico/tests/test_retrieval_and_answering.py)
- [test_imports.py](/D:/sistema-biomecanico/tests/test_imports.py)

## 16. Empujar migraciones de Supabase

### Comando

```powershell
supabase db push
```

### Para qué sirve

- aplica migraciones pendientes del proyecto a la base remota

### Archivos relacionados

- [supabase\migrations](/D:/sistema-biomecanico/supabase/migrations)

## 17. Sincronizar conocimiento legacy a Supabase

### Comando

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\sync_movement_knowledge_supabase.py
```

### Para qué sirve

- empuja migraciones si hace falta
- importa los JSON incrementales de `data/knowledge/video_knowledge_drafts`
- evita duplicados por `content_sha256`

### Archivos relacionados

- [sync_movement_knowledge_supabase.py](/D:/sistema-biomecanico/scripts/sync_movement_knowledge_supabase.py)
- [import_movement_knowledge_to_supabase.py](/D:/sistema-biomecanico/scripts/import_movement_knowledge_to_supabase.py)
- [movement_knowledge_import.py](/D:/sistema-biomecanico/video/movement_knowledge_import.py)

## Recomendación práctica

Para validar el flujo nuevo del RAG, la secuencia más útil hoy es:

1. `process_rag_source.py`
2. `analyze_rag_segments.py`
3. `sync_rag_knowledge_draft.py` o `import_gemini_knowledge_drafts.py`
4. `ask_rag.py`
5. `query_rag_segments.py`

Eso permite comprobar:

- extracción
- construcción de conocimiento
- retrieval

## 18. Levantar Qdrant local con puerto HTTP

### Comando

```powershell
powershell -ExecutionPolicy Bypass -File D:\sistema-biomecanico\scripts\start_qdrant_server.ps1
```

### Para qué sirve

- levanta Qdrant como servidor local en `http://127.0.0.1:6333`
- permite inspeccionar colecciones desde el navegador o por HTTP
- deja el proyecto listo para usar `QDRANT_PREFER_EMBEDDED=false`

### Archivos relacionados

- [start_qdrant_server.ps1](/D:/sistema-biomecanico/scripts/start_qdrant_server.ps1)
- [.env](/D:/sistema-biomecanico/.env)
- [settings.py](/D:/sistema-biomecanico/src/core/settings.py)

### Nota

- el binario oficial de Windows queda en `tools/qdrant-server/qdrant.exe`
- el endpoint útil para revisar colecciones es [http://127.0.0.1:6333/collections](http://127.0.0.1:6333/collections)

## 19. Reconstruir Supabase y Qdrant desde los lotes 11-20 y 21-30

### Comando

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\import_gemini_knowledge_drafts.py `
  --input-dir data/knowledge/video_knowledge_drafts/conorharris_newest_11_20 `
  --input-dir data/knowledge/video_knowledge_drafts/conorharris_newest_21_30 `
  --reset-rag-storage `
  --reset-qdrant `
  --write-qdrant `
  --output-json data/knowledge/rag_runs/import_conorharris_11_30_rebuild.json
```

### Para qué sirve

- limpia la información operativa previa en Supabase
- limpia las colecciones de Qdrant
- vuelve a cargar solo los drafts Gemini de esos dos lotes
- guarda todos los drafts en Supabase
- indexa en Qdrant únicamente los drafts útiles

### Nota

- este reset ya limpia solo las tablas vigentes del flujo actual
- ya no intenta truncar tablas legacy eliminadas del esquema

### Archivos relacionados

- [import_gemini_knowledge_drafts.py](/D:/sistema-biomecanico/scripts/import_gemini_knowledge_drafts.py)
- [gemini_draft_normalizer.py](/D:/sistema-biomecanico/src/analysis/gemini_draft_normalizer.py)
- [knowledge_projection.py](/D:/sistema-biomecanico/src/analysis/knowledge_projection.py)
- [persist_knowledge.py](/D:/sistema-biomecanico/src/pipelines/persist_knowledge.py)
- [import_conorharris_11_30_rebuild.json](/D:/sistema-biomecanico/data/knowledge/rag_runs/import_conorharris_11_30_rebuild.json)

## 20. Resetear Qdrant local del servidor cuando una colección queda corrupta

### Comando

```powershell
powershell -ExecutionPolicy Bypass -File D:\sistema-biomecanico\scripts\reset_qdrant_server.ps1
```

### Para qué sirve

- detiene el servidor local de Qdrant
- elimina por defecto solo la colección de evidencia `video_segments_v1`
- vuelve a levantar el servidor limpio
- evita errores como WAL bloqueado o colecciones visibles en disco pero no en la API

### Variante: reset completo del storage del servidor

```powershell
powershell -ExecutionPolicy Bypass -File D:\sistema-biomecanico\scripts\reset_qdrant_server.ps1 -FullReset
```

Usa esta variante solo cuando quieras reconstruir completamente las colecciones del servidor.

### Archivos relacionados

- [reset_qdrant_server.ps1](/D:/sistema-biomecanico/scripts/reset_qdrant_server.ps1)
- [start_qdrant_server.ps1](/D:/sistema-biomecanico/scripts/start_qdrant_server.ps1)
- [qdrant_store.py](/D:/sistema-biomecanico/src/indexing/qdrant_store.py)

## 21. Upgrade a Gemini por cantidad de drafts activos

### Comando

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\upgrade_drafts_to_gemini.py `
  --limit 10 `
  --order asc `
  --model gemini-2.5-flash `
  --output-json data/knowledge/rag_runs/upgrade_drafts_to_gemini_limit.json
```

### Para que sirve

- busca drafts activos con calidad `standard` o `fallback`
- excluye drafts cuyo proveedor ya sea `gemini`
- los reanaliza con Gemini
- guarda el nuevo draft en Supabase
- si Gemini devuelve un draft util o mixed, lo promueve como activo
- elimina en Qdrant la version activa anterior del mismo `source` y deja solo la nueva

### Regla importante

- si Gemini clasifica el video como `not_useful`, el nuevo draft se guarda en Supabase pero no reemplaza al draft activo anterior

### Archivos relacionados

- [upgrade_drafts_to_gemini.py](/D:/sistema-biomecanico/scripts/upgrade_drafts_to_gemini.py)
- [gemini_knowledge.py](/D:/sistema-biomecanico/video/gemini_knowledge.py)
- [supabase_store.py](/D:/sistema-biomecanico/src/storage/supabase_store.py)
- [persist_knowledge.py](/D:/sistema-biomecanico/src/pipelines/persist_knowledge.py)
- [qdrant_store.py](/D:/sistema-biomecanico/src/indexing/qdrant_store.py)

## 22. Upgrade a Gemini por URLs especificas

### Comando

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\upgrade_drafts_to_gemini.py `
  --url https://www.youtube.com/shorts/xFNPwIoJbTI `
  --url https://www.youtube.com/shorts/N2mMGWltYrI `
  --model gemini-2.5-flash `
  --output-json data/knowledge/rag_runs/upgrade_drafts_to_gemini_urls.json
```

### Para que sirve

- toma URLs especificas ya existentes en la base
- busca su draft activo actual
- si el draft activo ya es de Gemini, lo omite
- si no es de Gemini, intenta hacer el upgrade premium

### Archivos relacionados

- [upgrade_drafts_to_gemini.py](/D:/sistema-biomecanico/scripts/upgrade_drafts_to_gemini.py)
- [RAG_ANALYSIS_VERSIONING_AND_UPGRADE_STRATEGY.md](/D:/sistema-biomecanico/docs/RAG/RAG_ANALYSIS_VERSIONING_AND_UPGRADE_STRATEGY.md)

## 23. Listar intentos fallidos de analisis

### Comando

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\list_failed_analysis_attempts.py `
  --limit 10 `
  --order desc `
  --requested-backend gemini_upgrade `
  --output-json data/knowledge/rag_runs/failed_analysis_attempts.json
```

### Para que sirve

- lista intentos fallidos registrados en Supabase
- no toca Qdrant
- sirve para auditoria, depuracion y reintentos posteriores

### Archivos relacionados

- [list_failed_analysis_attempts.py](/D:/sistema-biomecanico/scripts/list_failed_analysis_attempts.py)
- [supabase_store.py](/D:/sistema-biomecanico/src/storage/supabase_store.py)

## 24. Reintentar intentos fallidos de analisis

### Comando

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\retry_failed_analysis_attempts.py `
  --limit 5 `
  --order desc `
  --requested-backend gemini_upgrade `
  --model gemini-2.5-flash `
  --output-json data/knowledge/rag_runs/retry_failed_analysis_attempts.json
```

### Para que sirve

- toma los fallos recientes desde `rag_analysis_attempts`
- reintenta el upgrade a Gemini para esas URLs
- deja un resumen del reintento y mantiene el historial de intentos

### Archivos relacionados

- [retry_failed_analysis_attempts.py](/D:/sistema-biomecanico/scripts/retry_failed_analysis_attempts.py)
- [upgrade_drafts_to_gemini.py](/D:/sistema-biomecanico/scripts/upgrade_drafts_to_gemini.py)
- [ARTIFACT_PATHS.md](/D:/sistema-biomecanico/src/rag/ARTIFACT_PATHS.md)
