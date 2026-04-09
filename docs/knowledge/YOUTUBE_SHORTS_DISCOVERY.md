# Descubrimiento Automatizado de YouTube Shorts

## Objetivo

Automatizar la obtencion de URLs de Shorts desde una pagina de canal como:

- `https://www.youtube.com/@conorharris/shorts`

con capacidad para:

- elegir cantidad maxima de resultados
- elegir orden (`newest`, `popular`, `oldest`)
- guardar un estado persistente de videos ya vistos
- detectar solo videos nuevos en ejecuciones posteriores
- dejar un snapshot listo para el pipeline de analisis con Gemini

## Implementacion

Se agrego:

- modulo reusable: `video/youtube_shorts.py`
- CLI: `scripts/scrape_youtube_shorts.py`

### Navegador

El scraper esta preparado para usar Playwright con Edge estable:

- `browser_channel="msedge"`

Esto evita depender de Chrome y aprovecha tu instalacion local de Microsoft Edge.

## Flujo

```text
channel shorts url
-> Playwright abre la pagina
-> selecciona orden
-> hace scroll hasta juntar N shorts o quedarse sin nuevos
-> extrae cards con url, titulo y vistas
-> compara contra state.json
-> guarda new_videos
```

## Estado persistente

El archivo de estado guarda:

- `channel_url`
- `last_checked_at`
- `seen_video_ids`
- `seen_urls`
- `history`

Con esto, en la siguiente corrida puedes detectar solo links nuevos y no reprocesar los ya analizados.

## Comando ejemplo

```bash
D:\anaconda4\envs\analisis-bio\python.exe scripts\scrape_youtube_shorts.py \
  --channel-url https://www.youtube.com/@conorharris/shorts \
  --limit 90 \
  --order newest \
  --browser-channel msedge
```

## Archivos de salida por defecto

- estado: `data/knowledge/youtube_channels/conorharris_state.json`
- snapshot: `data/knowledge/youtube_channels/latest_scrape.json`

## Uso esperado con Gemini

El siguiente paso natural es:

```text
new_videos
-> intake
-> Gemini video understanding
-> protocol draft JSON
```

## Notas

- YouTube puede cambiar su DOM y eso puede requerir ajustes en selectores.
- Si el canal esta en espanol o ingles, el scraper intenta soportar ambos labels de orden.
- Si luego quieres usar Opera GX, tambien se puede con `executable_path`, pero Edge estable es la opcion mas simple y soportada por Playwright.
