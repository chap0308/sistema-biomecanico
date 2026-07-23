# Datos de sentadilla bilateral

Esta carpeta organiza los videos y artefactos de la tesis sin publicar datos personales en GitHub.

```text
sentadilla_bilateral/
  raw/               Videos originales restringidos
  curated/           Videos aceptados por el protocolo
  metadata/          Registro local de casos
  labels_expertos/   Clasificaciones de evaluadores
  outputs/           JSON, CSV, overlays y reportes generados
```

Los contenidos de esas carpetas están ignorados por Git. Solo se versionan este documento y
`metadata/casos.example.csv`, que define el esquema sin información de participantes.

Inicialización local:

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\run_squat_analysis.py init
```

Flujo técnico por caso:

```powershell
# 1. Extraer puntos anatómicos clave y calidad de pose
D:\anaconda4\envs\analisis-bio\python.exe scripts\run_squat_analysis.py extract-pose `
  --case-id caso_001 `
  --video data\sentadilla_bilateral\raw\caso_001.mp4

# 2. Segmentar repeticiones y fases
D:\anaconda4\envs\analisis-bio\python.exe scripts\run_squat_analysis.py segment `
  --case-id caso_001 `
  --landmarks-csv data\sentadilla_bilateral\outputs\caso_001\landmarks.csv `
  --frame-quality-csv data\sentadilla_bilateral\outputs\caso_001\frame_quality.csv

# 3. Calcular variables biomecánicas observables
D:\anaconda4\envs\analisis-bio\python.exe scripts\run_squat_analysis.py metrics `
  --case-id caso_001 `
  --landmarks-csv data\sentadilla_bilateral\outputs\caso_001\landmarks.csv `
  --frame-phases-csv data\sentadilla_bilateral\outputs\caso_001\frame_phases.csv
```

Las especificaciones de cámara, encuadre, iluminación, vestimenta, ejecución y nombres de archivo se encuentran en [guia_tecnica_grabacion_videos_sentadilla.md](/D:/sistema-biomecanico/docs/guia_tecnica_grabacion_videos_sentadilla.md).
