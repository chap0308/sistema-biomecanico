# Evidencia de la fase F6: verificación y trazabilidad

## 1. Propósito

La fase F6 consolida la evidencia técnica del prototipo. No añade nuevas
compensaciones ni modifica los umbrales provisionales. Su función es demostrar
que los resultados implementados en las fases anteriores pueden explicarse,
reproducirse y verificarse mediante pruebas, artefactos visuales y diagramas
editables.

## 2. Verificación por capas

| Capa | Verificación | Evidencia |
|---|---|---|
| Procesamiento Python | Pruebas unitarias y de integración con `pytest` | Pose, segmentación, variables, reglas, API, comparación y exportaciones |
| Componentes web | Pruebas con Vitest | Formularios y evidencia de variables y reglas |
| Flujo completo | Pruebas con Playwright | Acceso, registro, resultado, evaluación experta, comparación y descargas |
| Presentación móvil | Playwright a 390 × 844 px | Resultado y comparación sin desbordamiento de página |
| Navegación por teclado | Playwright | Enlace para omitir la cabecera y enfocar el contenido |
| Diagramas | Validación XML y apertura en diagrams.net | Siete archivos `.drawio` editables |

Las pruebas E2E emplean servicios locales reales de Next.js, FastAPI y
Supabase. No sustituyen la evaluación final con la muestra ni con los
evaluadores expertos del estudio.

## 3. Flujos cubiertos

| Flujo | Prueba E2E |
|---|---|
| Página pública | `home.spec.ts` |
| Autenticación y rol investigador | `auth.spec.ts` |
| Instrumento 1 y carga de video | `case-intake.spec.ts` |
| Overlay, eventos, variables y reglas | `case-results.spec.ts` |
| Instrumento 3 ciego | `expert-evaluation.spec.ts` |
| Referencia experta, métricas y exportación | `case-comparison.spec.ts` |
| Presentación móvil y teclado | `responsive-accessibility.spec.ts` |

## 4. Trazabilidad con los objetivos específicos

| Objetivo específico | Resultado demostrable | Evidencia principal |
|---|---|---|
| OE1. Identificar puntos anatómicos clave en 2D | Overlay, disponibilidad, calidad y promedio de puntos clave por fotograma | `evidencia_objetivo_1_estimacion_pose_2d.md` |
| OE2. Definir variables biomecánicas observables | Fases, series temporales, fórmulas y métricas por repetición | `evidencia_objetivo_2_variables_biomecanicas.md` |
| OE3. Diseñar criterios biomecánicos interpretables | Valor, umbral, margen, versión y decisión independiente por patrón | `evidencia_objetivo_3_criterios_interpretables.md` |
| OE4. Implementar un prototipo funcional | Registro, procesamiento, historial, resultados y exportaciones persistentes | `evidencia_objetivo_4_prototipo_funcional.md` |
| OE5. Evaluar el desempeño técnico | Referencia experta consolidada, matriz de clasificación, F1-score y Kappa | `evidencia_objetivo_5_desempeno_tecnico.md` |

El archivo `trazabilidad_objetivos_evidencias.drawio` presenta esta relación
como objetivo, resultado observable, mecanismo de verificación y documento.

## 5. Evidencia visual

Se conservaron capturas de:

- resultado del investigador en escritorio;
- resultado del investigador en vista móvil;
- comparación experta-sistema en vista móvil;
- arquitectura abierta como formas editables en diagrams.net.

Las gráficas técnicas utilizan carga diferida. Para la captura de página
completa se recorrió el documento antes de generar la imagen y se verificó que
las seis imágenes del caso tuvieran carga completa y dimensiones naturales
mayores que cero.

## 6. Diagramas para sustentación

Los diagramas editables se encuentran en `docs/diagramas/fase6/`:

1. arquitectura general;
2. flujo del investigador;
3. flujo del evaluador experto;
4. control de calidad del video;
5. secuencia de procesamiento;
6. secuencia de comparación y métricas;
7. trazabilidad de objetivos y evidencias.

La fuente Mermaid de los flujos principales se conserva en
`flujos_sistema_roles_y_evidencias_fase6.md`. Los `.drawio` son la versión
destinada a edición y presentación.

## 7. Alcance de la evidencia

La fase demuestra funcionamiento técnico y trazabilidad del prototipo. No
demuestra todavía desempeño definitivo, porque las métricas disponibles
provienen de un piloto de integración con pocos pares comparables. La
evaluación final del OE5 requiere la muestra aprobada, evaluaciones expertas
independientes y umbrales estabilizados.

## 8. Resultado de la verificación

| Comando o conjunto | Resultado |
|---|---:|
| Pruebas Python específicas de sentadilla y diagramas | 20 aprobadas |
| Vitest | 6 aprobadas |
| ESLint | Sin errores |
| Compilación de producción de Next.js | Correcta |
| Playwright público e investigador | 10 aprobadas |
| Playwright evaluador experto | 2 aprobadas |

La suite Python global obtuvo 261 pruebas aprobadas y dos fallos externos al
alcance de sentadilla: una prueba RAG intentó usar una conexión Supabase remota
no disponible y otra encontró un bloqueo de almacenamiento Qdrant local. Las
pruebas específicas de esta fase no dependen de esos servicios y finalizaron
correctamente.
