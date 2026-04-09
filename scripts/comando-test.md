- python scripts\run_rest_analysis.py --rest-video "data\videos\rest\rest-1.mp4" --json

- python scripts\run_rest_analysis.py `
--rest-phase1-front "data\images\evaluations\frontal\frontal-1.jpeg" `
--rest-phase1-side "data\images\evaluations\lateral\lateral-1.jpeg" `
--rest-phase1-back "data\images\evaluations\posterior\posterior-1.jpeg" `
--face-front-face "data\images\evaluations\face\face-1.jpeg" `
--foot-triptych-front "data\images\evaluations\feet\frontal\frontal-lower-1.jpeg" `   
--foot-triptych-back "data\images\evaluations\feet\posterior\posterior-feet-1.jpeg" `
--foot-triptych-left-arch "data\images\evaluations\feet\lateral\arch-left-1.jpeg" `   
--foot-triptych-right-arch "data\images\evaluations\feet\lateral\arch-right-1.jpeg" ` 
--isa-front-torso "data\images\evaluations\isa\isa-1.jpeg" `
--scapula-back-upper-body "data\images\evaluations\escapula\escapula-1.jpeg" `        
--json


python scripts\run_rest_analysis.py `
    --breathing-video "data\videos\breathing_cycle_test\breathing-1.mp4" `
    --rest-phase1-front "data\images\evaluations\frontal\frontal-1.jpeg" `
    --rest-phase1-side "data\images\evaluations\lateral\lateral-1.jpeg" `
    --rest-phase1-back "data\images\evaluations\posterior\posterior-1.jpeg" `
    --face-front-face "data\images\evaluations\face\face-1.jpeg" `
    --foot-triptych-front "data\images\evaluations\feet\frontal\frontal-feet-1.jpeg" `   
    --foot-triptych-back "data\images\evaluations\feet\posterior\posterior-feet-1.jpeg" `
    --foot-triptych-left-arch "data\images\evaluations\feet\lateral\arch-left-1.jpeg" `   
    --foot-triptych-right-arch "data\images\evaluations\feet\lateral\arch-right-1.jpeg" ` 
    --isa-front-torso "data\images\evaluations\isa\isa-3.jpeg" `
    --scapula-back-upper-body "data\images\evaluations\escapula\escapula-1.jpeg" `        
    --json

python scripts/run_rest_analysis.py `
    --isa-front-torso "data/images/evaluations/isa/frontal-transparencia.JPG" `
    --breathing-video "data/videos/breathing_cycle_test/respiracion.mp4" `
    --aggregation median `
    --frame-step 10 `
    --max-frames 12 `
    --json `
    --save-json `
    --save-overlay-image `
    --save-overlay-video `
    --save-csv `
    --save-plots `
    --output-dir "debug/isa_test"

-- SE PUEDE ELEGIR EL DIRECTORIO DE SALIDA CON --output-dir


python scripts\run_rest_analysis.py `
>>     --rest-phase1-front "data\images\evaluations\frontal\frontal-1.jpeg" `
>>     --rest-phase1-side "data\images\evaluations\lateral\lateral-1.jpeg" `
>>     --rest-phase1-back "data\images\evaluations\posterior\posterior-1.jpeg" `
>>     --face-front-face "data\images\evaluations\face\face-1.jpeg" `
>>     --foot-triptych-front "data\images\evaluations\feet\frontal\frontal-lower-1.jpeg" `
>>     --foot-triptych-back "data\images\evaluations\feet\posterior\posterior-feet-1.jpeg" `
>>     --foot-triptych-left-arch "data\images\evaluations\feet\lateral\arch-left-1.jpeg" `
>>     --foot-triptych-right-arch "data\images\evaluations\feet\lateral\arch-right-1.jpeg" `
>>     --scapula-back-upper-body "data\images\evaluations\escapula\escapula-1.jpeg" `
>>     --json

--------
python scripts/run_rest_analysis.py `   
>>     --isa-front-torso "data/images/evaluations/isa/frontal-transparencia.JPG" `
>>     --breathing-video "data/videos/breathing_cycle_test/respiracion.mp4" `     
>>     --aggregation median `
>>     --frame-step 10 `
>>     --max-frames 12 `
>>     --json `
>>     --save-json `
>>     --save-overlay-image `
>>     --save-overlay-video `
>>     --save-csv `
>>     --save-plots `
>>     --output-dir "debug/isa_test/prueba-1"

--------

  Comando para reproducir prueba-1:

  python scripts\run_rest_analysis.py `
    --movement-type shoulder_abduction `
    --movement-back-video data\videos\shoulder_abduction\shoulder_abduction_1.mp4 `
    --aggregation median `
    --frame-step 2 `
    --max-frames 60 `
    --save-json `
    --save-overlay-video `
    --save-csv `
    --save-plots `
    --movement-overlay-mode both `
    --output-dir debug\shoulder_abduction_test\prueba-1

  Si quieres correr el segundo video como prueba aparte:

  python scripts\run_rest_analysis.py `
    --movement-type shoulder_abduction `
    --movement-back-video data\videos\shoulder_abduction\shoulder_abduction_2.mp4 `
    --aggregation median `
    --frame-step 2 `
    --max-frames 60 `
    --save-json `
    --save-overlay-video `
    --save-csv `
    --save-plots `
    --movement-overlay-mode both `
    --output-dir debug\shoulder_abduction_test\prueba-2

--------

Comando unico para analizar Shorts de YouTube con validacion previa:

Este comando hace todo en una sola ejecucion:
- obtiene los Shorts del canal segun el rango solicitado
- valida contra `data\knowledge\video_knowledge_registry.json`
- omite los videos ya analizados
- envia solo los pendientes a la API de Gemini
- guarda los JSON generados y actualiza el registro global

Comando base:

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\analyze_youtube_shorts_with_gemini.py `
  --channel-url https://www.youtube.com/@conorharris/shorts `
  --order newest `
  --start-rank 21 `
  --end-rank 30 `
  --browser-channel msedge `
  --model gemini-2.5-flash `
  --output-dir data/knowledge/video_knowledge_drafts/conorharris_newest_21_30
```

