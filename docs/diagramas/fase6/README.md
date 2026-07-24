# Diagramas editables de la fase 6

Esta carpeta contiene los diagramas utilizados para explicar la arquitectura,
los flujos por rol, el procesamiento y la trazabilidad de los objetivos
específicos del sistema de sentadilla bilateral.

## Inventario

| Archivo | Uso |
|---|---|
| `arquitectura_sistema_sentadilla.drawio` | Tecnologías, componentes y almacenamiento |
| `flujo_investigador_sentadilla.drawio` | Recorrido desde el registro hasta la exportación |
| `flujo_experto_instrumento3.drawio` | Evaluación ciega del experto |
| `flujo_video_no_apto_sentadilla.drawio` | Separación entre calidad de entrada y análisis biomecánico |
| `secuencia_procesamiento_video.drawio` | Interacción entre investigador, web, API, visión y Supabase |
| `secuencia_comparacion_metricas.drawio` | Evaluación, consolidación, consenso y métricas |
| `trazabilidad_objetivos_evidencias.drawio` | Relación entre objetivos, resultados y verificaciones |

## Edición

Los archivos usan XML nativo sin comprimir y pueden abrirse directamente en
[diagrams.net](https://app.diagrams.net/). Sus cajas, textos y conectores son
editables de forma independiente.

Los diagramas se regeneran con:

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\generate_phase6_drawio.py
```

La validez estructural se comprueba con:

```powershell
D:\anaconda4\envs\analisis-bio\python.exe -m pytest tests\test_generate_phase6_drawio.py
```

El generador evita depender de una aplicación de escritorio o de un MCP. Si
posteriormente se habilita `jgraph/drawio-mcp`, estos mismos archivos pueden
abrirse y editarse sin conversión.
