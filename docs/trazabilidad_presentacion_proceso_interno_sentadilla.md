# Trazabilidad de la presentación del proceso interno

## Fuente de verdad

La narrativa se mantiene en `guion_presentacion_proceso_interno_sentadilla.md`. El archivo PowerPoint es el entregable visual editable y la instantánea Markdown obtenida con AnyDoc permite comparar semánticamente cada versión binaria mediante Git.

```text
guion Markdown -> construcción visual -> PPTX -> AnyDoc -> instantánea Markdown
       |                                                    |
       +--------------------- revisión Git -----------------+
```

La conversión no pretende reproducir el diseño de PowerPoint. Su objetivo es verificar títulos, textos, fórmulas, notas y orden narrativo sin depender de una comparación visual entre archivos binarios.

## Versiones

### Versión 2

- Archivo: `presentacion_proceso_interno_sentadilla_v2.pptx`.
- Diapositivas: 16.
- Commit de referencia: `3ac1b4e`.
- Alcance: cadena desde video hasta reglas interpretables, calidad de pose, segmentación, variables y demostración web.

### Versión 3

- Archivo: `presentacion_proceso_interno_sentadilla_v3.pptx`.
- Diapositivas: 18.
- Fecha: 12 de agosto de 2026.
- Cambios principales:
  - se explica qué herramientas generan CSV, JSON, overlays, gráficos, PDF y Excel;
  - se corrige que SciPy es una referencia conceptual, no una llamada directa del pipeline;
  - se diferencia interpolación temporal e interpolación espacial mediante una misma relación lineal;
  - se incorpora el ejemplo real de la ventana centrada de cinco fotogramas;
  - se añaden dos clips HyperFrames: señal del centro de caderas y construcción geométrica de `W0` y las variables;
  - se actualizan las notas del expositor y la correspondencia con la web.

### Versión 4

- Archivo: `presentacion_proceso_interno_sentadilla_v4.pptx`.
- Diapositivas: 22.
- Fecha: 12 de agosto de 2026.
- Cambios principales:
  - se incorpora una muestra real de `landmarks.csv` con coordenadas normalizadas y visibilidad;
  - se explica que el número de filas es `fotogramas con pose × 13 puntos seleccionados`;
  - se muestra cómo `frame_quality.csv` deriva una decisión por fotograma;
  - se precisa que `valid_for_analysis` exige ocho puntos centrales y una referencia distal por cada pie;
  - se incluyen las fórmulas de fotogramas procesados, fotogramas válidos y promedio de puntos detectados;
  - se delimita la participación de OpenCV en la decodificación de fotogramas;
  - se relacionan ambos CSV con las gráficas “Disponibilidad de pose por fotograma” y “Visibilidad por punto anatómico”.

## Correspondencia de cambios

| Cambio | Guion | Presentación | Evidencia reproducible |
|---|---|---|---|
| Producción de artefactos | diapositiva 4 | flujo MediaPipe–derivados | código de `pose_video.py`, `evidence.py` y `exports.py` |
| Datos primarios de pose | diapositiva 7 | muestra tabular | `landmarks.csv` |
| Decisión por fotograma | diapositiva 8 | muestra tabular y regla binaria | `frame_quality.csv` y `pose_video.py` |
| Indicadores de pose | diapositiva 9 | fórmulas y resultados | `pose_summary.json` y `quality_gate.py` |
| Trazabilidad visual de pose | diapositiva 10 | imagen y gráfico editable | `pose_quality.png`, `frame_quality.csv` y `landmarks.csv` |
| Interpolación temporal y espacial | diapositiva 12 | esquema lineal comparativo | `segmentation.py` y `biomechanics.py` |
| Mediana y promedio centrados | diapositiva 13 | ejemplo del fotograma 388 | `frame_phases.csv` |
| Señal animada | diapositiva 11 | portada enlazada | `hyperframes_senal_caderas/senal_caderas_animada.mp4` |
| Geometría animada | diapositiva 19 | portada enlazada | `hyperframes_geometria_variables/construccion_geometrica_variables.mp4` |

## Regeneración de la instantánea

```powershell
powershell -ExecutionPolicy Bypass -File scripts\sync_presentation_pptx_to_markdown.ps1
```

El script conserva el PowerPoint, valida la salida UTF-8 y reemplaza la instantánea anterior solo si AnyDoc termina correctamente.
