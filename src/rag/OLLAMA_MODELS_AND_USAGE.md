# Ollama Models And Usage

## Objetivo

Documentar los modelos de Ollama usados o probados en este proyecto, cómo seleccionarlos en consultas RAG y qué esperar de ellos según el hardware disponible.

## Modelos observados en este equipo

Al momento de esta documentación, `ollama list` mostró:

- `gpt-oss:120b-cloud`
- `qwen3:8b`
- `qwen3:4b`

## Qué significa cada caso

### `gpt-oss:120b-cloud`

- no es una descarga local usable como modelo liviano
- el tag indica una ruta cloud
- no debe asumirse como una opción local barata

### `qwen3:8b`

- modelo local real descargado
- tamaño aproximado en disco: varios GB
- en esta máquina fue demasiado lento para el prompt actual de answering

### `qwen3:4b`

- modelo local real descargado
- más liviano que `qwen3:8b`
- sigue siendo una opción razonable para experimentar
- en esta máquina todavía resultó lento para el answering actual con contexto RAG amplio

## Cómo descargar más modelos

Ejemplos:

```powershell
ollama pull qwen3:4b
ollama pull qwen3:8b
ollama pull mistral:7b
```

Para listar modelos instalados:

```powershell
ollama list
```

Para ver qué está corriendo:

```powershell
ollama ps
```

## Cómo usar un modelo de Ollama en `ask_rag.py`

### Backend Ollama con modelo explícito

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\ask_rag.py `
  --query "No puedo elevar mi brazo derecho completamente" `
  --response-quality medium `
  --answer-backend ollama `
  --answer-model qwen3:4b `
  --output-json "D:\sistema-biomecanico\data\knowledge\rag_runs\ask_rag_ollama_qwen3_4b.json"
```

## Variables relacionadas

- `ANSWER_BACKEND`
- `OLLAMA_BASE_URL`
- `OLLAMA_ANSWER_MODEL`
- `OLLAMA_TIMEOUT_SEC`

## Recomendación práctica para este proyecto

En hardware modesto:

- usar `grounded` como default
- usar `openai` para consultas cuando se quiera mejor redacción
- usar `ollama` como opción experimental o para equipos más potentes

## Cuándo vale la pena probar más modelos

Tiene sentido probar más modelos locales si:

- el equipo tiene más RAM
- hay una GPU con más VRAM
- se reduce el contexto de prompting
- se simplifica el formato de salida

En ese caso, basta con:

1. descargar el modelo con `ollama pull`
2. pasar el tag con `--answer-model`
3. comparar tiempo y calidad sobre las mismas consultas RAG