Como funciona:
- `--channel-url`: canal o pestaña Shorts a revisar
- `--order`: orden de YouTube a usar, por ejemplo `newest`, `popular` u `oldest`
- `--start-rank` y `--end-rank`: rango de posiciones a evaluar
- `--browser-channel msedge`: usa Microsoft Edge con Playwright
- `--model`: modelo de Gemini a usar
- `--output-dir`: carpeta donde se guardan los resultados del lote

Archivos que actualiza:
- `data\knowledge\video_knowledge_registry.json`: registro global de videos ya analizados
- `data\knowledge\video_knowledge_drafts\...\aggregate_*.json`: agregado del lote
- `data\knowledge\video_knowledge_drafts\...\run_summary.json`: resumen del lote
- `data\knowledge\video_knowledge_drafts\...\XXX_videoid.json`: analisis individual por video

Ejemplo 1. Analizar posiciones 21 a 30:

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\analyze_youtube_shorts_with_gemini.py `
  --channel-url https://www.youtube.com/@conorharris/shorts `
  --order newest `
  --start-rank 21 `
  --end-rank 30 `
  --browser-channel msedge `
  --model gemini-2.5-flash `
  --output-dir data/knowledge/video_knowledge_drafts/conorharris_newest_21_30
```

Ejemplo 2. Revisar los primeros 20 y analizar solo los que aun no fueron procesados:

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\analyze_youtube_shorts_with_gemini.py `
  --channel-url https://www.youtube.com/@conorharris/shorts `
  --order newest `
  --start-rank 1 `
  --end-rank 20 `
  --browser-channel msedge `
  --model gemini-2.5-flash `
  --output-dir data/knowledge/video_knowledge_drafts/conorharris_newest_1_20_pending_only
```

