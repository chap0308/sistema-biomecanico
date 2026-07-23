# Backlog técnico inicial de la tesis de sentadilla bilateral

## Propósito de este archivo

Este archivo queda como lista de ejecución breve. No reemplaza al plan maestro.

Su función es concentrar solo las tareas inmediatas de arranque para que podamos abrir el desarrollo sin volver a revisar todo el documento grande.

## Referencia principal

El detalle metodológico, la arquitectura, el stack y la justificación de cada fase están en [plan_desarrollo_tecnico_sentadilla.md](/D:/sistema-biomecanico/docs/plan_desarrollo_tecnico_sentadilla.md).

## Backlog inmediato

### Tarea 1. Crear rama de desarrollo dedicada — completada

Resultado esperado:

- aislar el trabajo técnico de sentadilla del resto del repo.

### Tarea 2. Crear estructura del módulo `src/squat/` — completada

Resultado esperado:

- módulo aislado para la tesis.

### Tarea 3. Crear `tests/squat/` — completada

Resultado esperado:

- base de validación desde el inicio.

### Tarea 4. Crear `data/sentadilla_bilateral/` — completada

Resultado esperado:

- línea de datos separada y reproducible.

### Tarea 5. Crear `data/sentadilla_bilateral/metadata/casos.csv` — completada

Resultado esperado:

- trazabilidad base de la muestra.

### Tarea 6. Crear `scripts/run_squat_analysis.py` — completada

Resultado esperado:

- punto único de ejecución para la línea de sentadilla.

### Tarea 7. Definir contrato JSON mínimo de salida — completada

Resultado esperado:

- salida legible por script, pruebas e instrumentos.

### Tarea 8. Definir overlay mínimo esperado — definido; implementación pendiente en Fase 2

Debe mostrar como mínimo:

- landmarks;
- ejes o líneas relevantes;
- texto breve con fase o variables principales.

### Tarea 9. Definir política de anonimización facial — definida; implementación pendiente

Resultado esperado:

- decidir si la anonimización se aplica al video exportado, al overlay o a ambos.

### Tarea 10. Definir pruebas iniciales — completada

Pruebas mínimas:

- importación del módulo;
- creación de modelos;
- rutas válidas de salida;
- contrato de resultado.

## Orden sugerido de ejecución

1. rama dedicada;
2. estructura `src/squat/`, `tests/squat/` y `data/sentadilla_bilateral/`;
3. `casos.csv` vacío con cabeceras;
4. `run_squat_analysis.py` inicial;
5. contrato JSON de salida;
6. overlay base;
7. anonimización facial;
8. adaptación de pose a video.

## Resultado del incremento

El comando inicial ya inspecciona un archivo con OpenCV, registra metadatos reproducibles y genera un JSON versionado. Un video legible permanece como `pendiente_revision_protocolo` hasta que el investigador lo acepte con el Instrumento 1; solo entonces el contrato devuelve `listo_para_pose`.

La prueba de integración local se ejecutó con `data/videos/knee_valgus_dynamic/squat-1.mp4`. El archivo fue técnicamente legible, con 151 fotogramas, resolución de 474 por 850 píxeles y duración aproximada de 6,04 segundos. No se incorporó a la muestra oficial.

## Siguiente bloque

La próxima tarea activa es la Fase 2:

1. adaptar MediaPipe Pose al procesamiento secuencial de video;
2. exportar puntos anatómicos clave por fotograma;
3. calcular fotogramas procesados y fotogramas válidos;
4. generar un overlay mínimo con esqueleto, estado del fotograma y trazabilidad del caso;
5. aplicar anonimización facial a los artefactos compartibles.

## Verificación técnica

- pruebas específicas de sentadilla: 20 aprobadas, más la prueba general de importación del módulo;
- cobertura de `src/squat`: 100 % de líneas;
- prueba real de registro técnico: aprobada;
- suite general del repositorio: 179 pruebas aprobadas y 2 fallos de infraestructura ajenos al módulo de sentadilla, asociados a la conexión externa de Supabase y al bloqueo de una instancia local de Qdrant.

## Avance posterior: Fase 2

La extracción base de pose 2D ya fue implementada con:

- procesamiento secuencial de video con OpenCV;
- MediaPipe Pose en modo temporal;
- exportación de 13 puntos anatómicos relevantes por fotograma;
- cálculo de fotogramas procesados, pose detectada y fotogramas válidos;
- `landmarks.csv`, `frame_quality.csv` y `pose_summary.json`;
- overlay anonimizado mediante pixelado facial;
- gráfica temporal de visibilidad y disponibilidad de puntos;
- evidencia Mermaid vinculada al Objetivo Específico 1.

La siguiente fase activa es la segmentación temporal de la sentadilla: reposo inicial, descenso, punto de máxima profundidad, ascenso y cierre.
