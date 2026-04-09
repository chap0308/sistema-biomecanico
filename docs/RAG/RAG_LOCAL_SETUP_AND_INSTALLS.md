# RAG Local Setup And Installs

## Objetivo

Registrar qué componentes del stack RAG ya fueron instalados localmente y con qué comandos se hizo.

Este documento sirve como referencia operativa para reproducir el entorno local del proyecto en Windows.

## Entorno Python usado

Todos los comandos Python del proyecto se están ejecutando con:

```powershell
D:\anaconda4\envs\analisis-bio\python.exe
```

## Componentes RAG instalados

### Ya instalados

- `qdrant-client`
- `psycopg`
- `faster-whisper`
- `opencv-python`
- `scenedetect`
- `pytesseract`
- `ffmpeg` por `winget`
- `Tesseract OCR` por `winget`

### Estado práctico actual

- `ffmpeg`: disponible
- `scenedetect`: disponible en el entorno Python
- `pytesseract`: disponible en el entorno Python
- `tesseract.exe`: instalado y detectable por ruta común de Windows

## Comandos usados

### 1. Paquetes Python del stack RAG

```powershell
D:\anaconda4\envs\analisis-bio\python.exe -m pip install scenedetect pytesseract
```

### 2. FFmpeg en Windows

```powershell
winget install --source winget --id Gyan.FFmpeg.Essentials --accept-source-agreements --accept-package-agreements --silent
```

### 3. Tesseract OCR en Windows

```powershell
winget install --source winget --id UB-Mannheim.TesseractOCR --accept-source-agreements --accept-package-agreements --silent
```

## Comandos de verificación usados

### Verificar `ffmpeg`

```powershell
ffmpeg -version
```

### Verificar `scenedetect` y `pytesseract`

```powershell
@'
import scenedetect, pytesseract
print('scenedetect', scenedetect.__version__)
print('pytesseract', pytesseract.__version__)
'@ | D:\anaconda4\envs\analisis-bio\python.exe -
```

### Verificar `tesseract.exe`

```powershell
Get-ChildItem 'C:\Program Files' -Recurse -Filter tesseract.exe -ErrorAction SilentlyContinue | Select-Object -First 5 FullName
```

## Ajustes del proyecto

El código del pipeline local ya quedó preparado para resolver `tesseract` por tres vías:

1. variable de entorno `TESSERACT_CMD`
2. `PATH`
3. ruta típica de Windows:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

Para `ffmpeg`, el proyecto también puede resolver:

1. variable de entorno `FFMPEG_CMD`
2. `PATH`
3. ruta de instalación detectada bajo WinGet

## Variables de entorno recomendadas

Si quieres dejar el OCR totalmente explícito, puedes agregar a `.env`:

```env
TESSERACT_CMD="C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
```

Y para `ffmpeg`:

```env
FFMPEG_CMD="C:\\Users\\elias\\AppData\\Local\\Microsoft\\WinGet\\Packages\\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\\ffmpeg-8.1-essentials_build\\bin\\ffmpeg.exe"
```

Para Qdrant local ya embebido:

```env
QDRANT_PREFER_EMBEDDED=true
QDRANT_PATH="data/qdrant_local"
QDRANT_COLLECTION="video_segments_v1"
```

## Observaciones

- `ffmpeg` fue agregado por `winget` y puede requerir reiniciar la terminal para que el alias aparezca en nuevas sesiones.
- `Tesseract OCR` quedó instalado, pero no necesariamente expuesto en `PATH`; por eso el proyecto ahora también lo resuelve por ruta conocida.
- Este documento cubre el stack local del Nivel 1 del pipeline RAG.