Nota:
- Si el rango ya fue analizado antes, el comando no vuelve a gastar llamadas en esos videos.
- Solo si quieres forzar un reanalisis completo, agrega `--include-analyzed`.

--------

Comando corto recomendado para YouTube Shorts:

Este wrapper evita escribir el comando largo. Internamente llama a `scripts\analyze_youtube_shorts_with_gemini.py`, mantiene la validacion contra el registro global y construye automaticamente la carpeta de salida del lote.

Comando corto base:

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\run_youtube_batch.py --range 21-30
```

Para que sirve:
- obtiene el rango solicitado desde la pestaña Shorts del canal por defecto
- valida si cada video ya fue analizado usando `data\knowledge\video_knowledge_registry.json`
- analiza solo los pendientes con Gemini
- guarda el resultado en una carpeta con este formato:
  `data\knowledge\video_knowledge_drafts\conorharris_newest_21_30`

Ejecutar analisis de videos 21 a 30:

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\run_youtube_batch.py --range 21-30
```

Ejecutar el procedimiento completo para videos 31 a 40:

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\run_youtube_batch.py --range 31-40
```

Opciones utiles:
- usar otro orden:
  `D:\anaconda4\envs\analisis-bio\python.exe scripts\run_youtube_batch.py --range 31-40 --order popular`
- abrir Edge visible:
  `D:\anaconda4\envs\analisis-bio\python.exe scripts\run_youtube_batch.py --range 31-40 --headful`
- forzar reanalisis aunque ya exista en el registro:
  `D:\anaconda4\envs\analisis-bio\python.exe scripts\run_youtube_batch.py --range 21-30 --include-analyzed`

--------

Sincronizacion completa de conocimiento hacia Supabase:

Este proceso ya evita duplicados. El importador no vuelve a insertar el mismo analisis si el contenido JSON ya fue enviado antes.

Como evita duplicados:
- cada analisis individual se transforma y se calcula un `content_sha256`
- la tabla `movement_knowledge.video_analyses` tiene ese hash como `unique`
- antes de insertar, el script consulta si ese hash ya existe
- si ya existe, lo marca como `Skipped existing` y no lo vuelve a insertar

Eso significa:
- `supabase db push` no duplica migraciones porque Supabase rastrea qué migraciones ya fueron aplicadas
- la importacion no duplica analisis ya cargados

Comando unico recomendado:

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\sync_movement_knowledge_supabase.py
```

Como funciona:
- ejecuta `supabase db push`
- luego ejecuta la importacion incremental desde `data/knowledge/video_knowledge_drafts`
- si un JSON ya fue insertado antes, lo omite
- si un JSON nuevo aparece despues, ese si lo inserta

Comandos utiles:

Solo importacion incremental, sin volver a hacer `db push`:

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\sync_movement_knowledge_supabase.py --skip-db-push
```

Probar sin escribir en la base:

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\sync_movement_knowledge_supabase.py --dry-run
```

Limitar la cantidad de archivos:

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\sync_movement_knowledge_supabase.py --limit 5
```

Variables recomendadas en `.env`:

Para este proyecto, hoy conviene separar variables por tipo de uso:

- `SUPABASE_URL`
  URL del proyecto para clientes y SDKs.
- `SUPABASE_PUBLISHABLE_KEY`
  Reemplaza el uso recomendado de `anon` para frontend, apps cliente y usos públicos.
- `SUPABASE_SECRET_KEY`
  Reemplaza el uso recomendado de `service_role` para backend seguro.
- `SUPABASE_DB_URL`
  Conexion Postgres directa para scripts de importacion, psycopg y cargas masivas.
- `SUPABASE_BUCKET`
  Nombre del bucket si luego conectamos Storage.

Compatibilidad:
- `SUPABASE_ANON_KEY` y `SUPABASE_SERVICE_KEY` pueden seguir existiendo temporalmente si todavia tienes codigo viejo, pero para nuevo desarrollo conviene migrar a `SUPABASE_PUBLISHABLE_KEY` y `SUPABASE_SECRET_KEY`.
